"""
level class
"""
from dataclasses import dataclass
from block_data import Block, BlockType, Blocks
from game_structures import Collision
from typing import Union, Callable, Optional, Any
from constants import BARRIER_COLORS
from render_help import sin, cos, degree_to_rgb
from pygame.time import get_ticks
from in_game_player_data import InGamePlayer
from copy import deepcopy, copy
from pygame.font import Font
from pygame.surface import Surface
from math import floor
from pygame.draw import line, circle
from pygame.transform import smoothscale
from sortedcontainers import SortedList


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
    name: str
    gravity: tuple[int, float]
    blocks: dict[tuple[int, int], Block]
    links: list[list[tuple[int, int]]]
    player_starts: list[tuple[int, int]]
    dimensions: tuple[int, int] = (11, 11)
    version: int = 4
    next: Union[None, Level] = None


class LevelWrap:
    """
    dataclass containing completed level data
    """

    frame_skip = 1
    bounds = 12

    def __init__(
            self,
            level: Level
    ):
        self.level_on = level
        self.alive = True
        self.won = False
        self.achievements: Optional[Callable] = None
        self.skins: Optional[Callable] = None
        self.levels: Optional[Callable] = None
        self.text_output: Optional[Callable] = None
        self.alert_output: Optional[Callable] = None
        self.jump: Optional[int] = None
        self.left: Optional[int] = None
        self.right: Optional[int] = None
        self.control_check: Optional[Callable] = None
        self.tick_track: int = 0
        self.time: int = 0
        self.players: list[InGamePlayer] = []
        self.blocks: Optional[dict[tuple[int, int], Block]] = None
        self.links: Optional[list[list[tuple[int, int]]]] = None
        self.gravity: Optional[tuple[int, float]] = None
        self.priority_list: Union[tuple[Union[BlockType, None]], None] = None

    def next(self) -> bool:
        """
        gets next level data and prepares it if it exists.  Returns if there was a next one
        :return: if there is a next level/stage
        """
        if self.level_on.next is None:
            return False
        self.level_on = self.level_on.next
        self.prepare_for_play()
        self.alive = False
        self.won = False
        self.tick_track = 0
        self.time = 0
        return True

    def set_outputs(
            self,
            achievements: Callable,
            skins: Callable,
            levels: Callable,
            text_output: Callable,
            alert_output: Callable
    ) -> None:
        """
        sets out-of-level outputs for blocks
        :param achievements: where to put through for achievements
        :param skins: where to put through for skins
        :param levels: where to put through for easter egg levels
        :param text_output: where to put through for text announcements
        :param alert_output: where to put through for alerts
        :return: none
        """
        self.achievements: Optional[Callable] = achievements
        self.skins: Optional[Callable] = skins
        self.levels: Optional[Callable] = levels
        self.text_output: Optional[Callable] = text_output
        self.alert_output: Optional[Callable] = alert_output

    def set_controls(
            self,
            jump: int,
            left: int,
            right: int,
            control_check: Callable
    ):
        """
        sets controls
        :param jump:
        :param left:
        :param right:
        :param control_check:
        :return:
        """
        self.jump = jump
        self.left = left
        self.right = right
        self.control_check = control_check

    def prepare_for_play(self) -> None:
        """
        prepares for play
        :return:
        """
        # prepare board
        self.blocks = deepcopy(self.level_on.blocks)
        self.links = deepcopy(self.level_on.links)
        self.gravity = deepcopy(self.level_on.gravity)
        for i, link_objects in enumerate(self.links):
            for coordinates in link_objects:
                if coordinates in self.blocks.keys():
                    if isinstance(self.blocks[coordinates].other, tuple):
                        self.blocks[coordinates].other = {}
                    self.blocks[coordinates].link = i
                else:
                    self.blocks[coordinates] = Block(
                        Blocks.air,
                        [],
                        {},
                        i
                    )
        # prepare players
        self.players = [
            InGamePlayer([player_x * 30 + 15, player_y * 30 + 15]) for player_x, player_y in self.level_on.player_starts
        ]
        # prepare gamestate
        self.won = False
        self.alive = True
        # prepare collision priority list
        priority_list: SortedList[BlockType] = SortedList()
        for block in self.blocks.values():
            if block.type.collide_priority is not None:
                if block.type not in priority_list:
                    priority_list.add(block.type)
            for bar in block.barriers:
                if bar[0].collide_priority is not None:
                    if bar[0] not in priority_list:
                        priority_list.add(bar[0])
        priority_list: list[Union[BlockType, None]] = list(priority_list)
        i = 1
        while i < len(priority_list):
            if round(priority_list[i].collide_priority) != round(priority_list[i - 1].collide_priority):
                priority_list.insert(i, None)
                i += 1
            i += 1
        self.priority_list = tuple(priority_list)

    # noinspection PyTypeChecker
    def collision(
            self,
            player: InGamePlayer,
            colliding: list[tuple[int, int, int]],
            local: bool
    ) -> bool:
        """
        sets up a collision and gets list of blocks to collide, not hierarchied
        :param player: player to run collisions for
        :param colliding: what blocks you're colliding with
        :param local: if the player is local to the collisions (or link/activator)
        :return: tuple of coordinates, tuple of movement, set of block types collided with, dictionary for scheduled reactions, tuple of gravity info, if touched ground, and if it should stop movements
        """
        new_touched = self.get_collisions(colliding, local, self.gravity)
        new_scheduled = self.execute_collisions(new_touched, player)
        scheduled_merge(self.time, player.scheduled, new_scheduled)
        player.block_record.update(set(new_touched))

    def get_collisions(
            self,
            blocks: list[tuple[int, int, int]],
            local: bool,
            gravity: tuple[int, float]
    ) -> dict[BlockType, list[Collision]]:
        """
        sets up a collision and gets list of blocks to collide, not hierarchied
        :param blocks: list of coordinate tuples then direction integer
        :param local: if it is the player hitting these blocks (is it from an activation or not)
        :param gravity: gravity info to use
        :return: constructed new touched objects
        """
        # print(f"Collision called on {blocks}.")
        # print(block_info.keys())
        # keeps track of blocks previously reacted on to prevent double reactions
        hit = set()
        # keeps track of types of blocks previously reacted on, and records collision objects
        new_touched = dict()
        # if has touched the ground on this one
        for block in blocks:
            if block[0:2] in hit:
                continue
            hit.add(block[0:2])
            col = self.blocks.get(block[0:2])
            if col is None:
                continue
            # print(f"Collision with {block} detected.")
            add = Collision(
                block[2],
                local,
                block[0:2],
                col.other,
                col.link
            )
            block_collision = True
            typ = col.type
            for bar in col.barriers:
                if bar[2][3 * (block[2] - gravity[0] * bar[1]) % 4]:
                    add = Collision(
                        block[2],
                        local,
                        block[0:2]
                    )
                    typ = bar[0]
            if typ not in new_touched:
                new_touched[typ] = []
            new_touched[typ].append(add)
            if add.link is not None:
                for link_block in self.links[add.link]:
                    # checks if the block has already been collided with
                    if link_block in hit:
                        continue
                    # registers that the block has been hit
                    hit.add(link_block)
                    link_block_info = self.blocks[link_block]
                    if link_block_info.type not in new_touched:
                        new_touched[link_block_info.type] = []
                        # print(link_block_info.type)
                        # print(Collision(
                        #     block[2],
                        #     False,
                        #     link_block,
                        #     link_block_info.other
                        # ))
                    new_touched[link_block_info.type].append(Collision(
                        block[2],
                        False,
                        link_block,
                        link_block_info.other
                    ))
        return new_touched

    # noinspection PyTypeChecker
    def execute_collisions(
            self,
            new_touched: dict[str, list[Collision]],
            player: InGamePlayer
    ) -> dict[tuple[int, int], tuple[int, int]]:
        """
        runs collision reactions on blocks
        :param new_touched: list of coordinate tuples
        :param player: player that's colliding
        :return: tuple of coordinates, tuple of movement, set of block types collided with, dictionary for scheduled reactions, tuple of gravity info, and if touched ground
        """
        gravity = list(self.gravity)
        new_scheduled = dict()
        player.stop = False
        player.corrected = False
        for check in self.priority_list:
            if check is None:
                if not self.alive or self.won:
                    return new_scheduled
            if check in new_touched:
                check.collide(new_touched[check], self, player, gravity, new_scheduled)
        # if Blocks.lava in new_touched:
        #     Blocks.lava.collide(new_touched[Blocks.lava], cls, player, gravity, new_scheduled)
        # if not cls.alive or cls.won:
        #     return new_scheduled
        # if Blocks.goal in new_touched:
        #     Blocks.goal.collide(new_touched[Blocks.goal], cls, player, gravity, new_scheduled)
        # if Blocks.achievement_goal in new_touched:
        #     Blocks.achievement_goal.collide(new_touched[Blocks.achievement_goal], cls, player, gravity, new_scheduled)
        # if not cls.alive or cls.won:
        #     return new_scheduled
        # if Blocks.bouncy in new_touched:
        #     Blocks.bouncy.collide(new_touched[Blocks.bouncy], cls, player, gravity, new_scheduled)
        # if Blocks.ground in new_touched:
        #     Blocks.ground.collide(new_touched[Blocks.ground], cls, player, gravity, new_scheduled)
        # if Blocks.fragile_ground in new_touched:
        #     Blocks.fragile_ground.collide(new_touched[Blocks.fragile_ground], cls, player, gravity, new_scheduled)
        # if Blocks.sticky in new_touched:
        #     Blocks.sticky.collide(new_touched[Blocks.sticky], cls, player, gravity, new_scheduled)
        # if Blocks.ice in new_touched:
        #     Blocks.ice.collide(new_touched[Blocks.ice], cls, player, gravity, new_scheduled)
        # if Blocks.mud in new_touched:
        #     Blocks.mud.collide(new_touched[Blocks.mud], cls, player, gravity, new_scheduled)
        # if Blocks.jump in new_touched:
        #     Blocks.jump.collide(new_touched[Blocks.jump], cls, player, gravity, new_scheduled)
        # if Blocks.repel in new_touched:
        #     Blocks.repel.collide(new_touched[Blocks.repel], cls, player, gravity, new_scheduled)
        # if Blocks.gravity in new_touched:
        #     Blocks.gravity.collide(new_touched[Blocks.gravity], cls, player, gravity, new_scheduled)
        # if Blocks.activator in new_touched:
        #     Blocks.activator.collide(new_touched[Blocks.activator], cls, player, gravity, new_scheduled)
        # if Blocks.destroyer in new_touched:
        #     Blocks.destroyer.collide(new_touched[Blocks.destroyer], cls, player, gravity, new_scheduled)
        # if Blocks.rotator in new_touched:
        #     Blocks.rotator.collide(new_touched[Blocks.rotator], cls, player, gravity, new_scheduled)
        # if Blocks.coin in new_touched:
        #     Blocks.coin.collide(new_touched[Blocks.coin], cls, player, gravity, new_scheduled)
        # if Blocks.portal in new_touched:
        #     Blocks.portal.collide(new_touched[Blocks.portal], cls, player, gravity, new_scheduled)
        # if Blocks.easter_egg in new_touched:
        #     Blocks.easter_egg.collide(new_touched[Blocks.easter_egg], cls, player, gravity, new_scheduled)
        # if Blocks.msg in new_touched:
        #     Blocks.msg.collide(new_touched[Blocks.msg], cls, player, gravity, new_scheduled)
        self.gravity = tuple(gravity)
        return new_scheduled

    def in_between_collision(
            self,
            blocks: list[tuple[int, int, int]],
            player_pos: tuple[float, float],
            player_momentum: tuple[float, float]
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        """
        barebones collision to stop bleeding into other blocks
        :param blocks: list of coordinate tuples and direction
        :param player_pos: player position
        :param player_momentum: player momentum
        :return: tuple of coordinates, tuple of movement
        """
        for block in self.blocks:
            col = self.blocks.get(block[0:2])
            if col is None:
                continue
            typ = col.type
            for bar in col.barriers:
                if bar[2][3 * (block[2] - self.gravity[0] * bar[1]) % 4]:
                    typ = bar[0]
            if typ.solid:
                return position_correction(block[0:2], block[2], player_pos, player_momentum)
        return player_pos, player_momentum

    def in_between_physics(
            self,
            player_pos: tuple[Union[int, float], Union[int, float]],
            player_momentum: tuple[Union[int, float], Union[int, float]],
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        """
        does barebones physics for a single player entity
        :param player_pos: position of the player (x, y)
        :param player_momentum: momentum of the player (x, y)
        :return: new player position, player momentum, new block record, new scheduled
        """
        p_x, p_y = player_pos
        p_xm, p_ym = player_momentum
        if self.bounds + 30 > p_x + p_xm:
            p_xm = 0
            p_x = self.bounds + 30
        elif p_x + p_xm > 11 * 30 - self.bounds + 30:
            p_xm = 0
            p_x = 11 * 30 - self.bounds + 30
        if self.bounds + 30 > p_y + p_ym:
            p_ym = 0
            p_y = self.bounds + 30
        elif p_y + p_ym > 11 * 30 - self.bounds + 30:
            p_ym = 0
            p_y = 11 * 30 - self.bounds + 30
        p_x += p_xm
        if p_xm > 0:
            if (p_x + 10) // 30 != (p_x - p_xm + 10) // 30:
                (p_x, p_y), (p_xm, p_ym) = self.in_between_collision(
                    [
                        (int((p_x + 10) // 30), int((p_y + 10) // 30), 1),
                        (int((p_x + 10) // 30), int((p_y - 10) // 30), 1)
                    ],
                    (p_x, p_y),
                    (p_xm, p_ym)
                )
        else:
            if (p_x - 10) // 30 != (p_x - p_xm - 10) // 30:
                (p_x, p_y), (p_xm, p_ym) = self.in_between_collision(
                    [
                        (int((p_x - 10) // 30), int((p_y + 10) // 30), 3),
                        (int((p_x - 10) // 30), int((p_y - 10) // 30), 3)
                    ],
                    (p_x, p_y),
                    (p_xm, p_ym)
                )
        # y move
        p_y += p_ym
        # y collisions
        if p_ym > 0:
            if (p_y + 10) // 30 != (p_y - p_ym + 10) // 30:
                (p_x, p_y), (p_xm, p_ym) = self.in_between_collision(
                    [
                        (int((p_x + 10) // 30), int((p_y + 10) // 30), 2),
                        (int((p_x - 10) // 30), int((p_y + 10) // 30), 2)
                    ],
                    (p_x, p_y),
                    (p_xm, p_ym)
                )
        else:
            if (p_y - 10) // 30 != (p_y - p_ym - 10) // 30:
                (p_x, p_y), (p_xm, p_ym) = self.in_between_collision(
                    [
                        (int((p_x - 10) // 30), int((p_y - 10) // 30), 0),
                        (int((p_x + 10) // 30), int((p_y - 10) // 30), 0)
                    ],
                    (p_x, p_y),
                    (p_xm, p_ym)
                )
        return (p_x, p_y), (p_xm, p_ym)

    def do_physics(
            self,
            player: InGamePlayer,
    ) -> None:
        """
        does physics for a player entity in place
        :param player: player entity
        :return: nada
        """
        # scheduled updates
        run_reactions = []
        for schedule in player.scheduled.copy():
            if player.scheduled[schedule][1] < self.time:
                run_reactions.append((schedule[0], schedule[1], player.scheduled[schedule][0]))
                del player.scheduled[schedule]
        self.collision(player, run_reactions, False)

        # normal physics
        if Blocks.mud in player.block_record:
            sideways_accel = 0.75
            jump_power = 6
            gravity_strength = self.gravity[1] / 1.85
            friction = 0.85
        else:
            sideways_accel = 1.5
            jump_power = 12
            gravity_strength = self.gravity[1]
            friction = 0.9
        if Blocks.ice in player.block_record:
            friction = 1 - (1 - friction) * 0.25
        # controls
        if self.control_check(self.right):
            player.mom[0] += cos(self.gravity[0]) * sideways_accel
            player.mom[1] += sin(self.gravity[0]) * sideways_accel
        if self.control_check(self.left):
            player.mom[0] -= cos(self.gravity[0]) * sideways_accel
            player.mom[1] -= sin(self.gravity[0]) * sideways_accel
        if self.control_check(self.jump) and player.grounded and Blocks.sticky not in player.block_record:
            player.mom[0] -= sin(self.gravity[0]) * jump_power
            player.mom[1] += cos(self.gravity[0]) * jump_power
        player.grounded = False
        # gravity
        player.mom[0] -= sin(self.gravity[0]) * gravity_strength
        player.mom[1] += cos(self.gravity[0]) * gravity_strength
        # friction
        player.mom[self.gravity[0] % 2] *= friction
        # track of if collisions find ground
        new_ground = False
        player.block_record = set()
        # x collisions

        remaining_xm = player.mom[0]
        step = (player.mom[0] > 0) * 2 - 1
        for dif in range(0, abs(int(player.pos[0] + player.mom[0] + 10 * step) // 30 - int(player.pos[0] + 10 * step) // 30)):
            player.pos[0] += 30 * step
            remaining_xm -= 30 * step
            x = int(player.pos[0] + 10 * step) // 30
            self.collision(
                player,
                [
                    (x, int((player.pos[1] + 10) // 30), 2 - step),
                    (x, int((player.pos[1] - 10) // 30), 2 - step)
                ],
                True
            )
            if not self.alive:
                player.pos[0] += remaining_xm
                return
            if player.stop:
                remaining_xm = 0
                break
        player.pos[0] += remaining_xm
        # if not cls.alive:
        #     return
        # ground = ground or new_ground

        remaining_ym = player.mom[1]
        step = (player.mom[1] > 0) * 2 - 1
        for dif in range(0, abs(int(player.pos[1] + player.mom[1] + 10 * step) // 30 - int(player.pos[1] + 10 * step) // 30)):
            player.pos[1] += 30 * step
            remaining_ym -= 30 * step
            y = int(player.pos[1] + 10 * step) // 30
            self.collision(
                player,
                [
                    (int((player.pos[0] + 10) // 30), y, 1 + step),
                    (int((player.pos[0] - 10) // 30), y, 1 + step)
                ],
                True
            )
            if not self.alive:
                player.pos[1] += remaining_ym
                return
            if player.stop:
                remaining_ym = 0
                break
        player.pos[1] += remaining_ym

        # bounds
        if self.bounds + 30 > player.pos[0]:
            # noinspection PyTypeChecker
            player.mom[0] = max(0, player.mom[0])
            player.pos[0] = self.bounds + 30
            if self.gravity[0] == 3:
                player.grounded = True
        elif player.pos[0] > 11 * 30 - self.bounds + 30:
            # noinspection PyTypeChecker
            player.mom[0] = min(0, player.mom[0])
            player.pos[0] = 11 * 30 - self.bounds + 30
            if self.gravity[0] == 1:
                player.grounded = True
        if self.bounds + 30 > player.pos[1]:
            # noinspection PyTypeChecker
            player.mom[1] = max(0, player.mom[1])
            player.pos[1] = self.bounds + 30
            if self.gravity[0] == 0:
                player.grounded = True
        elif player.pos[1] > 11 * 30 - self.bounds + 30:
            # noinspection PyTypeChecker
            player.mom[1] = min(0, player.mom[1])
            player.pos[1] = 11 * 30 - self.bounds + 30
            if self.gravity[0] == 2:
                player.grounded = True

        # p_x += p_xm
        # if p_xm > 0:
        #     if (p_x + 10) // 30 != (p_x - p_xm + 10) // 30:
        #         (p_x, p_y), (p_xm, p_ym), add_touched, add_reactions, new_ground = collision(
        #             [
        #                 (int((p_x + 10) // 30), int((p_y + 10) // 30), 1),
        #                 (int((p_x + 10) // 30), int((p_y - 10) // 30), 1)
        #             ],
        #             (p_x, p_y),
        #             (p_xm, p_ym),
        #             True,
        #         )
        # else:
        #     if (p_x - 10) // 30 != (p_x - p_xm - 10) // 30:
        #         (p_x, p_y), (p_xm, p_ym), add_touched, add_reactions, new_ground = collision(
        #             [
        #                 (int((p_x - 10) // 30), int((p_y + 10) // 30), 3),
        #                 (int((p_x - 10) // 30), int((p_y - 10) // 30), 3)
        #             ],
        #             (p_x, p_y),
        #             (p_xm, p_ym),
        #             True,
        #         )
        # new_block_record.update(add_touched)
        # if not cls.alive:
        #     return (p_x, p_y), (p_xm, p_ym), new_block_record, add_reactions, ground
        # ground = ground or new_ground
        # scheduled_merge(time, scheduled, add_reactions)

        # # y move
        # p_y += p_ym  # / (frame_skip + 1)
        # # y collisions
        # if p_ym > 0:
        #     if (p_y + 10) // 30 != (p_y - p_ym + 10) // 30:
        #         (p_x, p_y), (p_xm, p_ym), add_touched, add_reactions, new_ground = collision(
        #             [
        #                 (int((p_x + 10) // 30), int((p_y + 10) // 30), 2),
        #                 (int((p_x - 10) // 30), int((p_y + 10) // 30), 2)
        #             ],
        #             (p_x, p_y),
        #             (p_xm, p_ym),
        #             True
        #         )
        # else:
        #     if (p_y - 10) // 30 != (p_y - p_ym - 10) // 30:
        #         (p_x, p_y), (p_xm, p_ym), add_touched, add_reactions, new_ground = collision(
        #             [
        #                 (int((p_x - 10) // 30), int((p_y - 10) // 30), 0),
        #                 (int((p_x + 10) // 30), int((p_y - 10) // 30), 0)
        #             ],
        #             (p_x, p_y),
        #             (p_xm, p_ym),
        #             True
        #         )
        # finish
        return

    def tick(self):
        """
        ticks level data
        :return:
        """
        self.time = get_ticks()
        if self.alive:
            if self.tick_track == self.frame_skip:
                self.tick_track = 0
                for player in self.players:
                    self.do_physics(player)
            else:
                self.tick_track += 1
                # noinspection PyTypeChecker
                # print(in_between_player_data[i])
                # cls.in_between_physics()

    def render_level(self, scale: int, font: Font, player_imgs: tuple[Surface, Surface, Surface, Surface]):
        """
        draws a level
        :param scale:
        :param font:
        :param player_imgs: list of player images corresponding to gravity direction
        :return:
        """
        # print(dimensions)
        drawn = Surface((11 * scale + floor(scale / 20), 11 * scale + floor(scale / 20)))
        drawn.fill((255, 255, 255))
        for coordinates, block in self.blocks.items():
            drawn.blit(
                self.draw_block(block, font, scale),
                ((coordinates[0] - 1) * scale, (11 - coordinates[1]) * scale)
            )
            # print(coordinates)
        for i in range(11 + 1):
            line(drawn, (0, 0, 0), (i * scale, 0), (i * scale, 11 * scale), floor(scale / 10))
        for i in range(11 + 1):
            line(drawn, (0, 0, 0), (0, i * scale), (11 * scale, i * scale), floor(scale / 10))
        player = smoothscale(player_imgs[self.gravity[0]], (scale * 3 / 4, scale * 3 / 4))
        for play in self.players:
            drawn.blit(
                player,
                (
                    (play.pos[0] - 30) * (scale / 30) - scale * 3 / 8 + floor(scale / 40),
                    (360 - play.pos[1]) * (scale / 30) - scale * 3 / 8 + floor(scale / 40)
                )
            )
        return drawn

    def draw_block(self, block: Block, font: Font, scale: int = 60) -> Surface:
        """
        draws a single block onto a surface
        :param block: block data
        :param font: font to write with
        :param scale: what size to use
        :return: drawn surface
        """
        res = block.type.render(block.other, self.gravity[0], font, scale)
        if res is None:
            res = Surface((scale, scale))
            res.fill((255, 255, 255))
        # barriers
        # if block.barriers:
        #     print(block.barriers)
        barrier_destination = ((scale, 0), (scale, scale), (0, scale), (0, 0))
        for barrier_type, grav_lock, barriers in block.barriers:
            for i in range(4):
                if barriers[i]:
                    line(
                        res,
                        BARRIER_COLORS[barrier_type][grav_lock],
                        barrier_destination[i - 1 - grav_lock * self.gravity[0]],
                        barrier_destination[i - grav_lock * self.gravity[0]],
                        round(scale * 0.285)
                    )
        # links
        if block.link is not None:
            circle(res, (0, 0, 0), (scale / 4, scale / 4), scale / 16 + 1)
            circle(res, degree_to_rgb(block.link * 54), (scale / 4, scale / 4), scale / 16)
        return res


def position_correction(
        block_coords: tuple[int, int],
        direction: int,
        player: InGamePlayer,
) -> None:
    """
    cleans position after block collision
    :param block_coords: coordinates of block collided with (maybe, just needs correct relevant data)
    :param direction: direction coming from
    :param player: player to correct
    :return: tuple of tuple of new position, new motion
    """
    if direction == 0:
        player.pos[1] = block_coords[1] * 30 + 40.25
        player.mom[1] = max(0, player.mom[1])
    elif direction == 2:
        player.pos[1] = block_coords[1] * 30 - 10.25
        player.mom[1] = min(0, player.mom[1])
    elif direction == 1:
        player.pos[0] = block_coords[0] * 30 - 10.25
        player.mom[0] = min(0, player.mom[0])
    elif direction == 3:
        player.pos[0] = block_coords[0] * 30 + 40.25
        player.mom[0] = max(0, player.mom[0])


def scheduled_merge(
        time: int,
        add_to: dict[tuple[int, int], tuple[int, int]],
        add_from: dict[tuple[int, int], tuple[int, float]]
) -> None:
    """
    merges between two scheduled dictionaries, one before scaling, one after
    :param time: what time is it?
    :param add_to: added to
    :param add_from: added from (pre-scaling)
    :return: none, does it in place
    """
    for block in add_from:
        if block not in add_to:
            add_to[block] = (add_from[block][0], time + int(add_from[block][1] * 1000))