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
import subprocess


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
    file_name = "uh___"
    print("How/why are you running this?")

root = "https://raw.githubusercontent.com/Firefly7-7/121_game/main/update_data/"
levels_path = None
levels_directory_path = "https://raw.githubusercontent.com/Firefly7-7/121_game/main/src/"
if safe_exists("121_testing.txt"):
    with open("121_testing.txt", "r") as testing_data:
        for line in testing_data.readlines():
            args = line.strip().split("=")
            match args[0]:
                case "levels_list_path":
                    levels_path = args[1]
                case "levels_directory_path":
                    levels_directory = args[1]
                case "runnable_path":
                    root = args[1]
                case "root":
                    root = args[1]
if levels_path is None:
    levels_path = root


def get(path: str) -> str:
    if path.startswith("https:"):
        return requests.get(path.replace(' ', '%20')).text
    else:
        if path.startswith("~"):
            path = getpath(path[1:])
        with open(path, 'r') as file_obj:
            res = file_obj.read()
        return res


def get_bytes(path: str) -> bytes:
    if path.startswith("https:"):
        return requests.get(path.replace(' ', '%20')).content
    else:
        if path.startswith("~"):
            path = getpath(path[1:])
        with open(path, 'rb') as file_obj:
            res = file_obj.read()
        return res


def fetch_updates():
    """
    fetches updates
    :return:
    """
    try:
        r = get(levels_path + "premade_levels.txt")
        for level in r.split("\n"):
            lvl = get(f"{levels_directory_path}premade_levels/{level}.txt")
            with open(getpath(f"premade_levels/{level}.txt"), "w") as lvl_file:
                lvl_file.write(lvl)
        r = get(levels_path + "easter_eggs.txt")
        for level in r.split("\n"):
            lvl = get(f"{levels_directory_path}easter_eggs/{level}.txt")
            with open(getpath(f"easter_eggs/{level}.txt"), "w") as lvl_file:
                lvl_file.write(lvl)
        r = get_bytes(root + file_name)
        with open(getpath(file_name), "wb") as exe:
            exe.write(r)
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