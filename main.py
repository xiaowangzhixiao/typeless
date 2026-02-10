"""
Typeless Mac - AI 语音输入法主程序
"""
import os
import sys
import logging
import signal
import threading
import time
import yaml
from pathlib import Path
from dotenv import load_dotenv

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from asr import ASREngine
from llm import LLMProcessor
from audio_recorder import SmartRecorder
from input_handler import InputHandler
from hotkey import HotkeyListener
from ui import StatusWindow

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('typeless.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class TypelessApp:
    """Typeless 主应用"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """初始化应用"""
        logger.info("=" * 60)
        logger.info("启动 Typeless Mac")
        logger.info("=" * 60)
        
        # 加载配置
        self.config = self.load_config(config_path)
        
        # 加载环境变量
        load_dotenv()
        
        # 初始化组件
        self.asr_engine = None
        self.llm_processor = None
        self.recorder = None
        self.input_handler = None
        self.hotkey_listener = None
        self.status_window = None
        
        # 状态
        self.is_recording = False
        self.is_processing = False
        self._shutdown_lock = threading.Lock()
        self._is_shutting_down = False
        self._stop_event = threading.Event()
        
        self.initialize_components()
    
    def load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"配置已加载: {config_path}")
            return config
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            sys.exit(1)
    
    def initialize_components(self):
        """初始化所有组件"""
        try:
            # ASR 引擎
            asr_config = self.config['asr']
            logger.info("初始化 ASR 引擎...")
            self.asr_engine = ASREngine(
                model_size=asr_config['model_size'],
                device=asr_config['device'],
                compute_type=asr_config['compute_type'],
                language=asr_config['language'],
                cache_dir=asr_config.get('cache_dir', '~/.cache/whisper')
            )
            preload_strategy = asr_config.get('preload_strategy', 'eager').lower()
            if preload_strategy not in {'lazy', 'background', 'eager'}:
                logger.warning(f"未知的 ASR preload_strategy: {preload_strategy}，回退为 eager")
                preload_strategy = 'eager'

            logger.info(
                f"ASR 预加载策略: {preload_strategy}，缓存目录: {asr_config.get('cache_dir', '~/.cache/whisper')}"
            )

            if preload_strategy == 'eager':
                logger.info("ASR 预加载模式: eager（启动时同步加载）")
                self.asr_engine.load_model()
            elif preload_strategy == 'background':
                logger.info("ASR 预加载模式: background（后台加载，不阻塞启动）")

                def _warmup_asr_model():
                    try:
                        self.asr_engine.load_model()
                    except Exception as e:
                        logger.warning(f"ASR 后台预热失败，将在首次识别时重试: {e}")

                threading.Thread(
                    target=_warmup_asr_model,
                    daemon=True,
                    name="asr-preload"
                ).start()
            else:
                logger.info("ASR 预加载模式: lazy（首次识别时再加载）")
            
            # LLM 处理器
            llm_config = self.config['llm']
            provider = os.getenv('LLM_PROVIDER', llm_config.get('provider', 'openrouter')).lower()
            
            logger.info(f"初始化 LLM 处理器（Provider: {provider}）...")
            
            if provider == 'openrouter':
                api_key = os.getenv('OPENROUTER_API_KEY')
                if not api_key:
                    logger.error("未设置 OPENROUTER_API_KEY 环境变量")
                    sys.exit(1)
                openrouter_model = os.getenv('DEFAULT_MODEL', llm_config.get('model', 'anthropic/claude-3.5-sonnet'))
                
                self.llm_processor = LLMProcessor(
                    provider='openrouter',
                    api_key=api_key,
                    model=openrouter_model,
                    system_prompt=llm_config['system_prompt'],
                    max_tokens=llm_config['max_tokens'],
                    temperature=llm_config['temperature'],
                    timeout=llm_config['timeout']
                )
            
            elif provider == 'ollama':
                ollama_config = llm_config.get('ollama', {})
                ollama_model = os.getenv('OLLAMA_MODEL', ollama_config.get('model', 'qwen3:0.6b'))
                ollama_base_url = os.getenv('OLLAMA_BASE_URL', ollama_config.get('base_url', 'http://localhost:11434'))
                
                self.llm_processor = LLMProcessor(
                    provider='ollama',
                    model=ollama_model,
                    ollama_base_url=ollama_base_url,
                    system_prompt=llm_config['system_prompt'],
                    max_tokens=llm_config['max_tokens'],
                    temperature=llm_config['temperature'],
                    timeout=llm_config['timeout']
                )
            
            else:
                logger.error(f"不支持的 LLM provider: {provider}")
                sys.exit(1)
            
            # 录音器
            audio_config = self.config['audio']
            logger.info("初始化录音器...")
            self.recorder = SmartRecorder(
                sample_rate=audio_config['sample_rate'],
                channels=audio_config['channels'],
                silence_threshold=audio_config['silence_threshold'],
                silence_duration=audio_config['silence_duration'],
                max_duration=audio_config['max_duration']
            )
            
            # 输入处理器
            logger.info("初始化输入处理器...")
            self.input_handler = InputHandler()
            
            # 快捷键监听
            hotkey_raw = self.config['app']['hotkey']
            # 转换快捷键格式：cmd+shift+space -> <cmd>+<shift>+space
            hotkey = hotkey_raw.replace('cmd', '<cmd>').replace('shift', '<shift>').replace('ctrl', '<ctrl>').replace('alt', '<alt>')
            logger.info(f"初始化快捷键监听: {hotkey_raw} -> {hotkey}")
            self.hotkey_listener = HotkeyListener(hotkey=hotkey)
            self.hotkey_listener.set_callback(self.on_hotkey_pressed)
            
            # 状态窗口
            if self.config['ui']['show_window']:
                logger.info("初始化状态窗口...")
                self.status_window = StatusWindow(
                    opacity=self.config['ui']['window_opacity']
                )
                self.status_window.start()
            
            logger.info("所有组件初始化完成 ✓")
            
        except Exception as e:
            logger.error(f"组件初始化失败: {e}", exc_info=True)
            sys.exit(1)
    
    def on_hotkey_pressed(self):
        """快捷键回调"""
        if self.is_processing:
            logger.info("正在处理中，忽略快捷键")
            return
        
        if not self.is_recording:
            # 开始录音
            self.start_recording()
        else:
            # 停止录音并处理
            self.stop_recording_and_process()
    
    def start_recording(self):
        """开始录音"""
        self.is_recording = True
        
        if self.status_window:
            self.status_window.show_recording()
        
        logger.info("🎤 开始录音")
        self.recorder.start_recording()
    
    def stop_recording_and_process(self):
        """停止录音并处理"""
        self.is_recording = False
        self.is_processing = True
        
        if self.status_window:
            self.status_window.show_processing("停止录音")
        
        logger.info("⏸ 停止录音")
        
        # 在新线程中处理，避免阻塞快捷键监听
        thread = threading.Thread(target=self.process_audio, daemon=True)
        thread.start()
    
    def process_audio(self):
        """处理音频（识别 + 润色 + 输入）"""
        try:
            # 停止录音
            audio_data = self.recorder.stop_recording()
            
            if audio_data is None or len(audio_data) < 1000:
                logger.warning("录音数据太短，跳过处理")
                if self.status_window:
                    self.status_window.update_message("⚠️ 录音太短")
                    time.sleep(1)
                    self.status_window.hide()
                self.is_processing = False
                return
            
            # 转换为 float32 格式（Whisper 要求）
            audio_float = audio_data.flatten().astype('float32') / 32768.0
            
            # 语音识别
            if self.status_window:
                self.status_window.show_processing("识别中")
            
            logger.info("🎯 开始语音识别")
            asr_result = self.asr_engine.transcribe_numpy(audio_float)
            raw_text = asr_result['text']
            
            if not raw_text:
                logger.warning("未识别到文本")
                if self.status_window:
                    self.status_window.update_message("⚠️ 未识别到内容")
                    time.sleep(1)
                    self.status_window.hide()
                self.is_processing = False
                return
            
            logger.info(f"识别结果: {raw_text}")
            
            # 文本润色
            offline_mode = self.config['features']['offline_mode']
            
            if offline_mode:
                final_text = raw_text
                logger.info("离线模式，跳过润色")
            else:
                if self.status_window:
                    self.status_window.show_processing("润色中")
                
                logger.info("🤖 开始文本润色")
                llm_result = self.llm_processor.polish(raw_text)
                final_text = llm_result['polished_text']
                
                logger.info(f"润色结果: {final_text}")
            
            # 自动输入
            if self.config['features']['auto_paste']:
                if self.status_window:
                    self.status_window.complete_processing()
                    time.sleep(0.2)
                    self.status_window.update_message("输入中")
                
                logger.info("⌨️ 自动输入文本")
                time.sleep(0.6)  # 等待快捷键按键释放并回到目标输入焦点
                self.input_handler.paste_text(final_text)
            
            # 完成
            if self.status_window:
                self.status_window.update_message("完成")
                time.sleep(0.8)
                self.status_window.hide()
            
            logger.info("✅ 处理完成")
            
        except Exception as e:
            logger.error(f"处理失败: {e}", exc_info=True)
            if self.status_window:
                self.status_window.update_message("❌ 出错了")
                time.sleep(1)
                self.status_window.hide()
        
        finally:
            self.is_processing = False
    
    def run(self):
        """运行应用"""
        try:
            # 在后台线程启动快捷键监听
            import threading
            hotkey_thread = threading.Thread(target=self.hotkey_listener.start, daemon=True)
            hotkey_thread.start()
            
            logger.info("=" * 60)
            logger.info(f"✨ Typeless Mac 已启动")
            logger.info(f"📌 快捷键: {self.config['app']['hotkey']}")
            logger.info(f"🎤 ASR: {self.config['asr']['model_size']} 模型")
            logger.info(f"🤖 LLM: {self.config['llm']['model']}")
            logger.info("=" * 60)
            logger.info("按快捷键开始使用，按 Ctrl+C 退出")
            logger.info("=" * 60)
            
            # 如果有 UI，在主线程运行 UI 事件循环
            if self.status_window:
                logger.info("在主线程运行 UI")
                self.status_window.run_mainloop()
                if not self._is_shutting_down:
                    self.shutdown()
            else:
                # 无 UI 模式，保持运行
                logger.info("无 UI 模式")
                while not self._stop_event.is_set():
                    time.sleep(0.2)
                
        except KeyboardInterrupt:
            logger.info("\n正在退出...")
            self.shutdown()
    
    def shutdown(self):
        """关闭应用"""
        with self._shutdown_lock:
            if self._is_shutting_down:
                return
            self._is_shutting_down = True

        logger.info("关闭应用...")
        self._stop_event.set()
        
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except Exception as e:
                logger.warning(f"停止快捷键监听失败: {e}")
        
        if self.status_window:
            try:
                self.status_window.stop()
            except Exception as e:
                logger.warning(f"停止状态窗口失败: {e}")
        
        logger.info("再见！👋")


def main():
    """主函数"""
    app = TypelessApp()

    def _handle_exit_signal(signum, _frame):
        sig_name = signal.Signals(signum).name
        logger.info(f"接收到信号 {sig_name}，准备退出...")
        app.shutdown()

    signal.signal(signal.SIGINT, _handle_exit_signal)
    signal.signal(signal.SIGTERM, _handle_exit_signal)
    app.run()


if __name__ == "__main__":
    main()
