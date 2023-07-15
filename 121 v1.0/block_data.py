"""
data for blocks
"""
from dataclasses import dataclass
from typing import Any
from enum import Enum
from abc import ABC, abstractmethod
from typing import Optional, Type
from pygame import SRCALPHA
from pygame.surface import Surface
from pygame.transform import smoothscale
from pygame.font import Font
from pygame.draw import line, lines, polygon, circle
from render_help import cos, sin, draw_arrow, clean_decimal


class BlockType(ABC):
    """
    stop yelling at me
    """
    pass


# noinspection PyRedeclaration
class BlockType(ABC):
    """
    abstract base class for blocks
    all blocks should inherit
    """

    # noinspection PyPropertyDefinition
    @staticmethod
    @property
    @abstractmethod
    def name() -> str:
        """
        name field
        :return:
        """
        pass

    # noinspection PyPropertyDefinition
    @staticmethod
    @property
    @abstractmethod
    def description() -> str:
        """
        name field
        :return:
        """
        pass

    #noinspection PyPropertyDefinition
    @staticmethod
    @property
    @abstractmethod
    def solid() -> bool:
        """
        whether or not it's a solid block
        :return:
        """
        pass

    @staticmethod
    @abstractmethod
    def collide() -> None:
        """
        colliding
        :return:
        """


    @staticmethod
    @abstractmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        """
        rendering
        :return:
        """

    @classmethod
    def declare_required(cls) -> set[BlockType]:
        """
        declares block types required by this block in the level
        :return: set of types required
        """
        return {cls}


@dataclass()
class Block:
    """
    dataclass containing block data
    """
    type: BlockType  # type of main block
    barriers: list[  # list of barriers
        tuple[  # single barrier object
            BlockType,  # type of barrier
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


class GivesAchievement:
    """
    enum for any block that gives achievements
    """
    achievement = 7


class PointedBlock:
    """
    default attribute enum for pointing blocks
    """
    grav_locked = 0
    rotation = 1


class VariableValue:
    """
    enum for blocks with variable strength/amount values
    """
    variable_value = 4


class HasTextField:
    """
    enum for any block with one freeform text field
    """
    text = 11


class Player(BlockType):
    """
    class for player (literally just has name, deprecated)
    """
    name = "player"
    description = None
    solid = False

    @staticmethod
    def collide() -> None:
        pass
    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        pass


class Delete(BlockType):
    """
    class for delete in construction area
    """

    description = "Delete a block."
    solid = False
    name = "delete"

    @staticmethod
    def collide() -> None:
        """
        collides with delete block (... um, how did they manage to place one lol)
        :return:
        """
        pass

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        """
        renders delete block
        :param data:
        :param gravity:
        :param font:
        :param scale:
        :return:
        """
        res = Surface((scale, scale), flags=SRCALPHA)
        res.fill((0, 0, 0, 0))
        line(
            res,
            (255, 0, 0),
            (0, 0),
            (scale - 1, scale - 1),
            round(scale / 6)
        )
        line(
            res,
            (255, 0, 0),
            (scale - 1, 0),
            (0, scale - 1),
            round(scale / 6)
        )
        return res


class Ground(BlockType):
    """
    class for ground block
    """

    name = "ground"
    description = "A solid block with no other properties."
    solid = True

    @staticmethod
    def collide() -> None:
        pass

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        return res



class Goal(BlockType):
    """
    class for goal block
    """
    name = "goal"
    description = "The block you need to finish a level.  You cannot export a level without being able to complete it."
    solid = False

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((50, 191, 0))
        return res


class Lava(BlockType):
    """
    class for lava block
    """
    name = "lava"
    description = "A block that kills you on touch."
    solid = False

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((255, 77, 0))
        return res


class Ice(BlockType):
    """
    class for ice block
    """
    name = "ice"
    description = "A block that reduces friction dramatically when touched."
    solid = True

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((171, 219, 227))
        return res


class Mud(BlockType):
    """
    class for mud block
    """
    name = "mud"
    description = "A block that slows acceleration and increases friction while touching."
    solid = True

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((171, 24, 10))
        return res


class Sticky(BlockType):
    """
    class for sticky block
    """
    name = "sticky"
    description = "A block that keeps the player from jumping while touching."
    solid = True

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((204, 37, 0))
        return res


class Bouncy(BlockType):
    """
    class for bouncy block
    """
    name = "bouncy"
    description = "A block that bounces players off of it."
    solid = True

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((171, 204, 78))
        return res


class Jump(PointedBlock, BlockType):
    """
    class for jump block
    """
    name = "jump"
    description = "A block that propels the player in a certain direction indicated by the arrow."
    solid = True

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((128, 255, 0))
        draw_arrow(
            res,
            (data[PointedBlock.rotation] - (1 - data[PointedBlock.grav_locked]) * gravity) % 4,
            tuple(((1 - data[PointedBlock.grav_locked]) * 255,) * 3),
            scale
        )
        return res


class Gravity(PointedBlock, VariableValue, BlockType):
    """
    enum for gravity blocks
    """
    name = "gravity"
    description = "When activated, changes either gravity direction or strength."
    solid = True
    type = 2
    mode = 3

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((255, 0, 138))
        if data[Gravity.type] == "set":
            res.blit(
                smoothscale(
                    font.render(
                        "=+-x/"[data[Gravity.mode]] + str(clean_decimal(data[Gravity.variable_value])),
                        True,
                        (0, 0, 0),
                        None
                    ),
                    (scale * 3 / 4, scale * 3 / 4)
                ),
                (scale / 8, scale / 8)
            )
        else:
            draw_arrow(
                res,
                (data[Gravity.rotation] - (1 - data[Gravity.grav_locked]) * gravity) % 4,
                tuple(((1 - data[Gravity.grav_locked]) * 255,) * 3),
                scale
            )
        return res


class EasterEgg(GivesAchievement, BlockType):
    """
    enum for easter egg class
    """
    name = "easter egg"
    description = "Unlocks an otherwise inaccessible level, skin, or achievement."
    solid = True
    type = 5
    level = 6
    skin = 8

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((255, 255, 255))
        lines(
            res,
            (255, 230, 0),
            True,
            ((scale / 2, scale / 4), (scale * 3 / 4, scale / 2), (scale / 2, scale * 3 / 4), (scale / 4, scale / 2)),
            round(scale / 6)
        )
        return res


class Repel(BlockType):
    """
    enum for repel block
    """
    name = "repel"
    description = "A block that throws you either linearly or directly away."
    solid = True
    mode = 9

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((255, 184, 0))
        if data[Repel.mode] == 1:
            lines(
                res,
                (255, 255, 255),
                True,
                (
                    (scale / 2, scale / 4),
                    (scale * 3 / 4, scale / 2),
                    (scale / 2, scale * 3 / 4),
                    (scale / 4, scale / 2)
                ),
                round(scale / 6)
            )
        else:
            line(
                res,
                (255, 255, 255),
                (scale / 2, scale / 4),
                (scale / 2, scale * 3 / 4),
                round(scale / 6)
            )
            line(
                res,
                (255, 255, 255),
                (scale / 4, scale / 2),
                (scale * 3 / 4, scale / 2),
                round(scale / 12)
            )
        return res


class Activator(BlockType, PointedBlock):
    """
    enum for activator block
    """
    name = "activator"
    description = "A block that activates a block in the given direction after a given delay."
    solid = True
    delay = 10

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((204, 41, 41))
        draw_arrow(
            res,
            (data[Activator.rotation] - (1 - data[Activator.grav_locked]) * gravity) % 4,
            tuple(((1 - data[Activator.grav_locked]) * 255,) * 3),
            scale
        )
        circle(
            res,
            (62, 56, 50),
            (scale / 8, scale / 8),
            scale / 12
        )
        circle(
            res,
            (62, 56, 50),
            (7 * scale / 8 + 1, scale / 8),
            scale / 12
        )
        circle(
            res,
            (62, 56, 50),
            (scale / 8, 7 * scale / 8 + 1),
            scale / 12
        )
        circle(
            res,
            (62, 56, 50),
            (7 * scale / 8 + 1, 7 * scale / 8 + 1),
            scale / 12
        )
        res.blit(
            smoothscale(
                font.render(
                    str(clean_decimal(data[Activator.delay])),
                    True,
                    (128, 128, 128),
                    None
                ),
                (scale * 3 / 4, scale * 3 / 4)
            ),
            (scale / 8, scale / 8)
        )
        return res


class Portal(BlockType):
    """
    enum for portal block
    """
    name = "portal"
    description = "A block that repositions the player.  Can also affect their momentum."
    solid = True
    rotation = PointedBlock.rotation
    relative = 12
    x = 13
    y = 14
    reflect_x = 15
    reflect_y = 16

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((0, 16, 97))
        lines(
            res,
            (51, 126, 213),
            False,
            [
                ((scale - 1) / 2, 0),
                (3 * (scale - 1) / 8, (scale - 1) / 4),
                ((scale - 1) / 2, (scale - 1) / 2)
            ],
            round(scale / 12)
        )
        lines(
            res,
            (51, 126, 213),
            False,
            [
                ((scale - 1), (scale - 1) / 6),
                (5 * (scale - 1) / 8, (scale - 1) / 4),
                ((scale - 1) / 2, (scale - 1) / 2)
            ],
            round(scale / 12)
        )
        lines(
            res,
            (51, 126, 213),
            False,
            [
                ((scale - 1), 5 * (scale - 1) / 6),
                (3 * (scale - 1) / 4, (scale - 1) / 2),
                ((scale - 1) / 2, (scale - 1) / 2)
            ],
            round(scale / 12)
        )
        lines(
            res,
            (51, 126, 213),
            False,
            [
                ((scale - 1) / 2, (scale - 1)),
                (5 * (scale - 1) / 8, 3 * (scale - 1) / 4),
                ((scale - 1) / 2, (scale - 1) / 2)
            ],
            round(scale / 12)
        )
        lines(
            res,
            (51, 126, 213),
            False,
            [
                (0, 5 * (scale - 1) / 6),
                (3 * (scale - 1) / 8, 3 * (scale - 1) / 4),
                ((scale - 1) / 2, (scale - 1) / 2)
            ],
            round(scale / 12)
        )
        lines(
            res,
            (51, 126, 213),
            False,
            [
                (0, (scale - 1) / 6),
                ((scale - 1) / 4, (scale - 1) / 2),
                ((scale - 1) / 2, (scale - 1) / 2)
            ],
            round(scale / 12)
        )
        return res


class FragileGround(BlockType):
    """
    enum for fragile ground
    """
    name = "fragile ground"
    description = "This block acts like ground as long as the player is moving below a certain threshold. If the player colides with it above that speed, then it breaks."
    solid = True
    sturdiness = 17
    remove_barriers = 18
    remove_link = 19

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        color = 180 - 6 * data[FragileGround.sturdiness]
        res.fill((color, color, color))
        return res


class Destroyer(BlockType, PointedBlock):
    """
    enum for destroyer block
    """
    name = "destroyer"
    description = "Destroys the block in a direction when activated."
    solid = True
    match_block = 20
    destroy_link = 21
    destroy_barriers = 22
    destroy_block = 23

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((153, 0, 51))
        draw_arrow(
            res,
            (data[Destroyer.rotation] - (1 - data[Destroyer.grav_locked]) * gravity) % 4,
            tuple(((1 - data[Destroyer.grav_locked]) * 255,) * 3),
            scale
        )
        circle(
            res,
            (62, 56, 50),
            (scale / 8, scale / 8),
            scale / 12
        )
        circle(
            res,
            (62, 56, 50),
            (7 * scale / 8 + 1, scale / 8),
            scale / 12
        )
        circle(
            res,
            (62, 56, 50),
            (scale / 8, 7 * scale / 8 + 1),
            scale / 12
        )
        circle(
            res,
            (62, 56, 50),
            (7 * scale / 8 + 1, 7 * scale / 8 + 1),
            scale / 12
        )
        return res


class Rotator(BlockType, VariableValue, PointedBlock):
    """
    enum for rotator block
    """
    name = "rotator"
    description = "Rotates a block if it has a direction component and/or barriers on that block."
    solid = True
    mode = 24
    rotate_block = 25
    rotate_barriers = 26
    grav_account = 27

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((83, 106, 90))
        draw_arrow(
            res,
            (data[Rotator.rotation] - (1 - data[Rotator.grav_locked]) * gravity) % 4,
            tuple(((1 - data[Rotator.grav_locked]) * 255,) * 3),
            scale,
            2 - data[Rotator.mode] + data.get(Rotator.grav_account, 0)
        )
        circle(
            res,
            (62, 56, 50),
            (scale / 8, scale / 8),
            scale / 12
        )
        circle(
            res,
            (62, 56, 50),
            (7 * scale / 8 + 1, scale / 8),
            scale / 12
        )
        circle(
            res,
            (62, 56, 50),
            (scale / 8, 7 * scale / 8 + 1),
            scale / 12
        )
        circle(
            res,
            (62, 56, 50),
            (7 * scale / 8 + 1, 7 * scale / 8 + 1),
            scale / 12
        )
        return res


class Coin(BlockType):
    """
    enum for coin block
    """
    name = "coin"
    description = "In order to complete a level, all of these must be collected."
    solid = False

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((255, 255, 255))
        polygon(
            res,
            (128, 84, 0),
            ((scale / 2, scale / 4), (scale * 3 / 4, scale / 2), (scale / 2, scale * 3 / 4), (scale / 4, scale / 2)),
            0
        )
        polygon(
            res,
            (255, 168, 0),
            ((scale / 2, scale / 4), (scale * 3 / 4, scale / 2), (scale / 2, scale * 3 / 4), (scale / 4, scale / 2)),
            round(scale / 6)
        )
        return res


class Msg(BlockType, HasTextField):
    """
    enum for message block
    """
    name = "msg"
    description = "Displays a message."
    solid = False

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((255, 255, 255))
        res.blit(
            smoothscale(
                font.render(
                    "MSG",
                    True,
                    (128, 128, 128),
                    None
                ),
                (scale * 3 / 4, scale * 3 / 4)
            ),
            (scale / 8, scale / 8)
        )
        return res


class AchievementGoal(GivesAchievement, Goal):
    """
    enum for achievement goal
    """
    name = "achievement goal"
    description = "A goal block only available to admins.  Gives an achievement and finishes the level."
    solid = False


class Air(BlockType):
    """
    air block (in other words, nothing)
    """

    description = None
    solid = False
    name = "air"

    @staticmethod
    def collide() -> None:
        """
        it's air.  Do nothing.
        """
        pass


@dataclass()
class Blocks:
    """
    enumerator for block data
    """
    player = Player  # this was depricated, but still needs to be here :(
    delete = Delete
    ground = Ground
    goal = Goal
    lava = Lava
    ice = Ice
    mud = Mud
    sticky = Sticky
    bouncy = Bouncy
    fragile_ground = FragileGround
    jump = Jump
    repel = Repel
    coin = Coin
    msg = Msg
    gravity = Gravity
    portal = Portal
    activator = Activator
    destroyer = Destroyer
    rotator = Rotator
    easter_egg = EasterEgg
    achievement_goal = AchievementGoal
    air = Air
