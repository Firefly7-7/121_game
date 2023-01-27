"""
holds level editing area
"""

from utility import Utility
from level_management import make_blank_level, encode_level_to_string, decode_safety_wrap, make_playable
from render_level import draw_level
from pyperclip import paste
from level_data import Level
from game_structures import Button
from multiprocessing.dummy import Pool


class Construction(Utility):
    """
    class holding editing area
    """

    def construction_place(self) -> None:
        """
        runs construction space
        :return:
        """

        def delete_current_level() -> None:
            """
            deletes the current level and loads next one (handles edge cases for on end and empty)
            :return: None
            """
            del self.working_on[self.constructing]
            if self.constructing == len(self.working_on):
                if self.constructing == 0:
                    load_editing_level(0)
                else:
                    load_editing_level(self.constructing - 1)
            else:
                load_editing_level(self.constructing)

        def move_to_editing_level(index: int) -> None:
            """
            moves to a new editing level and saves changes
            :param index: index to move to
            :return: None
            """
            self.working_on[self.constructing] = encode_level_to_string(self.level_data)
            load_editing_level(index)

        def load_editing_level(index: int) -> None:
            """
            loads new level from the list
            :param index: index to move to
            :return: None
            """
            self.end_typing()
            self.constructing = index
            if index == len(self.working_on):
                self.level_data = make_blank_level()
                self.working_on.append(encode_level_to_string(self.level_data))
            else:
                self.level_data = decode_safety_wrap(self.working_on[index])
            update_game_image()
            update_name_placard()

        def update_name_placard(name: str = None) -> None:
            """
            updates name placard to new value and handles moving iter buttons
            :return:None
            """
            if name is None:
                name = self.level_data.name
            name_button = self.draw_text(name, 75, max_line_pixels=240 * 6, preserve_words=True)

            width = name_button.get_width()
            if width > 512:
                name_button = self.draw_text(
                    name,
                    75 * 512 / width,
                    max_line_pixels=240 * 6 * 512 / width,
                    preserve_words=True
                )
                width = name_button.get_width()
            self.replace_button(2, Button(
                edit_level_name,
                name_button,
                name,
                name_button.get_rect(center=(240 * 2, 50)),
                (255, 255, 255),
                (0, 0, 0),
                (0.5, 0.5),
                outline_width=5
            ))

            if self.constructing == 0:
                self.replace_button(3, None)
            else:
                self.replace_button(3, self.make_text_button(
                    "<",
                    75,
                    move_to_editing_level,
                    (240 * 2 - width / 2 - 40, 50),
                    border_width=5,
                    arguments={"index": self.constructing - 1},
                    override_text="Last work in progress level."
                ))
            self.replace_button(4, self.make_text_button(
                "+" if self.constructing == len(self.working_on) - 1 else ">",
                75,
                move_to_editing_level,
                (240 * 2 + width / 2 + 40, 50),
                border_width=5,
                arguments={"index": self.constructing + 1},
                override_text="Add new work in progress level." if self.constructing == len(self.working_on) else "Next work in progress level."
            ))

        def edit_level_name() -> None:
            """
            edits the level name currently on display.  Wrapper for interior async function
            :return:
            """

            def async_edit_level_name() -> None:
                """
                asynchronously edits level name on display
                :return:
                """
                current = self.level_data.name
                update_name_placard(current + "_")
                self.start_typing(current)
                while self.typing:
                    if self.text != current:
                        current = self.text
                        if 1 < len(current) < 101:
                            if current[-1] == "\n":
                                self.level_data.name = current[:-1]
                                update_name_placard(current[:-1])
                                return
                        elif "\n" in current:
                            self.text = current[:current.index("\n")]
                            current = self.text
                        update_name_placard(current + "_")
                return

            pool = Pool(1)
            pool.apply_async(async_edit_level_name)

        def update_game_image() -> None:
            """
            changes game image after a change
            :return: None
            """
            # noinspection PyTypeChecker
            self.level_display = draw_level(
                *make_playable(self.level_data),
                self.player_img,
                self.fonts[20],
                40
            )

        # 0: back button [static]
        self.add_button(self.make_text_button(
            "Back",
            50,
            self.change_place,
            (0, 0),
            border_width=5,
            arguments={"place": "level_select"},
            x_align=0,
            y_align=0,
            max_width=140,
            special_press="Back"
        ))

        # 1: import level button [static]
        def import_level() -> None:
            """
            imports a level from clipboard
            :return:
            """
            code = paste()
            level = decode_safety_wrap(code)
            if isinstance(level, Level):
                self.level_data = level
                self.constructing = len(self.working_on)
                self.working_on.append(code)
                update_game_image()

        self.add_button(self.make_text_button(
            "Import from Clipboard",
            25,
            import_level,
            (0, 180 * 4),
            border_width=5,
            x_align=0,
            y_align=1,
            max_width=0
        ))
        # 2: level name button [nonstatic]
        self.add_button(None)
        # 3: level iter left [dynamic]
        self.add_button(None)
        # 4: level iter right [nonstatic]
        self.add_button(None)
        # 5: delete [static]
        self.add_button(self.make_text_button(
            "Delete",
            20,
            delete_current_level,
            (0, 180 * 2),
            border_width=5,
            x_align=0
        ))

        # 6: export [static]
        def play_current_level(exporting: bool) -> None:
            """
            plays current level, sets up for export or test
            :param exporting: if exporting level, not just testing
            :return: None
            """
            if exporting:
                self.after_game = "export"
            else:
                self.after_game = "construction"
            self.place = "enter_level"

        self.add_button(self.make_text_button(
            "Export",
            50,
            play_current_level,
            (240 * 2, 180 * 4),
            y_align=1,
            border_width=5,
            arguments={"exporting": True}
        ))
        # 7: test [static]
        self.add_button(self.make_text_button(
            "Test",
            25,
            play_current_level,
            (240 * 2, 180 * 4 - self.buttons[-1].rect.height),
            y_align=1,
            border_width=5,
            arguments={"exporting": False}
        ))

        load_editing_level(self.constructing)
        while self.place == "construction":
            self.tick()
            self.screen.blit(
                self.level_display,
                (240 * 2 - self.level_display.get_width() / 2, 180 * 2 - self.level_display.get_height() / 2)
            )
            self.handle_buttons()
        self.working_on[self.constructing] = encode_level_to_string(self.level_data)