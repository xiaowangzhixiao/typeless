"""
快捷键监听模块
"""
import logging
from pynput import keyboard
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class HotkeyListener:
    """快捷键监听器"""
    
    def __init__(self, hotkey: str = "<cmd>+<shift>+space"):
        """
        初始化快捷键监听器
        
        Args:
            hotkey: 快捷键组合（如 "<cmd>+<shift>+space"）
        """
        self.hotkey = hotkey
        self.callback: Optional[Callable] = None
        self.listener: Optional[keyboard.GlobalHotKeys] = None
        
        logger.info(f"初始化快捷键监听器: {hotkey}")
    
    def set_callback(self, callback: Callable):
        """
        设置快捷键回调函数
        
        Args:
            callback: 按下快捷键时调用的函数
        """
        self.callback = callback
    
    def start(self):
        """开始监听"""
        if self.listener is not None:
            logger.warning("监听器已在运行")
            return
        
        if self.callback is None:
            logger.error("未设置回调函数")
            return
        
        # pynput的GlobalHotKeys需要特殊的格式
        # 将 <cmd>+<shift>+space 转换为正确格式
        # 特殊键映射
        special_keys_map = {
            'space': keyboard.Key.space,
            'enter': keyboard.Key.enter,
            'return': keyboard.Key.enter,
            'tab': keyboard.Key.tab,
            'esc': keyboard.Key.esc,
            'escape': keyboard.Key.esc,
            'backspace': keyboard.Key.backspace,
        }
        
        # 解析快捷键
        hotkey_parsed = self.hotkey
        for key_name, key_obj in special_keys_map.items():
            if key_name in hotkey_parsed:
                # 将 'space' 替换为 '<space>'
                hotkey_parsed = hotkey_parsed.replace(key_name, f'<{key_obj.name}>')
        
        logger.info(f"解析快捷键: {self.hotkey} -> {hotkey_parsed}")
        
        hotkeys = {
            hotkey_parsed: self.callback
        }
        
        self.listener = keyboard.GlobalHotKeys(hotkeys)
        self.listener.start()
        
        logger.info(f"快捷键监听已启动: {hotkey_parsed}")
    
    def stop(self):
        """停止监听"""
        if self.listener is None:
            return
        
        self.listener.stop()
        self.listener = None
        
        logger.info("快捷键监听已停止")


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    import time
    
    def on_hotkey():
        print("快捷键被按下！")
    
    listener = HotkeyListener()
    listener.set_callback(on_hotkey)
    listener.start()
    
    print("按 Cmd+Shift+Space 测试快捷键，按 Ctrl+C 退出")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        listener.stop()
        print("已停止")
