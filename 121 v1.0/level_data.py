"""
level data class
"""
from dataclasses import dataclass
from block_data import Block
from typing import Union


@dataclass()
class Level:
    """
    here so that below doesn't yell at us when we try and say it can hold another level :P
    """


@dataclass()
class Level:
    """
    dataclass containing completed level data
    """
    published: bool
    name: str
    gravity: tuple[int, float]
    blocks: dict[tuple[int, int], Block]
    links: list[list[tuple[int, int]]]
    player_starts: list[tuple[int, int]]
    dimensions: tuple[int, int] = (11, 11)
    version: int = 4
    next: Union[None, Level] = None