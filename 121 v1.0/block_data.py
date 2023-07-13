"""
data for blocks
"""
from dataclasses import dataclass
from typing import Any
# from enum import Enum


@dataclass()
class Block:
    """
    dataclass containing block data
    """
    type: str  # type of main block
    barriers: list[  # list of barriers
        tuple[  # single barrier object
            str,  # name of type
            bool,  # if gravity locked (False if does not move with gravity, True if does)
            tuple[  # tuple of if sides are there
                bool,  # 0, up
                bool,  # 1, right
                bool,  # 2, down
                bool  # 3, left
            ]
        ]
    ]
    other: dict[int, Any] = ()  # dictionary containing any extra tags the block needs

# can't let 2 attributes in enums have same value.


class PointedBlock():
    """
    default attribute enum for pointing blocks
    """
    grav_locked = 0
    rotation = 1


class VariableValue():
    """
    enum for blocks with variable strength/amount values
    """
    value = 4


class Gravity():
    """
    enum for gravity blocks
    """
    grav_locked = PointedBlock.grav_locked
    rotation = PointedBlock.rotation
    value = VariableValue.value
    type = 2
    mode = 3


class GivesAchievement():
    """
    enum for any block that gives achievements
    """
    achievement = 7


class EasterEgg():
    """
    enum for easter egg class
    """
    achievement = GivesAchievement.achievement
    type = 5
    level = 6
    skin = 8


class Repel():
    """
    enum for repel block
    """
    mode = 9


class Activator():
    """
    enum for activator block
    """
    grav_locked = PointedBlock.grav_locked
    rotation = PointedBlock.rotation
    delay = 10


class HasTextField():
    """
    enum for any block with a freeform text field
    """
    text = 11


class Portal():
    """
    enum for portal block
    """
    rotation = PointedBlock.rotation
    relative = 12
    x = 13
    y = 14
    reflect_x = 15
    reflect_y = 16


class FragileGround():
    """
    enum for fragile ground
    """
    sturdiness = 17
    remove_barriers = 18
    remove_link = 19


class Destroyer():
    """
    enum for destroyer block
    """
    grav_locked = PointedBlock.grav_locked
    rotation = PointedBlock.rotation
    match_block = 20
    destroy_link = 21
    destroy_barriers = 22
    destroy_block = 23


class Rotator():
    """
    enum for rotator block
    """
    grav_locked = PointedBlock.grav_locked
    rotation = PointedBlock.rotation
    value = VariableValue.value
    mode = 24
    rotate_block = 25
    rotate_barriers = 26
    grav_account = 27
