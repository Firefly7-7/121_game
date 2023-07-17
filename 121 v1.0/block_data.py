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
from game_structures import Collision
Wrap = IGP = None
# from level_data import LevelWrap as Wrap  # TODO this needs to be commented out for circular reasons
# from in_game_player_data import InGamePlayer as IGP # TODO this needs to be commented out for circular reasons


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
    @property
    @abstractmethod
    def collide_priority() -> int:
        """
        collide priority field
        :return:
        """

    @staticmethod
    @abstractmethod
    def collide(
            collision_list: list[Collision],
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int],tuple[int, int]]
    ) -> None:
        """
        colliding
        :param collision_list: list of collision objects to compute through
        :param level: level data to modify
        :param player: which player is doing the collision (modify its data)
        :param gravity: gravity data to manipulate
        :param new_scheduled: newly scheduled block updates
        :return: nada
        """


    @staticmethod
    @abstractmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        """
        rendering
        :return:
        """


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
    link: Optional[int] = None  # link number

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


class BasicSolid(BlockType, ABC):
    """
    class to inherit from if only collision action is just position correction
    """

    solid = True

    @staticmethod
    def collide(
            collision_list: list[Collision],
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]]
    ) -> None:
        """
        colliding
        :param collision_list: list of collision objects to compute through
        :param level: level data to modify
        :param player: which player is doing the collision (modify its data)
        :param gravity: gravity data to manipulate
        :param new_scheduled: newly scheduled block updates
        :return: nada
        """
        for check in collision_list:
            if check.local:
                player.stop = True
                position_correction(
                    check.coordinates,
                    check.direction,
                    player
                )
                if level.gravity[0] == check.direction:
                    player.grounded = True
                player.corrected = True
                return


class AdvancedSolid(BlockType, ABC):
    """
    solid type that does something after position correction
    """

    solid = True
    reverse: bool = False

    @staticmethod
    @abstractmethod
    def post_correction_collide(
            check: Collision,
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]],
            pre_collision_momentum: tuple,
            activate: bool
    ) -> None:
        """
        does post-correction collision calculations.  Abstract.
        :param check:
        :param level:
        :param player:
        :param gravity:
        :param new_scheduled:
        :param pre_collision_momentum:
        :param activate:
        :return:
        """


    @classmethod
    def collide(
            cls,
            collision_list: list[Collision],
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int],tuple[int, int]]
    ) -> None:
        """
        does basic collision requirements, then calls post-correction collision check
        :param collision_list:
        :param level:
        :param player:
        :param gravity:
        :param new_scheduled:
        :return:
        """
        pre_collision_momentum = tuple(player.mom)
        if cls.reverse:
            collision_list = collision_list.__reversed__()
        for check in collision_list:
            activate = not check.local or abs(player.mom[(check.direction + 1) % 2]) > 3
            if check.local and not player.corrected:
                player.stop = True
                position_correction(
                    check.coordinates,
                    check.direction,
                    player
                )
                if level.gravity[0] == check.direction:
                    player.grounded = True
                player.corrected = False
            cls.post_correction_collide(check, level, player, gravity, new_scheduled, pre_collision_momentum, activate)



class Player(BlockType):
    """
    class for player (literally just has name, deprecated)
    """
    name = "Player"
    description = None
    solid = False

    @staticmethod
    def collide(
            collision_list: list[Collision],
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]]
    ) -> None:
        """
        colliding
        :param collision_list: list of collision objects to compute through
        :param level: level data to modify
        :param player: which player is doing the collision (modify its data)
        :param gravity: gravity data to manipulate
        :param new_scheduled: newly scheduled block updates
        :return: nada
        """
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
    name = "Delete"

    @staticmethod
    def collide(
            collision_list: list[Collision],
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]]
    ) -> None:
        """
        colliding
        :param collision_list: list of collision objects to compute through
        :param level: level data to modify
        :param player: which player is doing the collision (modify its data)
        :param gravity: gravity data to manipulate
        :param new_scheduled: newly scheduled block updates
        :return: nada
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


class Ground(BasicSolid):
    """
    class for ground block
    """

    name = "Ground"
    description = "A solid block with no other properties."

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        return res



class Goal(BlockType):
    """
    class for goal block
    """
    name = "Goal"
    description = "The block you need to finish a level.  You cannot export a level without being able to complete it."
    solid = False

    @staticmethod
    def collide(
            collision_list: list[Collision],
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]]
    ) -> None:
        """
        colliding
        :param collision_list: list of collision objects to compute through
        :param level: level data to modify
        :param player: which player is doing the collision (modify its data)
        :param gravity: gravity data to manipulate
        :param new_scheduled: newly scheduled block updates
        :return: nada
        """
        if Coin in {level.blocks[block].type for block in level.blocks}:
            level.text_output(
                "You must collect all coins before reaching the goal."
            )
        else:
            level.won = True

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((50, 191, 0))
        return res


class Lava(BlockType):
    """
    class for lava block
    """
    name = "Lava"
    description = "A block that kills you on touch."
    solid = False

    @staticmethod
    def collide(
            collision_list: list[Collision],
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]]
    ) -> None:
        """
        colliding
        :param collision_list: list of collision objects to compute through
        :param level: level data to modify
        :param player: which player is doing the collision (modify its data)
        :param gravity: gravity data to manipulate
        :param new_scheduled: newly scheduled block updates
        :return: nada
        """
        level.alive = False

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((255, 77, 0))
        return res


class Ice(BasicSolid):
    """
    class for ice block
    """
    name = "Ice"
    description = "A block that reduces friction dramatically when touched."

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((171, 219, 227))
        return res


class Mud(BasicSolid):
    """
    class for mud block
    """
    name = "Mud"
    description = "A block that slows acceleration and increases friction while touching."

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((171, 24, 10))
        return res


class Sticky(BasicSolid):
    """
    class for sticky block
    """
    name = "Sticky"
    description = "A block that keeps the player from jumping while touching."

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((204, 37, 0))
        return res


class Bouncy(AdvancedSolid):
    """
    class for bouncy block
    """
    name = "Bouncy"
    description = "A block that bounces players off of it."

    @staticmethod
    def post_correction_collide(
            check: Collision,
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]],
            pre_collision_momentum: tuple,
            activate: bool
    ) -> None:
        """
        colliding
        :param check: collision object to compute
        :param level: level data to modify
        :param player: which player is doing the collision (modify its data)
        :param gravity: gravity data to manipulate
        :param new_scheduled: newly scheduled block updates
        :param pre_collision_momentum:
        :param activate:
        :return: nada
        """
        match check.direction:
            case 0:
                player.mom[1] = max(0, pre_collision_momentum[1] * -0.75)
            case 1:
                player.mom[0] = min(pre_collision_momentum[0] * -0.75, 0)
            case 2:
                player.mom[1] = min(0, pre_collision_momentum[1] * -0.75)
            case 3:
                player.mom[0] = max(pre_collision_momentum[0] * -0.75, 0)

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        res.fill((171, 204, 78))
        return res


class Jump(PointedBlock, AdvancedSolid):
    """
    class for jump block
    """

    name = "Jump"
    description = "A block that propels the player in a certain direction indicated by the arrow."
    reverse = True

    @staticmethod
    def post_correction_collide(
            check: Collision,
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]],
            pre_collision_momentum: tuple,
            activate: bool
    ) -> None:
        """

        :param check:
        :param level:
        :param player:
        :param gravity:
        :param new_scheduled:
        :param pre_collision_momentum:
        """
        if (check.other[Jump.rotation] + level.gravity[0] * (
                1 - check.other[Jump.grav_locked])) % 2 == 0:
            if abs(player.mom[1]) < 16.25:
                player.mom[1] = 16.25 * cos(
                    (check.other[Jump.rotation] - level.gravity[0] * (
                            1 - check.other[Jump.grav_locked])) % 4
                )
        else:
            if abs(player.mom[0]) < 16.25:
                player.mom[0] = 16.25 * sin(
                    (check.other[Jump.rotation] + level.gravity[0] * (
                            -1 + check.other[Jump.grav_locked])) % 4
                )

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        """

        :param data:
        :param gravity:
        :param font:
        :param scale:
        :return:
        """
        res = Surface((scale, scale))
        res.fill((128, 255, 0))
        draw_arrow(
            res,
            (data[PointedBlock.rotation] - (1 - data[PointedBlock.grav_locked]) * gravity) % 4,
            tuple(((1 - data[PointedBlock.grav_locked]) * 255,) * 3),
            scale
        )
        return res


class Gravity(PointedBlock, VariableValue, AdvancedSolid):
    """
    enum for gravity blocks
    """
    name = "Gravity"
    description = "When activated, changes either gravity direction or strength."
    type = 2
    mode = 3
    reverse = True

    @staticmethod
    def post_correction_collide(
            check: Collision,
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]],
            pre_collision_momentum: tuple,
            activate: bool
    ) -> None:
        """
        does post-correction collision calculations.  Abstract.
        :param check:
        :param level:
        :param player:
        :param gravity:
        :param new_scheduled:
        :param pre_collision_momentum:
        :return:
        """
        if activate:
            if check.other[Gravity.type] == "direction":
                gravity[0] = (3 * (check.other[Gravity.rotation] - (
                        1 - check.other[Gravity.grav_locked]) *
                                    level.gravity[0]) + 2) % 4
            else:
                match check.other[Gravity.mode]:
                    case 0:
                        gravity[1] = -1 * check.other[Gravity.variable_value]
                    case 1:
                        gravity[1] -= check.other[Gravity.variable_value]
                        if gravity[1] < -2.5:
                            gravity[1] = -2.5
                    case 2:
                        gravity[1] += check.other[Gravity.variable_value]
                        if gravity[1] > 0:
                            gravity[1] = 0
                    case 3:
                        gravity[1] *= check.other[Gravity.variable_value]
                        if gravity[1] < -2.5:
                            gravity[1] = -2.5
                    case 4:
                        if check.other[Gravity.variable_value] == 0:
                            gravity[1] = -2.5
                        else:
                            gravity[1] /= check.other[Gravity.variable_value]
                            if gravity[1] < -2.5:
                                gravity[1] = -2.5
                    case _:
                        print(check.other[Gravity.mode])


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
    name = "Easter Egg"
    description = "Unlocks an otherwise inaccessible level, skin, or achievement."
    solid = False
    type = 5
    level = 6
    skin = 8

    @staticmethod
    def collide(
            collision_list: list[Collision],
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]]
    ) -> None:
        """
        colliding
        :param collision_list: list of collision objects to compute through
        :param level: level data to modify
        :param player: which player is doing the collision (modify its data)
        :param gravity: gravity data to manipulate
        :param new_scheduled: newly scheduled block updates
        :return: nada
        """
        for check in collision_list:
            level.blocks[check.coordinates[0:2]].type = Air
            match level.blocks[check.coordinates[0:2]].other[EasterEgg.type]:
                case "level":
                    level.levels(level.blocks[check.coordinates[0:2]].other[EasterEgg.level])
                case "skin":
                    level.skins(level.blocks[check.coordinates[0:2]].other[EasterEgg.skin])
                case "achievement":
                    level.achievements(
                        level.blocks[check.coordinates[0:2]].other[EasterEgg.achievement])
            level.blocks[check.coordinates[0:2]].other = {}

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


class Repel(AdvancedSolid):
    """
    enum for repel block
    """
    name = "Repel"
    description = "A block that throws you either linearly or directly away."
    mode = 9

    @staticmethod
    def post_correction_collide(
            check: Collision,
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]],
            pre_collision_momentum: tuple,
            activate: bool
    ) -> None:
        """
        do post_position correction collision
        :param check:
        :param level:
        :param player:
        :param gravity:
        :param new_scheduled:
        :param pre_collision_momentum:
        :return:
        """
        if isinstance(check.other, tuple) or check.other[Blocks.repel.mode] == 0:
            if check.direction % 2 == 0:
                player.mom[1] = -16.25 * (check.direction - 1)
            else:
                player.mom[0] = 16.25 * (check.direction - 2)
        else:
            dx = player.pos[0] - check.coordinates[0] * 30 - 15
            dy = player.pos[1] - check.coordinates[1] * 30 - 15
            d = (dx ** 2 + dy ** 2) ** 0.5
            player.mom[0] = 16.25 * dx / d
            player.mom[1] = 16.25 * dy / d

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


class Activator(AdvancedSolid, PointedBlock):
    """
    enum for activator block
    """
    name = "Activator"
    description = "A block that activates a block in the given direction after a given delay."
    solid = True
    delay = 10

    @staticmethod
    def post_correction_collide(
            check: Collision,
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]],
            pre_collision_momentum: tuple,
            activate: bool
    ) -> None:
        """
        does post-correction collision calculations.  Abstract.
        :param check:
        :param level:
        :param player:
        :param gravity:
        :param new_scheduled:
        :param pre_collision_momentum:
        :return:
        """
        look = 3 * (check.other[Blocks.activator.rotation] + (1 - check.other[Blocks.activator.grav_locked]) *
                    level.gravity[0] + 2) % 4
        coordinates = (
            check.coordinates[0] + sin(look),
            check.coordinates[1] - cos(look)
        )
        if coordinates not in new_scheduled:
            new_scheduled[coordinates] = (look, check.other[Activator.delay])

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
    name = "Portal"
    description = "A block that repositions the player.  Can also affect their momentum."
    solid = True
    rotation = PointedBlock.rotation
    relative = 12
    x = 13
    y = 14
    reflect_x = 15
    reflect_y = 16

    @staticmethod
    def collide(
            collision_list: list[Collision],
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]]
    ) -> None:
        """
        colliding
        :param collision_list: list of collision objects to compute through
        :param level: level data to modify
        :param player: which player is doing the collision (modify its data)
        :param gravity: gravity data to manipulate
        :param new_scheduled: newly scheduled block updates
        :return: nada
        """
        portal = collision_list[0]
        if portal.other[Portal.relative]:
            player.pos[0] += portal.other[Portal.x] * 30
            player.pos[1] += portal.other[Portal.y] * 30
        else:
            player.pos[0] = portal.other[Portal.x] * 30 + 15
            player.pos[1] = portal.other[Portal.y] * 30 + 15
        player_momentum = (
            player.mom[0] * (1 - 2 * portal.other[Portal.reflect_x]),
            player.mom[1] * (1 - 2 * portal.other[Portal.reflect_y])
        )
        player.mom[0], player.mom[1] = (
            player.mom[0] * cos(portal.other[Portal.rotation]) + player_momentum[1] * sin(
                portal.other[Portal.rotation]),
            player.mom[1] * cos(portal.other[Portal.rotation]) - player_momentum[0] * sin(
                portal.other[Portal.rotation])
        )
        player.stop = True

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


class FragileGround(AdvancedSolid):
    """
    enum for fragile ground
    """
    name = "Fragile Ground"
    description = "This block acts like ground as long as the player is moving below a certain threshold. If the player colides with it above that speed, then it breaks."
    solid = True
    sturdiness = 17
    remove_barriers = 18
    remove_link = 19

    @staticmethod
    def post_correction_collide(
            check: Collision,
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]],
            pre_collision_momentum: tuple,
            activate: bool
    ) -> None:
        """
        does post-correction collision calculations.  Abstract.
        :param check:
        :param level:
        :param player:
        :param gravity:
        :param new_scheduled:
        :param pre_collision_momentum:
        :return:
        """
        if check.other[FragileGround.sturdiness] < abs(pre_collision_momentum[(check.direction + 1) % 2]):
            block = level.blocks[check.coordinates]
            block.type = Air
            if check.other[FragileGround.remove_barriers]:
                block.barriers = []
            if check.other[FragileGround.remove_link]:
                if block.link is not None:
                    level.links[block.link].remove(check.coordinates)
                    block.link = None

    @staticmethod
    def render(data: dict[int, Any], gravity: int, font: Font, scale: int = 60) -> Surface:
        res = Surface((scale, scale))
        color = 180 - 6 * data[FragileGround.sturdiness]
        res.fill((color, color, color))
        return res


class Destroyer(AdvancedSolid, PointedBlock):
    """
    enum for destroyer block
    """
    name = "Destroyer"
    description = "Destroys the block in a direction when activated."
    match_block = 20
    destroy_link = 21
    destroy_barriers = 22
    destroy_block = 23

    @staticmethod
    def post_correction_collide(
            check: Collision,
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]],
            pre_collision_momentum: tuple,
            activate: bool
    ) -> None:
        """
        does post-correction collision calculations.  Abstract.
        :param check:
        :param level:
        :param player:
        :param gravity:
        :param new_scheduled:
        :param pre_collision_momentum:
        :return:
        """
        if not activate:
            return
        look = 3 * (check.other[Destroyer.rotation] + (1 - check.other[Destroyer.grav_locked]) *
                    level.gravity[0] + 2) % 4
        coordinates = (
            check.coordinates[0] + sin(look),
            check.coordinates[1] - cos(look)
        )
        block = level.blocks.get(coordinates, None)
        if block is None:
            return
        if not isinstance(check.other[Destroyer.match_block], bool):
            if check.other[Destroyer.match_block] is None:
                if block.type != Air:
                    return
            else:
                if block.type != check.other[Destroyer.match_block]:
                    return
        if check.other[Destroyer.destroy_link]:
            if block.link is not None:
                level.links[block.link].remove(coordinates)
                block.link = None
        match check.other[Destroyer.destroy_barriers]:
            case 1:
                block.barriers = []
            case 2:
                if isinstance(block.barriers, tuple):
                    block.barriers = list(block.barriers)
                if block.barriers:
                    del block.barriers[-1]
        if check.other[Destroyer.destroy_block]:
            block.type = Blocks.air

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


class Rotator(AdvancedSolid, VariableValue, PointedBlock):
    """
    enum for rotator block
    """
    name = "Rotator"
    description = "Rotates a block if it has a direction component and/or barriers on that block."
    mode = 24
    rotate_block = 25
    rotate_barriers = 26
    grav_account = 27

    @staticmethod
    def post_correction_collide(
            check: Collision,
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]],
            pre_collision_momentum: tuple,
            activate: bool
    ) -> None:
        """
        does post-correction collision calculations.  Abstract.
        :param check:
        :param level:
        :param player:
        :param gravity:
        :param new_scheduled:
        :param pre_collision_momentum:
        :param activate:
        :return:
        """
        if activate:
            look = 3 * (check.other[Rotator.rotation] - (1 - check.other[Rotator.grav_locked]) *
                        level.gravity[0] + 2) % 4
            coordinates = (
                check.coordinates[0] + sin(look),
                check.coordinates[1] - cos(look)
            )
            block = level.blocks.get(check.coordinates, None)
            if block is None:
                return
            block_rotate = check.other[Rotator.variable_value]
            if check.other[Rotator.rotate_block] and Rotator.rotation in block.other:
                if not check.other[Rotator.mode]:  # if setting, not rotating
                    if check.other[Rotator.grav_account] and not block.other.get(
                            Rotator.grav_locked, True):
                        block_rotate = (check.other[Rotator.variable_value] - block.other[
                            Rotator.rotation] + gravity[0]) % 4
                    else:
                        block_rotate = (check.other[Rotator.variable_value] - block.other[
                            Rotator.rotation]) % 4
                # block.other["rotation"] = (check.other["mode"] * block.other["rotation"] + check.other["amount"]) % 4
                block.other[Rotator.rotation] = (block.other[Rotator.rotation] + block_rotate) % 4
            elif not check.other[Rotator.mode]:
                block_rotate = 0
            if check.other[Rotator.rotate_barriers]:
                for i in range(len(block.barriers)):
                    block.barriers[i] = (
                        block.barriers[i][0],
                        block.barriers[i][1],
                        block.barriers[i][2][4 - block_rotate:]
                        + block.barriers[i][2][:4 - block_rotate]
                    )

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
    name = "Coin"
    description = "In order to complete a level, all of these must be collected."
    solid = False

    @staticmethod
    def collide(
            collision_list: list[Collision],
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]]
    ) -> None:
        """
        colliding
        :param collision_list: list of collision objects to compute through
        :param level: level data to modify
        :param player: which player is doing the collision (modify its data)
        :param gravity: gravity data to manipulate
        :param new_scheduled: newly scheduled block updates
        :return: nada
        """
        for check in collision_list:
            level.blocks[check.coordinates[0:2]].type = Blocks.air

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
    name = "MSG"
    description = "Displays a message."
    solid = False

    @staticmethod
    def collide(
            collision_list: list[Collision],
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]]
    ) -> None:
        """
        colliding
        :param collision_list: list of collision objects to compute through
        :param level: level data to modify
        :param player: which player is doing the collision (modify its data)
        :param gravity: gravity data to manipulate
        :param new_scheduled: newly scheduled block updates
        :return: nada
        """
        level.text_output(collision_list[0].other[Msg.text])

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
    name = "Achievement Goal"
    description = "A goal block only available to admins.  Gives an achievement and finishes the level."
    solid = False

    @staticmethod
    def collide(
            collision_list: list[Collision],
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]]
    ) -> None:
        """
        colliding
        :param collision_list: list of collision objects to compute through
        :param level: level data to modify
        :param player: which player is doing the collision (modify its data)
        :param gravity: gravity data to manipulate
        :param new_scheduled: newly scheduled block updates
        :return: nada
        """
        if Coin in {level.blocks[block].type for block in level.blocks}:
            level.text_output(
                "You must collect all coins before reaching the goal."
            )
        else:
            for check in collision_list:
                level.achievements(
                    level.blocks[check.coordinates[0:2]].other[Blocks.achievement_goal.achievement])
            level.won = True


class Air(BlockType):
    """
    air block (in other words, nothing)
    """

    description = None
    solid = False
    name = "Air"

    @staticmethod
    def collide(
            collision_list: list[Collision],
            level: Wrap,
            player: IGP,
            gravity: list[int, float],
            new_scheduled: dict[tuple[int, int], tuple[int, int]]
    ) -> None:
        """
        it's air.  Do nothing
        :param collision_list: list of collision objects to compute through
        :param level: level data to modify
        :param player: which player is doing the collision (modify its data)
        :param gravity: gravity data to manipulate
        :param new_scheduled: newly scheduled block updates
        :return: nada
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

def position_correction(
        block_coords: tuple[int, int],
        direction: int,
        player: IGP,
) -> None:
    """
    cleans position after block collision
    :param block_coords: coordinates of block collided with (maybe, just needs correct relevant data)
    :param direction: direction coming from
    :param player: player to correct
    :return: nada (in place)
    """
    match direction:
        case 0:
            player.pos[1] = block_coords[1] * 30 + 40.25
            player.mom[1] = max(0, player.mom[1])
        case 1:
            player.pos[0] = block_coords[0] * 30 - 10.25
            player.mom[0] = min(0, player.mom[0])
        case 2:
            player.pos[1] = block_coords[1] * 30 - 10.25
            player.mom[1] = min(0, player.mom[1])
        case 3:
            player.pos[0] = block_coords[0] * 30 + 40.25
            player.mom[0] = max(0, player.mom[0])