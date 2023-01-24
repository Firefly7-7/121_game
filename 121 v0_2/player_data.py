"""
player data class
"""
from dataclasses import dataclass
from level_data import Level
from typing import Any


@dataclass()
class PlayerData:
    """
    a class containing player data
    """
    level_on: int
    level_list: list[tuple[str, bool]]
    easter_eggs: list[str]
    working_on: list[Level]
    controls: dict[str, Any]
    version: int = 4