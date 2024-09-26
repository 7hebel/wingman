import sys
import os

STARTUPS_PATH = f"C:/Users/{os.getlogin()}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/"
STARTUP_FILE = STARTUPS_PATH + "wingmanStartup.bat"
MAIN_FILE = os.path.abspath("./main.py")


def add_to_startup() -> str:
    """ Automatically start main.py file on system's startup. """
    
    bat_content = f"py {MAIN_FILE}"
    
    if os.path.exists(STARTUP_FILE):
        os.remove(STARTUP_FILE)

    with open(STARTUPS_PATH + "wingmanStartup.bat", "a+") as file:
        file.write(bat_content)
        
    print("Added wingman to autostart.")


if "--startup" in sys.argv:
    add_to_startup()
