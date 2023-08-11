"""
level class
"""
from dataclasses import dataclass
from block_data import Block, BlockType, Blocks, ControlEffect
from game_structures import Collision
from typing import Union, Callable, Optional, Any
from constants import BARRIER_COLORS
from render_help import sin, cos, degree_to_rgb
from pygame.time import get_ticks
from in_game_player_data import InGamePlayer, InGamePlayerInBetween
from copy import deepcopy, copy
from pygame.font import Font
from pygame.surface import Surface
from math import floor
from pygame.draw import line, circle
from pygame.transform import smoothscale
from sortedcontainers import SortedList
from abc import ABCMeta
import traceback


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
    center: tuple[int, int]
    version: int = 5
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
        self.center: Optional[list[int, int]] = None
        self.priority_list: Union[tuple[Union[BlockType, None]], None] = None
        self.in_between_track: list[InGamePlayerInBetween] = []
        self.run_in_between: bool = False

    @property
    def name(self):
        return self.level_on.name

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
        self.tick_track = 1
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
        self.center = list(self.level_on.center)
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
                        [],
                        i
                    )
        # prepare gamestate
        self.won = False
        self.alive = True
        # prepare collision priority list
        for val in Blocks.__dict__.values():
            if isinstance(val, ABCMeta):
                val.priority_index = None
        priority_list: SortedList[BlockType] = SortedList()
        negative_priority_list: SortedList[BlockType] = SortedList()

        def add_to_priority(block_type: BlockType) -> None:
            if block_type.collide_priority is None:
                return
            if block_type.collide_priority < 0:
                if block_type not in negative_priority_list:
                    negative_priority_list.add(block_type)
            else:
                if block_type not in priority_list:
                    priority_list.add(block_type)

        for block in self.blocks.values():
            adding = block.type.declare_required()
            for add in adding:
                add_to_priority(add)
            for bar in block.barriers:
                adding = bar[0].declare_required()
                for add in adding:
                    add_to_priority(add)
        priority_list: list[Union[BlockType, None]] = list(priority_list) + list(negative_priority_list)
        for index in range(len(priority_list)):
            priority_list[index].priority_list_index = index
        i = 1
        while i < len(priority_list):
            if round(priority_list[i].collide_priority) != round(priority_list[i - 1].collide_priority):
                priority_list.insert(i, None)
                i += 1
            i += 1
        self.priority_list = tuple(priority_list)
        # prepare players
        self.players = [
            InGamePlayer([player_x * 30 + 15, player_y * 30 + 15]) for player_x, player_y in self.level_on.player_starts
        ]
        self.in_between_track.clear()
        for player in self.players:
            player.collision_record = tuple(list() for typ in self.priority_list)
            self.in_between_track.append(InGamePlayerInBetween(player))

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
        self.get_collisions(colliding, local, self.gravity, player)
        new_scheduled = self.execute_collisions(player)
        scheduled_merge(self.time, player.scheduled, new_scheduled)

    def add_collision_to_player_collision_list(
            self,
            collision: Collision,
            typ: BlockType,
            player: InGamePlayer
    ):
        if typ.priority_list_index is None:
            return
        i = 0
        while i < len(player.collision_record[typ.priority_list_index]):
            col = player.collision_record[typ.priority_list_index][i]
            if col.local:
                i += 1
                continue
            if col.other is collision.other and col.coordinates == collision.coordinates and collision.local:
                del player.collision_record[typ.priority_list_index][i]
                break
            i += 1
        player.collision_record[typ.priority_list_index].append(collision)

    def get_collisions(
            self,
            blocks: list[tuple[int, int, int]],
            local: bool,
            gravity: tuple[int, float],
            player: InGamePlayer
    ) -> None:
        """
        sets up a collision and gets list of blocks to collide, not hierarchied
        :param blocks: list of coordinate tuples then direction integer
        :param local: if it is the player hitting these blocks (is it from an activation or not)
        :param gravity: gravity info to use
        :param player: player object that is doing the colliding
        :return: constructed new touched objects
        """
        # keeps track of blocks previously reacted on to prevent double reactions
        # hit = set()
        hit_links = set()
        # if has touched the ground on this one
        for block in blocks:
            # if block[0:2] in hit:
            #     continue
            # hit.add(block[0:2])
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
            typ = col.type
            for bar in col.barriers:
                if bar[2][3 * (block[2] - gravity[0] * bar[1]) % 4]:
                    add = Collision(
                        block[2],
                        local,
                        block[0:2]
                    )
                    typ = bar[0]
            self.add_collision_to_player_collision_list(add, typ, player)
            if add.link is not None:
                print(add.link)
                if add.link not in hit_links:
                    print("Propagated")
                    hit_links.add(add.link)
                    for link_block in self.links[add.link]:
                        # checks if the block has already been collided with
                        # if link_block in hit:
                        #     continue
                        # # registers that the block has been hit
                        # hit.add(link_block)
                        link_block_info = self.blocks[link_block]
                        if link_block_info.type.priority_list_index is not None:
                            self.add_collision_to_player_collision_list(
                                Collision(
                                    block[2],
                                    False,
                                    link_block,
                                    link_block_info.other
                                ),
                                link_block_info.type,
                                player
                            )
                            # player.collision_record[link_block_info.type.priority_list_index].append(Collision(
                            #     block[2],
                            #     False,
                            #     link_block,
                            #     link_block_info.other
                            # ))

    # noinspection PyTypeChecker
    def execute_collisions(
            self,
            player: InGamePlayer
    ) -> dict[tuple[int, int], tuple[int, int]]:
        """
        runs collision reactions on blocks
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
                    self.gravity = tuple(gravity)
                    return new_scheduled
                if player.stop:
                    for record in player.collision_record:
                        record.clear()
            elif player.collision_record[check.priority_list_index]:
                if issubclass(check, ControlEffect):
                    player.block_record.add(check)
                check.collide(self, player, gravity, new_scheduled)
                player.collision_record[check.priority_list_index].clear()
        self.gravity = tuple(gravity)
        return new_scheduled

    def in_between_collision(
            self,
            blocks: list[tuple[int, int, int]],
            player: InGamePlayer
    ) -> None:
        """
        barebones collision to stop bleeding into other blocks
        :param blocks: list of coordinate tuples and direction
        :param player:
        :return: nada
        """
        for block in blocks:
            col = self.blocks.get(block[0:2])
            if col is None:
                continue
            typ = col.type
            for bar in col.barriers:
                if bar[2][3 * (block[2] - self.gravity[0] * bar[1]) % 4]:
                    typ = bar[0]
            if typ.solid:
                position_correction(block[0:2], block[2], player)
                return

    def in_between_physics(
            self,
            player: InGamePlayer,
    ) -> None:
        """
        does barebones physics for a single player entity
        :param player:
        :return: new player position, player momentum, new block record, new scheduled
        """
        if self.bounds + (self.center[0] - 5) * 30 > player.pos[0]:
            player.mom[0] = max(0, player.mom[0])
            player.pos[0] = self.bounds + (self.center[0] - 5) * 30
        elif player.pos[0] > (self.center[0] + 6) * 30 - self.bounds:
            player.mom[0] = min(0, player.mom[0])
            player.pos[0] = (self.center[0] + 6) * 30 - self.bounds
        if self.bounds + (self.center[1] - 5) * 30 > player.pos[1]:
            player.mom[1] = max(0, player.mom[1])
            player.pos[1] = self.bounds + (self.center[1] - 5) * 30
        elif player.pos[1] > (self.center[1] + 6) * 30 - self.bounds:
            player.mom[1] = min(0, player.mom[1])
            player.pos[1] = (self.center[1] + 6) * 30 - self.bounds
        player.pos[0] += player.mom[0]
        if player.mom[0] > 0:
            if (player.pos[0] + 10) // 30 != (player.pos[0] - player.mom[0] + 10) // 30:
                self.in_between_collision(
                    [
                        (int((player.pos[0] + 10) // 30), int((player.pos[1] + 10) // 30), 1),
                        (int((player.pos[0] + 10) // 30), int((player.pos[1] - 10) // 30), 1)
                    ],
                    player
                )
        else:
            if (player.pos[0] - 10) // 30 != (player.pos[0] - player.mom[0] - 10) // 30:
                self.in_between_collision(
                    [
                        (int((player.pos[0] - 10) // 30), int((player.pos[1] + 10) // 30), 3),
                        (int((player.pos[0] - 10) // 30), int((player.pos[1] - 10) // 30), 3)
                    ],
                    player
                )
        # y move
        player.pos[1] += player.mom[1]
        # y collisions
        if player.mom[1] > 0:
            if (player.pos[1] + 10) // 30 != (player.pos[1] - player.mom[1] + 10) // 30:
                self.in_between_collision(
                    [
                        (int((player.pos[0] + 10) // 30), int((player.pos[1] + 10) // 30), 2),
                        (int((player.pos[0] - 10) // 30), int((player.pos[1] + 10) // 30), 2)
                    ],
                    player
                )
        else:
            if (player.pos[1] - 10) // 30 != (player.pos[1] - player.mom[1] - 10) // 30:
                self.in_between_collision(
                    [
                        (int((player.pos[0] - 10) // 30), int((player.pos[1] - 10) // 30), 0),
                        (int((player.pos[0] + 10) // 30), int((player.pos[1] - 10) // 30), 0)
                    ],
                    player
                )

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
        sideways_accel = 1.5
        jump_power = 12
        gravity_strength = self.gravity[1]
        friction = 0.9

        for typ in player.block_record:
            if typ.friction_mult >= 0:
                friction *= typ.friction_mult
            else:
                friction = 1 - (friction - 1) * typ.friction_mult
            sideways_accel *= typ.accel_mult
            jump_power *= typ.jump_mult
            gravity_strength *= typ.gravity_mult

        # controls
        if self.control_check(self.right):
            player.mom[0] += cos(self.gravity[0]) * sideways_accel
            player.mom[1] += sin(self.gravity[0]) * sideways_accel
        if self.control_check(self.left):
            player.mom[0] -= cos(self.gravity[0]) * sideways_accel
            player.mom[1] -= sin(self.gravity[0]) * sideways_accel
        if self.control_check(self.jump) and player.grounded:  # and Blocks.sticky not in player.block_record:
            player.mom[0] -= sin(self.gravity[0]) * jump_power
            player.mom[1] += cos(self.gravity[0]) * jump_power
        player.grounded = False
        # gravity
        player.mom[0] -= sin(self.gravity[0]) * gravity_strength
        player.mom[1] += cos(self.gravity[0]) * gravity_strength
        # friction
        player.mom[self.gravity[0] % 2] *= friction
        # track of if collisions find ground
        player.block_record = SortedList()
        # x collisions

        remaining_xm = player.mom[0]
        step = (player.mom[0] > 0) * 2 - 1
        start_sign = player.mom[0] > 0
        reps = abs(int(player.pos[0] + player.mom[0] + 10 * step) // 30 - int(player.pos[0] + 10 * step) // 30)
        if reps > 0:
            x_init = int(player.pos[0] + 10 * step) // 30
            x_next = x_init + (1 - step) / 2
            req_x = x_next * 30 - 10 * step
            disp = req_x - player.pos[0]
            player.pos[0] += disp
            remaining_xm -= disp
        elif self.bounds + (self.center[0] - 5) * 30 > player.pos[0] + player.mom[0] or player.pos[0] + player.mom[0] > (self.center[0] + 6) * 30 - self.bounds:
            reps = 1
        for dif in range(reps):
            player.pos[0] += 30 * step
            remaining_xm -= 30 * step
            x = int(player.pos[0] + 11 * step) // 30
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

        remaining_ym = player.mom[1]
        step = (player.mom[1] > 0) * 2 - 1
        reps = abs(int(player.pos[1] + player.mom[1] + 10 * step) // 30 - int(player.pos[1] + 10 * step) // 30)
        if reps > 0:
            y_init = int(player.pos[1] + 10 * step) // 30
            y_next = y_init + (1 - step) / 2
            req_y = y_next * 30 - 10 * step
            disp = req_y - player.pos[1]
            player.pos[1] += disp
            remaining_ym -= disp
        elif self.bounds + (self.center[1] - 5) * 30 > player.pos[1] + player.mom[1] or player.pos[1] + player.mom[1] > (self.center[1] + 6) * 30 - self.bounds:
            reps = 1
        for dif in range(reps):
            player.pos[1] += 30 * step
            remaining_ym -= 30 * step
            y = int(player.pos[1] + 11 * step) // 30
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
        if self.bounds + (self.center[0] - 5) * 30 > player.pos[0]:
            # noinspection PyTypeChecker
            player.mom[0] = max(0, player.mom[0])
            player.pos[0] = self.bounds + (self.center[0] - 5) * 30
            if self.gravity[0] == 3:
                player.grounded = True
        elif player.pos[0] > (self.center[0] + 6) * 30 - self.bounds:
            # noinspection PyTypeChecker
            player.mom[0] = min(0, player.mom[0])
            player.pos[0] = (self.center[0] + 6) * 30 - self.bounds
            if self.gravity[0] == 1:
                player.grounded = True
        if self.bounds + (self.center[1] - 5) * 30 > player.pos[1]:
            # noinspection PyTypeChecker
            player.mom[1] = max(0, player.mom[1])
            player.pos[1] = self.bounds + (self.center[1] - 5) * 30
            if self.gravity[0] == 0:
                player.grounded = True
        elif player.pos[1] > (self.center[1] + 6) * 30 - self.bounds:
            # noinspection PyTypeChecker
            player.mom[1] = min(0, player.mom[1])
            player.pos[1] = (self.center[1] + 6) * 30 - self.bounds
            if self.gravity[0] == 2:
                player.grounded = True
        return

    def tick(self):
        """
        ticks level data
        :return:
        """
        self.time = get_ticks()
        if self.alive:
            if self.tick_track == self.frame_skip:
                self.run_in_between = True
                self.tick_track = 0
                self.in_between_track.clear()
                for player in self.players:
                    self.do_physics(player)
                    self.in_between_track.append(InGamePlayerInBetween(player))
            else:
                self.tick_track += 1
                if self.run_in_between:
                    for player in self.in_between_track:
                        self.in_between_physics(player)

    def render_level(self, scale: int, font: Font, player_imgs: tuple[Surface, Surface, Surface, Surface]):
        """
        draws a level
        :param scale:
        :param font:
        :param player_imgs: list of player images corresponding to gravity direction
        :return:
        """
        drawn = Surface((11 * scale + floor(scale / 20), 11 * scale + floor(scale / 20)))
        drawn.fill((255, 255, 255))
        for coordinates, block in self.blocks.items():
            if abs(coordinates[0] - self.center[0]) > 6 or abs(coordinates[1] - self.center[1]) > 6:
                continue
            drawn.blit(
                self.draw_block(block, font, scale),
                ((coordinates[0] - self.center[0] + 5) * scale, (5 - coordinates[1] + self.center[1]) * scale)
            )
            # print(coordinates)
        x_offset = self.center[0] % 1
        for i in range(11 + 1):
            line(drawn, (0, 0, 0), ((i - x_offset) * scale, 0), ((i - x_offset) * scale, 11 * scale), floor(scale / 10))
        y_offset = self.center[1] % 1
        for i in range(11 + 1):
            line(drawn, (0, 0, 0), (0, (i + y_offset) * scale), (11 * scale, (i + y_offset) * scale), floor(scale / 10))
        player = smoothscale(player_imgs[self.gravity[0]], (scale * 3 / 4, scale * 3 / 4))
        if self.tick_track == 0:
            for play in self.players:
                drawn.blit(
                    player,
                    (
                        (play.pos[0] - 30 * (self.center[0] - 5)) * (scale / 30) - scale * 3 / 8 + floor(scale / 40),
                        (30 * (self.center[1] + 6) - play.pos[1]) * (scale / 30) - scale * 3 / 8 + floor(scale / 40)
                    )
                )
        else:
            # for play in self.players:
            for play in self.in_between_track:
                drawn.blit(
                    player,
                    (
                        (play.pos[0] - 30 * (self.center[0] - 5)) * (scale / 30) - scale * 3 / 8 + floor(scale / 40),
                        (30 * (self.center[1] + 6) - play.pos[1]) * (scale / 30) - scale * 3 / 8 + floor(scale / 40)
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
        try:
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
        except:
            print(block.type, block.barriers, block.other)
            traceback.print_exc()
            return Blocks.error_block.render([], 0, font, scale)

    def rename(self, name: str):
        """
        renames level
        :param name: new name
        :return:
        """
        self.level_on.name = name


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