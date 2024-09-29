from modules import windows
from modules import arrange

import threading
import win32gui
import ctypes
import time


class _EventsListener:
    """ Detect uncatched changes in displayed windows. """

    def __init__(self):
        self.CHECK_FREQ = 0.1
        self.buffer = self.__load_visible_hwnds()
        self.listener_thread = threading.Thread(target=self.__listen, daemon=True)
        self.listener_thread.start()

    def __load_visible_hwnds(self) -> list[int]:
        """ Get list of currently visible window's handles. """

        class TITLEBARINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.wintypes.DWORD),
                ("rcTitleBar", ctypes.wintypes.RECT),
                ("rgstate", ctypes.wintypes.DWORD * 6)
            ]

        visible_windows: list[int] = []

        def callback(hwnd: int, _):
            title_info = TITLEBARINFO()
            title_info.cbSize = ctypes.sizeof(title_info)
            ctypes.windll.user32.GetTitleBarInfo(hwnd, ctypes.byref(title_info))

            is_cloaked = ctypes.c_int(0)
            ctypes.WinDLL("dwmapi").DwmGetWindowAttribute(hwnd, 14, ctypes.byref(is_cloaked), ctypes.sizeof(is_cloaked))

            if all((
                not win32gui.IsIconic(hwnd),
                win32gui.IsWindowVisible(hwnd),
                win32gui.GetWindowText(hwnd) != '',
                is_cloaked.value == 0,
                not (title_info.rgstate[0] & 0x00008000)
            )):
                visible_windows.append(hwnd)

        win32gui.EnumWindows(callback, None)

        return visible_windows

    def __listen(self) -> None:
        """ Detect changes and report them to the screen's groups. """

        while 1:
            time.sleep(self.CHECK_FREQ)

            active_hwnds = self.__load_visible_hwnds()

            for hwnd in active_hwnds:
                if hwnd not in self.buffer:
                    win = windows.load_window_hwnd(hwnd, force_reinit=True)

                    if win and win.screen:
                        win.screen.group.rearrange()

            for hwnd in self.buffer:
                if hwnd not in active_hwnds:
                    win = windows._windows_cache.get(hwnd)

                    if win is not None:
                        # win.screen might be lost due to minimized rect.
                        for group in arrange.Group.all_groups:
                            group.remove_window(win)

            self.buffer = active_hwnds


def init_listener():
    """ Start background changes listener. """

    _EventsListener()
