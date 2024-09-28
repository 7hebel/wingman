from modules import settings
from modules import windows
from modules import events
from modules import logs

from ahk import AHK
import time


windows.load_visible_windows()
events.init_listener()

ahk = AHK()

if not settings.BLUR_MODE_ONLY:

    # Move window.
    ahk.add_hotkey(f"{settings.PUSH_KEY}Right", lambda: windows.get_focused_window().shift_right())  # Win + RIGHT
    ahk.add_hotkey(f"{settings.PUSH_KEY}Left", lambda: windows.get_focused_window().shift_left())    # Win + LEFT
    ahk.add_hotkey(f"{settings.PUSH_KEY}Up", lambda: windows.get_focused_window().maximize())        # Win + UP
    ahk.add_hotkey(f"{settings.PUSH_KEY}Down", lambda: windows.get_focused_window().unmaximize())    # Win + DOWN

    # Resize windows in groups.
    ahk.add_hotkey(f"{settings.RESIZE_KEY}Left", lambda: windows.get_focused_window().resize_left())    # Win + Alt + LEFT
    ahk.add_hotkey(f"{settings.RESIZE_KEY}Right", lambda: windows.get_focused_window().resize_right())  # Win + Alt + RIGHT

    # Change focus.
    ahk.add_hotkey(f"{settings.FOCUS_KEY}Left", lambda: windows.shift_focus_left())    # Win + Shift + Left
    ahk.add_hotkey(f"{settings.FOCUS_KEY}Right", lambda: windows.shift_focus_right())  # Win + Shift + Right

    # (Supress windows shortcuts)
    ahk.add_hotkey("#+Up", lambda: None)
    ahk.add_hotkey("#+Down", lambda: None)
    
# Change opacity.
ahk.add_hotkey(f"{settings.OPACITY_KEY}WheelUp", lambda: windows.get_focused_window().increase_opacity())    # Ctrl + Shift + MouseWheelUp
ahk.add_hotkey(f"{settings.OPACITY_KEY}WheelDown", lambda: windows.get_focused_window().decrease_opacity())  # Ctrl + Shift + MouseWheelDown

# Toogle blur.
ahk.add_hotkey(f"{settings.BLUR_TOOGLE_SHORTCUT}", lambda: windows.get_focused_window().toogle_blur())  # Win + shift + b

ahk.start_hotkeys()
logs.system_log("Started mainloop...")

while 1:
    time.sleep(1)

# mouse drag and drop window to group
# minimizing a window causes all groups to rearrange losing config
