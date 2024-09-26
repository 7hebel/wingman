from modules.position import Rect, Direction
from modules import arrange

from typing import TYPE_CHECKING
import win32api

if TYPE_CHECKING:
    from modules.windows import Window


class Screen:
    """ Represents display monitor. """

    def __init__(self, monitor_data) -> None:
        self.hMonitor, *_ = monitor_data

        monitor_info = win32api.GetMonitorInfo(self.hMonitor)
        work_area = monitor_info.get("Work")
        real_rect = monitor_info.get("Monitor")

        self.x = work_area[0]
        self.y = work_area[1]
        self.w = abs(work_area[2] - work_area[0])
        self.h = abs(work_area[3] - work_area[1])
        self.rect = Rect.from_list(real_rect)
        self.group = arrange.Group(Rect.from_list(work_area))

        self.right_monitor = None
        self.left_monitor = None

    def arrange_bounding_monitors(self, all_screens: list["Screen"]) -> None:
        """ Check other display screen's positions and find neighbours. """

        for screen in all_screens:
            if screen == self:
                continue

            if screen.rect.right == self.rect.left:
                self.left_monitor = screen

            elif screen.rect.left == self.rect.right:
                self.right_monitor = screen

    def attach_window(self, window: "Window", from_direction: Direction = Direction.RIGHT) -> bool:
        """ Attach window to this screen's group. """

        return self.group.attach_window(window, from_direction)

    def dettach_window(self, window: "Window") -> None:
        """ Remove window from this screen's group. """

        self.group.remove_window(window)


screens = [Screen(monitor_data) for monitor_data in win32api.EnumDisplayMonitors()]
for screen in screens:
    screen.arrange_bounding_monitors(screens)


def get_screen(handle) -> Screen | None:
    """ Get initialized screen by it's monitor handle. (For use with win32api) """

    for screen in screens:
        if handle == screen.hMonitor:
            return screen


def leftmost_screen() -> Screen:
    """ Get first monitor from the left. """

    screen = screens[0]
    while screen.left_monitor is not None:
        screen = screen.left_monitor

    return screen


def rightmost_screen() -> Screen:
    """ Get the last monitor. """

    screen = screens[0]
    while screen.right_monitor is not None:
        screen = screen.right_monitor

    return screen
