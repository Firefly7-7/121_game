"""
contains class for level select area
"""

from level_management import unpack_level, decode_safety_wrap, save_level, encode_level_to_string
from utility import Utility, LEVEL_LIST
from pyperclip import paste, copy
from os import listdir, remove
from pygame import Surface
from pygame.draw import lines
from pygame.transform import rotate
from block_data import Block
from game_structures import Button
from level_data import LevelWrap, Level
from block_data import EasterEgg


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
                self.level_data.prepare_for_play()
                # noinspection PyTypeChecker
                self.level_display = self.level_data.render_level(
                    40,
                    self.fonts[20],
                    tuple(rotate(self.player_img, 90 * i) for i in range(4))
                )
                length = 1
                track = self.level_data.level_on
                while track.next is not None:
                    length += 1
                    track = track.next
                if length > 1:
                    name += " (" + str(length) + " stages)"
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
                    special_press="Play",
                    max_width=256
                ))
            name_button = self.draw_text(name, 75, max_line_pixels=240 * 6, preserve_words=True)
            height = name_button.get_height()
            width = name_button.get_width() + (
                    self.levels[self.custom][self.look_at[self.custom]][
                        1] / 2 + 5 * (name not in LEVEL_LIST and self.custom == 0) / 8) * height
            if width > 512:
                name_button = self.draw_text(
                    name,
                    75 * 512 / width,
                    max_line_pixels=240 * 6 * 512 / width,
                    preserve_words=True
                )
                height = name_button.get_height()
                width = name_button.get_width() + (
                        self.levels[self.custom][self.look_at[self.custom]][1] / 2 + 5 * (
                        name not in LEVEL_LIST and self.custom == 0) / 8
                ) * height
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
                    self.level_data.draw_block(Block(EasterEgg, []), self.fonts[50], 5 * height / 8),
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
                max_width=160
            ))
            self.replace_button(10, self.make_text_button(
                "Copy Level Code",
                25,
                copy_level,
                (240 * 4, self.buttons[2].img.get_height() + self.buttons[3].img.get_height()),
                (255, 255, 255),
                (0, 0, 0),
                5,
                y_align=0,
                x_align=1,
                max_width=160,
                arguments={"level": self.level_data}
            ))
            # print(cls.custom, cls.look_at, cls.level_on)

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
            if isinstance(self.level_data, LevelWrap):
                level_on = self.level_data.level_on
                while isinstance(level_on, Level):
                    self.working_on.append(encode_level_to_string(level_on))
                    self.alerts.add_alert(
                        f"Imported level '{level_on.name}' from level select to level construction."
                    )
                    level_on = level_on.next
                self.constructing = len(self.working_on) - 1
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
                max_width=280
            ))
            if self.custom == 1:
                self.replace_button(11, self.make_text_button(
                    "delete",
                    20,
                    delete_level,
                    (0, 180 * 2),
                    border_width=5,
                    x_align=0
                ))
            else:
                self.replace_button(11, None)

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
            if isinstance(level, LevelWrap):
                name_append = ""
                copies = 0
                unique_name = False
                while not unique_name:
                    unique_name = True
                    for lvl_index in range(len(self.levels[1])):
                        if level.level_on.name + name_append == self.levels[1][lvl_index][0]:
                            copies += 1
                            name_append = "(" + str(copies) + ")"
                            unique_name = False
                            break
                level.level_on.name = level.level_on.name + name_append
                save_level(level)
                self.look_at[1] = len(self.levels[1])
                self.levels[1].append((level.level_on.name, False))
                self.custom = 1
                get_level()
                make_switch_button()
            else:
                self.alerts.add_alert("Level code from clipboard is not valid.")

        # 7: open custom folder [static] (done)
        # 8: -1 level button [dynamic] (done)
        # 9: +1 level button [dynamic] (done)

        def copy_level(level: LevelWrap) -> None:
            """
            copies level data to clipboard
            :param level: level object
            :return: none
            """
            copy(encode_level_to_string(level))

        # 10: copy level code to clipboard [dynamic]

        def delete_level() -> None:
            """
            deletes a level from the custom level directory
            :return: nothing
            """
            del_lvl = self.levels[1].pop(self.look_at[1])
            remove(f"custom_levels/{del_lvl[0]}.txt")
            if self.look_at[1] > 0:
                self.look_at[1] -= 1
            get_level()

        # 11: delete level from directory [dynamic]

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
        ))  # 0
        self.add_button(None)  # 1 replaced with play
        # cls.add_button(None)
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
            max_width=160
        ))  # 2
        self.add_button(None)  # 3 replaced by edit button
        self.add_button(None)  # 4 replaced by switch level
        self.add_button(None)  # 5 replaced by name
        self.add_button(self.make_text_button(
            "Open Custom Folder",
            40,
            self.open_directory,
            (0, 180 * 4),
            (255, 255, 255),
            (0, 0, 0),
            5,
            y_align=1,
            x_align=0,
            max_width=280,
            arguments={"args": ["custom_levels"]}
        ))  # 6
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
            max_width=260
        ))  # 7
        self.add_button(None)  # 8 replaced by arrow keys
        self.add_button(None)  # 9 replaced by arrow keys
        self.add_button(None)  # 10 replaced by copy button
        self.add_button(None)  # 11 replaced by delete button
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
