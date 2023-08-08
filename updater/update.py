"""
handles updating
"""
import requests
import threading
import sys
import traceback
import tkinter as tk
from platform import system
import os
# import sys
import subprocess
# from platform import system


def getpath(relative_path):
    """ Handle paths cross-platform (thank you mac person)"""
    plat = system()
    match plat:
        case "Linux":
            # Linux
            return os.path.join(os.getcwd(), relative_path)
        case "Darwin":
            # OS X
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
        case "Windows":
            # Windows
            return os.path.join(os.getcwd(), relative_path)
        case _:
            return os.path.join(os.getcwd(), relative_path)


def safe_exists(relative_path):
    return os.path.exists(getpath(relative_path))


if safe_exists("121.exe"):  # from windows executable
    file_name = "121.exe"
elif safe_exists("121.app"):  # from mac app (check w/ mac person to make sure this works)
    file_name = "121.app"
else:
    print("How/why are you running this?")


def fetch_updates():
    """
    fetches updates
    :return:
    """
    global status
    try:
        r = requests.get("https://firefly7-7.github.io/121/premade_levels.txt")
        for level in r.text.split("\n"):
            lvl = requests.get(f"https://firefly7-7.github.io/121/premade_levels/{level.replace(' ', '%20')}.txt")
            with open(getpath(f"premade_levels/{level}.txt"), "w") as lvl_file:
                lvl_file.write(lvl.text)
        r = requests.get("https://firefly7-7.github.io/121/easter_eggs.txt")
        for level in r.text.split("\n"):
            lvl = requests.get(f"https://firefly7-7.github.io/121/easter_eggs/{level.replace(' ', '%20')}.txt")
            with open(getpath(f"easter_eggs/{level}.txt"), "w") as lvl_file:
                lvl_file.write(lvl.text)
        r = requests.get(f"https://firefly7-7.github.io/121/{file_name}")
        with open(getpath(file_name), "wb") as exe:
            exe.write(r.content)
        status_message.set("Update successfully installed, please close the window to re-launch the game!")
    except:
        status_message.set(
            "There was an error installing update.  Please close the window and try again later.  If this problem persists, please ask for help in the discord server."
            + "\n" + traceback.format_exc()
        )


window = tk.Tk()
status_message = tk.StringVar()
status_message.set("An update for 121 was found!  Please wait until it completes!")
txt = tk.Label(textvariable=status_message)
txt.pack()

thread = threading.Thread(target=fetch_updates)
thread.start()

window.mainloop()

if status_message.get() == "Update successfully installed, please close the window to re-launch the game!":
    subprocess.Popen([file_name, "--ignore_updates"])
sys.exit()