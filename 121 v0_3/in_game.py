"""
plays the game
"""

from utility import Utility
from level_management import make_playable
from render_level import draw_level, sin, cos
from typing import Union
from pygame.time import get_ticks
from game_structures import Collision
from constants import SOLID_BLOCKS


class InGame(Utility):
    """
    class that handles the in game areas
    """

    # noinspection PyAttributeOutsideInit
    def in_game_place(self, start_message: str = "", include_back: bool = True) -> None:
        """
        runs the game
        :param start_message: message displaying at start of level
        :param include_back: whether to include the back button (used for tutorial levels)
        :return: None
        """
        frame_skip = 1
        bounds = 12

        # noinspection PyTypeChecker
        def collision(
                blocks: list[tuple[int, int, int]],
                player_pos: tuple[float, float],
                player_momentum: tuple[float, float],
                local: bool = True,
                gravity: list[int, float] = None
        ) -> tuple[
            tuple[float, float],
            tuple[float, float],
            set[str],
            dict[tuple[int, int], tuple[int, int]],
            tuple[int, float],
            bool
        ]:
            """
            sets up a collision and gets list of blocks to collide, not hierarchied
            :param blocks: list of coordinate tuples, then direction integer
            :param player_pos: player position
            :param player_momentum: player momentum
            :param local: if player touching
            :param gravity: gravity info
            :return: tuple of coordinates, tuple of movement, set of block types collided with, dictionary for scheduled reactions, tuple of gravity info, and if touched ground
            """
            if gravity is None:
                gravity = gravity_info
            new_touched = get_collisions(blocks, local, gravity)
            return execute_collisions(new_touched, player_pos, player_momentum, gravity)

        def get_collisions(
                blocks: list[tuple[int, int, int]],
                local: bool,
                gravity: tuple[int, float]
        ) -> dict[str, list[Collision]]:
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
                col = block_info.get(block[0:2])
                if col is None:
                    continue
                # print(f"Collision with {block} detected.")
                add = Collision(
                    block[2],
                    local,
                    block[0:2],
                    col.other
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
                        block_collision = False
                if typ not in new_touched:
                    new_touched[typ] = []
                new_touched[typ].append(add)
                if block_collision:
                    if "link" in add.other:
                        for link_block in link_info[add.other["link"]]:
                            # checks if the block has already been collided with
                            if link_block in hit:
                                continue
                            # registers that the block has been hit
                            hit.add(link_block)
                            link_block_info = block_info[link_block]
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
                new_touched: dict[str, list[Collision]],
                player_pos: tuple[float, float],
                player_momentum: tuple[float, float],
                gravity: list[int, float]
        ) -> tuple[
            tuple[float, float],
            tuple[float, float],
            set[str],
            dict[tuple[int, int], tuple[int, float]],
            tuple[int, float],
            bool
        ]:
            """
            runs collision reactions on blocks
            :param new_touched: list of coordinate tuples
            :param player_pos: player position
            :param player_momentum: player momentum
            :param gravity: gravity data to use and change
            :return: tuple of coordinates, tuple of movement, set of block types collided with, dictionary for scheduled reactions, tuple of gravity info, and if touched ground
            """
            gravity = list(gravity)
            new_scheduled = dict()
            ground = False
            if "lava" in new_touched:
                self.alive = False
                return player_pos, player_momentum, set(new_touched), new_scheduled, tuple(gravity), ground
            if "goal" in new_touched:
                if "coin" in {block_info[block].type for block in block_info}:
                    draw_game_message(
                        "You must collect all coins before reaching the goal."
                    )
                else:
                    self.won = True
                    return player_pos, player_momentum, set(new_touched), new_scheduled, tuple(gravity), ground
            corrected = False
            if "bouncy" in new_touched:
                for check in new_touched["bouncy"]:
                    if check.direction == 0:
                        player_momentum = (player_momentum[0], max(0, player_momentum[1] * -0.75))
                    elif check.direction == 1:
                        player_momentum = (min(player_momentum[0] * -0.75, 0), player_momentum[1])
                    elif check.direction == 2:
                        player_momentum = (player_momentum[0], min(0, player_momentum[1] * -0.75))
                    elif check.direction == 3:
                        player_momentum = (max(player_momentum[0] * -0.75, 0), player_momentum[1])
                    if check.local:
                        player_pos, player_momentum = position_correction(
                            check.coordinates,
                            check.direction,
                            player_pos,
                            player_momentum
                        )
                        corrected = True
                        if gravity_info[0] == check.direction:
                            ground = True
                        break
            if "ground" in new_touched and not corrected:
                for check in new_touched["ground"]:
                    if check.local:
                        player_pos, player_momentum = position_correction(
                            check.coordinates,
                            check.direction,
                            player_pos,
                            player_momentum
                        )
                        if gravity_info[0] == check.direction:
                            ground = True
                        corrected = True
                        break
            if "mud" in new_touched and not corrected:
                for check in new_touched["mud"]:
                    if check.local:
                        player_pos, player_momentum = position_correction(
                            check.coordinates,
                            check.direction,
                            player_pos,
                            player_momentum
                        )
                        if gravity_info[0] == check.direction:
                            ground = True
                        corrected = False
                        break
            if "jump" in new_touched:
                for check in new_touched["jump"][::-1]:
                    if check.local and not corrected:
                        player_pos, player_momentum = position_correction(
                            check.coordinates,
                            check.direction,
                            player_pos,
                            player_momentum
                        )
                        if gravity_info[0] == check.direction:
                            ground = True
                        corrected = False
                    if (check.other["rotation"] + gravity_info[0] * (1 - check.other["grav_locked"])) % 2 == 0:
                        if abs(player_momentum[1]) < 16.25:
                            player_momentum = (
                                player_momentum[0],
                                16.25 * cos(
                                    check.other["rotation"] + gravity_info[0] * (1 - check.other["grav_locked"])
                                )
                            )
                    else:
                        if abs(player_momentum[0]) < 16.25:
                            player_momentum = (
                                16.25 * sin(
                                    check.other["rotation"] + gravity_info[0] * (1 - check.other["grav_locked"])
                                ),
                                player_momentum[1]
                            )
            if "repel" in new_touched:
                for check in new_touched["repel"]:
                    if check.local and not corrected:
                        player_pos, player_momentum = position_correction(
                            check.coordinates,
                            check.direction,
                            player_pos,
                            player_momentum
                        )
                        if gravity_info[0] == check.direction:
                            ground = True
                        corrected = False
                    if isinstance(check.other, tuple) or check.other["mode"] == 0:
                        if check.direction % 2 == 0:
                            player_momentum = (player_momentum[0], -16.25 * (check.direction - 1))
                        else:
                            player_momentum = (16.25 * (check.direction - 2), player_momentum[1])
                    else:
                        dx = player_pos[0] - check.coordinates[0] * 30 - 15
                        dy = player_pos[1] - check.coordinates[1] * 30 - 15
                        d = (dx ** 2 + dy ** 2) ** 0.5
                        player_momentum = (16.25 * dx / d, 16.25 * dy / d)

            if "gravity" in new_touched:
                for check in new_touched["gravity"][::-1]:
                    activate = not check.local
                    if check.direction % 2 == 0 and abs(player_momentum[1]) > 3:
                        activate = True
                    elif check.direction % 2 == 1 and abs(player_momentum[0]) > 3:
                        activate = True
                    if activate:
                        if check.other["type"] == "direction":
                            gravity[0] = (3 * (check.other["rotation"] - (1 - check.other["grav_locked"]) *
                                               gravity_info[0]) + 2) % 4
                        else:
                            if check.other["mode"] == 0:
                                gravity[1] = -1 * check.other["value"]
                            else:
                                print(check.other["mode"])
                    if check.local and not corrected:
                        player_pos, player_momentum = position_correction(
                            check.coordinates,
                            check.direction,
                            player_pos,
                            player_momentum
                        )
                        if gravity[0] == check.direction:
                            ground = True
                        corrected = False
            if "activator" in new_touched:
                for check in new_touched["activator"]:
                    if check.local and not corrected:
                        player_pos, player_momentum = position_correction(
                            check.coordinates,
                            check.direction,
                            player_pos,
                            player_momentum
                        )
                        if gravity_info[0] == check.direction:
                            ground = True
                        corrected = False
                    look = 3 * (check.other["rotation"] + (1 - check.other["grav_locked"]) * gravity_info[0] + 2) % 4
                    coordinates = (
                        check.coordinates[0] + sin(look),
                        check.coordinates[1] - cos(look)
                    )
                    if coordinates not in new_scheduled:
                        # print(check.coordinates, coordinates)
                        new_scheduled[coordinates] = (look, check.other["delay"])
            if "coin" in new_touched:
                for check in new_touched["coin"]:
                    block_info[check.coordinates[0:2]].type = ""
            if "easter egg" in new_touched:
                for check in new_touched["easter egg"]:
                    block_info[check.coordinates[0:2]].type = None
                    if block_info[check.coordinates[0:2]].other["level"] in {lvl[0] for lvl in self.levels[0]}:
                        draw_game_message(
                            f"You have already collected easter egg level {block_info[check.coordinates[0:2]].other['level']}."
                        )
                    else:
                        draw_game_message(
                            f"Easter egg level {block_info[check.coordinates[0:2]].other['level']} unlocked!"
                        )
                        self.levels[0].insert(
                            self.look_at[0],
                            (block_info[check.coordinates[0:2]].other["level"], False)
                        )
                        self.look_at[0] += 1
                        self.level_on += 1
                    block_info[check.coordinates[0:2]].other = ()
            if "msg" in new_touched:
                draw_game_message(new_touched["msg"][0].other["text"])
            return player_pos, player_momentum, set(new_touched), new_scheduled, tuple(gravity), ground

        def draw_game_message(text: str) -> None:
            """
            draws game message on sidebar
            :param text: text of message
            :return: None
            """
            self.message = self.draw_text(
                text,
                16,
                max_line_pixels=128,
                max_width=128
            )
            if self.tts:
                self.speak(text)

        def in_between_collision(
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
            for block in blocks:
                col = block_info.get(block[0:2])
                if col is None:
                    continue
                typ = col.type
                for bar in col.barriers:
                    if bar[2][3 * (block[2] - gravity_info[0] * bar[1]) % 4]:
                        typ = bar[0]
                if typ in SOLID_BLOCKS:
                    return position_correction(block[0:2], block[2], player_pos, player_momentum)
            return player_pos, player_momentum

        def in_between_physics(
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
            if bounds + 30 > p_x + p_xm:
                p_xm = 0
                p_x = bounds + 30
            elif p_x + p_xm > dimensions[0] * 30 - bounds + 30:
                p_xm = 0
                p_x = dimensions[0] * 30 - bounds + 30
            if bounds + 30 > p_y + p_ym:
                p_ym = 0
                p_y = bounds + 30
            elif p_y + p_ym > dimensions[1] * 30 - bounds + 30:
                p_ym = 0
                p_y = dimensions[1] * 30 - bounds + 30
            p_x += p_xm
            if p_xm > 0:
                if (p_x + 10) // 30 != (p_x - p_xm + 10) // 30:
                    (p_x, p_y), (p_xm, p_ym) = in_between_collision(
                        [
                            (int((p_x + 10) // 30), int((p_y + 10) // 30), 1),
                            (int((p_x + 10) // 30), int((p_y - 10) // 30), 1)
                        ],
                        (p_x, p_y),
                        (p_xm, p_ym)
                    )
            else:
                if (p_x - 10) // 30 != (p_x - p_xm - 10) // 30:
                    (p_x, p_y), (p_xm, p_ym) = in_between_collision(
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
                    (p_x, p_y), (p_xm, p_ym) = in_between_collision(
                        [
                            (int((p_x + 10) // 30), int((p_y + 10) // 30), 2),
                            (int((p_x - 10) // 30), int((p_y + 10) // 30), 2)
                        ],
                        (p_x, p_y),
                        (p_xm, p_ym)
                    )
            else:
                if (p_y - 10) // 30 != (p_y - p_ym - 10) // 30:
                    (p_x, p_y), (p_xm, p_ym) = in_between_collision(
                        [
                            (int((p_x - 10) // 30), int((p_y - 10) // 30), 0),
                            (int((p_x + 10) // 30), int((p_y - 10) // 30), 0)
                        ],
                        (p_x, p_y),
                        (p_xm, p_ym)
                    )
            return (p_x, p_y), (p_xm, p_ym)

        def do_physics(
                player_pos: tuple[Union[int, float], Union[int, float]],
                player_momentum: tuple[Union[int, float], Union[int, float]],
                block_record: set[str],
                scheduled: dict[tuple[int, int], tuple[int, int]],
                grounded: bool
        ) -> tuple[
            tuple[float, float],
            tuple[float, float],
            set[str],
            dict[tuple[int, int], tuple[int, int]],
            bool,
            tuple[int, float]
        ]:
            """
            does physics for a single player entity
            :param player_pos: position of the player (x, y)
            :param player_momentum: momentum of the player (x, y)
            :param block_record: record of blocks touched last time, cleaned to be only useful
            :param scheduled: scheduled block updates
            :param grounded: if player is on ground
            :return: new player position, player momentum, new block record, new scheduled, grounded, new gravity info
            """
            # scheduled updates
            run_reactions = []
            for schedule in scheduled.copy():
                if scheduled[schedule][1] < time:
                    run_reactions.append((schedule[0], schedule[1], scheduled[schedule][0]))
                    del scheduled[schedule]
            player_pos, player_momentum, new_block_record, add_reactions, gravity, new_ground = collision(
                run_reactions,
                player_pos,
                player_momentum,
                False
            )
            p_x, p_y = player_pos
            p_xm, p_ym = player_momentum
            scheduled_merge(time, scheduled, add_reactions)

            # normal physics
            if "mud" in block_record:
                sideways_accel = 0.75
                jump_power = 6
                gravity_strength = gravity_info[1] / 1.85
                friction = 0.85
            else:
                sideways_accel = 1.5
                jump_power = 12
                gravity_strength = gravity_info[1]
                friction = 0.9
            ground = False
            # controls
            if self.pressed[right]:
                p_xm += cos(gravity[0]) * sideways_accel
                p_ym += sin(gravity[0]) * sideways_accel
            if self.pressed[left]:
                p_xm -= cos(gravity[0]) * sideways_accel
                p_ym -= sin(gravity[0]) * sideways_accel
            if self.pressed[jump] and grounded and "sticky" not in block_record:
                p_xm -= sin(gravity[0]) * jump_power
                p_ym += cos(gravity[0]) * jump_power
            # gravity
            p_xm -= sin(gravity[0]) * gravity_strength
            p_ym += cos(gravity[0]) * gravity_strength
            # friction
            if gravity[0] % 2 == 0:
                p_xm = p_xm * friction
            else:
                p_ym = p_ym * friction
            # bounds
            if bounds + 30 > p_x + p_xm:
                p_xm = 0
                p_x = bounds + 30
                if gravity[0] == 3:
                    ground = True
            elif p_x + p_xm > dimensions[0] * 30 - bounds + 30:
                p_xm = 0
                p_x = dimensions[0] * 30 - bounds + 30
                if gravity[0] == 1:
                    ground = True
            if bounds + 30 > p_y + p_ym:
                p_ym = 0
                p_y = bounds + 30
                if gravity[0] == 0:
                    ground = True
            elif p_y + p_ym > dimensions[1] * 30 - bounds + 30:
                p_ym = 0
                p_y = dimensions[1] * 30 - bounds + 30
                if gravity[0] == 2:
                    ground = True
            # track of if collisions find ground
            new_ground = False
            # x move
            p_x += p_xm  # / (frame_skip + 1)
            # x collisions
            add_touched = set()
            gravity = list(gravity)
            if p_xm > 0:
                if (p_x + 10) // 30 != (p_x - p_xm + 10) // 30:
                    (p_x, p_y), (p_xm, p_ym), add_touched, add_reactions, gravity, new_ground = collision(
                        [
                            (int((p_x + 10) // 30), int((p_y + 10) // 30), 1),
                            (int((p_x + 10) // 30), int((p_y - 10) // 30), 1)
                        ],
                        (p_x, p_y),
                        (p_xm, p_ym),
                        True,
                        gravity
                    )
            else:
                if (p_x - 10) // 30 != (p_x - p_xm - 10) // 30:
                    (p_x, p_y), (p_xm, p_ym), add_touched, add_reactions, gravity, new_ground = collision(
                        [
                            (int((p_x - 10) // 30), int((p_y + 10) // 30), 3),
                            (int((p_x - 10) // 30), int((p_y - 10) // 30), 3)
                        ],
                        (p_x, p_y),
                        (p_xm, p_ym),
                        True,
                        gravity
                    )
            new_block_record.update(add_touched)
            if not self.alive:
                return (p_x, p_y), (p_xm, p_ym), new_block_record, add_reactions, ground, tuple(gravity)
            ground = ground or new_ground
            scheduled_merge(time, scheduled, add_reactions)
            # y move
            p_y += p_ym  # / (frame_skip + 1)
            # y collisions
            if p_ym > 0:
                if (p_y + 10) // 30 != (p_y - p_ym + 10) // 30:
                    (p_x, p_y), (p_xm, p_ym), add_touched, add_reactions, gravity, new_ground = collision(
                        [
                            (int((p_x + 10) // 30), int((p_y + 10) // 30), 2),
                            (int((p_x - 10) // 30), int((p_y + 10) // 30), 2)
                        ],
                        (p_x, p_y),
                        (p_xm, p_ym),
                        True,
                        gravity
                    )
            else:
                if (p_y - 10) // 30 != (p_y - p_ym - 10) // 30:
                    (p_x, p_y), (p_xm, p_ym), add_touched, add_reactions, gravity, new_ground = collision(
                        [
                            (int((p_x - 10) // 30), int((p_y - 10) // 30), 0),
                            (int((p_x + 10) // 30), int((p_y - 10) // 30), 0)
                        ],
                        (p_x, p_y),
                        (p_xm, p_ym),
                        True,
                        gravity
                    )
            new_block_record.update(add_touched)
            ground = ground or new_ground
            scheduled_merge(time, scheduled, add_reactions)
            # finish
            return (p_x, p_y), (p_xm, p_ym), new_block_record, scheduled, ground, tuple(gravity)

        def dead_start_button() -> None:
            """
            sets back up the level and starts re-entry countdown
            :return: None
            """
            nonlocal death_time, tick, dimensions, gravity_info, block_info, link_info, player_positions, player_data, in_between_player_data
            death_time = time
            self.replace_button(1, self.make_text_button(
                "Reset",
                50,
                self.reset,
                (240 * 4, 0),
                border_width=5,
                x_align=1,
                y_align=0,
                max_width=140,
                special_press="Reset"
            ))
            self.replace_button(2, None)
            tick = 0
            dimensions, gravity_info, block_info, link_info, player_positions = make_playable(
                self.level_data)
            player_data = [(p, (0, 0), set(), dict(), False) for p in player_positions]
            in_between_player_data = [(p, (0, 0)) for p in player_positions]
            self.level_display = draw_level(
                dimensions,
                gravity_info,
                block_info,
                link_info,
                [p[0] for p in in_between_player_data],
                self.player_img,
                self.fonts[60], 60
            )

        self.alive = True
        self.won = False
        self.message = None
        draw_game_message(start_message)
        if include_back:
            self.add_button(self.make_text_button(
                "Back",
                50,
                self.change_place,
                (0, 0),
                border_width=5,
                arguments={"place": "exit_level"},
                x_align=0,
                y_align=0,
                max_width=140,
                special_press="Back"
            ))
        else:
            self.add_button(None)
        self.add_button(self.make_text_button(
            "Reset",
            50,
            self.reset,
            (240 * 4, 0),
            border_width=5,
            x_align=1,
            y_align=0,
            max_width=140,
            special_press="Reset"
        ))
        self.add_button(None)
        right = self.get_special_click("Right")
        left = self.get_special_click("Left")
        jump = self.get_special_click("Jump")
        tick = 0
        death_time = False
        dimensions, gravity_info, block_info, link_info, player_positions = make_playable(self.level_data)
        player_data = [(p, (0, 0), set(), dict(), False) for p in player_positions]
        in_between_player_data = [(p, (0, 0)) for p in player_positions]
        while self.place == "in_game" and not self.won:
            self.tick()
            time = get_ticks()
            if self.alive:
                if tick == frame_skip:
                    tick = 0
                    for i in range(len(player_data)):
                        # noinspection PyTypeChecker
                        *player_data[i], gravity_info = do_physics(*player_data[i])
                        in_between_player_data = [
                            (pos, (mom[0] / (frame_skip + 1), mom[1] / (frame_skip + 1)))
                            for pos, mom, *arg in player_data
                        ]
                        if not self.alive:
                            self.replace_button(2, self.make_text_button(
                                "Start",
                                100,
                                dead_start_button,
                                (240 * 2, 180 * 2),
                                (255, 255, 255, 192),
                                border_width=5,
                                special_press="Play"
                            ))
                            death_time = None
                            self.replace_button(1, None)
                    self.level_display = draw_level(
                        dimensions,
                        gravity_info,
                        block_info,
                        link_info,
                        [p[0] for p in player_data],
                        self.player_img,
                        self.fonts[60],
                        60
                    )
                else:
                    tick += 1
                    for i in range(len(player_data)):
                        # noinspection PyTypeChecker
                        # print(in_between_player_data[i])
                        in_between_player_data[i] = in_between_physics(*in_between_player_data[i])
                    self.level_display = draw_level(
                        dimensions,
                        gravity_info,
                        block_info,
                        link_info,
                        [p[0] for p in in_between_player_data],
                        self.player_img,
                        self.fonts[60], 60
                    )
            self.screen.blit(
                self.level_display,
                (240 * 2 - self.level_display.get_width() / 2, 180 * 2 - self.level_display.get_height() / 2)
            )
            if self.message is not None:
                self.screen.blit(
                    self.message,
                    (4, 180 * 2 - self.message.get_height() / 2)
                )
            if not self.alive:
                if death_time is None:
                    pass
                elif isinstance(death_time, bool):
                    tick = 0
                    dimensions, gravity_info, block_info, link_info, player_positions = make_playable(
                        self.level_data)
                    player_data = [(p, (0, 0), set(), dict(), False) for p in player_positions]
                    in_between_player_data = [(p, (0, 0)) for p in player_positions]
                    self.alive = True
                elif time >= death_time + 1000:
                    self.alive = True
                    death_time = False
                else:
                    self.blit_text(
                        str(round((death_time + 1000 - time) / 100) / 10),
                        100,
                        240 * 2,
                        180 * 2,
                        (0, 0, 0, 0),
                        (64, 64, 64),
                        centerx=0.5,
                        centery=0.5
                    )
            self.handle_buttons()
        # finished game
        self.change_place("exit_level")
        if self.won:
            if self.after_game == "construction" or self.after_game == "export":
                # TODO change this back to pass after export screen made
                self.after_game = "construction"
            else:
                self.levels[self.custom][self.look_at[self.custom]] = (
                    self.levels[self.custom][self.look_at[self.custom]][0],
                    True
                )
                if self.custom == 0:
                    if self.level_on == self.look_at[0] and self.level_on < len(self.levels[0]) - 1:
                        self.level_on += 1
                        self.look_at[0] += 1
        else:
            if self.after_game == "export":
                self.after_game = "construction"

    # noinspection PyAttributeOutsideInit
    def reset(self):
        """
        resets in game
        :return: none
        """
        self.alive = False


# noinspection PyTypeChecker
def position_correction(
        block_coords: tuple[int, int],
        direction: int,
        player_pos: tuple[float, float],
        player_mom: tuple[float, float],
) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    cleans position after block collision
    :param block_coords: coordinates of block collided with (maybe, just needs correct relevant data)
    :param direction: direction coming from
    :param player_pos: player position going in
    :param player_mom: player momentum going in
    :return: tuple of tuple of new position, new motion
    """
    if direction == 0:
        return (player_pos[0], block_coords[1] * 30 + 40.25), (player_mom[0], max(0, player_mom[1]))
    elif direction == 2:
        return (player_pos[0], block_coords[1] * 30 - 10.25), (player_mom[0], min(0, player_mom[1]))
    elif direction == 1:
        return (block_coords[0] * 30 - 10.25, player_pos[1]), (min(0, player_mom[0]), player_mom[1])
    elif direction == 3:
        return (block_coords[0] * 30 + 40.25, player_pos[1]), (max(0, player_mom[0]), player_mom[1])


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