"""
UI 模块 - 状态显示窗口
"""
import logging
import tkinter as tk
from tkinter import ttk
from threading import Thread
from typing import Optional

logger = logging.getLogger(__name__)


class StatusWindow:
    """状态显示窗口"""
    
    def __init__(self, opacity: float = 0.9):
        """
        初始化状态窗口
        
        Args:
            opacity: 窗口不透明度 (0-1)
        """
        self.opacity = opacity
        self.root: Optional[tk.Tk] = None
        self.label: Optional[tk.Label] = None
        self.is_running = False
        
        logger.info("初始化状态窗口")
    
    def start(self):
        """启动窗口（必须在主线程中调用）"""
        if self.is_running:
            logger.warning("窗口已在运行")
            return
        
        self.is_running = True
        
        self.root = tk.Tk()
        self.root.title("Typeless Mac")
        
        # 设置窗口属性
        self.root.overrideredirect(True)  # 无边框
        self.root.attributes('-alpha', self.opacity)  # 透明度
        self.root.attributes('-topmost', True)  # 置顶
        
        # 设置窗口大小和位置（右上角）
        window_width = 300
        window_height = 80
        screen_width = self.root.winfo_screenwidth()
        x = screen_width - window_width - 20
        y = 60
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置背景色
        self.root.configure(bg='#2d2d2d')
        
        # 创建标签
        self.label = tk.Label(
            self.root,
            text="⏹ 就绪",
            font=("SF Pro Display", 18),
            bg='#2d2d2d',
            fg='#ffffff',
            padx=20,
            pady=20
        )
        self.label.pack(expand=True)
        
        # 默认隐藏
        self.root.withdraw()
        
        logger.info("UI 已启动")
    
    def run_mainloop(self):
        """运行主循环（必须在主线程中调用）"""
        if self.root:
            logger.info("启动 tkinter 主循环")
            self.root.mainloop()
            self.is_running = False
    
    def show(self, message: str = "⏹ 就绪"):
        """显示窗口并更新消息"""
        if not self.is_running or not self.root:
            logger.warning("窗口未初始化")
            return
        
        def update():
            if self.label:
                self.label.config(text=message)
            if self.root:
                self.root.deiconify()
        
        self.root.after(0, update)
        logger.debug(f"显示窗口: {message}")
    
    def hide(self):
        """隐藏窗口"""
        if not self.is_running or not self.root:
            return
        
        def update():
            if self.root:
                self.root.withdraw()
        
        self.root.after(0, update)
        logger.debug("隐藏窗口")
    
    def update_message(self, message: str):
        """更新消息（不改变显示状态）"""
        if not self.is_running or not self.label:
            return
        
        def update():
            if self.label:
                self.label.config(text=message)
        
        self.root.after(0, update)
        logger.debug(f"更新消息: {message}")
    
    def stop(self):
        """停止窗口"""
        if not self.is_running or not self.root:
            return
        
        def quit_app():
            if self.root:
                self.root.quit()
        
        self.root.after(0, quit_app)
        logger.info("停止 UI")


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    import time
    
    window = StatusWindow()
    window.start()
    
    time.sleep(1)
    
    # 测试显示
    window.show("🎤 录音中...")
    time.sleep(2)
    
    window.update_message("🤖 处理中...")
    time.sleep(2)
    
    window.update_message("✅ 完成")
    time.sleep(1)
    
    window.hide()
    time.sleep(1)
    
    print("测试完成，按 Ctrl+C 退出")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        window.stop()
