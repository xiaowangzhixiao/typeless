"""
ASR 模块 - 使用 faster-whisper 进行本地语音识别
"""
import os
import logging
from typing import Optional
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class ASREngine:
    """语音识别引擎"""
    
    def __init__(self, model_size: str = "tiny", device: str = "cpu", 
                 compute_type: str = "int8", language: str = "zh"):
        """
        初始化 ASR 引擎
        
        Args:
            model_size: 模型大小 (tiny, base, small, medium, large)
            device: 计算设备 (cpu, cuda)
            compute_type: 计算类型 (int8, float16, float32)
            language: 主要语言代码 (zh, en, auto)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = None if language == "auto" else language
        self.model: Optional[WhisperModel] = None
        
        logger.info(f"初始化 ASR 引擎: model={model_size}, device={device}")
    
    def load_model(self):
        """加载模型（首次使用时会自动下载）"""
        if self.model is not None:
            logger.info("模型已加载，跳过")
            return
        
        try:
            logger.info(f"正在加载 Whisper 模型: {self.model_size}...")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=os.path.expanduser("~/.cache/whisper")
            )
            logger.info("模型加载成功")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def transcribe(self, audio_file: str) -> dict:
        """
        转录音频文件
        
        Args:
            audio_file: 音频文件路径
            
        Returns:
            包含识别结果的字典 {text, language, segments}
        """
        if self.model is None:
            self.load_model()
        
        try:
            logger.info(f"开始转录音频: {audio_file}")
            segments, info = self.model.transcribe(
                audio_file,
                language=self.language,
                vad_filter=True,  # 启用 VAD 过滤静音
                beam_size=5
            )
            
            # 收集所有片段的文本
            text_parts = []
            all_segments = []
            
            for segment in segments:
                text_parts.append(segment.text)
                all_segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                })
            
            full_text = "".join(text_parts).strip()
            
            result = {
                "text": full_text,
                "language": info.language,
                "language_probability": info.language_probability,
                "segments": all_segments
            }
            
            logger.info(f"转录完成: 语言={info.language}, 文本长度={len(full_text)}")
            logger.debug(f"识别文本: {full_text}")
            
            return result
            
        except Exception as e:
            logger.error(f"转录失败: {e}")
            raise
    
    def transcribe_numpy(self, audio_data) -> dict:
        """
        转录 NumPy 数组格式的音频
        
        Args:
            audio_data: NumPy 数组 (float32, 采样率 16000)
            
        Returns:
            包含识别结果的字典
        """
        if self.model is None:
            self.load_model()
        
        try:
            logger.info("开始转录音频数据")
            segments, info = self.model.transcribe(
                audio_data,
                language=self.language,
                vad_filter=True,
                beam_size=5
            )
            
            text_parts = []
            all_segments = []
            
            for segment in segments:
                text_parts.append(segment.text)
                all_segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                })
            
            full_text = "".join(text_parts).strip()
            
            result = {
                "text": full_text,
                "language": info.language,
                "language_probability": info.language_probability,
                "segments": all_segments
            }
            
            logger.info(f"转录完成: {full_text}")
            return result
            
        except Exception as e:
            logger.error(f"转录失败: {e}")
            raise


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    asr = ASREngine(model_size="tiny", language="zh")
    
    # 这里可以测试一个音频文件
    # result = asr.transcribe("test.wav")
    # print(result["text"])
