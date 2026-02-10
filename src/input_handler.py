"""
输入处理模块 - 自动粘贴文本到当前应用
"""
import logging
import time
import pyperclip
from pynput.keyboard import Controller, Key

logger = logging.getLogger(__name__)


class InputHandler:
    """文本输入处理器"""
    
    def __init__(self):
        self.keyboard = Controller()
        logger.info("初始化输入处理器")
    
    def paste_text(self, text: str):
        """
        将文本粘贴到当前光标位置
        
        Args:
            text: 要粘贴的文本
        """
        if not text:
            logger.warning("文本为空，跳过粘贴")
            return
        
        try:
            logger.info(f"准备粘贴文本: {text[:50]}..." if len(text) > 50 else f"准备粘贴文本: {text}")
            
            # 保存当前剪贴板内容
            original_clipboard = ""
            try:
                original_clipboard = pyperclip.paste()
            except:
                pass
            
            # 将文本复制到剪贴板
            pyperclip.copy(text)

            # 等待一小段时间确保复制完成
            time.sleep(0.12)

            # 模拟 Cmd+V 粘贴
            with self.keyboard.pressed(Key.cmd):
                self.keyboard.press('v')
                self.keyboard.release('v')
            logger.info("已触发 Cmd+V")
            
            logger.info("文本已粘贴（已发送粘贴按键）")
            
            # 等待粘贴完成后恢复原剪贴板（可选）
            time.sleep(1.0)
            try:
                pyperclip.copy(original_clipboard)
                logger.info("已恢复原剪贴板")
            except:
                pass
            
        except Exception as e:
            logger.error(f"粘贴失败: {e}")
            raise
    
    def type_text(self, text: str, interval: float = 0.01):
        """
        逐字符输入文本（较慢但更可靠）
        
        Args:
            text: 要输入的文本
            interval: 字符间隔（秒）
        """
        if not text:
            logger.warning("文本为空，跳过输入")
            return
        
        try:
            logger.info(f"开始输入文本: {text[:50]}...")
            
            for char in text:
                self.keyboard.type(char)
                time.sleep(interval)
            
            logger.info("文本输入完成")
            
        except Exception as e:
            logger.error(f"输入失败: {e}")
            raise
    
    def clear_current_line(self):
        """清除当前行"""
        try:
            # Cmd+Shift+Left 选中当前行
            with self.keyboard.pressed(Key.cmd):
                with self.keyboard.pressed(Key.shift):
                    self.keyboard.press(Key.left)
                    self.keyboard.release(Key.left)
            
            # Delete 删除
            self.keyboard.press(Key.backspace)
            self.keyboard.release(Key.backspace)
            
            logger.info("已清除当前行")
        except Exception as e:
            logger.error(f"清除失败: {e}")


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    handler = InputHandler()
    
    print("3 秒后将粘贴文本，请切换到任意文本编辑器...")
    time.sleep(3)
    
    handler.paste_text("这是一段测试文本 🎉")
