"""
UI 模块 - 状态显示窗口
macOS 下使用 AppKit 浮层（全屏辅助 + 不抢焦点）
"""
import logging
import math
import random
import sys
import tkinter as tk
import warnings
from typing import Optional

logger = logging.getLogger(__name__)

try:
    if sys.platform == "darwin":
        import AppKit  # type: ignore
        import objc  # type: ignore
        from PyObjCTools import AppHelper  # type: ignore
        warnings.filterwarnings("ignore", category=objc.ObjCPointerWarning)
    else:
        AppKit = None
        AppHelper = None
except Exception:
    AppKit = None
    AppHelper = None


class _MacOverlayWindow:
    """macOS AppKit 浮层窗口"""

    def __init__(self, opacity: float = 0.92):
        self.opacity = opacity
        self.is_running = False
        self._mode = "hidden"  # hidden|recording|processing
        self._progress_value = 0.0
        self._progress_running = False
        self._wave_running = False
        self._wave_phase = 0.0

        self.window: Optional[AppKit.NSPanel] = None
        self.content: Optional[AppKit.NSView] = None
        self.status_label: Optional[AppKit.NSTextField] = None
        self.progress_overlay: Optional[AppKit.NSView] = None
        self.wave_container: Optional[AppKit.NSView] = None
        self.wave_bars = []
        self._wave_meta = []

        # 视觉整体缩放到 80%
        self.scale = 0.8
        self.width = 560.0 * self.scale
        self.height = 94.0 * self.scale

    def start(self):
        if self.is_running:
            return

        if AppKit is None:
            raise RuntimeError("AppKit 不可用")

        style = (
            AppKit.NSWindowStyleMaskBorderless
            | AppKit.NSWindowStyleMaskNonactivatingPanel
        )
        rect = AppKit.NSMakeRect(0, 0, self.width, self.height)
        panel = AppKit.NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            rect,
            style,
            AppKit.NSBackingStoreBuffered,
            False,
        )
        panel.setOpaque_(False)
        panel.setBackgroundColor_(AppKit.NSColor.clearColor())
        panel.setHasShadow_(True)
        panel.setFloatingPanel_(True)
        panel.setHidesOnDeactivate_(False)
        panel.setIgnoresMouseEvents_(True)
        panel.setLevel_(AppKit.NSPopUpMenuWindowLevel)

        behavior = (
            AppKit.NSWindowCollectionBehaviorTransient
            | AppKit.NSWindowCollectionBehaviorFullScreenAuxiliary
            | AppKit.NSWindowCollectionBehaviorIgnoresCycle
        )
        if hasattr(AppKit, "NSWindowCollectionBehaviorCanJoinAllApplications"):
            behavior |= AppKit.NSWindowCollectionBehaviorCanJoinAllApplications
        else:
            behavior |= AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces
        panel.setCollectionBehavior_(behavior)

        content = AppKit.NSView.alloc().initWithFrame_(rect)
        content.setWantsLayer_(True)
        content.layer().setCornerRadius_(self.height / 2)
        content.layer().setMasksToBounds_(True)
        content.layer().setBackgroundColor_(
            AppKit.NSColor.colorWithCalibratedWhite_alpha_(0.07, 0.9).CGColor()
        )
        panel.setContentView_(content)

        label_h = 30.0 * self.scale
        side_padding = 20.0 * self.scale
        label = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(
                side_padding,
                (self.height - label_h) / 2.0,
                self.width - side_padding * 2.0,
                label_h,
            )
        )
        label.setBezeled_(False)
        label.setDrawsBackground_(False)
        label.setEditable_(False)
        label.setSelectable_(False)
        label.setStringValue_("")
        label.setAlignment_(AppKit.NSTextAlignmentCenter)
        label.setTextColor_(AppKit.NSColor.whiteColor())
        label.setFont_(
            AppKit.NSFont.systemFontOfSize_weight_(20.0, AppKit.NSFontWeightSemibold)
        )
        content.addSubview_(label)

        wave_h = 34.0 * self.scale
        wave_padding = 24.0 * self.scale
        wave_container = AppKit.NSView.alloc().initWithFrame_(
            AppKit.NSMakeRect(
                wave_padding,
                (self.height - wave_h) / 2.0,
                self.width - wave_padding * 2.0,
                wave_h,
            )
        )
        wave_container.setWantsLayer_(True)
        wave_container.layer().setBackgroundColor_(AppKit.NSColor.clearColor().CGColor())
        content.addSubview_(wave_container)

        progress_overlay = AppKit.NSView.alloc().initWithFrame_(
            AppKit.NSMakeRect(0, 0, 0, self.height)
        )
        progress_overlay.setWantsLayer_(True)
        progress_overlay.layer().setCornerRadius_(self.height / 2)
        progress_overlay.layer().setMasksToBounds_(True)
        progress_overlay.layer().setBackgroundColor_(
            AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(
                0.95, 0.97, 1.0, 0.24
            ).CGColor()
        )
        progress_overlay.setHidden_(True)
        content.addSubview_positioned_relativeTo_(
            progress_overlay,
            AppKit.NSWindowBelow,
            label,
        )

        self.window = panel
        self.content = content
        self.status_label = label
        self.progress_overlay = progress_overlay
        self.wave_container = wave_container
        self._setup_wave_bars()
        self._reposition_bottom_center()

        self.window.setAlphaValue_(0.0)
        self.window.orderFront_(None)
        self.is_running = True
        logger.info("AppKit 状态浮层已启动")

    def _setup_wave_bars(self):
        if self.wave_container is None:
            return

        self.wave_bars = []
        self._wave_meta = []
        total_w = self.wave_container.frame().size.width
        total_h = self.wave_container.frame().size.height
        count = 28
        bar_w = 8.0 * self.scale
        gap = (total_w - count * bar_w) / (count - 1)
        min_h = 5.0 * self.scale
        max_h = total_h - 2.0 * self.scale

        for i in range(count):
            x = i * (bar_w + gap)
            h = min_h
            y = (total_h - h) / 2.0
            bar = AppKit.NSView.alloc().initWithFrame_(AppKit.NSMakeRect(x, y, bar_w, h))
            bar.setWantsLayer_(True)
            bar.layer().setCornerRadius_(bar_w / 2.0)
            bar.layer().setBackgroundColor_(
                AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(
                    0.28, 0.85, 0.95, 0.95
                ).CGColor()
            )
            self.wave_container.addSubview_(bar)
            self.wave_bars.append(bar)
            self._wave_meta.append((x, bar_w, min_h, max_h))

    def _active_screen_visible_frame(self):
        screens = AppKit.NSScreen.screens()
        if not screens:
            return AppKit.NSMakeRect(0, 0, 1440, 900)

        mouse = AppKit.NSEvent.mouseLocation()
        for screen in screens:
            f = screen.frame()
            if (
                mouse.x >= f.origin.x
                and mouse.x <= f.origin.x + f.size.width
                and mouse.y >= f.origin.y
                and mouse.y <= f.origin.y + f.size.height
            ):
                return screen.visibleFrame()
        return AppKit.NSScreen.mainScreen().visibleFrame()

    def _reposition_bottom_center(self):
        if not self.window:
            return
        vf = self._active_screen_visible_frame()
        x = vf.origin.x + (vf.size.width - self.width) / 2.0
        y = vf.origin.y + 28.0
        self.window.setFrame_display_(AppKit.NSMakeRect(x, y, self.width, self.height), True)

    def _run_on_main(self, fn, *args):
        if AppHelper is None:
            return
        AppHelper.callAfter(fn, *args)

    def show_recording(self):
        self._run_on_main(self._show_recording_impl)

    def _show_recording_impl(self):
        if not self.is_running:
            return
        self._mode = "recording"
        self._reposition_bottom_center()
        if self.status_label is not None:
            self.status_label.setStringValue_("")
            self.status_label.setHidden_(True)
        self._set_progress_fill(0.0, hidden=True)
        if self.wave_container is not None:
            self.wave_container.setHidden_(False)
        if self.window is not None:
            self.window.setAlphaValue_(self.opacity)
            self.window.orderFront_(None)
            self.window.setLevel_(AppKit.NSPopUpMenuWindowLevel)
        self._start_wave_animation()
        self._stop_progress_animation()

    def show_processing(self, message: str = "处理中"):
        self._run_on_main(self._show_processing_impl, message)

    def _show_processing_impl(self, message: str):
        if not self.is_running:
            return

        entering_processing = self._mode != "processing"
        self._mode = "processing"
        self._reposition_bottom_center()

        plain_text = self._plain_processing_text(message)
        if self.status_label is not None:
            self.status_label.setHidden_(False)
            self.status_label.setStringValue_(plain_text)
        if self.wave_container is not None:
            self.wave_container.setHidden_(True)
        self._set_progress_fill(self._progress_value, hidden=False)
        if self.window is not None:
            self.window.setAlphaValue_(self.opacity)
            self.window.orderFront_(None)
            self.window.setLevel_(AppKit.NSPopUpMenuWindowLevel)

        self._stop_wave_animation()
        if entering_processing:
            self._progress_value = 0.0
            self._set_progress_fill(0.0, hidden=False)
            self._start_progress_animation()

    def complete_processing(self):
        self._run_on_main(self._complete_processing_impl)

    def _complete_processing_impl(self):
        self._stop_progress_animation()
        self._progress_value = 100.0
        self._set_progress_fill(100.0, hidden=False)
        if self.status_label is not None:
            self.status_label.setHidden_(False)
            self.status_label.setStringValue_("完成")

    def update_message(self, message: str):
        self._run_on_main(self._update_message_impl, message)

    def _update_message_impl(self, message: str):
        if not self.is_running:
            return
        if "录音" in message:
            self._show_recording_impl()
            return
        if any(k in message for k in ("识别", "润色", "输入", "处理")):
            self._show_processing_impl(message)
            return
        if self.status_label is not None:
            self.status_label.setStringValue_(message)

    def show(self, message: str = "⏹ 就绪"):
        self.update_message(message)

    def hide(self):
        self._run_on_main(self._hide_impl)

    def _hide_impl(self):
        if not self.is_running:
            return
        self._mode = "hidden"
        self._stop_wave_animation()
        self._stop_progress_animation()
        if self.window is not None:
            self.window.setAlphaValue_(0.0)

    def _start_wave_animation(self):
        if self._wave_running:
            return
        self._wave_running = True
        self._schedule_wave_tick()

    def _stop_wave_animation(self):
        self._wave_running = False

    def _schedule_wave_tick(self):
        if not self._wave_running or AppHelper is None:
            return
        self._wave_tick()
        AppHelper.callLater(0.06, self._schedule_wave_tick)

    def _wave_tick(self):
        if self._mode != "recording":
            return
        self._wave_phase += 0.33
        for idx, bar in enumerate(self.wave_bars):
            x, bar_w, min_h, max_h = self._wave_meta[idx]
            wave = abs(math.sin(self._wave_phase + idx * 0.42))
            noise = random.uniform(0.05, 0.42)
            ratio = min(1.0, wave * 0.78 + noise)
            h = min_h + (max_h - min_h) * ratio
            y = (max_h - h) / 2.0 + 1.0
            bar.setFrame_(AppKit.NSMakeRect(x, y, bar_w, h))

    def _start_progress_animation(self):
        if self._progress_running:
            return
        self._progress_running = True
        self._schedule_progress_tick()

    def _stop_progress_animation(self):
        self._progress_running = False

    def _schedule_progress_tick(self):
        if not self._progress_running or AppHelper is None:
            return
        self._progress_tick()
        AppHelper.callLater(0.08, self._schedule_progress_tick)

    def _progress_tick(self):
        if self._mode != "processing":
            return
        if self._progress_value < 92.0:
            self._progress_value += random.uniform(0.8, 2.2)
        elif self._progress_value < 97.0:
            self._progress_value += random.uniform(0.05, 0.25)
        self._progress_value = min(self._progress_value, 97.0)
        self._set_progress_fill(self._progress_value, hidden=False)

    def _set_progress_fill(self, progress_value: float, hidden: bool):
        if self.progress_overlay is None:
            return
        if hidden:
            self.progress_overlay.setHidden_(True)
            return
        self.progress_overlay.setHidden_(False)
        p = max(0.0, min(100.0, progress_value)) / 100.0
        width = self.width * p
        self.progress_overlay.setFrame_(AppKit.NSMakeRect(0, 0, width, self.height))

    def _plain_processing_text(self, message: str) -> str:
        text = message or ""
        if "识别" in text:
            return "识别中"
        if "润色" in text:
            return "润色中"
        if "输入" in text:
            return "输入中"
        if "停止录音" in text:
            return "处理中"
        if "完成" in text:
            return "完成"
        if "错误" in text or "出错" in text:
            return "处理失败"
        if "未识别" in text:
            return "未识别到内容"
        cleaned = "".join(ch for ch in text if ch.isalnum() or ("\u4e00" <= ch <= "\u9fff"))
        return cleaned or "处理中"

    def run_mainloop(self):
        if AppHelper is None:
            return
        logger.info("启动 AppKit 事件循环")
        AppHelper.runConsoleEventLoop(installInterrupt=False, maxTimeout=0.2)

    def stop(self):
        self._run_on_main(self._stop_impl)

    def _stop_impl(self):
        self._stop_wave_animation()
        self._stop_progress_animation()
        if self.window is not None:
            self.window.orderOut_(None)
            self.window.close()
        self.is_running = False
        if AppHelper is not None:
            try:
                AppHelper.stopEventLoop()
            except Exception:
                pass


class _TkFallbackWindow:
    """非 macOS fallback"""

    def __init__(self, opacity: float = 0.9):
        self.opacity = opacity
        self.root: Optional[tk.Tk] = None
        self.label: Optional[tk.Label] = None
        self.is_running = False

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", self.opacity)
        self.root.attributes("-topmost", True)
        w, h = 460, 84
        sw = self.root.winfo_screenwidth()
        x = (sw - w) // 2
        y = self.root.winfo_screenheight() - h - 40
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.configure(bg="#1f1f1f")
        self.label = tk.Label(
            self.root,
            text="⏹ 就绪",
            font=("Helvetica", 15, "bold"),
            bg="#1f1f1f",
            fg="#ffffff",
        )
        self.label.pack(expand=True, fill="both")
        self.root.withdraw()

    def show_recording(self):
        self.show("")

    def show_processing(self, message: str = "处理中"):
        self.show(message)

    def complete_processing(self):
        self.update_message("完成")

    def show(self, message: str = "⏹ 就绪"):
        if not self.root:
            return
        if self.label:
            self.label.config(text=message)
        self.root.deiconify()

    def update_message(self, message: str):
        if not self.root:
            return
        if self.label:
            self.label.config(text=message)

    def hide(self):
        if self.root:
            self.root.withdraw()

    def run_mainloop(self):
        if self.root:
            self.root.mainloop()

    def stop(self):
        if self.root:
            self.root.quit()
            self.root.destroy()
        self.is_running = False


class StatusWindow:
    """统一 UI 封装"""

    def __init__(self, opacity: float = 0.9):
        self.opacity = opacity
        if AppKit is not None and AppHelper is not None and sys.platform == "darwin":
            logger.info("使用 AppKit 浮层 UI")
            self._impl = _MacOverlayWindow(opacity=max(0.1, min(1.0, opacity)))
            self.root = None
        else:
            logger.info("使用 tkinter fallback UI")
            self._impl = _TkFallbackWindow(opacity=opacity)
            self.root = getattr(self._impl, "root", None)

    def start(self):
        self._impl.start()
        self.root = getattr(self._impl, "root", None)
        logger.info("UI 已启动")

    def run_mainloop(self):
        self._impl.run_mainloop()

    def show_recording(self):
        self._impl.show_recording()

    def show_processing(self, message: str = "处理中"):
        self._impl.show_processing(message)

    def complete_processing(self):
        self._impl.complete_processing()

    def show(self, message: str = "⏹ 就绪"):
        self._impl.show(message)

    def update_message(self, message: str):
        self._impl.update_message(message)

    def hide(self):
        self._impl.hide()

    def stop(self):
        self._impl.stop()
