from modules import settings
from modules import windows
from modules import startup
from modules import events
from modules import logs

from ahk import AHK
import time
import sys

startup.execute_flags()
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
    
    # Restore window.
    ahk.add_hotkey(f"{settings.RESTORE_SHORTCUT}", lambda: windows.get_focused_window().draw_in_rect(restore=True))  # Win + Ctrl + R
    
# Change opacity.
ahk.add_hotkey(f"{settings.OPACITY_KEY}WheelUp", lambda: windows.get_focused_window().increase_opacity())    # Ctrl + Shift + MouseWheelUp
ahk.add_hotkey(f"{settings.OPACITY_KEY}WheelDown", lambda: windows.get_focused_window().decrease_opacity())  # Ctrl + Shift + MouseWheelDown

# Toogle blur.
ahk.add_hotkey(f"{settings.BLUR_TOOGLE_SHORTCUT}", lambda: windows.get_focused_window().toogle_blur())  # Win + shift + b

ahk.start_hotkeys()
logs.system_log("Started mainloop...")

while 1:
    try:
        time.sleep(1)
        
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)

# mouse drag and drop window to group
# if cannot fit window to other group when shifting, replace windows
# check window's opacity and dont assume its 255
# wide window recovery dont animate, use 1 step

# wide window might replace std window when more than 2 wins in group.

# win alt r - restore position to current (if window were moved by user)
