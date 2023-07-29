"""
holds level editing area
"""

from utility import Utility
from level_management import make_blank_level, encode_level_to_string, decode_safety_wrap
from pyperclip import paste
from level_data import LevelWrap
from game_structures import Button, ButtonHolder
from pygame.mouse import get_pos, get_pressed
from pygame.transform import smoothscale, rotate
from construction_areas import ParentConstructionArea, PlayerEditing, GravityEditing, BlockEditing, BarrierEditing, LinkEditing


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
            deletes the current level and loads next_ one (handles edge cases for on end and empty)
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
            if self.typing.typing and self.typing.button_target == 2:
                self.level_data.level_on.name = self.typing.text
                self.end_typing()
            else:
                self.level_data.level_on.name = self.buttons[2][0].text
            save_current_editing()
            load_editing_level(index)

        def save_current_editing() -> None:
            """
            saves the current editing level in a way that will never crash.
            :return: nothing
            """
            if isinstance(self.level_data, LevelWrap):
                self.working_on[self.constructing] = encode_level_to_string(self.level_data)

        def load_editing_level(index: int) -> None:
            """
            loads new level from the list
            :param index: index to move to
            :return: None
            """
            self.end_typing()
            self.constructing = index
            if index == len(self.working_on):
                self.level_data = LevelWrap(make_blank_level())
                self.working_on.append(encode_level_to_string(self.level_data))
            else:
                self.level_data = decode_safety_wrap(self.working_on[index])
            update_game_image()
            update_name_placard()
            ParentConstructionArea.update_construction_area(0)

        def update_name_placard(name: str = None) -> None:
            """
            updates name placard to new value and handles moving iter buttons
            :return:None
            """
            if not isinstance(self.level_data, LevelWrap):

                name = "ERROR"
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
                name_button_obj = Button(
                    None,
                    name_button,
                    name,
                    name_button.get_rect(center=(240 * 2, 50)),
                    (255, 255, 255),
                    (0, 0, 0),
                    (0.5, 0.5),
                    outline_width=5
                )
            else:
                if name is None:
                    name = self.level_data.level_on.name
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
                name_button_obj = Button(
                    self.write_button_text,
                    name_button,
                    name,
                    name_button.get_rect(center=(240 * 2, 50)),
                    (255, 255, 255),
                    (0, 0, 0),
                    (0.5, 0.5),
                    outline_width=5
                )
            level_name_control_buttons[0] = name_button_obj

            if self.constructing == 0:
                level_name_control_buttons[1] = None
            else:
                level_name_control_buttons[1] = self.make_text_button(
                    "<",
                    75,
                    move_to_editing_level,
                    (240 * 2 - width / 2 - 40, 50),
                    border_width=5,
                    arguments={"index": self.constructing - 1},
                    override_text="Last work in progress level."
                )
            level_name_control_buttons[2] = self.make_text_button(
                "+" if self.constructing == len(self.working_on) - 1 else ">",
                75,
                move_to_editing_level,
                (240 * 2 + width / 2 + 40, 50),
                border_width=5,
                arguments={"index": self.constructing + 1},
                override_text="Add new work in progress level." if self.constructing == len(
                    self.working_on) else "Next work in progress level."
            )
            name_button_obj.arguments = {
                "button_obj": name_button_obj,
                "font": 75,
                "max_characters": 100,
                "min_characters": 2,
                "others": [
                    (level_name_control_buttons[1], -0.5, 0, -40, 0),
                    (level_name_control_buttons[2], 0.5, 0, 40, 0)
                ],
                "max_line_pixels": 240 * 6,
                "max_width": 512,
                "callback": self.level_data.rename
            }

        def update_game_image() -> None:
            """
            changes game image after a change
            :return: None
            """
            if isinstance(self.level_data, TypeError):
                self.level_display = self.draw_text(
                    "Level does not have a valid version indicator.",
                    40
                )
            elif isinstance(self.level_data, ValueError):
                self.level_display = self.draw_text(
                    "There was an error loading level.",
                    40
                )
            else:
                self.level_data.prepare_for_play()
                # noinspection PyTypeChecker
                self.level_display = self.level_data.render_level(
                    40,
                    self.fonts[20],
                    player_imgs
                )

        if self.constructing == len(self.working_on):
            self.level_data = LevelWrap(make_blank_level())
            self.working_on.append(encode_level_to_string(self.level_data))
        else:
            self.level_data = decode_safety_wrap(self.working_on[self.constructing])
        scaled_player = smoothscale(self.player_img, (30, 30))
        player_imgs = tuple(rotate(scaled_player, 90 * i) for i in range(4))
        update_game_image()

        # 0: back button [static]
        self.buttons.add_button(self.make_text_button(
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
            if isinstance(level, LevelWrap):
                self.level_data = level
                self.constructing = len(self.working_on)
                self.working_on.append(code)
                update_game_image()

        self.buttons.add_button(self.make_text_button(
            "Import from Clipboard",
            25,
            import_level,
            (0, 180 * 4),
            border_width=5,
            x_align=0,
            y_align=1,
            max_width=256
        ))
        # 2.0-2: level name control buttons [nonstatic]
        level_name_control_buttons = ButtonHolder()
        level_name_control_buttons.add_button(None)
        level_name_control_buttons.add_button(None)
        level_name_control_buttons.add_button(None)
        self.buttons.add_button(level_name_control_buttons)
        # 3: delete [static]
        self.buttons.add_button(self.make_text_button(
            "Delete",
            20,
            delete_current_level,
            (0, 180 * 2),
            border_width=5,
            x_align=0
        ))

        # 4: export [static]
        def play_current_level(exporting: bool) -> None:
            """
            plays current level, sets up for export or test
            :param exporting: if exporting level, not just testing
            :return: None
            """
            save_current_editing()
            if exporting:
                self.after_game = "export"
            else:
                self.after_game = "construction"
            self.place = "enter_level"

        def force_export_level() -> None:
            """
            force exports a level, only for use if in admin mode
            :return: none
            """
            save_current_editing()
            if not self.admin:
                return
            name_append = ""
            copies = 0
            custom_names = {self.levels[1][lvl_index][0] for lvl_index in range(len(self.levels[1]))}
            while self.level_data.level_on.name + name_append in custom_names:
                copies += 1
                name_append = "(" + str(copies) + ")"

            name = f"custom_levels/{self.level_data.level_on.name}.txt"
            with open(name, "w", encoding="utf-8") as file:
                file.write(self.working_on[self.constructing])

            self.look_at[1] = len(self.levels[1])
            self.levels[1].append((self.level_data.level_on.name, False))
            self.custom = 1
            self.place = "level_select"

        if self.admin:
            self.buttons.add_button(self.make_text_button(
                "Force Export",
                50,
                force_export_level,
                (240 * 2, 180 * 4),
                y_align=1,
                border_width=5,
                max_width=256
            ))
        else:
            self.buttons.add_button(self.make_text_button(
                "Export",
                50,
                play_current_level,
                (240 * 2, 180 * 4),
                y_align=1,
                border_width=5,
                arguments={"exporting": True},
                max_width=256
            ))
        # 5: test [static]
        self.buttons.add_button(self.make_text_button(
            "Test",
            25,
            play_current_level,
            (240 * 2, 180 * 4 - self.buttons[-1].rect.height),
            y_align=1,
            border_width=5,
            arguments={"exporting": False},
            special_press="Play"
        ))

        # 6...: all construction area buttons

        ParentConstructionArea.register_areas(
            [PlayerEditing, GravityEditing, BlockEditing, BarrierEditing, LinkEditing]
        )
        self.add_button(ParentConstructionArea.single_time_prepare(update_game_image, self))

        mouse_down = False
        click_tick = False
        load_editing_level(self.constructing)
        while self.place == "construction":
            self.tick()
            # handle clicks
            mouse_pos = get_pos()
            if abs(mouse_pos[0] - 240 * 2) < self.level_display.get_width() / 2 - 2 and abs(
                    mouse_pos[1] - 180 * 2) < self.level_display.get_height() / 2 - 2:
                mouse_coords = (
                    round((mouse_pos[0] - 240 * 2 + self.level_display.get_width() / 2 - 1) / 40 + 0.5),
                    round(-1 * (mouse_pos[1] - 180 * 2 - self.level_display.get_height() / 2 + 1) / 40 + 0.5)

                )
            else:
                mouse_coords = None
            if get_pressed(3)[0]:
                if mouse_down:
                    click_tick = False
                else:
                    mouse_down = True
                    click_tick = True
            else:
                mouse_down = False
            if click_tick and mouse_coords is not None:
                ParentConstructionArea.click_tick(mouse_coords)

            self.screen.blit(
                self.level_display,
                (240 * 2 - self.level_display.get_width() / 2, 180 * 2 - self.level_display.get_height() / 2)
            )
            # handle construction screen specific visual changes
            ParentConstructionArea.tick(mouse_pos, mouse_coords)
        self.level_data.level_on.name = self.buttons[2][0].text
        save_current_editing()