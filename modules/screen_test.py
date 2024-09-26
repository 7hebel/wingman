from modules.position import Rect
from modules import settings

from ctypes import wintypes
import win32gui
import ctypes

dwmapi = ctypes.WinDLL("dwmapi")


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


DwmGetWindowAttribute = dwmapi.DwmGetWindowAttribute
DwmGetWindowAttribute.restype = ctypes.HRESULT
DwmGetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.POINTER(RECT), ctypes.c_size_t]


def get_extended_frame_bounds(hwnd: int) -> RECT:
    """ Returns real window's rect (including shadows etc.) """

    rect = RECT()
    DwmGetWindowAttribute(hwnd, 9, ctypes.byref(rect), ctypes.sizeof(rect))
    return rect


def set_window_rect(hwnd: int, rect: Rect) -> None:
    win32gui.MoveWindow(
        hwnd,
        rect.left,
        rect.top,
        rect.w,
        rect.h,
        True
    )


def get_bounding_diff(hwnd: int) -> tuple[int, int, int, int]:
    """
    Check difference between window's default rect and actual, extended rect.
    Used to massively increase window's placement accuracy.
    Return format: (diff_x, diff_y, diff_w, diff_h)
    """

    rect_x, rect_y, rect_r, rect_b = win32gui.GetWindowRect(hwnd)

    extended_frame = get_extended_frame_bounds(hwnd)
    ext_frame_x = extended_frame.left
    ext_frame_y = extended_frame.top
    ext_frame_r = extended_frame.right
    ext_frame_b = extended_frame.bottom

    diff_x = ext_frame_x - rect_x
    diff_y = ext_frame_y - rect_y
    diff_w = ext_frame_r - rect_r
    diff_h = ext_frame_b - rect_b

    return (diff_x, diff_y, diff_w, diff_h)


def get_window_min_width(hwnd: int) -> int:
    """
    Some windows can refuse to shrink to requested size and there is no way to check their
    custom-set minimum width without checking how will they respond to shrinking request
    and what will be their actual size output that might not be what was expected.
    """

    start_rect = Rect.from_list(win32gui.GetWindowRect(hwnd))
    test_rect = Rect.from_xywh(0, 0, settings.WINDOW_MIN_W, settings.WINDOW_MIN_W)

    set_window_rect(hwnd, test_rect)
    minimum_width = Rect.from_RECT(get_extended_frame_bounds(hwnd)).w

    set_window_rect(hwnd, start_rect)
    return minimum_width
