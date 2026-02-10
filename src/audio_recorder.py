"""
音频录制模块
"""
import os
import logging
import tempfile
import numpy as np
import sounddevice as sd
import wave
from typing import Optional
from threading import Event

logger = logging.getLogger(__name__)


class AudioRecorder:
    """音频录制器"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        """
        初始化录音器
        
        Args:
            sample_rate: 采样率（Hz）
            channels: 声道数
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.audio_data = []
        self.stream = None
        
        logger.info(f"初始化音频录制器: {sample_rate}Hz, {channels}声道")
    
    def start_recording(self):
        """开始录音"""
        if self.recording:
            logger.warning("已在录音中")
            return
        
        self.recording = True
        self.audio_data = []
        
        logger.info("开始录音...")
        
        def callback(indata, frames, time, status):
            if status:
                logger.warning(f"录音状态: {status}")
            if self.recording:
                self.audio_data.append(indata.copy())
        
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=callback,
            dtype='int16'
        )
        self.stream.start()
    
    def stop_recording(self) -> Optional[np.ndarray]:
        """
        停止录音
        
        Returns:
            录音数据（NumPy 数组）
        """
        if not self.recording:
            logger.warning("未在录音中")
            return None
        
        self.recording = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        logger.info("停止录音")
        
        if not self.audio_data:
            logger.warning("没有录制到音频数据")
            return None
        
        # 合并音频数据
        audio_array = np.concatenate(self.audio_data, axis=0)
        
        logger.info(f"录音完成: {len(audio_array)} 样本 ({len(audio_array)/self.sample_rate:.1f}秒)")
        
        return audio_array
    
    def save_audio(self, audio_data: np.ndarray, filename: Optional[str] = None) -> str:
        """
        保存音频到文件
        
        Args:
            audio_data: 音频数据
            filename: 文件名（可选，默认使用临时文件）
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            fd, filename = tempfile.mkstemp(suffix='.wav')
            os.close(fd)
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        logger.info(f"音频已保存到: {filename}")
        return filename
    
    def record_audio(self, duration: float) -> np.ndarray:
        """
        录制指定时长的音频
        
        Args:
            duration: 录音时长（秒）
            
        Returns:
            音频数据
        """
        logger.info(f"录制 {duration} 秒音频...")
        
        audio_data = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='int16'
        )
        sd.wait()
        
        logger.info("录制完成")
        return audio_data


class SmartRecorder(AudioRecorder):
    """智能录音器（支持静音检测）"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1,
                 silence_threshold: float = 500, silence_duration: float = 2.0,
                 max_duration: float = 60):
        """
        初始化智能录音器
        
        Args:
            sample_rate: 采样率
            channels: 声道数
            silence_threshold: 静音阈值（音量 RMS）
            silence_duration: 多少秒静音后自动停止
            max_duration: 最大录音时长
        """
        super().__init__(sample_rate, channels)
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.max_duration = max_duration
        self.stop_event = Event()
        
        logger.info(f"智能录音器: 静音阈值={silence_threshold}, 静音时长={silence_duration}s")
    
    def is_silent(self, audio_chunk: np.ndarray) -> bool:
        """判断音频片段是否为静音"""
        rms = np.sqrt(np.mean(audio_chunk.astype(float) ** 2))
        return rms < self.silence_threshold
    
    def record_until_silence(self) -> Optional[np.ndarray]:
        """
        录音直到检测到持续静音
        
        Returns:
            录音数据
        """
        logger.info("开始智能录音（检测静音）...")
        
        audio_data = []
        silence_frames = 0
        silence_threshold_frames = int(self.silence_duration * self.sample_rate / 1024)
        max_frames = int(self.max_duration * self.sample_rate / 1024)
        frame_count = 0
        
        def callback(indata, frames, time, status):
            nonlocal silence_frames, frame_count
            
            if status:
                logger.warning(f"录音状态: {status}")
            
            audio_data.append(indata.copy())
            frame_count += 1
            
            # 检查是否静音
            if self.is_silent(indata):
                silence_frames += 1
            else:
                silence_frames = 0
            
            # 达到静音阈值或最大时长
            if silence_frames >= silence_threshold_frames or frame_count >= max_frames:
                self.stop_event.set()
        
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=callback,
            dtype='int16',
            blocksize=1024
        ):
            self.stop_event.wait()
        
        if not audio_data:
            logger.warning("没有录制到音频数据")
            return None
        
        audio_array = np.concatenate(audio_data, axis=0)
        
        logger.info(f"录音完成: {len(audio_array)/self.sample_rate:.1f}秒")
        
        return audio_array


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    recorder = SmartRecorder()
    
    print("开始录音，说话后停顿 2 秒将自动停止...")
    audio = recorder.record_until_silence()
    
    if audio is not None:
        filename = recorder.save_audio(audio, "test_recording.wav")
        print(f"已保存到: {filename}")
