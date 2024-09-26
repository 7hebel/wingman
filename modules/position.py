from dataclasses import dataclass
from typing import Any
from math import dist


@dataclass
class Rect:
    left: int
    top: int
    right: int
    bottom: int

    @staticmethod
    def from_list(rect: list[int, int, int, int]) -> "Rect":
        """ Create Rect object from it's values in format: [left, top, right, bottom] """

        return Rect(*rect)

    @staticmethod
    def from_xywh(x: int, y: int, w: int, h: int) -> "Rect":
        """ Create Rect object from provided left, top, width and height values. """

        left = x
        top = y
        right = left + w
        bottom = top + h

        return Rect(
            left, top, right, bottom
        )

    @staticmethod
    def from_RECT(rect) -> "Rect":
        """ Convert dwmapi RECT C-like structure to Rect. """

        return Rect.from_list([rect.left, rect.top, rect.right, rect.bottom])

    def __setattr__(self, name: str, value: Any) -> None:
        object.__setattr__(self, name, value)

        if name in ["left", "top", "right", "bottom"]:
            self.__recalc()

    def __post_init__(self) -> None:
        self.__recalc()

    def __recalc(self) -> None:
        if hasattr(self, 'left') and hasattr(self, 'right') and hasattr(self, 'top') and hasattr(self, 'bottom'):
            self.w = int(dist([self.left], [self.right]))
            self.h = int(dist([self.top], [self.bottom]))
            self.raw = (self.left, self.top, self.right, self.bottom)

    def geometry(self) -> str:
        """ Return this rectangle in the Tkinter's geometry format. """

        return f"{self.w}x{self.h}+{self.left}+{self.top}"


class Direction:
    LEFT = 0
    RIGHT = 1
