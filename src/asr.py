"""
ASR 模块 - 使用 faster-whisper 进行本地语音识别
"""
import os
import logging
import threading
import time
from typing import Optional
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class ASREngine:
    """语音识别引擎"""
    
    def __init__(self, model_size: str = "tiny", device: str = "cpu", 
                 compute_type: str = "int8", language: str = "zh",
                 cache_dir: str = "~/.cache/whisper"):
        """
        初始化 ASR 引擎
        
        Args:
            model_size: 模型大小 (tiny, base, small, medium, large-v3-turbo, large)
            device: 计算设备 (cpu, cuda)
            compute_type: 计算类型 (int8, float16, float32)
            language: 主要语言代码 (zh, en, auto)
            cache_dir: 模型缓存目录
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = None if language == "auto" else language
        self.cache_dir = os.path.expanduser(cache_dir)
        self.model: Optional[WhisperModel] = None
        self._model_lock = threading.Lock()
        
        logger.info(
            f"初始化 ASR 引擎: model={model_size}, device={device}, cache_dir={self.cache_dir}"
        )
    
    def load_model(self):
        """加载模型（首次使用时会自动下载）"""
        if self.model is not None:
            logger.info("模型已加载，跳过")
            return

        with self._model_lock:
            if self.model is not None:
                logger.info("模型已加载，跳过")
                return

            started_at = time.perf_counter()
            try:
                logger.info(f"正在加载 Whisper 模型: {self.model_size}...")
                try:
                    # 优先从本地缓存加载，避免每次启动都等待远程校验。
                    self.model = WhisperModel(
                        self.model_size,
                        device=self.device,
                        compute_type=self.compute_type,
                        download_root=self.cache_dir,
                        local_files_only=True
                    )
                    elapsed = time.perf_counter() - started_at
                    logger.info(f"模型已从本地缓存加载成功，耗时 {elapsed:.2f}s")
                except Exception as cache_error:
                    logger.warning(f"本地缓存不可用，尝试联网下载模型: {cache_error}")
                    self.model = WhisperModel(
                        self.model_size,
                        device=self.device,
                        compute_type=self.compute_type,
                        download_root=self.cache_dir,
                        local_files_only=False
                    )
                    elapsed = time.perf_counter() - started_at
                    logger.info(f"模型下载并加载成功，耗时 {elapsed:.2f}s")
            except Exception as e:
                elapsed = time.perf_counter() - started_at
                logger.error(f"模型加载失败（耗时 {elapsed:.2f}s）: {e}")
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
