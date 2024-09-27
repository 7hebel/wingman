# Mode.
BLUR_MODE_ONLY = False  # Disable all tiling managements. Keep only BgBlur and opacity features.

# Windows.
MARGIN_PX = 16
WINDOW_MIN_W = 480
OPACITY_VALUE_STEP = 5
DEFAULT_OPACITY_ON_BLUR = 225
MAX_WINS_IN_GROUP = 4

# Shortcuts.
"""
# - Windows Key
! - Alt Key
+ - Shift Key
^ - Ctrl Key
"""
PUSH_KEY = "#"
RESIZE_KEY = "#!"
FOCUS_KEY = "#+"
OPACITY_KEY = "^+"
BLUR_TOOGLE_SHORTCUT = "#+b"

# Ignoring.
IGNORE_WIN_TEXT = [
    "Snipping Tool Overlay",
    "Recording toolbar",
    "Calculator",
    "Mechvibes",
    "Delete File",
] 
INGORE_CHILDREN = True

# Other.
OVERLAPPING_FOCUS_SHIFT = True
