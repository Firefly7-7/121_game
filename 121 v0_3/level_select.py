"""
contains class for level select area
"""

from level_management import unpack_level, decode_safety_wrap, save_level, make_playable, encode_level_to_string
from utility import Utility, LEVEL_LIST
from pyperclip import paste, copy
from subprocess import run
from pathlib import Path
from os import listdir
from render_level import draw_level
from pygame import Surface
from pygame.draw import lines
from render_level import draw_block
from block_data import Block
from game_structures import Button
from level_data import Level


class LevelSelect(Utility):
    """
    handles level select area
    """

    def level_select_place(self) -> None:
        """
        runs level select area
        :return: none
        """

        def get_level() -> None:
            """
            utility to get level based on current looking
            :return: none
            """
            if self.levels[1] == [] and self.custom == 1:
                self.level_data = None
                self.level_display = None
                self.replace_button(1, self.make_text_button(
                    "It appears you don't have any custom levels!  Please copy one from clipboard, or open the custom level folder and add the file!",
                    50,
                    None,
                    (240 * 2, 180 * 2),
                    max_line_pixels=512,
                    preserve_words=True,
                    text_align=0.5
                ))
                self.replace_button(5, None)
                self.replace_button(3, None)
                self.replace_button(8, None)
                self.replace_button(9, None)
                self.replace_button(10, None)
                return
            name = self.levels[self.custom][self.look_at[self.custom]][0]
            self.level_data = unpack_level(
                name,
                self.custom,
                name not in LEVEL_LIST and self.custom == 0
            )
            if self.level_data is None:
                self.level_display = None
                self.replace_button(1, self.make_text_button(
                    f"Level '{name}' not found.",
                    40,
                    None,
                    (240 * 2, 180 * 2),
                    max_line_pixels=480,
                    preserve_words=True,
                    text_align=0.5
                ))
                self.replace_button(3, None)
                self.replace_button(10, None)
            elif isinstance(self.level_data, TypeError):
                self.level_display = None
                self.replace_button(1, self.make_text_button(
                    f"Level code for level '{name}' does not have a valid version indicator.  It may have been removed, or the file may have been replaced.",
                    40,
                    None,
                    (240 * 2, 180 * 2),
                    max_line_pixels=480,
                    preserve_words=True,
                    text_align=0.5
                ))
                self.replace_button(3, None)
                self.replace_button(10, None)
            elif isinstance(self.level_data, ValueError):
                self.level_display = None
                self.replace_button(1, self.make_text_button(
                    f"There was an error loading level '{name}'.",
                    40,
                    None,
                    (240 * 2, 180 * 2),
                    max_line_pixels=480,
                    preserve_words=True,
                    text_align=0.5
                ))
                self.replace_button(3, None)
                self.replace_button(10, None)
            else:
                # noinspection PyTypeChecker
                self.level_display = draw_level(*make_playable(self.level_data), self.player_img, self.fonts[20], 40)
                self.replace_button(1, self.make_text_button(
                    "Play",
                    100,
                    self.change_place,
                    (240 * 2, 180 * 4),
                    (255, 255, 255),
                    (0, 0, 0),
                    5,
                    arguments={"place": "enter_level"},
                    y_align=1,
                    x_align=0.5,
                    special_press="Play"
                ))
            name_button = self.draw_text(name, 75, max_line_pixels=240 * 6, preserve_words=True)
            # self.replace_button(5, self.make_text_button(
            #     name,
            #     75,
            #     border_width=5,
            #     click=None,
            #     center=(240 * 2, 50),
            #     max_width=512
            # ))
            height = name_button.get_height()
            # print(self.levels[self.custom][self.look_at[self.custom]][1])
            width = name_button.get_width() + (self.levels[self.custom][self.look_at[self.custom]][
                                                   1] + (name not in LEVEL_LIST and self.custom == 0)) * height / 2
            if width > 512:
                name_button = self.draw_text(
                    name,
                    75 * 512 / width,
                    max_line_pixels=240 * 6 * 512 / width,
                    preserve_words=True
                )
                height = name_button.get_height()
                width = name_button.get_width() + (self.levels[self.custom][self.look_at[self.custom]][
                                                       1] + (name not in LEVEL_LIST and self.custom == 0)) * height / 2
            name_placard = Surface((int(width), height))
            name_placard.fill((255, 255, 255))
            name_desc = name
            if self.levels[self.custom][self.look_at[self.custom]][1]:
                lines(name_placard, (68, 179, 0), False, (
                    (height / 8, height / 2),
                    (height / 4, 7 * height / 8),
                    (3 * height / 8, height / 8)
                ), 5)
                name_placard.blit(name_button, (height / 2, 0))
                name_desc += ", Completed"
            else:
                name_placard.blit(name_button, (0, 0))
            if name not in LEVEL_LIST and self.custom == 0:
                name_placard.blit(
                    draw_block(Block("easter egg", []), 0, self.fonts[50], 5 * height / 8),
                    (width - 5 * height / 8, 3 * height / 16)
                )
                name_desc += ", Easter Egg"

            self.replace_button(5, Button(
                None,
                name_placard,
                name_desc,
                name_placard.get_rect(center=(240 * 2, 50)),
                (255, 255, 255),
                (0, 0, 0),
                (0, 0),
                5
            ))
            if self.custom == 0:
                if self.look_at[0] < self.level_on and self.look_at[0] < len(self.levels[0]) - 1:
                    self.replace_button(9, self.make_text_button(
                        ">",
                        90,
                        change_level,
                        (240 * 2 + 280, 180 * 2),
                        border_width=5,
                        arguments={"change": 1},
                        special_press="Right"
                    ))
                else:
                    self.replace_button(9, None)
            elif self.look_at[1] < len(self.levels[1]) - 1:
                self.replace_button(9, self.make_text_button(
                    ">",
                    90,
                    change_level,
                    (240 * 2 + 280, 180 * 2),
                    border_width=5,
                    arguments={"change": 1},
                    special_press="Right"
                ))
            else:
                self.replace_button(9, None)
            if self.look_at[self.custom] <= 0:
                self.replace_button(8, None)
            else:
                self.replace_button(8, self.make_text_button(
                    "<",
                    90,
                    change_level,
                    (240 * 2 - 280, 180 * 2),
                    border_width=5,
                    arguments={"change": -1},
                    special_press="Left"
                ))
            self.replace_button(3, self.make_text_button(
                "Edit Level",
                50,
                edit_current,
                (240 * 4, self.buttons[2].img.get_height()),
                (255, 255, 255),
                (0, 0, 0),
                5,
                y_align=0,
                x_align=1,
                max_width=192
            ))
            self.replace_button(10, self.make_text_button(
                "Copy level to clipboard",
                25,
                copy_level,
                (0, 180 * 4 - self.buttons[2].img.get_height()),
                (255, 255, 255),
                (0, 0, 0),
                5,
                y_align=0,
                x_align=1,
                max_width=192,
                arguments={"level": self.level_data}
            ))
            # print(self.custom, self.look_at, self.level_on)

        # buttons order:
        # 0: back button [static] (done)
        # 1: play button / error message [unstatic]
        # 2: make level [static] (done)
        # 3: edit level [unstatic] (done)

        def edit_current() -> None:
            """
            moves to construction area to edit current level
            :return: none
            """
            self.constructing = len(self.working_on)
            self.working_on.append(encode_level_to_string(self.level_data))
            self.place = "construction"

        # 4: switch level select [unstatic] (done)

        def make_switch_button() -> None:
            """
            makes switch button for correct place
            :return: none
            """
            self.replace_button(4, self.make_text_button(
                "Custom Levels" if self.custom == 0 else "Premade Levels",
                50,
                switch,
                (240 * 4, 180 * 4),
                (255, 255, 255),
                (0, 0, 0),
                5,
                x_align=1,
                y_align=1,
                max_width=400
            ))

        def switch() -> None:
            """
            switches between looking at custom and premade levels
            :return: none
            """
            self.custom = (self.custom + 1) % 2
            get_level()
            make_switch_button()

        # 5: name [unstatic] (done)
        # 6: import from keyboard [static] (done, versions untested)

        def import_from_clipboard() -> None:
            """
            imports a level from clipboard
            :return: none
            """
            level = decode_safety_wrap(paste())
            if level is None:
                pass
            else:
                if level.name in [lvl_check[0] for lvl_check in self.levels[1]]:
                    save_level(level)
                    self.look_at[1] = len(self.levels[1])
                    self.levels[1].append((level.name, False))
                    self.custom = 1
                    get_level()
                    make_switch_button()
                else:
                    save_level(level)
                    self.look_at[1] = len(self.levels[1])
                    self.levels[1].append((level.name, False))
                    self.custom = 1
                    get_level()
                    make_switch_button()

        # 7: open custom folder [static] (done)
        # 8: -1 level button [dynamic] (done)
        # 9: +1 level button [dynamic] (done)

        def copy_level(level: Level) -> None:
            """
            copies level data to clipboard
            :param level: level object
            :return: none
            """
            copy(encode_level_to_string(level))

        # 10: copy level code to clipboard [dynamic]

        def change_level(change: int) -> None:
            """
            changes level selector is looking at
            does not check for anything, if the button exists, it should be fine to press
            :param change: number to change by (-1, 1)
            :return: None
            """
            self.look_at[self.custom] += change
            get_level()

        self.add_button(self.make_text_button(
            "Back",
            50,
            self.change_place,
            (0, 0),
            (255, 255, 255),
            (0, 0, 0),
            5,
            arguments={"place": "start"},
            y_align=0,
            x_align=0,
            special_press="Back"
        ))
        self.add_button(None)  # replaced with play
        # self.add_button(None)
        self.add_button(self.make_text_button(
            "Make Level",
            50,
            self.change_place,
            (240 * 4, 0),
            (255, 255, 255),
            (0, 0, 0),
            5,
            arguments={"place": "construction"},
            y_align=0,
            x_align=1,
            max_width=192
        ))
        self.add_button(None)  # replaced by edit button
        self.add_button(None)  # replaced by switch level
        self.add_button(None)  # replaced by name
        self.add_button(self.make_text_button(
            "Open Custom Folder",
            40,
            run,
            (0, 180 * 4),
            (255, 255, 255),
            (0, 0, 0),
            5,
            y_align=1,
            x_align=0,
            max_width=400,
            arguments={"args": fr"explorer /open, {Path().resolve()}\custom_levels"}
        ))
        self.add_button(self.make_text_button(
            "Import From Clipboard",
            30,
            import_from_clipboard,
            (0, 180 * 4 - self.buttons[-1].img.get_height()),
            (255, 255, 255),
            (0, 0, 0),
            5,
            y_align=1,
            x_align=0,
            max_width=300
        ))
        self.add_button(None)  # replaced by arrow keys
        self.add_button(None)  # replaced by arrow keys
        self.add_button(None)  # replaced by copy button
        make_switch_button()
        get_level()
        while self.place == "level_select":
            self.tick()
            for lvl in [(c_lvl[:-4], False) for c_lvl in listdir("custom_levels")]:
                if lvl[0] not in [level[0] for level in self.levels[1]]:
                    self.levels[1].append(lvl)
                    get_level()
            if self.level_display is not None:
                self.screen.blit(
                    self.level_display,
                    (240 * 2 - self.level_display.get_width() / 2, 180 * 2 - self.level_display.get_height() / 2)
                )
            self.handle_buttons()
