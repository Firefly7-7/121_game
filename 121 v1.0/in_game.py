"""
plays the game
"""

from utility import Utility
from pygame.transform import rotate
from pygame.time import get_ticks


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

        def dead_start_button() -> None:
            """
            sets back up the level and starts re-entry countdown
            :return: None
            """
            nonlocal death_time
            death_time = get_ticks()
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
            self.level_data.prepare_for_play()
            self.level_display = self.level_data.render_level(
                60,
                self.fonts[60],
                player_imgs
            )
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
        self.level_data.set_controls(
            self.get_special_click("Jump"),
            self.get_special_click("Left"),
            self.get_special_click("Right"),
            self.check_pressed
        )
        if self.admin or (self.after_game == "level_select" and self.custom == 0):
            self.level_data.set_outputs(
                self.give_achievement,
                self.give_skin,
                self.give_level,
                draw_game_message,
                self.alerts.add_alert
            )
        else:
            def deny_special() -> None:
                """
                when in custom level or in construction, denies players collection of levels, achievements and skins
                :return: nada
                """
                self.alerts.add_alert(
                    "You may only collect easter egg levels, achievements, or skins in premade levels."
                )

            self.level_data.set_outputs(
                deny_special,
                deny_special,
                deny_special,
                draw_game_message,
                self.alerts.add_alert
            )
        death_time = None
        player_imgs = tuple(rotate(self.player_img, 90 * i) for i in range(4))
        while self.place == "in_game" and not self.level_data.won:
            self.tick()
            if death_time is None:  # check if already handling when dead/respawn/pause
                if self.level_data.alive:  # only do following if alive at start of tick
                    self.level_data.tick()
                if self.level_data.alive:  # check if still alive
                    if self.level_data.won:  # check if you won.
                        self.level_data.next()  # fakeclaim it
                else:  # check if not still alive
                    self.replace_button(2, self.make_text_button(
                        "Start",
                        100,
                        dead_start_button,
                        (240 * 2, 180 * 2),
                        (255, 255, 255, 192),
                        border_width=5,
                        special_press="Play"
                    ))
                    self.replace_button(1, None)
                # do the drawing thingy
                self.level_display = self.level_data.render_level(
                    60,
                    self.fonts[60],
                    player_imgs
                )
            # do the printing thingy
            self.screen.blit(
                self.level_display,
                (240 * 2 - self.level_display.get_width() / 2, 180 * 2 - self.level_display.get_height() / 2)
            )
            if self.message is not None:
                self.screen.blit(
                    self.message,
                    (4, 180 * 2 - self.message.get_height() / 2)
                )
            if isinstance(death_time, int):
                if get_ticks() >= death_time + self.controls[9].value * 1000:
                    death_time = None
                else:
                    self.blit_text(
                        str(round((death_time + self.controls[9].value * 1000 - get_ticks()) / 100) / 10),
                        100,
                        240 * 2,
                        180 * 2,
                        (0, 0, 0, 0),
                        (64, 64, 64),
                        centerx=0.5,
                        centery=0.5
                    )
        # finished game
        self.change_place("exit_level")
        if self.level_data.won:
            if self.after_game == "export":
                self.after_game = "level_select"
                name_append = ""
                copies = 0
                for lvl_index in range(len(self.levels[1])):
                    if self.level_data.level_on.name + name_append == self.levels[1][lvl_index][0]:
                        copies += 1
                        name_append = "(" + str(copies) + ")"

                name = f"custom_levels/{self.level_data.level_on.name}.txt"
                with open(name, "w", encoding="utf-8") as file:
                    file.write(self.working_on[self.constructing])

                self.look_at[1] = len(self.levels[1])
                self.levels[1].append((self.level_data.name, False))
                self.custom = 1
            elif self.after_game == "construction":
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
        self.level_data.prepare_for_play()


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