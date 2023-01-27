"""
player data class
"""
from dataclasses import dataclass
from typing import Union
from json import dumps, loads
from zlib import decompress
from level_management import VERSION
from constants import NAME, PATH


@dataclass()
class PlayerData:
    """
    a class containing player data
    """
    level_on: int = 0
    level_list: list[tuple[str, bool]] = ()
    easter_eggs: list[str] = ()
    working_on: list[str] = ()
    controls: dict[str, Union[int, float, str, bool]] = ()
    version: int = 4


def update_player_data(player_data) -> PlayerData:
    """
    updates an out of date player data with all new player data required set to correct defaults.
    :param player_data: PlayerData object, out of date version
    :return:
    """
    res = empty_player_data()
    for attr, val in player_data.__dict__:
        setattr(res, attr, val)
    return res


def empty_player_data() -> PlayerData:
    """
    constructs empty player data object
    :return: PlayerData object
    """
    return PlayerData(0, list(), list(), list(), dict())


def load_player_data(name: str = NAME, prepend: str = PATH, typ: str = ".dat") -> PlayerData:
    """
    loads player data from a (currently) json file, assumes it exists
    :param name: name of file
    :param prepend: prepend to file (path to)
    :param typ: type of file
    :return: constructed PlayerData
    """
    # print("Loading player data")
    player_data = PlayerData(0, list(), list(), list(), dict())
    with open(f"{prepend}{name}{typ}", "rb") as file:
        read = file.read()
        # noinspection PyBroadException
        try:
            dat = str(read, "utf-8")
        except:
            dat = str(decompress(read))[2:-1]
        player_dict = loads(dat)
    for attr, val in player_dict.items():
        setattr(player_data, attr, val)
    if player_data.version < VERSION:
        player_data = update_player_data(player_data)
    return player_data


def save_player_data(player_data: PlayerData, name: str = NAME, prepend: str = PATH, typ: str = ".dat") -> None:
    """
    saves player data to a (currently) txt file
    :param player_data: player data to save
    :param name: name of file to save to
    :param prepend: prepend to file (path to)
    :param typ: type of file
    :return: None
    """
    with open(f"{prepend}{name}{typ}", "wb") as file:
        file.write(bytes(dumps(player_data.__dict__), "utf-8"))