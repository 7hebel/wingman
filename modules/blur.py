from BlurWindow.blurWindow import blur
from ctypes import windll
from tkinter import Tk
import threading

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.windows import Window


class BlurSlaveWindow:
    """ Create blur window behind master's window. """

    def __init__(self, window: "Window") -> None:
        self.__figure_window = window
        self.__handler = threading.Thread(target=self.__start_handler, daemon=True)
        self.__handler.start()

    def __start_handler(self) -> None:
        """ Create slave window. """

        self.root = Tk()
        self.root.config(bg='green')

        self.root.wm_attributes("-transparent", 'green')
        self.root.geometry(self.__figure_window.rect.geometry())
        self.root.overrideredirect(True)

        self.root.update()

        hwnd = windll.user32.GetParent(self.root.winfo_id())
        blur(hwnd, Acrylic=False, Dark=False)

        self.root.mainloop()

    def resize_to_window(self) -> None:
        """ Update slave's rect to master's one. """

        master_rect = self.__figure_window.rect
        self.root.geometry(master_rect.geometry())
        self.root.update()

    def destroy(self) -> None:
        """ Exit slave window. """

        self.root.quit()
        self.root.update()
        self.__handler.join()
