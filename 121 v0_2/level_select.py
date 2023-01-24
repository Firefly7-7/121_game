"""
contains class for level select area
"""

from level_management import unpack_level, decode_safety_wrap, save_level, make_playable
from utility import Utility, LEVEL_LIST
from pyperclip import paste
from subprocess import run
from pathlib import Path
from os import listdir
from render_level import draw_level


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
                self.level_display = self.draw_text(
                    "It appears you don't have any custom levels!  Please copy one from clipboard, or open the custom level folder and add the file!",
                    self.fonts[50],
                    max_line_pixels=512,
                    preserve_words=True,
                    text_align=0.5
                )
                self.replace_button(5, None)
                self.replace_button(1, None)
                self.replace_button(8, None)
                self.replace_button(9, None)
                return
            name = self.levels[self.custom][self.look_at[self.custom]][0]
            self.level_data = unpack_level(
                name,
                self.custom,
                name not in LEVEL_LIST and self.custom == 0
            )
            if self.level_data is None:
                self.level_display = self.draw_text(
                    f"Level '{name}' not found.",
                    self.fonts[50]
                )
                self.replace_button(1, None)
            else:
                self.level_display = draw_level(*make_playable(self.level_data), self.player_img, self.fonts[20], 40)
                self.replace_button(1, self.make_text_button(
                    "Play",
                    self.fonts[100],
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
            self.replace_button(5, self.make_text_button(
                name,
                self.fonts[75],
                border_width=5,
                click=None,
                center=(240 * 2, 50)
            ))
            if self.custom == 0:
                if self.look_at[0] < self.level_on and self.look_at[0] < len(self.levels[0]) - 1:
                    self.replace_button(9, self.make_text_button(
                        ">",
                        self.fonts[90],
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
                    self.fonts[90],
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
                    self.fonts[90],
                    change_level,
                    (240 * 2 - 280, 180 * 2),
                    border_width=5,
                    arguments={"change": -1},
                    special_press="Left"
                ))
            # print(self.custom, self.look_at, self.level_on)

        # buttons order:
        # 0: back button [static] (done)
        # 1: play button [static] (done)
        # 2: make level [static] (done)
        # 3: edit level [static] (done)

        def edit_current() -> None:
            """
            moves to construction area to edit current level
            :return: none
            """
            self.constructing = len(self.working_on)
            self.working_on.append(self.level_data)
            self.place = "construction"

        # 4: switch level select [unstatic] (done)

        def make_switch_button() -> None:
            """
            makes switch button for correct place
            :return: none
            """
            self.replace_button(4, self.make_text_button(
                "Custom Levels" if self.custom == 0 else "Premade Levels",
                self.fonts[50],
                switch,
                (240 * 4, 180 * 4),
                (255, 255, 255),
                (0, 0, 0),
                5,
                x_align=1,
                y_align=1,
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
                if level.name in self.levels[1]:
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
            self.fonts[50],
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
        self.add_button(None)
        self.add_button(None)
        # self.add_button(self.make_text_button(
        #     "Make Level",
        #     self.fonts[50],
        #     self.change_place,
        #     (240 * 4, 0),
        #     (255, 255, 255),
        #     (0, 0, 0),
        #     5,
        #     arguments={"place": "construction"},
        #     y_align=0,
        #     x_align=1
        # ))
        self.add_button(None)
        # self.add_button(self.make_text_button(
        #     "Edit Level",
        #     self.fonts[50],
        #     edit_current,
        #     (240 * 4, self.buttons[-1].img.get_height()),
        #     (255, 255, 255),
        #     (0, 0, 0),
        #     5,
        #     y_align=0,
        #     x_align=1
        # ))
        self.add_button(None)
        self.add_button(None)
        self.add_button(self.make_text_button(
            "Open Custom Folder",
            self.fonts[40],
            run,
            (0, 180 * 4),
            (255, 255, 255),
            (0, 0, 0),
            5,
            y_align=1,
            x_align=0,
            arguments={"args": fr"explorer /open, {Path().resolve()}\custom_levels"}
        ))
        self.add_button(self.make_text_button(
            "Import From Clipboard",
            self.fonts[30],
            import_from_clipboard,
            (0, 180 * 4 - self.buttons[-1].img.get_height()),
            (255, 255, 255),
            (0, 0, 0),
            5,
            y_align=1,
            x_align=0
        ))
        self.add_button(None)
        self.add_button(None)
        make_switch_button()
        get_level()
        while self.place == "level_select":
            self.tick()
            for lvl in [(c_lvl[:-4], False) for c_lvl in listdir("custom_levels")]:
                if lvl[0] not in [level[0] for level in self.levels[1]]:
                    self.levels[1].append(lvl)
                    get_level()
            self.screen.blit(
                self.level_display,
                (240 * 2 - self.level_display.get_width() / 2, 180 * 2 - self.level_display.get_height() / 2)
            )
            self.handle_buttons()
