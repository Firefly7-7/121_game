"""
a bunch of classes defining different construction areas in the construction screen
"""

from abc import ABC, abstractmethod
from game_structures import ButtonHolder, Button
from level_data import LevelWrap
from typing import Callable
from pygame.transform import smoothscale, rotate
from typing import Union
from render_help import clean_decimal, draw_arrow, cos, sin, degree_to_rgb
from pygame.draw import circle
from pygame import Surface
from constants import BLOCK_LIST, BLOCK_CONSTRUCTION, BUTTON_COUNT, FieldType, BARRIERS
from block_data import Block, BlockType, Blocks
from math import ceil
from copy import copy, deepcopy


class ParentConstructionArea(ABC):
    """
    abstract class detailing requirements for a construction area to implement
    """

    buttons = ButtonHolder()
    name_buttons = ButtonHolder()
    update_display: Callable = None
    display_width: int = None
    construction_center: int = None
    game_object = None
    construction_areas_available = list()
    construction_area_pointer = 0

    total_width = 200
    per_line = 7
    scale = 22
    line_spacing = total_width // per_line

    @property
    @staticmethod
    def game_object():
        return ParentConstructionArea._game_object

    @property
    @staticmethod
    @abstractmethod
    def name():
        pass

    @staticmethod
    @game_object.setter
    def game_object(value):
        ParentConstructionArea._game_object = value

    @staticmethod
    def register_areas(lst: list):
        ParentConstructionArea.construction_areas_available.clear()
        ParentConstructionArea.construction_areas_available.extend(lst)

    @classmethod
    def single_time_prepare(cls, update_level_display: Callable, game_object) -> ButtonHolder:
        """
        sets single time prepare things
        :return:
        """
        ParentConstructionArea.update_display = update_level_display
        ParentConstructionArea.display_width = game_object.level_display.get_width()
        ParentConstructionArea.construction_center = round(240 * 3 + ParentConstructionArea.display_width / 4)
        ParentConstructionArea.game_object = game_object

        ParentConstructionArea.name_buttons.clear()
        ParentConstructionArea.name_buttons.add_button(None)
        # 6.0.1-2: construction area iter buttons
        ParentConstructionArea.name_buttons.add_button(ParentConstructionArea.game_object.make_text_button(
            "<",
            20,
            ParentConstructionArea.update_construction_area,
            center=(0, 0),
            y_align=0.5,
            border_width=5,
            arguments={"index_change": -1},
            special_press="Left"
        ))
        ParentConstructionArea.name_buttons.add_button(ParentConstructionArea.game_object.make_text_button(
            ">",
            20,
            ParentConstructionArea.update_construction_area,
            center=(0, 0),
            y_align=0.5,
            border_width=5,
            arguments={"index_change": 1},
            special_press="Right"
        ))

        for cl in cls.__subclasses__():
            cl.single_time_prep(game_object)
        total = ButtonHolder()
        total.add_button(ParentConstructionArea.name_buttons)
        total.add_button(ParentConstructionArea.buttons)
        return total

    @classmethod
    def single_time_prep(cls, game_object):
        """
        single time prep for
        :param game_object:
        :return:
        """
        pass

    @staticmethod
    def update_construction_area(index_change: int) -> None:
        """
        changes construction space
        :return: none
        """
        ParentConstructionArea.construction_area_pointer = (ParentConstructionArea.construction_area_pointer + index_change) % len(ParentConstructionArea.construction_areas_available)
        ParentConstructionArea.buttons.clear()
        if not isinstance(ParentConstructionArea.game_object.level_data, LevelWrap):
            return
        ParentConstructionArea.name_buttons[0] = ParentConstructionArea.game_object.make_text_button(
            ParentConstructionArea.construction_areas_available[ParentConstructionArea.construction_area_pointer].name,
            30,
            None,
            (240 * 3 + ParentConstructionArea.game_object.level_display.get_width() / 4, 140),
            y_align=0.5,
            border_width=5
        )
        width = ParentConstructionArea.name_buttons[0].rect.width / 2
        display_width = ParentConstructionArea.game_object.level_display.get_width()
        ParentConstructionArea.name_buttons[1].rect.center = (240 * 3 + display_width / 4 - 20 - width, 140)
        ParentConstructionArea.name_buttons[2].rect.center = (240 * 3 + display_width / 4 + 20 + width, 140)
        if ParentConstructionArea.game_object.typing.typing and ParentConstructionArea.game_object.typing.button_target not in ParentConstructionArea.game_object.buttons:
            ParentConstructionArea.game_object.end_typing()
        ParentConstructionArea.construction_areas_available[ParentConstructionArea.construction_area_pointer].update_construction_area()

    @staticmethod
    def click_tick(mouse_coords: tuple[int, int]) -> None:
        """
        runs when clicking on level display with that construction screen on
        :param mouse_coords:
        :return:
        """
        if ParentConstructionArea.construction_areas_available[ParentConstructionArea.construction_area_pointer].click_tick is not ParentConstructionArea.click_tick:
            ParentConstructionArea.construction_areas_available[ParentConstructionArea.construction_area_pointer].click_tick(mouse_coords)

    @staticmethod
    def tick(mouse_pos: tuple[int, int], mouse_coords: tuple[int, int]) -> None:
        """
        every tick does something (if overridden)
        :param mouse_pos:
        :param mouse_coords:
        :return:
        """
        if ParentConstructionArea.construction_areas_available[
            ParentConstructionArea.construction_area_pointer].tick is not ParentConstructionArea.tick:
            ParentConstructionArea.construction_areas_available[
                ParentConstructionArea.construction_area_pointer].tick(mouse_pos, mouse_coords)


class PlayerEditing(ParentConstructionArea):
    """
    edit players
    """

    name = "Players"

    player_grabbed = False

    @staticmethod
    def grab_player() -> None:
        """
        grabs a player, either from new player space or from game screen
        :return: None
        """
        PlayerEditing.player_grabbed = not PlayerEditing.player_grabbed
        # if coords is None:
        #     PlayerEditing.player_grabbed = True
        # else:
        #     PlayerEditing.player_grabbed = coords
        #     # print(coords)
        #     # print(cls.level_data.player_starts)
        #     ParentConstructionArea.game_object.level_data.level_on.player_starts.remove(coords)
        #     ParentConstructionArea.update_display()
        #     button = 1
        #     while True:
        #         if PlayerEditing.buttons[button].arguments["coords"] is coords:
        #             del PlayerEditing.buttons[button]
        #             break
        #         button += 1

    player_imgs = None
    scaled_player = None

    @classmethod
    def single_time_prep(cls, game_object):
        """
        gets player images
        :param game_object:
        :return:
        """
        PlayerEditing.scaled_player = smoothscale(game_object.player_img, (30, 30))
        PlayerEditing.player_imgs = tuple(rotate(PlayerEditing.scaled_player, 90 * i) for i in range(4))

    @staticmethod
    def update_construction_area() -> None:
        PlayerEditing.buttons.add_button(Button.make_img_button(
            PlayerEditing.grab_player,
            PlayerEditing.player_imgs[ParentConstructionArea.game_object.level_data.level_on.gravity[0]],
            (ParentConstructionArea.construction_center, 200),
            "new player"
        ))

    @staticmethod
    def click_tick(mouse_coords: tuple[int, int]) -> None:
        if PlayerEditing.player_grabbed:
            if mouse_coords in ParentConstructionArea.game_object.level_data.level_on.player_starts:
                ParentConstructionArea.game_object.level_data.level_on.player_starts.remove(mouse_coords)
            else:
                ParentConstructionArea.game_object.level_data.level_on.player_starts.append(mouse_coords)
            PlayerEditing.update_display()

    @staticmethod
    def tick(mouse_pos: tuple[int, int], mouse_coords):
        """
        draws player if player grabbed
        :param mouse_pos:
        :param mouse_coords:
        :return:
        """
        if PlayerEditing.player_grabbed:
            ParentConstructionArea.game_object.screen.blit(
                PlayerEditing.scaled_player,
                (mouse_pos[0] - 15, mouse_pos[1] - 15)
            )


class GravityEditing(ParentConstructionArea):
    """
    gravity editor
    """

    name = "Gravity"

    @staticmethod
    def change_gravity(index: int, change: Union[float, int]) -> None:
        """
        changes a gravity setting
        :param index: index to change at (0 is dir, 1 is strength)
        :param change: how much to change it by
        :return: None
        """
        grav = list(GravityEditing.game_object.level_data.level_on.gravity)
        grav[index] = clean_decimal(
            (1 - 2 * index) * (
                    ((1 - 2 * index) * GravityEditing.game_object.level_data.level_on.gravity[index] + change) % (4 - 1.25 * index))
        )
        GravityEditing.game_object.level_data.level_on.gravity = grav
        GravityEditing.update_display()
        GravityEditing.buttons.clear()
        GravityEditing.update_construction_area()

    @staticmethod
    def update_construction_area() -> None:
        arrow = Surface((60, 60))
        arrow.fill((255, 255, 255))
        draw_arrow(arrow, (2 - GravityEditing.game_object.level_data.level_on.gravity[0]) % 4, (0, 0, 0), 60)
        GravityEditing.buttons.add_button(Button.make_img_button(
            None,
            arrow,
            (GravityEditing.construction_center, 200),
            f"Gravity is pointing {('down', 'right', 'up', 'left')[GravityEditing.game_object.level_data.level_on.gravity[0]]} with strength "
            f"{GravityEditing.game_object.level_data.level_on.gravity[1]}."
        ))
        GravityEditing.buttons.add_button(GravityEditing.game_object.make_text_button(
            f"Strength: {-1 * GravityEditing.game_object.level_data.level_on.gravity[1]}",
            16,
            None,
            (GravityEditing.construction_center, 260),
            border_width=5
        ))
        width = GravityEditing.buttons[-1].rect.width / 2 + 20
        if GravityEditing.game_object.level_data.level_on.gravity[1] >= 0:
            GravityEditing.buttons.add_button(None)
        else:
            GravityEditing.buttons.add_button(GravityEditing.game_object.make_text_button(
                "-",
                16,
                GravityEditing.change_gravity,
                (GravityEditing.construction_center - width, 260),
                border_width=5,
                arguments={"index": 1, "change": -0.25}
            ))
        if GravityEditing.game_object.level_data.level_on.gravity[1] <= -2.5:
            GravityEditing.buttons.add_button(None)
        else:
            GravityEditing.buttons.add_button(GravityEditing.game_object.make_text_button(
                "+",
                16,
                GravityEditing.change_gravity,
                (GravityEditing.construction_center + width, 260),
                border_width=5,
                arguments={"index": 1, "change": 0.25}
            ))
        GravityEditing.buttons.add_button(GravityEditing.game_object.make_text_button(
            f"Direction: {('down', 'right', 'up', 'left')[GravityEditing.game_object.level_data.level_on.gravity[0]]}",
            16,
            None,
            (GravityEditing.construction_center, 300),
            border_width=5
        ))
        width = GravityEditing.buttons[-1].rect.width / 2 + 20
        GravityEditing.buttons.add_button(GravityEditing.game_object.make_text_button(
            "<",
            16,
            GravityEditing.change_gravity,
            (GravityEditing.construction_center - width, 300),
            border_width=5,
            arguments={"index": 0, "change": 1}
        ))
        GravityEditing.buttons.add_button(GravityEditing.game_object.make_text_button(
            ">",
            16,
            GravityEditing.change_gravity,
            (GravityEditing.construction_center + width, 300),
            border_width=5,
            arguments={"index": 0, "change": -1}
        ))


class BlockEditing(ParentConstructionArea):
    """
    edit blocks in the level
    """

    name = "Blocks"

    editing_block: BlockType = Blocks.delete
    editing_block_fields = dict()
    for block_name, field_list in BLOCK_CONSTRUCTION.items():
        editing_block_fields[block_name] = []
        for field_index, display, field_type, default, *etc in field_list:
            while len(editing_block_fields[block_name]) <= field_index:
                editing_block_fields[block_name].append(None)
            editing_block_fields[block_name][field_index] = default

    @staticmethod
    def update_construction_area() -> None:
        select_blocks = ButtonHolder()
        for construction_i, construction_block in enumerate(BLOCK_LIST):
            select_blocks.add_button(Button.make_img_button(
                BlockEditing.switch_construction_block,
                BlockEditing.game_object.level_data.draw_block(
                    Block(
                        construction_block,
                        [],
                        BlockEditing.editing_block_fields[construction_block]
                    ),
                    ParentConstructionArea.game_object.fonts[BlockEditing.scale],
                    BlockEditing.scale
                ),
                (
                    BlockEditing.construction_center + round(
                        construction_i % BlockEditing.per_line - BlockEditing.per_line / 2 + 0.5
                    ) * BlockEditing.line_spacing,
                    round(165 + (construction_i // BlockEditing.per_line + 0.5) * BlockEditing.line_spacing)
                ),
                construction_block.name,
                arguments={"block_name_switch": construction_block}
            ))
        BlockEditing.buttons.add_button(select_blocks)
        on_block_buttons = ButtonHolder()
        on_block_buttons_base = ButtonHolder()
        on_block_buttons_base.add_button(None)  # name
        on_block_buttons_base.add_button(None)  # img
        on_block_buttons_base.add_button(None)  # description
        on_block_buttons.add_button(on_block_buttons_base)  # 1.0: name, img, desc
        on_block_buttons.add_button(ButtonHolder())  # 1.1: fields
        BlockEditing.buttons.add_button(on_block_buttons)
        BlockEditing.switch_construction_block(BlockEditing.editing_block)

    @staticmethod
    def switch_construction_block(block_name_switch: BlockType) -> None:
        """
        switches the construction_block used
        :param block_name_switch:
        :return:
        """
        if ParentConstructionArea.game_object.typing.typing and ParentConstructionArea.game_object.typing.button_target in BlockEditing.buttons[1][1]:
            ParentConstructionArea.game_object.end_typing()
        BlockEditing.editing_block = block_name_switch
        BlockEditing.buttons[1][0][0] = ParentConstructionArea.game_object.make_text_button(
            BlockEditing.editing_block.name,
            30,
            None,
            (
                ParentConstructionArea.construction_center,
                0
            ),
            max_line_pixels=256,
            max_width=256,
            text_align=0.5
        )
        BlockEditing.buttons[1][0][2] = ParentConstructionArea.game_object.make_text_button(
            BlockEditing.editing_block.description,
            10,
            None,
            (
                ParentConstructionArea.construction_center,
                0
            ),
            y_align=0,
            max_line_pixels=200
        )
        BlockEditing.prep_construction_control_buttons()
        BlockEditing.update_construction_control_buttons()

    @staticmethod
    def prep_construction_control_buttons() -> None:
        """
        preps the buttons list with empty buttons
        :return: None
        """
        BlockEditing.buttons[1][1].clear()
        for field in BLOCK_CONSTRUCTION[BlockEditing.editing_block]:
            BlockEditing.buttons[1][1].add_button(ButtonHolder())

    @staticmethod
    def update_construction_control_buttons() -> None:
        """
        updates display of the control buttons
        :return:
        """
        BlockEditing.buttons[0][BLOCK_LIST.index(BlockEditing.editing_block)] = Button.make_img_button(
            BlockEditing.switch_construction_block,
            ParentConstructionArea.game_object.level_data.draw_block(
                Block(
                    BlockEditing.editing_block,
                    [],
                    BlockEditing.editing_block_fields[BlockEditing.editing_block]
                ),
                ParentConstructionArea.game_object.fonts[BlockEditing.scale],
                BlockEditing.scale
            ),
            (
                round(ParentConstructionArea.construction_center + (
                        BLOCK_LIST.index(BlockEditing.editing_block) % BlockEditing.per_line - BlockEditing.per_line / 2 + 0.5) * BlockEditing.line_spacing),
                round(165 + (BLOCK_LIST.index(BlockEditing.editing_block) // BlockEditing.per_line + 0.5) * BlockEditing.line_spacing)
            ),
            BlockEditing.editing_block.name,
            arguments={"block_name_switch": BlockEditing.editing_block}
        )

        y = (180 + ceil(len(BLOCK_LIST) / BlockEditing.per_line) * BlockEditing.line_spacing)
        round(260 + ceil(len(BLOCK_LIST) / BlockEditing.per_line) * BlockEditing.line_spacing)

        BlockEditing.buttons[1][0][0].rect.y = y

        y += BlockEditing.buttons[1][0][0].img.get_height()

        block_img = ParentConstructionArea.game_object.level_data.draw_block(
            Block(
                BlockEditing.editing_block,
                [],
                BlockEditing.editing_block_fields[BlockEditing.editing_block]
            ),
            ParentConstructionArea.game_object.fonts[60],
            60
        )

        y += block_img.get_height() / 2

        BlockEditing.buttons[1][0][1] = Button.make_img_button(
            None,
            block_img,
            (
                ParentConstructionArea.construction_center,
                y
            ),
            None,
        )

        y += block_img.get_height() / 2

        BlockEditing.buttons[1][0][2].rect.top = y

        y += BlockEditing.buttons[1][0][2].rect.height + 12

        field_buttons = BlockEditing.buttons[1][1]

        field_index = -1
        for field_name, display_name, field_type, default, conditional, *args in BLOCK_CONSTRUCTION[BlockEditing.editing_block]:
            field_index += 1
            value = BlockEditing.editing_block_fields[BlockEditing.editing_block][field_name]
            on_field: ButtonHolder = field_buttons[field_index]
            on_field.clear()
            place_field = True
            for field, condition in conditional:
                if BlockEditing.editing_block_fields[BlockEditing.editing_block][field] not in condition:
                    place_field = False
                    break
            if not place_field:
                continue
            if field_type == FieldType.boolean:
                if len(args) > 0:
                    display = args[0][value]
                else:
                    display = value
                on_field.add_button(ParentConstructionArea.game_object.make_text_button(
                    f"{display_name}: {display}",
                    12,
                    BlockEditing.change_field,
                    (
                        ParentConstructionArea.construction_center,
                        y - 7
                    ),
                    border_width=5,
                    y_align=0,
                    arguments={"field": field_name, "field_index": field_index},
                    max_width=256
                ))
                on_field[0].inflate_center = (0.5, 0.5)
                y += 6 + on_field[0].rect.height
            elif field_type == FieldType.iterator:
                if len(args) > 3:
                    display = args[3][round((value - args[0]) / args[2])]
                else:
                    display = value
                button = ParentConstructionArea.game_object.make_text_button(
                    f"{display_name}: {display}",
                    12,
                    None,
                    (
                        ParentConstructionArea.construction_center,
                        y - 7
                    ),
                    max_line_pixels=BlockEditing.total_width,
                    y_align=0,
                    border_width=5,
                )
                button.inflate_center = (0.5, 0.5)
                offset = round(button.img.get_width() / 2 + 20)
                on_field.add_button(button)
                on_field.add_button(ParentConstructionArea.game_object.make_text_button(
                    "<",
                    12,
                    BlockEditing.change_field,
                    (
                        ParentConstructionArea.construction_center - offset,
                        y
                    ),
                    border_width=5,
                    arguments={"field": field_name, "field_index": field_index, "direction": -1}
                ))
                on_field.add_button(ParentConstructionArea.game_object.make_text_button(
                    ">",
                    12,
                    BlockEditing.change_field,
                    (
                        ParentConstructionArea.construction_center + offset,
                        y
                    ),
                    border_width=5,
                    arguments={"field": field_name, "field_index": field_index, "direction": 1}
                ))
                y += 6 + max(on_field[0].rect.height, on_field[2].rect.height)
            elif field_type == FieldType.list:
                if len(args) > 1:
                    display = args[1][value]
                else:
                    display = value
                on_field.add_button(ParentConstructionArea.game_object.make_text_button(
                    f"{display_name}: {display}",
                    12,
                    BlockEditing.change_field,
                    (
                        ParentConstructionArea.construction_center,
                        y - 7
                    ),
                    y_align=0,
                    border_width=5,
                    max_line_pixels=BlockEditing.total_width,
                    arguments={"field": field_name, "field_index": field_index}
                ))
                on_field[0].inflate_center = (0.5, 0.5)
                y += 6 + on_field[0].rect.height
            elif field_type == FieldType.text:
                on_field.add_button(ParentConstructionArea.game_object.make_text_button(
                    f"{display_name}: {value}",
                    12,
                    BlockEditing.change_field,
                    (
                        ParentConstructionArea.construction_center,
                        y - 7
                    ),
                    border_width=5,
                    max_line_pixels=BlockEditing.total_width,
                    y_align=0,
                    arguments={"field": field_name, "field_index": field_index}
                ))
                on_field[0].inflate_center = (0.5, 0.5)
                y += on_field[0].rect.height + 6

    @staticmethod
    def change_field(field: str, field_index: int, **kwargs) -> None:
        """
        changes field value
        :param field: field to change
        :param field_index: index of field in BLOCK_CONSTRUCTION
        :param kwargs: field to catch named fields not required for all items
        :return: None
        """
        field_name, display_name, field_type, default, conditional, *args = BLOCK_CONSTRUCTION[BlockEditing.editing_block][
            field_index]
        if field_type == FieldType.boolean:
            BlockEditing.editing_block_fields[BlockEditing.editing_block][field] = not BlockEditing.editing_block_fields[BlockEditing.editing_block][field]
        if field_type == FieldType.iterator:
            BlockEditing.editing_block_fields[BlockEditing.editing_block][field] = args[0] + (
                    BlockEditing.editing_block_fields[BlockEditing.editing_block][field] + kwargs["direction"] * args[2] - args[0]
            ) % (args[1] - args[0])
        if field_type == FieldType.list:
            BlockEditing.editing_block_fields[BlockEditing.editing_block][field] = args[0][
                (args[0].index(BlockEditing.editing_block_fields[BlockEditing.editing_block][field]) + 1) % len(args[0])
                ]
        if field_type == FieldType.text:
            set_block = BlockEditing.editing_block

            others = []

            x, y = BlockEditing.buttons[1][1][field_index][0].rect.midtop

            for button_holder in BlockEditing.buttons[1][1][field_index + 1:]:
                for button in button_holder:
                    others.append((
                        button[0], 0, 1,
                        button.rect.centerx - x,
                        button.rect.centery - y - BlockEditing.buttons[1][1][field_index][0].rect.height
                    ))

            def save_text_field(result: str) -> None:
                """
                used to save typing result
                :param result: string result from typing
                :return:
                """
                BlockEditing.editing_block_fields[set_block][field] = result

            ParentConstructionArea.game_object.write_button_text(
                BlockEditing.buttons[1][1][field_index][0],
                12,
                max_characters=args[1],
                min_characters=args[0],
                max_line_pixels=200,
                prepend=f"{display_name}: ",
                start_text=BlockEditing.editing_block_fields[set_block][field],
                callback=save_text_field,
                y_align=0,
                others=others
            )
            return
        BlockEditing.update_construction_control_buttons()

    @staticmethod
    def click_tick(mouse_coords: tuple[int, int]) -> None:
        if BlockEditing.editing_block is Blocks.delete:
            if mouse_coords in ParentConstructionArea.game_object.level_data.level_on.blocks:
                if not ParentConstructionArea.game_object.level_data.level_on.blocks[mouse_coords].barriers and ParentConstructionArea.game_object.level_data.level_on.blocks[mouse_coords].link is None:
                    del ParentConstructionArea.game_object.level_data.level_on.blocks[mouse_coords]
                else:
                    ParentConstructionArea.game_object.level_data.level_on.blocks[mouse_coords].type = Blocks.air
        else:
            other = deepcopy(BlockEditing.editing_block_fields[BlockEditing.editing_block])

            for block_prune_info in BLOCK_CONSTRUCTION[BlockEditing.editing_block]:
                for check_field, check_condition in block_prune_info[4]:
                    if BlockEditing.editing_block_fields[BlockEditing.editing_block][check_field] not in check_condition:
                        if len(other) > block_prune_info[0]:
                            other[block_prune_info[0]] = None
                        break
            if mouse_coords in ParentConstructionArea.game_object.level_data.level_on.blocks:
                ParentConstructionArea.game_object.level_data.level_on.blocks[mouse_coords].type = BlockEditing.editing_block
                ParentConstructionArea.game_object.level_data.level_on.blocks[mouse_coords].other = other
            else:
                ParentConstructionArea.game_object.level_data.level_on.blocks[mouse_coords] = Block(
                    BlockEditing.editing_block,
                    [],
                    other
                )
        ParentConstructionArea.update_display()

    @staticmethod
    def tick(mouse_pos: tuple[int, int], mouse_coords: tuple[int, int]) -> None:
        if mouse_coords is not None:
            drawn = Block(
                BlockEditing.editing_block,
                ParentConstructionArea.game_object.level_data.level_on.blocks.get(mouse_coords, Block(Blocks.air, [])).barriers,
                copy(BlockEditing.editing_block_fields[BlockEditing.editing_block]),
            )
            for i in range(len(ParentConstructionArea.game_object.level_data.level_on.links)):
                if mouse_coords in ParentConstructionArea.game_object.level_data.level_on.links[i]:
                    drawn.link = i
                    break
            ParentConstructionArea.game_object.screen.blit(
                ParentConstructionArea.game_object.level_data.draw_block(
                    drawn,
                    ParentConstructionArea.game_object.fonts[40],
                    40
                ),
                (
                    240 * 2 - 11 * 20 + mouse_coords[0] * 40 - 40,
                    180 * 2 + 11 * 20 - mouse_coords[1] * 40
                )
            )


class BarrierEditing(ParentConstructionArea):
    """
    for editing barriers
    """

    name = "Barriers"

    editing_barrier: list[BlockType, bool, list[bool]] = [Blocks.delete, False, [True, True, True, True]]

    @staticmethod
    def update_construction_area() -> None:
        barrier_select_buttons = ButtonHolder()
        BarrierEditing.buttons.add_button(barrier_select_buttons)
        barrier_select_buttons.add_button(Button.make_img_button(
            BarrierEditing.switch_construction_barrier,
            BarrierEditing.game_object.level_data.draw_block(
                Block(
                    Blocks.delete,
                    []
                ),
                BarrierEditing.game_object.fonts[BarrierEditing.scale],
                BarrierEditing.scale
            ),
            (
                BarrierEditing.construction_center + round(0 % BarrierEditing.per_line - BarrierEditing.per_line / 2 + 0.5) * BarrierEditing.line_spacing,
                round(165 + (0 // BarrierEditing.per_line + 0.5) * BarrierEditing.line_spacing)
            ),
            Blocks.delete,
            arguments={"barrier": Blocks.delete}
        ))  # 0.0: delete option
        y = 245 + ceil(len(BARRIERS) / BarrierEditing.per_line) * BarrierEditing.line_spacing
        for construction_i, barrier in enumerate(BARRIERS):  # 0.1:len(BARRIERS): barriers
            barrier_select_buttons.add_button(Button.make_img_button(
                BarrierEditing.switch_construction_barrier,
                BarrierEditing.game_object.level_data.draw_block(
                    Block(
                        Blocks.air,
                        [(barrier, BarrierEditing.editing_barrier[1], (True, True, True, True))]
                    ),
                    BarrierEditing.game_object.fonts[BarrierEditing.scale],
                    BarrierEditing.scale
                ),
                (
                    BarrierEditing.construction_center + round(
                        (
                                construction_i + 1) % BarrierEditing.per_line - BarrierEditing.per_line / 2 + 0.5) * BarrierEditing.line_spacing,
                    round(165 + ((construction_i + 1) // BarrierEditing.per_line + 0.5) * BarrierEditing.line_spacing)
                ),
                barrier.name,
                arguments={"barrier": barrier}
            ))
        barrier_side_buttons = ButtonHolder()  # 1...: change side values of barrier
        BarrierEditing.buttons.add_button(barrier_side_buttons)
        if BarrierEditing.editing_barrier[0] == Blocks.delete:
            for direction in range(0, 4):
                barrier_side_buttons.add_button(None)
            BarrierEditing.buttons.add_button(None)  # 2: grav lock
        else:
            for direction in range(0, 4):
                barrier_side_buttons.add_button(Button.make_img_button(
                    BarrierEditing.update_barrier_side,
                    BarrierEditing.game_object.level_data.draw_block(
                        Block(
                            Blocks.air,
                            [(Blocks.ground, False, (True, True, True, True))]
                        ),
                        BarrierEditing.game_object.fonts[BarrierEditing.scale],
                        scale=16
                    ),
                    (
                        BarrierEditing.construction_center + 50 * cos(direction),
                        y - 50 * sin(direction)
                    ),
                    ("top barrier", "right barrier", "bottom barrier", "left barrier")[direction],
                    arguments={"side": (1 - direction) % 4}
                ))
            BarrierEditing.buttons.add_button(BarrierEditing.game_object.make_text_button(
                f"Gravity Locked: {not BarrierEditing.editing_barrier[1]}",
                12,
                BarrierEditing.switch_grav_lock_barriers,
                (
                    BarrierEditing.construction_center,
                    y + 106
                ),
                border_width=5
            ))  # 2: grav lock
        BarrierEditing.buttons.add_button(Button.make_img_button(
            None,
            BarrierEditing.game_object.level_data.draw_block(
                Block(Blocks.air, []),
                BarrierEditing.game_object.fonts[BarrierEditing.scale],
                scale=2
            ),
            (BarrierEditing.construction_center, y),
            None
        ))  # 3: big barrier image
        BarrierEditing.buttons.add_button(None)  # 4: barrier name
        BarrierEditing.update_barrier_img()

    @staticmethod
    def switch_construction_barrier(barrier: str) -> None:
        """
        switches construction barrier type
        :param barrier: barrier type to switch to
        :return: none
        """
        reinitialize = barrier == Blocks.delete or BarrierEditing.editing_barrier[0] == Blocks.delete
        BarrierEditing.editing_barrier[0] = barrier
        if reinitialize:
            BarrierEditing.update_construction_area()
        else:
            BarrierEditing.update_barrier_img()

    @staticmethod
    def update_barrier_img() -> None:
        """
        updates big barrier image to new value in editing_barrier[0]
        :return: nothing
        """
        if BarrierEditing.editing_barrier[0] == Blocks.delete:
            BarrierEditing.buttons[3].img = BarrierEditing.game_object.level_data.draw_block(
                Block(
                    Blocks.delete,
                    []
                ),
                BarrierEditing.game_object.fonts[10],
                80
            )
        else:
            BarrierEditing.buttons[3].img = BarrierEditing.game_object.level_data.draw_block(
                Block(
                    Blocks.air,
                    [(BarrierEditing.editing_barrier[0], BarrierEditing.editing_barrier[1], tuple(BarrierEditing.editing_barrier[2]))]
                ),
                BarrierEditing.game_object.fonts[10],
                80
            )
        BarrierEditing.buttons[3].rect = BarrierEditing.buttons[3].img.get_rect(
            center=BarrierEditing.buttons[3].rect.center)
        BarrierEditing.buttons[4] = BarrierEditing.game_object.make_text_button(
            BarrierEditing.editing_barrier[0].name,
            20,
            None,
            (
                BarrierEditing.construction_center,
                BarrierEditing.buttons[3].rect.y + 120
            ),
            border_width=5
        )

    @staticmethod
    def update_barrier_side(side: int) -> None:
        """
        updates a barrier's side
        :param side:
        :return: None
        """
        BarrierEditing.editing_barrier[2][side] = not BarrierEditing.editing_barrier[2][side]
        BarrierEditing.update_barrier_img()

    @staticmethod
    def switch_grav_lock_barriers() -> None:
        """
        switches grav lock for the barriers and updates area to reflect it
        :return: None
        """
        BarrierEditing.editing_barrier[1] = not BarrierEditing.editing_barrier[1]
        BarrierEditing.update_construction_area()

    @staticmethod
    def tick(mouse_pos: tuple[int, int], mouse_coords: tuple[int, int]) -> None:
        if mouse_coords is not None:
            if BarrierEditing.editing_barrier[0] == Blocks.delete:
                BarrierEditing.game_object.screen.blit(
                    BarrierEditing.game_object.level_data.draw_block(
                        Block(
                            Blocks.delete,
                            []
                        ),
                        BarrierEditing.game_object.fonts[40],
                        40
                    ),
                    (
                        240 * 2 - 11 * 20 + mouse_coords[0] * 40 - 40,
                        180 * 2 + 11 * 20 - mouse_coords[1] * 40
                    )
                )
            else:
                block = deepcopy(BarrierEditing.game_object.level_data.level_on.blocks.get(mouse_coords, Block(Blocks.air, [])))
                for i in reversed(range(0, len(block.barriers))):
                    if (block.barriers[i][0] == BarrierEditing.editing_barrier[0] and
                            block.barriers[i][1] == BarrierEditing.editing_barrier[1]):
                        block.barriers.pop(i)
                block.barriers.append((BarrierEditing.editing_barrier[0], BarrierEditing.editing_barrier[1], tuple(BarrierEditing.editing_barrier[2])))
                BarrierEditing.game_object.screen.blit(
                    BarrierEditing.game_object.level_data.draw_block(
                        block,
                        BarrierEditing.game_object.fonts[40],
                        40
                    ),
                    (
                        240 * 2 - 11 * 20 + mouse_coords[0] * 40 - 40,
                        180 * 2 + 11 * 20 - mouse_coords[1] * 40
                    )
                )

    @staticmethod
    def click_tick(mouse_coords: tuple[int, int]) -> None:
        if mouse_coords in BarrierEditing.game_object.level_data.level_on.blocks:
            if BarrierEditing.editing_barrier[0] is Blocks.delete:
                if len(BarrierEditing.game_object.level_data.level_on.blocks[mouse_coords].barriers) > 0:
                    del BarrierEditing.game_object.level_data.level_on.blocks[mouse_coords].barriers[-1]
                    BarrierEditing.update_display()
            else:
                for i in reversed(range(0, len(BarrierEditing.game_object.level_data.level_on.blocks[mouse_coords].barriers))):
                    if (BarrierEditing.game_object.level_data.level_on.blocks[mouse_coords].barriers[i][0] is BarrierEditing.editing_barrier[0] and
                            BarrierEditing.game_object.level_data.level_on.blocks[mouse_coords].barriers[i][1] is BarrierEditing.editing_barrier[1]):
                        BarrierEditing.game_object.level_data.level_on.blocks[mouse_coords].barriers.pop(i)
                if True in BarrierEditing.editing_barrier[2]:
                    BarrierEditing.game_object.level_data.level_on.blocks[mouse_coords].barriers.append(
                        (BarrierEditing.editing_barrier[0], BarrierEditing.editing_barrier[1], tuple(BarrierEditing.editing_barrier[2])))
                BarrierEditing.update_display()
        else:
            if BarrierEditing.editing_barrier[0] is not Blocks.delete and True in BarrierEditing.editing_barrier[2]:
                BarrierEditing.game_object.level_data.level_on.blocks[mouse_coords] = Block(
                    Blocks.air,
                    [(BarrierEditing.editing_barrier[0], BarrierEditing.editing_barrier[1], tuple(BarrierEditing.editing_barrier[2]))]
                )
                BarrierEditing.update_display()


class LinkEditing(ParentConstructionArea):
    """
    edit links (the video game character, obviously)
    """

    name = "Links"

    editing_link = ["Place", 0]

    @staticmethod
    def update_construction_area() -> None:
        for num, place in enumerate(["Remove", "Pick", "Place"]):
            LinkEditing.buttons.add_button(LinkEditing.game_object.make_text_button(
                place,
                20,
                LinkEditing.switch_link_place,
                (LinkEditing.construction_center, 300 + 30 * num),
                border_width=5,
                arguments={"place": place}
            ))  # 0:2 switch places buttons
        LinkEditing.switch_link_place(LinkEditing.editing_link[0])

    @staticmethod
    def switch_link_place(place: str) -> None:
        """
        switches link place to given value
        :param place: the place/setting to change to
        :return: None
        """
        LinkEditing.editing_link[0] = place
        del LinkEditing.buttons[3:]
        if place == "Place":
            LinkEditing.buttons.add_button(LinkEditing.game_object.make_text_button(
                f"Link # {LinkEditing.editing_link[1] + 1}",
                20,
                None,
                (LinkEditing.construction_center, 180),
                border_width=5
            ))  # 3: link num display
            img = Surface((60, 60))
            img.fill((255, 255, 255))
            circle(img, degree_to_rgb(LinkEditing.editing_link[1] * 54), (30, 30), 30)
            LinkEditing.buttons.add_button(Button.make_img_button(
                None,
                img,
                (LinkEditing.construction_center, 235),
                None
            ))  # 4: link img display
            LinkEditing.buttons.add_button(LinkEditing.game_object.make_text_button(
                "-",
                16,
                LinkEditing.change_link_number,
                (LinkEditing.construction_center - 50, 235),
                border_width=5,
                arguments={"change": -1}
            ))  # 5: link num -
            LinkEditing.buttons.add_button(LinkEditing.game_object.make_text_button(
                "+",
                16,
                LinkEditing.change_link_number,
                (LinkEditing.construction_center + 50, 235),
                border_width=5,
                arguments={"change": 1}
            ))  # 6: link num +
        elif place == "Pick":
            LinkEditing.buttons.add_button(LinkEditing.game_object.make_text_button(
                "?",
                100,
                None,
                (LinkEditing.construction_center, 222),
                override_text="pick mode"
            ))  # 3: pick mode indicator
        elif place == "Remove":
            LinkEditing.buttons.add_button(Button.make_img_button(
                None,
                LinkEditing.game_object.level_data.draw_block(Block(Blocks.delete, []), LinkEditing.game_object.fonts[60], 100),
                (LinkEditing.construction_center, 222),
                "delete mode"
            ))  # 3: remove mode indicator

    @staticmethod
    def change_link_number(change: int) -> None:
        """
        changes link number up or down
        :param change: what to change the link number by
        :return: None
        """
        LinkEditing.editing_link[1] = (LinkEditing.editing_link[1] + change) % (len(LinkEditing.game_object.level_data.level_on.links) + 1)
        if LinkEditing.editing_link[1] == len(LinkEditing.game_object.level_data.level_on.links):
            if not LinkEditing.game_object.level_data.level_on.links[-1]:
                if change > 0:
                    LinkEditing.editing_link[1] = 0
                else:
                    LinkEditing.editing_link[1] = len(LinkEditing.game_object.level_data.level_on.links) - 1
            else:
                LinkEditing.game_object.level_data.level_on.links.append([])
        if len(LinkEditing.game_object.level_data.level_on.links) > LinkEditing.editing_link[1] + 1 and not LinkEditing.game_object.level_data.level_on.links[LinkEditing.editing_link[1]]:
            while len(LinkEditing.game_object.level_data.level_on.links) > LinkEditing.editing_link[1] + 1 and not LinkEditing.game_object.level_data.level_on.links[
                LinkEditing.editing_link[1]]:
                del LinkEditing.game_object.level_data.level_on.links[LinkEditing.editing_link[1]]
                LinkEditing.editing_link[1] = (LinkEditing.editing_link[1] + change) % len(LinkEditing.game_object.level_data.level_on.links)
            LinkEditing.update_display()
        LinkEditing.buttons[3] = LinkEditing.game_object.make_text_button(
            f"Link # {LinkEditing.editing_link[1] + 1}",
            20,
            None,
            (LinkEditing.construction_center, 180),
            border_width=5
        )
        img = Surface((60, 60))
        img.fill((255, 255, 255))
        circle(img, degree_to_rgb(LinkEditing.editing_link[1] * 54), (30, 30), 30)
        LinkEditing.buttons[4] = Button.make_img_button(
            None,
            img,
            (LinkEditing.construction_center, 235),
            None
        )

    @staticmethod
    def click_tick(mouse_coords: tuple[int, int]) -> None:
        if LinkEditing.editing_link[0] == "Remove":
            for i in range(len(LinkEditing.game_object.level_data.level_on.links)):
                if mouse_coords in LinkEditing.game_object.level_data.level_on.links[i]:
                    LinkEditing.game_object.level_data.level_on.links[i].remove(mouse_coords)
                    LinkEditing.update_display()
                    break
        elif LinkEditing.editing_link[0] == "Place":
            for i in range(len(LinkEditing.game_object.level_data.level_on.links)):
                if mouse_coords in LinkEditing.game_object.level_data.level_on.links[i]:
                    LinkEditing.game_object.level_data.level_on.links[i].remove(mouse_coords)
                    break
            if len(LinkEditing.game_object.level_data.level_on.links) == LinkEditing.editing_link[1]:
                LinkEditing.game_object.level_data.level_on.links.append([])
            LinkEditing.game_object.level_data.level_on.links[LinkEditing.editing_link[1]].append(mouse_coords)
            LinkEditing.update_display()
        elif LinkEditing.editing_link[0] == "Pick":
            for i in range(len(LinkEditing.game_object.level_data.level_on.links)):
                if mouse_coords in LinkEditing.game_object.level_data.level_on.links[i]:
                    LinkEditing.editing_link[1] = i
                    LinkEditing.switch_link_place("Place")
                    break

    @staticmethod
    def tick(mouse_pos: tuple[int, int], mouse_coords: tuple[int, int]) -> None:
        if mouse_coords is not None:
            if LinkEditing.editing_link[0] == "Remove":
                LinkEditing.game_object.screen.blit(
                    LinkEditing.game_object.level_data.draw_block(
                        Block(
                            Blocks.delete,
                            []
                        ),
                        LinkEditing.game_object.fonts[40],
                        40
                    ),
                    (
                        240 * 2 - 11 * 20 + mouse_coords[0] * 40 - 40,
                        180 * 2 + 11 * 20 - mouse_coords[1] * 40
                    )
                )
            elif LinkEditing.editing_link[0] == "Place":
                block = deepcopy(LinkEditing.game_object.level_data.level_on.blocks.get(mouse_coords, Block(Blocks.air, [])))
                if isinstance(block.other, tuple):
                    block.other = dict()
                block.link = LinkEditing.editing_link[1]
                LinkEditing.game_object.screen.blit(
                    LinkEditing.game_object.level_data.draw_block(
                        block,
                        LinkEditing.game_object.fonts[40],
                        40
                    ),
                    (
                        240 * 2 - 11 * 20 + mouse_coords[0] * 40 - 40,
                        180 * 2 + 11 * 20 - mouse_coords[1] * 40
                    )
                )