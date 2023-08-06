from platform import system
import os
import sys
from os import listdir, remove


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


def safe_listdir(relative_path):
    return listdir(getpath(relative_path))


def safe_remove(relative_path):
    remove(getpath(relative_path))