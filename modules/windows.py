from modules.position import Rect, Direction
from modules import screen_test
from modules import settings
from modules import monitor
from modules import arrange
from modules import blur
from modules import logs

from win32gui import EnumWindows, GetWindowText, IsWindowVisible, IsIconic
from collections.abc import Callable
from dataclasses import dataclass
from threading import Thread
from ctypes import wintypes
import pywintypes
import win32gui
import win32api
import win32con
import ctypes
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


_windows_cache: dict[int, "Window"] = {}


class _WindowUpdatesMonitor:
    """ Listen for window's position changes and report when it was killed. """

    def __init__(self, hwnd: int, on_pos_changed: Callable[[Rect], None], on_killed: Callable[[], None]) -> None:
        self.CHECK_FREQ = 0.1
        self.hwnd = hwnd
        self.__on_pos_changed = on_pos_changed
        self.__on_killed = on_killed
        self.__rect = self.__get_rect()

        checker = Thread(target=self.threaded_checker, daemon=True)
        checker.start()

    def __get_rect(self) -> Rect:
        return Rect.from_list(win32gui.GetWindowRect(self.hwnd))

    def threaded_checker(self) -> None:
        while 1:
            time.sleep(self.CHECK_FREQ)

            try:
                new_rect = self.__get_rect()

            except pywintypes.error:
                return self.__on_killed()

            if new_rect != self.__rect:
                self.__on_pos_changed(new_rect)

            self.__rect = new_rect


@dataclass
class Window:
    hwnd: int
    _rect: Rect
    _screen: monitor.Screen

    def __post_init__(self) -> None:
        _windows_cache[self.hwnd] = self

        self.blur_bg: blur.BlurSlaveWindow | None = None
        self.opacity = 255
        self.l_shift = 0

        if not settings.BLUR_MODE_ONLY:
            self.__fix_max_win()
            self._bounding_error = screen_test.get_bounding_diff(self.hwnd)
            self._min_w = screen_test.get_window_min_width(self.hwnd)

            if self.screen is not None:
                if not self.screen.attach_window(self):
                    if not arrange.attach_to_any_group(self):
                        self.log("There is no group that could fit this window...")
                        self.minimize()

        _WindowUpdatesMonitor(self.hwnd, self.on_rect_update, self.on_window_killed)

    def __repr__(self) -> str:
        return f"<Win: {self.text}>"

    def log(self, content: str) -> None:
        """ Log message with this window's reference. """

        logs.window_log(self, content)

    def on_rect_update(self, rect: Rect) -> None:
        """ Standard position update callback. """

        self.rect = rect

        if self.blur_bg is not None:
            self.blur_bg.resize_to_window()

        self._screen = monitor.get_screen(win32api.MonitorFromRect(self.rect.raw))

    def on_window_killed(self) -> None:
        """ Standard window kill callback. """

        self.screen.dettach_window(self)

        if self.blur_bg is not None:
            self.blur_bg.destroy()

        if self.hwnd in _windows_cache:
            _windows_cache.pop(self.hwnd)

        self.log("Window killed.")

    @property
    def text(self) -> str:
        """ Returns current window's title. """

        return win32gui.GetWindowText(self.hwnd)

    @property
    def rect(self) -> Rect:
        if self._screen is None:
            self._rect = Rect.from_list(win32gui.GetWindowRect(self.hwnd))

        return self._rect

    @rect.setter
    def rect(self, rect: Rect) -> None:
        self._rect = rect

    @property
    def screen(self) -> monitor.Screen:
        if self._screen is None:
            self._screen = monitor.get_screen(win32api.MonitorFromRect(self.rect.raw))
        return self._screen

    @screen.setter
    def screen(self, screen: monitor.Screen) -> None:
        if self._screen is not None:
            self._screen.dettach_window(self)

        self._screen = screen
        self._screen.attach_window(self)

    @property
    def is_visible(self) -> bool:
        return bool(not win32gui.IsIconic(self.hwnd)) and \
               win32gui.IsWindowVisible(self.hwnd) and \
               win32gui.GetWindowPlacement(self.hwnd)[1] != win32con.SW_MINIMIZE

    @property
    def minimum_width(self) -> int:
        if self._min_w > settings.WINDOW_MIN_W:
            return self._min_w

        return settings.WINDOW_MIN_W

    def __fix_max_win(self) -> None:
        """ Ensure window is not displayed in SW_MAXIMIZE mode as Microsoft couldn't do that. """

        win32gui.ShowWindow(self.hwnd, win32con.SW_NORMAL)
        self._rect = Rect.from_list(win32gui.GetWindowRect(self.hwnd))

        if self.blur_bg is not None:
            self.blur_bg.resize_to_window()

    def toogle_blur(self) -> None:
        """ Toogle blur background slave window. """

        if self.blur_bg is None:
            self.blur_bg = blur.BlurSlaveWindow(self)
            self.opacity = settings.DEFAULT_OPACITY_ON_BLUR
            self.__update_opacity()

            self.log("Enabled BlurBG.")

        else:
            self.blur_bg = self.blur_bg.destroy()
            self.opacity = 255
            self.__update_opacity()

            self.log("Disabled BlurBG.")

    def reset_shift(self) -> None:
        """ Reset window's border shift. """

        self.l_shift = 0

    def minimize(self) -> None:
        """ Minimize window to taskbar. """

        win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)
        self._rect = Rect.from_list(win32gui.GetWindowRect(self.hwnd))

        if self.blur_bg is not None:
            self.blur_bg.resize_to_window()

        self.screen.dettach_window(self)
        self.log("Minimized.")

    def maximize(self) -> None:
        """ Maximize window to take up entire screen. """

        win32gui.ShowWindow(self.hwnd, win32con.SW_MAXIMIZE)
        self._rect = Rect.from_list(win32gui.GetWindowRect(self.hwnd))

        if self.blur_bg is not None:
            self.blur_bg.resize_to_window()

        self.log("Maximized.")

    def unmaximize(self) -> None:
        """ If window is maximized, bring it back to group. If it's not maximized, minimize it. """

        if win32gui.GetWindowPlacement(self.hwnd)[1] == win32con.SW_MAXIMIZE:
            win32gui.ShowWindow(self.hwnd, win32con.SW_NORMAL)
            self.screen.group.rearrange()

        else:
            self.minimize()

    def focus(self) -> None:
        """ Switch system and keyboard focus to this window. """

        # Stupid windows.
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32gui.SetForegroundWindow(self.hwnd)
        self.log("Focused.")

    def draw_in_rect(self, rect: Rect | None = None) -> Rect:
        """ Move to specified (or current) rectangle, apply bounding error fixes, returns real Rect after set. """

        if rect is None:
            rect = self.rect

        self.__fix_max_win()
        win32gui.MoveWindow(
            self.hwnd,
            rect.left - self._bounding_error[0],
            rect.top - self._bounding_error[1],
            rect.w - self._bounding_error[2],
            rect.h - self._bounding_error[3],
            True
        )

        if self.blur_bg is not None:
            self.blur_bg.resize_to_window()

        return Rect.from_RECT(screen_test.get_extended_frame_bounds(self.hwnd))

    def __update_opacity(self) -> None:
        """ Apply window opacity. """

        if self.opacity < 75:
            self.opacity = 75

        if self.opacity > 255:
            self.opacity = 255

        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(0, 0, 0), self.opacity, win32con.LWA_ALPHA)

        self.log(f"Updated opacity to: {self.opacity}")

    def decrease_opacity(self) -> None:
        """ Decrease window's opacity by fixed value. """

        self.opacity -= settings.OPACITY_VALUE_CHANGE
        self.__update_opacity()

    def increase_opacity(self) -> None:
        """ Increase window's opacity by fixed value. """

        self.opacity += settings.OPACITY_VALUE_CHANGE
        self.__update_opacity()

    def shift_left(self) -> None:
        """ Move this window to the left side of the group or to the other screen on the left. """

        self.screen.group.shift_window(self, Direction.LEFT)

    def shift_right(self) -> None:
        """ Move this window to the right side of the group or to the other screen on the right. """

        self.screen.group.shift_window(self, Direction.RIGHT)

    def resize_left(self) -> None:
        self.screen.group.resize_window(self, Direction.LEFT)

    def resize_right(self) -> None:
        self.screen.group.resize_window(self, Direction.RIGHT)

    def can_shrink(self) -> bool:
        """ Check if this window can be shrinked to create space for other window in group. """

        return self.rect.w - settings.MARGIN_PX >= self.minimum_width


def load_window_hwnd(hwnd, force_reinit: bool = False) -> Window | None:
    """
    Initialize (or load cached) Window object by it's handle if it shouldn't be ignored.
    force_reinit flag removes cached state and performs initialization.
    """

    text = win32gui.GetWindowText(hwnd)
    if not text or text in settings.IGNORE_WIN_TEXT:
        return

    if hwnd in _windows_cache:
        if force_reinit:
            _windows_cache.pop(hwnd)

        else:
            return _windows_cache.get(hwnd)

    if settings.INGORE_CHILDREN:
        for win in _windows_cache.values():
            # Ensure the main app's window will be handled, not a child.
            owner = win32gui.GetWindow(hwnd, win32con.GW_OWNER)
            if owner != 0:
                return

    rect = Rect.from_list(win32gui.GetWindowRect(hwnd))
    screen = monitor.get_screen(win32api.MonitorFromRect(rect.raw))

    window = Window(
        hwnd, rect, screen
    )

    return window


def load_visible_windows(only_screen: monitor.Screen | None = None) -> list[Window]:
    """
    Returns array of initalized windows that are currently visible on the screen.
    only_screen argument filters result to return only those windows that are displayed on selected screen.
    """

    class TITLEBARINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.wintypes.DWORD),
            ("rcTitleBar", ctypes.wintypes.RECT),
            ("rgstate", ctypes.wintypes.DWORD * 6)
        ]

    visible_windows: list[Window] = []

    def callback(hwnd, _):
        title_info = TITLEBARINFO()
        title_info.cbSize = ctypes.sizeof(title_info)
        ctypes.windll.user32.GetTitleBarInfo(hwnd, ctypes.byref(title_info))

        is_cloaked = ctypes.c_int(0)
        ctypes.WinDLL("dwmapi").DwmGetWindowAttribute(hwnd, 14, ctypes.byref(is_cloaked), ctypes.sizeof(is_cloaked))

        if not IsIconic(hwnd) and IsWindowVisible(hwnd) and GetWindowText(hwnd) != '' and is_cloaked.value == 0:
            if not (title_info.rgstate[0] & 0x00008000):
                window = load_window_hwnd(hwnd)

                if window:
                    visible_windows.append(window)

    EnumWindows(callback, None)

    if only_screen is not None:
        return filter(lambda w: w.screen == only_screen, visible_windows)

    return visible_windows


def get_focused_window() -> Window | None:
    """ Return's currently focused window. """

    global RECENT_FOCUSED

    hwnd = win32gui.GetForegroundWindow()
    if hwnd not in _windows_cache:
        load_window_hwnd(hwnd)

    win = _windows_cache.get(hwnd)
    if win is None:
        return RECENT_FOCUSED

    RECENT_FOCUSED = win
    return win


RECENT_FOCUSED = get_focused_window()


def shift_focus_left() -> None:
    """ Move focus to the first window on the left. """

    current = get_focused_window()
    if current is None:
        return

    def _find_next_left_win(screen: monitor.Screen) -> Window | None:
        candidate = None

        for window in load_visible_windows(screen):
            if window.rect.left < current.rect.left:
                if candidate is None:
                    candidate = window
                    continue

                if window.rect.left > candidate.rect.left:
                    candidate = window

        return candidate

    next_win = _find_next_left_win(current.screen)
    if next_win is not None:
        next_win.log("Shifted focus from another window on the right.")
        return next_win.focus()

    if not settings.OVERLAPPING_FOCUS_SHIFT:
        return

    left_screen = current.screen.left_monitor
    if left_screen:
        next_win = _find_next_left_win(left_screen)
        if next_win is not None:
            next_win.log("Shifted focus from another window on east.")
            return next_win.focus()

    rightmost = monitor.rightmost_screen()
    if rightmost == current.screen:
        return

    if rightmost.group.windows:
        next_win = rightmost.group.windows[-1]
        next_win.focus()
        next_win.log("(Overlappingly) Shifted focus from another window.")


def shift_focus_right() -> None:
    """ Move focus to the first window on the right. """

    current = get_focused_window()
    if current is None:
        return

    def _find_next_right_win(screen: monitor.Screen) -> Window | None:
        candidate = None

        for window in load_visible_windows(screen):
            if window.rect.right > current.rect.right:
                if candidate is None:
                    candidate = window
                    continue

                if window.rect.right < candidate.rect.right:
                    candidate = window

        return candidate

    next_win = _find_next_right_win(current.screen)
    if next_win is not None:
        next_win.log("Shifted focus from another window on west.")
        return next_win.focus()

    if not settings.OVERLAPPING_FOCUS_SHIFT:
        return

    right_screen = current.screen.right_monitor
    if right_screen:
        next_win = _find_next_right_win(right_screen)
        if next_win is not None:
            next_win.log("Shifted focus from another window on west.")
            return next_win.focus()

    leftmost = monitor.leftmost_screen()
    if leftmost == current.screen:
        return

    if leftmost.group.windows:
        next_win = leftmost.group.windows[0]
        next_win.focus()
        next_win.log("(Overlappingly) Shifted focus from another window.")
