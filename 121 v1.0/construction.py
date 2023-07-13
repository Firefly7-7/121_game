"""
holds level editing area
"""

from utility import Utility
from level_management import make_blank_level, encode_level_to_string, decode_safety_wrap, make_playable
from render_level import draw_level, draw_block, sin, cos, draw_arrow, clean_decimal, degree_to_rgb
from pyperclip import paste
from level_data import Level
from game_structures import Button
from constants import CONSTRUCTION_MENUS, BLOCK_LIST, BARRIERS, BLOCK_CONSTRUCTION, BLOCK_DESCRIPTIONS, BUTTON_COUNT, FieldType
from pygame.mouse import get_pos, get_pressed
from pygame.transform import smoothscale, rotate
from block_data import Block
from copy import deepcopy, copy
from math import ceil
from typing import Union
from pygame.surface import Surface
from pygame.draw import circle


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
            if self.typing.typing and self.typing.button_target == 2:
                self.level_data.name = self.typing.text
                self.end_typing()
            else:
                self.level_data.name = self.button_names[2]
            save_current_editing()
            load_editing_level(index)

        def save_current_editing() -> None:
            """
            saves the current editing level in a way that will never crash.
            :return: nothing
            """
            if isinstance(self.level_data, Level):
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
                self.level_data = make_blank_level()
                self.working_on.append(encode_level_to_string(self.level_data))
            else:
                self.level_data = decode_safety_wrap(self.working_on[index])
            update_game_image()
            update_name_placard()
            update_construction_area(0)

        def update_name_placard(name: str = None) -> None:
            """
            updates name placard to new value and handles moving iter buttons
            :return:None
            """
            if not isinstance(self.level_data, Level):

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
                self.replace_button(2, Button(
                    None,
                    name_button,
                    name,
                    name_button.get_rect(center=(240 * 2, 50)),
                    (255, 255, 255),
                    (0, 0, 0),
                    (0.5, 0.5),
                    outline_width=5,
                    arguments={
                        "index": 2,
                        "font": 75,
                        "max_characters": 100,
                        "min_characters": 2,
                        "others": [
                            (3, -0.5, 0, -40, 0),
                            (4, 0.5, 0, 40, 0)
                        ],
                        "max_line_pixels": 240 * 6,
                        "max_width": 512,
                    }
                ))
            else:
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
                    self.write_button_text,
                    name_button,
                    name,
                    name_button.get_rect(center=(240 * 2, 50)),
                    (255, 255, 255),
                    (0, 0, 0),
                    (0.5, 0.5),
                    outline_width=5,
                    arguments={
                        "index": 2,
                        "font": 75,
                        "max_characters": 100,
                        "min_characters": 2,
                        "others": [
                            (3, -0.5, 0, -40, 0),
                            (4, 0.5, 0, 40, 0)
                        ],
                        "max_line_pixels": 240 * 6,
                        "max_width": 512,
                    }
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
                override_text="Add new work in progress level." if self.constructing == len(
                    self.working_on) else "Next work in progress level."
            ))

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
                # noinspection PyTypeChecker
                self.level_display = draw_level(
                    *make_playable(self.level_data),
                    player_imgs[self.level_data.gravity[0]],
                    self.fonts[20],
                    40
                )

        if self.constructing == len(self.working_on):
            self.level_data = make_blank_level()
            self.working_on.append(encode_level_to_string(self.level_data))
        else:
            self.level_data = decode_safety_wrap(self.working_on[self.constructing])
        scaled_player = smoothscale(self.player_img, (30, 30))
        player_imgs = tuple(rotate(scaled_player, 90 * i) for i in range(4))
        update_game_image()

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
            max_width=256
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
            while self.level_data.name + name_append in custom_names:
                copies += 1
                name_append = "(" + str(copies) + ")"

            name = f"custom_levels/{self.level_data.name}.txt"
            with open(name, "w", encoding="utf-8") as file:
                file.write(self.working_on[self.constructing])

            self.look_at[1] = len(self.levels[1])
            self.levels[1].append((self.level_data.name, False))
            self.custom = 1
            self.place = "level_select"

        if self.admin:
            self.add_button(self.make_text_button(
                "Force Export",
                50,
                force_export_level,
                (240 * 2, 180 * 4),
                y_align=1,
                border_width=5,
                max_width=256
            ))
        else:
            self.add_button(self.make_text_button(
                "Export",
                50,
                play_current_level,
                (240 * 2, 180 * 4),
                y_align=1,
                border_width=5,
                arguments={"exporting": True},
                max_width=256
            ))
        # 7: test [static]
        self.add_button(self.make_text_button(
            "Test",
            25,
            play_current_level,
            (240 * 2, 180 * 4 - self.buttons[-1].rect.height),
            y_align=1,
            border_width=5,
            arguments={"exporting": False},
            special_press="Play"
        ))

        player_grabbed = None

        def grab_player(coords: tuple[int, int] = None) -> None:
            """
            grabs a player, either from new player space or from game screen
            :param coords: coordinates of game to grab from
            :return: None
            """
            nonlocal player_grabbed
            if coords is None:
                player_grabbed = True
            else:
                player_grabbed = coords
                # print(coords)
                # print(self.level_data.player_starts)
                player_grabbed = coords
                self.level_data.player_starts.remove(coords)
                update_game_image()
                button = 12
                while True:
                    if self.buttons[button].arguments["coords"] == coords:
                        del self.buttons[button]
                        break
                    button += 1

        def change_gravity(index: int, change: Union[float, int]) -> None:
            """
            changes a gravity setting
            :param index: index to change at (0 is dir, 1 is strength)
            :param change: how much to change it by
            :return: None
            """
            grav = list(self.level_data.gravity)
            grav[index] = clean_decimal((1 - 2 * index) * (((1 - 2 * index) * grav[index] + change) % (4 - 1.25 * index)
                                                           ))
            self.level_data.gravity = grav
            update_game_image()
            update_construction_area(0)

        editing_block = "delete"
        editing_block_fields = dict()
        for block_name, field_list in BLOCK_CONSTRUCTION.items():
            editing_block_fields[block_name] = {
                field_name: default for field_name, display, field_type, default, *etc in field_list
            }

        total_width = 200
        per_line = 7
        scale = 22
        line_spacing = total_width // per_line
        construction_center = round(240 * 3 + self.level_display.get_width() / 4)

        def switch_construction_block(block_name_switch: str) -> None:
            """
            switches the construction_block used
            :param block_name_switch:
            :return:
            """
            nonlocal editing_block
            if self.typing.typing and self.typing.button_target > 10:
                self.end_typing()
            editing_block = block_name_switch
            self.replace_button(11 + len(BLOCK_LIST), self.make_text_button(
                editing_block.title(),
                30,
                None,
                (
                    construction_center,
                    0
                ),
                max_line_pixels=256,
                max_width=256,
                text_align=0.5
            ))
            self.replace_button(13 + len(BLOCK_LIST), self.make_text_button(
                BLOCK_DESCRIPTIONS[editing_block],
                10,
                None,
                (
                    construction_center,
                    0
                ),
                y_align=0,
                max_line_pixels=200
            ))
            del self.buttons[14 + len(BLOCK_LIST):]
            prep_construction_control_buttons()
            update_construction_control_buttons()

        def change_field(field: str, field_index: int, **kwargs) -> None:
            """
            changes field value
            :param field: field to change
            :param field_index: index of field in BLOCK_CONSTRUCTION
            :param kwargs: field to catch named fields not required for all items
            :return: None
            """
            field_name, display_name, field_type, default, conditional, *args = BLOCK_CONSTRUCTION[editing_block][
                field_index]
            if field_type == FieldType.boolean:
                editing_block_fields[editing_block][field] = not editing_block_fields[editing_block][field]
            if field_type == FieldType.iterator:
                editing_block_fields[editing_block][field] = args[0] + (
                        editing_block_fields[editing_block][field] + kwargs["direction"] * args[2] - args[0]
                ) % (args[1] - args[0])
            if field_type == FieldType.list:
                editing_block_fields[editing_block][field] = args[0][
                    (args[0].index(editing_block_fields[editing_block][field]) + 1) % len(args[0])
                    ]
            if field_type == FieldType.text:
                set_block = editing_block

                others = []

                x, y = self.buttons[kwargs["button_index"]].rect.midtop

                for index, button in list(enumerate(self.buttons))[kwargs["button_index"] + 1:]:
                    others.append((
                        index, 0, 1,
                        button.rect.centerx - x,
                        button.rect.centery - y - self.buttons[kwargs["button_index"]].rect.height
                    ))

                def save_text_field(result: str) -> None:
                    """
                    used to save typing result
                    :param result: string result from typing
                    :return:
                    """
                    editing_block_fields[set_block][field] = result

                self.write_button_text(
                    kwargs["button_index"],
                    12,
                    max_characters=args[1],
                    min_characters=args[0],
                    max_line_pixels=200,
                    prepend=f"{display_name}: ",
                    start_text=editing_block_fields[set_block][field],
                    callback=save_text_field,
                    y_align=0,
                    others=others
                )
            update_construction_control_buttons()

        def prep_construction_control_buttons() -> None:
            """
            preps the buttons list with empty buttons
            :return: None
            """
            for field_name, display_name, field_type, *args in BLOCK_CONSTRUCTION[editing_block]:
                for count in range(0, BUTTON_COUNT[field_type]):
                    self.add_button(None)

        def update_construction_control_buttons() -> None:
            """
            updates display of the control buttons
            :return:
            """
            index = 14 + len(BLOCK_LIST)
            self.replace_button(11 + BLOCK_LIST.index(editing_block), self.make_img_button(
                switch_construction_block,
                draw_block(
                    Block(
                        editing_block,
                        [],
                        editing_block_fields[editing_block]
                    ),
                    self.level_data.gravity[0],
                    self.fonts[scale],
                    scale
                ),
                (
                    construction_center + (
                            BLOCK_LIST.index(editing_block) % per_line - per_line / 2 + 0.5) * line_spacing,
                    round(165 + (BLOCK_LIST.index(editing_block) // per_line + 0.5) * line_spacing)
                ),
                editing_block,
                arguments={"block_name_switch": editing_block}
            ))

            y = (180 + ceil(len(BLOCK_LIST) / per_line) * line_spacing)
            round(260 + ceil(len(BLOCK_LIST) / per_line) * line_spacing)

            self.buttons[11 + len(BLOCK_LIST)].rect.y = y

            y += self.buttons[11 + len(BLOCK_LIST)].img.get_height()

            block_img = draw_block(
                Block(
                    editing_block,
                    [],
                    editing_block_fields[editing_block]
                ),
                self.level_data.gravity[0],
                self.fonts[60],
                60
            )

            y += block_img.get_height() / 2

            self.replace_button(12 + len(BLOCK_LIST), self.make_img_button(
                None,
                block_img,
                (
                    construction_center,
                    y
                ),
                None,
            ))

            y += block_img.get_height() / 2

            self.buttons[13 + len(BLOCK_LIST)].rect.top = y

            y += self.buttons[13 + len(BLOCK_LIST)].rect.height + 12

            field_index = -1
            for field_name, display_name, field_type, default, conditional, *args in BLOCK_CONSTRUCTION[editing_block]:
                field_index += 1
                value = editing_block_fields[editing_block][field_name]
                place_field = True
                for field, condition in conditional:
                    if editing_block_fields[editing_block][field] not in condition:
                        place_field = False
                        break
                if not place_field:
                    for m in range(0, BUTTON_COUNT[field_type]):
                        self.replace_button(index, None)
                        index += 1
                    continue
                if field_type == FieldType.boolean:
                    if len(args) > 0:
                        display = args[0][value]
                    else:
                        display = value
                    self.replace_button(index, self.make_text_button(
                        f"{display_name}: {display}",
                        12,
                        change_field,
                        (
                            construction_center,
                            y - 7
                        ),
                        border_width=5,
                        y_align=0,
                        arguments={"field": field_name, "field_index": field_index},
                        max_width=256
                    ))
                    self.buttons[index].inflate_center = (0.5, 0.5)
                    y += 6 + self.buttons[index].rect.height
                    index += 1
                elif field_type == FieldType.iterator:
                    if len(args) > 3:
                        display = args[3][round((value - args[0]) / args[2])]
                    else:
                        display = value
                    button = self.make_text_button(
                        f"{display_name}: {display}",
                        12,
                        None,
                        (
                            construction_center,
                            y - 7
                        ),
                        max_line_pixels=total_width,
                        y_align=0,
                        border_width=5,
                    )
                    button.inflate_center = (0.5, 0.5)
                    offset = round(button.img.get_width() / 2 + 20)
                    self.replace_button(index, button)
                    index += 1
                    self.replace_button(index, self.make_text_button(
                        "<",
                        12,
                        change_field,
                        (
                            construction_center - offset,
                            y
                        ),
                        border_width=5,
                        arguments={"field": field_name, "field_index": field_index, "direction": -1}
                    ))
                    index += 1
                    self.replace_button(index, self.make_text_button(
                        ">",
                        12,
                        change_field,
                        (
                            construction_center + offset,
                            y
                        ),
                        border_width=5,
                        arguments={"field": field_name, "field_index": field_index, "direction": 1}
                    ))
                    index += 1
                    y += 6 + max(self.buttons[index - 1].rect.height, self.buttons[index - 3].rect.height)
                elif field_type == FieldType.list:
                    if len(args) > 1:
                        display = args[0][value]
                    else:
                        display = value
                    self.replace_button(index, self.make_text_button(
                        f"{display_name}: {display}",
                        12,
                        change_field,
                        (
                            construction_center,
                            y - 7
                        ),
                        y_align=0,
                        border_width=5,
                        max_line_pixels=total_width,
                        arguments={"field": field_name, "field_index": field_index}
                    ))
                    self.buttons[index].inflate_center = (0.5, 0.5)
                    y += 6 + self.buttons[index].rect.height
                    index += 1
                elif field_type == FieldType.text:
                    self.replace_button(index, self.make_text_button(
                        f"{display_name}: {value}",
                        12,
                        change_field,
                        (
                            construction_center,
                            y - 7
                        ),
                        border_width=5,
                        max_line_pixels=total_width,
                        y_align=0,
                        arguments={"field": field_name, "field_index": field_index, "button_index": index}
                    ))
                    self.buttons[index].inflate_center = (0.5, 0.5)
                    y += self.buttons[index].rect.height + 6
                    index += 1
                elif field_type == FieldType.freeform_num:
                    display = value
                    button = self.make_text_button(
                        f"{display_name}: {display}",
                        12,
                        None,
                        (
                            construction_center,
                            y - 7
                        ),
                        max_line_pixels=total_width,
                        y_align=0,
                        border_width=5,
                    )
                    button.inflate_center = (0.5, 0.5)
                    offset = round(button.img.get_width() / 2 + 20)
                    self.replace_button(index, button)
                    index += 1
                    self.replace_button(index, self.make_text_button(
                        "<",
                        12,
                        change_field,
                        (
                            construction_center - offset,
                            y
                        ),
                        border_width=5,
                        arguments={"field": field_name, "field_index": field_index, "direction": -1}
                    ))
                    index += 1
                    self.replace_button(index, self.make_text_button(
                        ">",
                        12,
                        change_field,
                        (
                            construction_center + offset,
                            y
                        ),
                        border_width=5,
                        arguments={"field": field_name, "field_index": field_index, "direction": 1}
                    ))
                    index += 1
                    y += 6 + max(self.buttons[index - 1].rect.height, self.buttons[index - 3].rect.height)

        editing_barrier = ["delete", False, [True, True, True, True]]

        def switch_construction_barrier(barrier: str) -> None:
            """
            switches construction barrier type
            :param barrier: barrier type to switch to
            :return: none
            """
            nonlocal editing_barrier
            reinitialize = barrier == "delete" or editing_barrier[0] == "delete"
            editing_barrier[0] = barrier
            if reinitialize:
                update_construction_area(0)
            else:
                update_barrier_img()

        def update_barrier_img() -> None:
            """
            updates big barrier image to new value in editing_barrier[0]
            :return: nothing
            """
            if editing_barrier[0] == "delete":
                self.buttons[17 + len(BARRIERS)].img = draw_block(
                    Block(
                        "delete",
                        []
                    ),
                    0,
                    self.fonts[10],
                    80
                )
            else:
                self.buttons[17 + len(BARRIERS)].img = draw_block(
                    Block(
                        "",
                        [(editing_barrier[0], editing_barrier[1], tuple(editing_barrier[2]))]
                    ),
                    0,
                    self.fonts[10],
                    80
                )
            self.buttons[17 + len(BARRIERS)].rect = self.buttons[17 + len(BARRIERS)].img.get_rect(center=self.buttons[
                17 + len(BARRIERS)].rect.center)
            self.replace_button(18 + len(BARRIERS), self.make_text_button(
                editing_barrier[0].title(),
                20,
                None,
                (
                    construction_center,
                    self.buttons[17 + len(BARRIERS)].rect.y + 120
                ),
                border_width=5
            ))

        def update_barrier_side(side: int) -> None:
            """
            updates a barrier's side
            :param side:
            :return: None
            """
            nonlocal editing_barrier
            editing_barrier[2][side] = not editing_barrier[2][side]
            update_barrier_img()

        def switch_grav_lock_barriers() -> None:
            """
            switches grav lock for the barriers and updates area to reflect it
            :return: None
            """
            nonlocal editing_barrier
            editing_barrier[1] = not editing_barrier[1]
            update_construction_area(0)

        editing_link = ["Place", 0]

        def switch_link_place(place: str) -> None:
            """
            switches link place to given value
            :param place: the place/setting to change to
            :return: None
            """
            nonlocal editing_link
            editing_link[0] = place
            del self.buttons[14:]
            if place == "Place":
                self.add_button(self.make_text_button(
                    f"Link # {editing_link[1] + 1}",
                    20,
                    None,
                    (construction_center, 180),
                    border_width=5
                ))
                img = Surface((60, 60))
                img.fill((255, 255, 255))
                circle(img, degree_to_rgb(editing_link[1] * 54), (30, 30), 30)
                self.add_button(self.make_img_button(
                    None,
                    img,
                    (construction_center, 235),
                    None
                ))
                self.add_button(self.make_text_button(
                    "-",
                    16,
                    change_link_number,
                    (construction_center - 50, 235),
                    border_width=5,
                    arguments={"change": -1}
                ))
                self.add_button(self.make_text_button(
                    "+",
                    16,
                    change_link_number,
                    (construction_center + 50, 235),
                    border_width=5,
                    arguments={"change": 1}
                ))
            elif place == "Pick":
                self.add_button(self.make_text_button(
                    "?",
                    100,
                    None,
                    (construction_center, 222),
                    override_text="pick mode"
                ))  # 11:13 switch places buttons
            elif place == "Remove":
                self.add_button(self.make_img_button(
                    None,
                    draw_block(Block("delete", []), 0, self.fonts[60], 100),
                    (construction_center, 222),
                    "delete mode"
                ))

        def change_link_number(change: int) -> None:
            """
            changes link number up or down
            :param change: what to change the link number by
            :return: None
            """
            nonlocal editing_link
            editing_link[1] = (editing_link[1] + change) % (len(self.level_data.links) + 1)
            if editing_link[1] == len(self.level_data.links):
                if not self.level_data.links[-1]:
                    if change > 0:
                        editing_link[1] = 0
                    else:
                        editing_link[1] = len(self.level_data.links) - 1
                else:
                    self.level_data.links.append([])
            if len(self.level_data.links) > editing_link[1] + 1 and not self.level_data.links[editing_link[1]]:
                while len(self.level_data.links) > editing_link[1] + 1 and not self.level_data.links[editing_link[1]]:
                    del self.level_data.links[editing_link[1]]
                    editing_link[1] = (editing_link[1] + change) % len(self.level_data.links)
                update_game_image()
            self.replace_button(14, self.make_text_button(
                f"Link # {editing_link[1] + 1}",
                20,
                None,
                (construction_center, 180),
                border_width=5
            ))
            img = Surface((60, 60))
            img.fill((255, 255, 255))
            circle(img, degree_to_rgb(editing_link[1] * 54), (30, 30), 30)
            self.replace_button(15, self.make_img_button(
                None,
                img,
                (construction_center, 235),
                None
            ))

        def update_construction_area(index_change: int) -> None:
            """
            changes construction space
            :param index_change: left (-1) or right (1) (or no movement (0))
            :return: none
            """
            if self.typing.typing and self.typing.button_target > 10:
                self.end_typing()
            if not isinstance(self.level_data, Level):
                del self.buttons[11:]
                return
            nonlocal construction_pointer
            construction_pointer = (construction_pointer + index_change) % len(CONSTRUCTION_MENUS)
            self.replace_button(8, self.make_text_button(
                CONSTRUCTION_MENUS[construction_pointer],
                30,
                None,
                (240 * 3 + self.level_display.get_width() / 4, 140),
                y_align=0.5,
                border_width=5
            ))
            width = self.buttons[8].rect.width / 2
            display_width = self.level_display.get_width()
            self.buttons[9].rect.center = (240 * 3 + display_width / 4 - 20 - width, 140)
            self.buttons[10].rect.center = (240 * 3 + display_width / 4 + 20 + width, 140)
            del self.buttons[11:]
            if construction_pointer == 0:  # players editing
                self.add_button(self.make_img_button(
                    grab_player,
                    player_imgs[self.level_data.gravity[0]],
                    (240 * 3 + display_width / 4, 200),
                    "new player"
                ))
                for coords in self.level_data.player_starts:
                    self.add_button(Button(
                        grab_player,
                        player_imgs[self.level_data.gravity[0]],
                        f"at {coords[0]}, {coords[1]}",
                        scaled_player.get_rect(center=(
                            240 * 2 - display_width / 2 - 20 + 40 * coords[0] + 1,
                            180 * 2 + display_width / 2 + 20 - 40 * coords[1] - 1
                        )),
                        inflate_center=(0.5, 0.5),
                        outline_width=0,
                        arguments={"coords": coords}
                    ))
            elif construction_pointer == 1:  # gravity setting
                arrow = Surface((60, 60))
                arrow.fill((255, 255, 255))
                draw_arrow(arrow, (2 - self.level_data.gravity[0]) % 4, (0, 0, 0), 60)
                self.add_button(self.make_img_button(
                    None,
                    arrow,
                    (construction_center, 200),
                    f"Gravity is pointing {('down', 'right', 'up', 'left')[self.level_data.gravity[0]]} with strength "
                    f"{self.level_data.gravity[1]}."
                ))
                self.add_button(self.make_text_button(
                    f"Strength: {-1 * self.level_data.gravity[1]}",
                    16,
                    None,
                    (construction_center, 260),
                    border_width=5
                ))
                width = self.buttons[-1].rect.width / 2 + 20
                if self.level_data.gravity[1] >= 0:
                    self.add_button(None)
                else:
                    self.add_button(self.make_text_button(
                        "-",
                        16,
                        change_gravity,
                        (construction_center - width, 260),
                        border_width=5,
                        arguments={"index": 1, "change": -0.25}
                    ))
                if self.level_data.gravity[1] <= -2.5:
                    self.add_button(None)
                else:
                    self.add_button(self.make_text_button(
                        "+",
                        16,
                        change_gravity,
                        (construction_center + width, 260),
                        border_width=5,
                        arguments={"index": 1, "change": 0.25}
                    ))
                self.add_button(self.make_text_button(
                    f"Direction: {('down', 'right', 'up', 'left')[self.level_data.gravity[0]]}",
                    16,
                    None,
                    (construction_center, 300),
                    border_width=5
                ))
                width = self.buttons[-1].rect.width / 2 + 20
                self.add_button(self.make_text_button(
                    "<",
                    16,
                    change_gravity,
                    (construction_center - width, 300),
                    border_width=5,
                    arguments={"index": 0, "change": 1}
                ))
                self.add_button(self.make_text_button(
                    ">",
                    16,
                    change_gravity,
                    (construction_center + width, 300),
                    border_width=5,
                    arguments={"index": 0, "change": -1}
                ))
            elif construction_pointer == 2:  # blocks setting
                for construction_i, construction_block in enumerate(BLOCK_LIST):  # 11:10+len(BLOCK_LIST): blocks
                    self.add_button(self.make_img_button(
                        switch_construction_block,
                        draw_block(
                            Block(
                                construction_block,
                                [],
                                editing_block_fields[construction_block]
                            ),
                            self.level_data.gravity[0],
                            self.fonts[scale],
                            scale
                        ),
                        (
                            240 * 3 + display_width / 4 + (construction_i % per_line - per_line / 2 + 0.5
                                                           ) * line_spacing,
                            round(165 + (construction_i // per_line + 0.5) * line_spacing)
                        ),
                        construction_block,
                        arguments={"block_name_switch": construction_block}
                    ))
                self.add_button(None)  # 11 + len(BLOCK_LIST): construction_block name
                self.add_button(None)  # 12 + len(BLOCK_LIST): construction_block img
                self.add_button(None)  # 13 + len(BLOCK_LIST): construction_block description
                switch_construction_block(editing_block)
            elif construction_pointer == 3:  # barriers setting
                self.add_button(self.make_img_button(
                    switch_construction_barrier,
                    draw_block(
                        Block(
                            "delete",
                            []
                        ),
                        self.level_data.gravity[0],
                        self.fonts[scale],
                        scale
                    ),
                    (
                        240 * 3 + display_width / 4 + (0 % per_line - per_line / 2 + 0.5) * line_spacing,
                        round(165 + (0 // per_line + 0.5) * line_spacing)
                    ),
                    "delete",
                    arguments={"barrier": "delete"}
                ))  # 11: delete option
                y = 245 + ceil(len(BARRIERS) / per_line) * line_spacing
                for construction_i, barrier in enumerate(BARRIERS):  # 12:11+len(BARRIERS): barriers
                    self.add_button(self.make_img_button(
                        switch_construction_barrier,
                        draw_block(
                            Block(
                                "",
                                [(barrier, editing_barrier[1], (True, True, True, True))]
                            ),
                            self.level_data.gravity[0],
                            self.fonts[scale],
                            scale
                        ),
                        (
                            240 * 3 + display_width / 4 + (
                                    (construction_i + 1) % per_line - per_line / 2 + 0.5) * line_spacing,
                            round(165 + ((construction_i + 1) // per_line + 0.5) * line_spacing)
                        ),
                        barrier,
                        arguments={"barrier": barrier}
                    ))
                if editing_barrier[0] == "delete":
                    for direction in range(0, 4):  # 12 + len(BARRIER_LIST):15 + len(BARRIER_LIST): buttons
                        self.add_button(None)
                    self.add_button(None)  # 16 + len(BARRIER_LIST): grav lock
                else:
                    for direction in range(0, 4):  # 12 + len(BARRIER_LIST):15 + len(BARRIER_LIST): buttons
                        self.add_button(self.make_img_button(
                            update_barrier_side,
                            draw_block(
                                Block(
                                    "",
                                    [("ground", False, (True, True, True, True))]
                                ),
                                self.level_data.gravity[0],
                                self.fonts[scale],
                                scale=16
                            ),
                            (
                                construction_center + 50 * cos(direction),
                                y - 50 * sin(direction)
                            ),
                            ("top barrier", "right barrier", "bottom barrier", "left barrier")[direction],
                            arguments={"side": (1 - direction) % 4}
                        ))
                    self.add_button(self.make_text_button(
                        f"Gravity Locked: {not editing_barrier[1]}",
                        12,
                        switch_grav_lock_barriers,
                        (
                            construction_center,
                            y + 106
                        ),
                        border_width=5
                    ))  # 16 + len(BARRIER_LIST): grav lock
                self.add_button(self.make_img_button(
                    None,
                    draw_block(
                        Block("lol", []),
                        0,
                        self.fonts[scale],
                        scale=2
                    ),
                    (construction_center, y),
                    None
                ))  # 17 + len(BARRIERS): big barrier image
                self.add_button(None)  # 18 + len(BARRIERS): barrier name
                update_barrier_img()
            elif construction_pointer == 4:  # links setting
                for num, place in enumerate(["Remove", "Pick", "Place"]):
                    self.add_button(self.make_text_button(
                        place,
                        20,
                        switch_link_place,
                        (construction_center, 300 + 30 * num),
                        border_width=5,
                        arguments={"place": place}
                    ))  # 11:13 switch places buttons
                switch_link_place(editing_link[0])

        construction_pointer = 0

        # 8: construction area [nonstatic]
        self.add_button(None)
        # 9: construction area iter [nonstatic]
        self.add_button(self.make_text_button(
            "<",
            20,
            update_construction_area,
            center=(0, 0),
            y_align=0.5,
            border_width=5,
            arguments={"index_change": -1},
            special_press="Left"
        ))
        # 10: construction area iter [nonstatic]
        self.add_button(self.make_text_button(
            ">",
            20,
            update_construction_area,
            center=(0, 0),
            y_align=0.5,
            border_width=5,
            arguments={"index_change": 1},
            special_press="Right"
        ))
        # 11-> dynamic, construction area parts

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
            if construction_pointer == 0:  # players
                if click_tick and mouse_coords is not None:
                    if player_grabbed is not None and player_grabbed != mouse_coords:
                        if mouse_coords not in self.level_data.player_starts:
                            self.level_data.player_starts.append(mouse_coords)
                            self.add_button(Button(
                                grab_player,
                                scaled_player,
                                f"at {mouse_coords[0]}, {mouse_coords[1]}",
                                scaled_player.get_rect(center=(
                                    240 * 2 - self.level_display.get_width() / 2 - 20 + 40 * mouse_coords[0] + 1,
                                    180 * 2 + self.level_display.get_height() / 2 + 20 - 40 * mouse_coords[1] - 1
                                )),
                                inflate_center=(0.5, 0.5),
                                outline_width=0,
                                arguments={"coords": mouse_coords}
                            ))
                            update_game_image()
                            player_grabbed = None
            elif construction_pointer == 1:  # gravity (nothing should be done here)
                pass
            elif construction_pointer == 2:  # blocks case
                if click_tick and mouse_coords is not None:
                    if editing_block == "delete":
                        if mouse_coords in self.level_data.blocks:
                            if not self.level_data.blocks[mouse_coords].barriers:
                                del self.level_data.blocks[mouse_coords]
                            else:
                                self.level_data.blocks[mouse_coords].type = ""
                                self.level_data.blocks[mouse_coords].other = ()
                    else:
                        other = deepcopy(editing_block_fields[editing_block])

                        for block_prune_info in BLOCK_CONSTRUCTION[editing_block]:
                            for check_field, check_condition in block_prune_info[4]:
                                if editing_block_fields[editing_block][check_field] not in check_condition:
                                    del other[block_prune_info[0]]
                                    break
                        if mouse_coords in self.level_data.blocks:
                            self.level_data.blocks[mouse_coords].type = editing_block
                            self.level_data.blocks[mouse_coords].other = other
                        else:
                            self.level_data.blocks[mouse_coords] = Block(
                                editing_block,
                                [],
                                other
                            )
                    update_game_image()
            elif construction_pointer == 3:  # barriers case
                if click_tick and mouse_coords is not None:
                    if mouse_coords in self.level_data.blocks:
                        if editing_barrier[0] == "delete":
                            if len(self.level_data.blocks[mouse_coords].barriers) > 0:
                                del self.level_data.blocks[mouse_coords].barriers[-1]
                                update_game_image()
                        else:
                            for i in reversed(range(0, len(self.level_data.blocks[mouse_coords].barriers))):
                                if (self.level_data.blocks[mouse_coords].barriers[i][0] == editing_barrier[0] and
                                        self.level_data.blocks[mouse_coords].barriers[i][1] == editing_barrier[1]):
                                    self.level_data.blocks[mouse_coords].barriers.pop(i)
                            if True in editing_barrier[2]:
                                self.level_data.blocks[mouse_coords].barriers.append(
                                    (editing_barrier[0], editing_barrier[1], tuple(editing_barrier[2])))
                            update_game_image()
                    else:
                        if editing_barrier[0] != "delete" and True in editing_barrier[2]:
                            self.level_data.blocks[mouse_coords] = Block(
                                "",
                                [(editing_barrier[0], editing_barrier[1], tuple(editing_barrier[2]))]
                            )
                            update_game_image()
            elif construction_pointer == 4:  # links case
                if click_tick and mouse_coords is not None:
                    if editing_link[0] == "Remove":
                        for i in range(len(self.level_data.links)):
                            if mouse_coords in self.level_data.links[i]:
                                self.level_data.links[i].remove(mouse_coords)
                                update_game_image()
                                break
                    elif editing_link[0] == "Place":
                        for i in range(len(self.level_data.links)):
                            if mouse_coords in self.level_data.links[i]:
                                self.level_data.links[i].remove(mouse_coords)
                                break
                        if len(self.level_data.links) == editing_link[1]:
                            self.level_data.links.append([])
                        self.level_data.links[editing_link[1]].append(mouse_coords)
                        update_game_image()
                    elif editing_link[0] == "Pick":
                        for i in range(len(self.level_data.links)):
                            if mouse_coords in self.level_data.links[i]:
                                editing_link[1] = i
                                switch_link_place("Place")
                                break

            self.screen.blit(
                self.level_display,
                (240 * 2 - self.level_display.get_width() / 2, 180 * 2 - self.level_display.get_height() / 2)
            )
            # handle construction screen specific visual changes
            if construction_pointer == 0:  # players
                if player_grabbed is not None:
                    self.screen.blit(
                        scaled_player,
                        (mouse_pos[0] - 15, mouse_pos[1] - 15)
                    )
            elif construction_pointer == 1:  # gravity (nothing should be done here)
                pass
            elif construction_pointer == 2:  # blocks (drawing blocks hovered over the board should be done here)
                if mouse_coords is not None:
                    drawn = Block(
                        editing_block,
                        self.level_data.blocks.get(mouse_coords, Block("", [])).barriers,
                        copy(editing_block_fields[editing_block]),
                    )
                    for i in range(len(self.level_data.links)):
                        if mouse_coords in self.level_data.links[i]:
                            drawn.other["link"] = i
                            break
                    self.screen.blit(
                        draw_block(
                            drawn,
                            self.level_data.gravity[0],
                            self.fonts[40],
                            40
                        ),
                        (
                            240 * 2 - self.level_data.dimensions[0] * 20 + mouse_coords[0] * 40 - 40,
                            180 * 2 + self.level_data.dimensions[1] * 20 - mouse_coords[1] * 40
                        )
                    )
            elif construction_pointer == 3:  # barriers (drawing barriers hovered over the board should be done here)
                if mouse_coords is not None:
                    if editing_barrier[0] == "delete":
                        self.screen.blit(
                            draw_block(
                                Block(
                                    "delete",
                                    []
                                ),
                                self.level_data.gravity[0],
                                self.fonts[40],
                                40
                            ),
                            (
                                240 * 2 - self.level_data.dimensions[0] * 20 + mouse_coords[0] * 40 - 40,
                                180 * 2 + self.level_data.dimensions[1] * 20 - mouse_coords[1] * 40
                            )
                        )
                    else:
                        block = deepcopy(self.level_data.blocks.get(mouse_coords, Block("", [])))
                        for i in reversed(range(0, len(block.barriers))):
                            if (block.barriers[i][0] == editing_barrier[0] and
                                    block.barriers[i][1] == editing_barrier[1]):
                                block.barriers.pop(i)
                        block.barriers.append((editing_barrier[0], editing_barrier[1], tuple(editing_barrier[2])))
                        self.screen.blit(
                            draw_block(
                                block,
                                self.level_data.gravity[0],
                                self.fonts[40],
                                40
                            ),
                            (
                                240 * 2 - self.level_data.dimensions[0] * 20 + mouse_coords[0] * 40 - 40,
                                180 * 2 + self.level_data.dimensions[1] * 20 - mouse_coords[1] * 40
                            )
                        )
            elif construction_pointer == 4:
                if mouse_coords is not None:
                    if editing_link[0] == "Remove":
                        self.screen.blit(
                            draw_block(
                                Block(
                                    "delete",
                                    []
                                ),
                                self.level_data.gravity[0],
                                self.fonts[40],
                                40
                            ),
                            (
                                240 * 2 - self.level_data.dimensions[0] * 20 + mouse_coords[0] * 40 - 40,
                                180 * 2 + self.level_data.dimensions[1] * 20 - mouse_coords[1] * 40
                            )
                        )
                    elif editing_link[0] == "Place":
                        block = deepcopy(self.level_data.blocks.get(mouse_coords, Block("", [])))
                        if isinstance(block.other, tuple):
                            block.other = dict()
                        block.other["link"] = editing_link[1]
                        self.screen.blit(
                            draw_block(
                                block,
                                self.level_data.gravity[0],
                                self.fonts[40],
                                40
                            ),
                            (
                                240 * 2 - self.level_data.dimensions[0] * 20 + mouse_coords[0] * 40 - 40,
                                180 * 2 + self.level_data.dimensions[1] * 20 - mouse_coords[1] * 40
                            )
                        )
        self.level_data.name = self.button_names[2]
        save_current_editing()