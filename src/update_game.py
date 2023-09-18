"""
updates the game, checking for dev/test environment, and removing the updater file
"""
import traceback

from safe_paths import safe_exists, safe_remove
from requests import get
import subprocess
from sys import argv, exit


def compare_verbose_versions(v1: str, v2: str, base: int = 10) -> bool:
    """
    compares two verbose version numbers (ex: 1.2.0)
    :param v1: old/current version
    :param v2: potentially new version
    :param base: base for numbers
    :return: if v2 is newer than v1
    """
    v1_args = v1.split(".")
    v2_args = v2.split(".")
    index = 0
    while True:
        if len(v1_args) <= index:
            if len(v2_args) <= index:
                return False  # if they have gotten here, they are identical prior
            else:
                return True  # if they have gotten here, they are identical prior, and if v2 has more, it is newer
        if int(v1_args[index], base) < int(v2_args[index], base):
            return True
        index += 1


updater_download = "but"
if safe_exists("121.py"):
    file_check = "version_source.txt"
    req = False
    version = "1.2.1.0"
elif safe_exists("121.exe"):
    file_check = "version_windows.txt"
    updater_download = "update.exe"
    req = True
    version = "1.2.1"
elif safe_exists("121.app"):
    file_check = "version_mac.txt"
    updater_download = "update.app"
    req = True
    version = "1.1"
elif safe_exists("121"):
    file_check = "version_unix.txt"
    updater_download = "update"
    req = True
    version = "1.1"
else:
    print("How/why are you running this?")
    req = False
up_to_date = True

if "--ignore_updates" not in argv:
    root = "https://raw.githubusercontent.com/Firefly7-7/121_game/main/update_data/"
    version_check = None
    updater_version = None
    updater_path = None
    if safe_exists("121_testing.txt"):
        with open("121_testing.txt", "r") as testing_data:
            for line in testing_data.readlines():
                args = line.strip().split("=")
                match args[0]:
                    case "updater_version":
                        updater_version = args[1]
                    case "updater_path":
                        updater_path = args[1]
                    case "game_version":
                        version = args[1]
                    case "version_check_path":
                        version_check = args[1]
                    case "root":
                        root = args[1]
    if version_check is None:
        version_check = root

    try:
        if updater_version is None:
            updater_version = get(version_check + file_check).text
        if compare_verbose_versions(version, updater_version) or "--force_updates" in argv:
            up_to_date = False
            if req:
                if updater_path is None:
                    updater_download_gotten = get(root + updater_download).content
                else:
                    with open(updater_path, "rb") as file_obj:
                        updater_download_gotten = file_obj.read()
                with open(updater_download, "wb") as updater_file:
                    updater_file.write(updater_download_gotten)
                subprocess.Popen([updater_download] + argv[1:])
                exit()
    except Exception:
        traceback.print_exc()
else:
    up_to_date = True

if safe_exists(updater_download):
    safe_remove(updater_download)