<div align="center">
    <br>
    <img src="./assets/full_logo.png" width="280" alt="Wingman" />
    <br>
    <br>
    <h2>🪽 Windows Tiling Manager</h2>
</div>

![Showcase](https://raw.githubusercontent.com/7hebel/wingman/refs/heads/main/assets/showcase-vid/tiling_usage.webp)

<div align="center">
    <br>
    <h2>🪽 Background Blur</h2>
</div>

![Showcase](https://raw.githubusercontent.com/7hebel/wingman/refs/heads/main/assets/showcase-vid/blur_usage.webp)

<div align="center">
    <br>
    <h2>✨ Features</h2>
</div>

- 🔮 <b>Apply background blur to any window.</b>

- 🪟 Horizontal windows tiling with margin.

- ⌨️ Intuitive keyboard shortcuts.

- 🖥️ Multiple screens support.

- 🛠️ Easily configurable.

<div align="center">
    <br>
    <h2>💾 Installation</h2>
</div>

1. Ensure Python3 and PiP are installed

2. Clone / Download this repo.

3. `pip install -r requirements.txt`

4. `py main.py`

<div align="center">
    <br>
    <h2>🔧 Configuration</h2>
</div>

### 📄 Settings file: `/modules/settings.py`

| **NAME** | **DESCRIPTION** | *DEFAULT* |
| :--- | :--- | ---: |
| `BLUR_MODE_ONLY` | Disable all tiling features and shortcuts, leaves only the blur and opacity management enabled. | `False` |
| `MARGIN_PX` | Amount of pixels in between tiled windows and screen borders. | `16` |
| `WINDOW_MIN_W` | Minimum window width in pixels. *(Some windows has hardcoded minimum width that cannot be changed)* | `480` |
| `OPACITY_VALUE_STEP` | Update window's opacity by this amount. | `5` |
| `DEFAULT_OPACITY_ON_BLUR` | After applying background blur effect, this opacity will be set for the window | `225` |
| `MAX_WINS_IN_GROUP` | Maximum amount of windows that can fit in single group. *(`WINDOW_MIN_W` has higher priority, and if window cannot fit because there is no space available, this value won't matter.)* | `4` |
| `PUSH_KEY` | Leader key for moving windows around in groups. | `#` |
| `RESIZE_KEY` | Leader key for resizing windows in groups. | `#!` |
| `FOCUS_KEY` | Leader key for shifting focus between windows on the screen. | `#+` |
| `OPACITY_KEY` | Leader key for updating window's opacity with mouse wheel | `^+` |
| `BLUR_TOOGLE_SHORTCUT` | Full shortcut to toogle background blur for window | `#+b` |
| `IGNORE_WIN_TEXT` | List of window's titles that will be ignored. | ` "Snipping Tool Overlay","Recording toolbar", "Calculator", "Mechvibes", "Delete File" ` |
| `INGORE_CHILDREN` | Ignore sub-windows (highly recomended) | `True` |
| `OVERLAPPING_FOCUS_SHIFT` | Shifting focus to the right on the rightmost window will overlap screen and apply focus to the leftmost window. | `True` |



