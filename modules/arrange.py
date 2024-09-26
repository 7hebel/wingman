from modules.position import Rect, Direction
from modules import settings
from modules import logs

from typing import TYPE_CHECKING, Generator
from math import ceil

if TYPE_CHECKING:
    from modules.windows import Window


def swap_window_shifts(w1: "Window", w2: "Window") -> None:
    w1.l_shift, w2.l_shift = w2.l_shift, w1.l_shift


class Group:
    """ Contain, arrange and manage windows on the screen. """

    all_groups: list["Group"] = []

    def __init__(self, screen_rect: Rect) -> None:
        self.screen_rect = screen_rect
        self.windows: list["Window"] = []
        Group.all_groups.append(self)

    def __win_index(self, window: "Window") -> int:
        """ Get window's index in the group. """

        assert window in self.windows, f"Cannot find index of window: {window} in the group as it is not registered."
        return self.windows.index(window)

    def __window_pairs(self) -> Generator[tuple["Window", "Window | None"], None, None]:
        """ Stream all windows from this group paired with the next one. (wins[n], wins[n + 1]) """

        for next_i, win in enumerate(self.windows, 1):
            if len(self.windows) - 1 < next_i:
                yield (win, None)

            else:
                yield (win, self.windows[next_i])

    def attach_window(self, window: "Window", from_direction: Direction) -> bool:
        """ Append new window from selected side. Returns False if maximum windows in group. """

        if len(self.windows) >= settings.MAX_WINS_IN_GROUP:
            logs.system_log(f"Cannot add window: {window.text} to group (group is full)")
            return False

        if not self.can_fit_window(window):
            return False

        self.reset_shifts()
        window.reset_shift()

        if from_direction == Direction.LEFT:
            self.windows.insert(0, window)
            
        if from_direction == Direction.RIGHT:
            self.windows.append(window)

        logs.system_log(f"Added {len(self.windows)} window {window.text} to group.")
        self.rearrange()

        return True

    def remove_window(self, window: "Window") -> None:
        """ Remove window from this group if exists. """

        if window in self.windows:
            self.windows.remove(window)
            logs.system_log(f"Removed window: {window.text} from group.")

        self.rearrange()

    def can_fit_window(self, window: "Window") -> bool:
        """ Check if group's rect can fit another window by checking all window's min width. """

        current_width = sum([win.minimum_width + settings.MARGIN_PX for win in self.windows])

        if current_width + window.minimum_width > self.screen_rect.w:
            window.log("Group refused attaching this window as it won't fit to the group's screen.")
            return False

        return True

    def rearrange(self) -> None:
        """ Arrange windows in group respecting border shifts. """

        if not self.windows:
            return

        TOP = self.screen_rect.top + settings.MARGIN_PX
        BOTTOM = self.screen_rect.bottom - settings.MARGIN_PX
        WIN_WIDTH = ceil(self.screen_rect.w / len(self.windows))
        prev_rect = Rect(self.screen_rect.left, self.screen_rect.top, self.screen_rect.left, self.screen_rect.bottom)

        for win, next_win in self.__window_pairs():
            if not win.is_visible:
                continue

            new_left = prev_rect.right + settings.MARGIN_PX
            new_right = new_left + WIN_WIDTH - settings.MARGIN_PX - win.l_shift

            if next_win is not None:
                new_right += next_win.l_shift
                if (new_right - new_left) < settings.WINDOW_MIN_W:
                    new_right = new_left + settings.WINDOW_MIN_W

            if self.is_rightmost(win):
                new_right = self.screen_rect.right - settings.MARGIN_PX

            rect = Rect(
                new_left, TOP, new_right, BOTTOM
            )

            prev_rect = win.draw_in_rect(rect)

    def reset_shifts(self) -> None:
        """ Reset border shift value in all windows in this group. """

        for window in self.windows:
            window.reset_shift()

    def is_leftmost(self, window: "Window") -> bool:
        """ Check if window is first window in this group. """

        return self.windows[0] == window

    def is_rightmost(self, window: "Window") -> bool:
        """ Check if window is last window in this group. """

        return self.windows[-1] == window

    def shift_window(self, window: "Window", direction: Direction) -> None:
        """ Update windows order in this group by shifting selected window in given direction. """

        if window not in self.windows:
            window.log(f"Tried to shift window which is not registered in group. (Registering...)")

            if self.attach_window(window, Direction.LEFT):
                self.rearrange()

            return

        if direction == Direction.LEFT and self.is_leftmost(window):
            if not window.screen.left_monitor:
                window.log("Cannot move window to the left: Is leftmost in group and no other monitor on the left.")
                return

            if window.screen.left_monitor.attach_window(window, Direction.RIGHT):
                self.remove_window(window)
                window.reset_shift()
                window.log("Shifted window into group on the left monitor.")

            return

        if direction == Direction.RIGHT and self.is_rightmost(window):
            if not window.screen.right_monitor:
                window.log("Cannot move window to the right: Is rightmost in group and no other monitor on the right.")
                return

            if window.screen.right_monitor.attach_window(window, Direction.LEFT):
                self.remove_window(window)
                window.reset_shift()
                window.log("Shifted window into group on the right monitor.")

            return

        WIN_INDEX = self.__win_index(window)
        shifted_neighbour = self.get_neighbour(window, direction)
        self.windows.remove(window)

        if direction == Direction.LEFT:
            self.windows.insert(WIN_INDEX - 1, window)

        if direction == Direction.RIGHT:
            self.windows.insert(WIN_INDEX + 1, window)

        if shifted_neighbour:
            swap_window_shifts(window, shifted_neighbour)

        self.rearrange()

    def get_neighbour(self, window: "Window", direction: Direction) -> "Window | None":
        """ Return neighbour window on for selected window in the same group. """

        if self.is_leftmost(window) and direction == Direction.LEFT or \
           self.is_rightmost(window) and direction == Direction.RIGHT:
            return None

        if direction == Direction.LEFT:
            return self.windows[self.__win_index(window) - 1]

        if direction == Direction.RIGHT:
            return self.windows[self.__win_index(window) + 1]

    def windows_on_left(self, window: "Window") -> list["Window"]:
        """ Returns all windows on the left from target. """

        return self.windows[:self.__win_index(window)]

    def windows_on_right(self, window: "Window") -> list["Window"]:
        """ Returns all windows on the right from target. """

        return self.windows[self.__win_index(window) + 1:]

    def resize_window(self, window: "Window", direction: Direction) -> None:
        """ Try to update selected window's size. It may update other windows to make space for selected one. """

        if self.is_leftmost(window) and self.is_rightmost(window):
            return logs.system_log("Cannot stretch the only window in group.")

        # If shrinking border window, expand neighbour instead.
        if self.is_leftmost(window) and direction == Direction.LEFT:
            return self.resize_window(self.get_neighbour(window, Direction.RIGHT), direction)

        if self.is_rightmost(window) and direction == Direction.RIGHT:
            return self.resize_window(self.get_neighbour(window, Direction.LEFT), direction)

        # When the window is expanded, decrease it's border shift instead of finding other strategy.
        if direction == Direction.RIGHT and window.l_shift < 0:
            window.l_shift += settings.MARGIN_PX
            self.rearrange()
            return

        next_windows = self.windows_on_left(window)[::-1] if direction == Direction.LEFT else self.windows_on_right(window)
        unshrinkable_wins: list["Window"] = []

        for next_win in next_windows:
            if not next_win.can_shrink():
                unshrinkable_wins.append(next_win)
                continue

            if direction == Direction.LEFT:
                window.l_shift -= settings.MARGIN_PX
                if self.get_neighbour(window, Direction.LEFT) != next_win:
                    self.get_neighbour(next_win, Direction.RIGHT).l_shift -= settings.MARGIN_PX

            if direction == Direction.RIGHT:
                next_win.l_shift += settings.MARGIN_PX
                if next_win != self.get_neighbour(window, Direction.RIGHT):

                    # Shift skipped windows as one of the next windows has shrinked and previous would take up that space.
                    for skipped_win in unshrinkable_wins:
                        skipped_win.l_shift += settings.MARGIN_PX

            self.rearrange()
            return

        window.log("Cannot stretch this window.")


def attach_to_any_group(window: "Window") -> bool:
    """ Try to attach window to any group that can fit it. """

    for group in Group.all_groups:
        if group.attach_window(window, Direction.RIGHT):
            return True

    return False
