"""
skins area, drawing skins, etc.
"""

from dataclasses import dataclass
from typing import Union, Literal
from pygame.surface import Surface
from pygame.draw import circle, lines, polygon, rect
from pygame.rect import Rect
from pygame import SRCALPHA
from pyperclip import copy


@dataclass()
class Instruction:
    """
    holds data for an individual instruction
    """
    type: Union[Literal["lines", "circle", "rect"], str]
    coords: list[tuple[int, int]]
    size: list[int]
    closed_filled: bool
    color: Union[tuple[int, int, int], tuple[int, int, int, int]]


@dataclass()
class Skin:
    """
    holds data for an individual skin
    """
    name: str
    transparent: bool
    fill: Union[tuple[int, int, int], tuple[int, int, int, int]]
    instructions: list[Instruction]


def draw_skin(skin: Skin) -> Surface:
    """
    draws a skin according to skin class passed in
    :param skin: skin dataclass
    :return: a drawn surface
    """
    surface = Surface((40, 40), flags=SRCALPHA * skin.transparent)
    surface.fill(skin.fill)
    for instruction in skin.instructions:
        if instruction.type == "lines":
            if instruction.closed_filled and len(instruction.coords) >= 3:
                polygon(surface, instruction.color, instruction.coords, instruction.size[0])
            else:
                lines(surface, instruction.color, instruction.closed_filled, instruction.coords, instruction.size[0])
        elif instruction.type == "circle":
            circle(surface, instruction.color, instruction.coords[0], instruction.size[0],
                   instruction.size[1] * (1 - instruction.closed_filled))
        elif instruction.type == "rect":
            rect(surface, instruction.color, Rect(
                instruction.coords[0],
                (instruction.coords[1][0] - instruction.coords[0][0],
                 instruction.coords[1][1] - instruction.coords[0][1])
            ), instruction.size[0])
    return surface


def tuple_to_hex(color: Union[tuple[int, int, int], tuple[int, int, int, int]]) -> str:
    """
    converts color tuple to a hex code
    :param color: color tuple (3 or 4 items)
    :return: string hex code
    """
    result = ["%02x" % c for c in color]
    return "".join(result)


def hex_to_tuple(color: str) -> Union[tuple[int, int, int], tuple[int, int, int, int], tuple[int, ...]]:
    """
    converts hex to color tuple
    :param color: color string
    :return: color tuple
    """
    res = list()
    for i in range(len(color) // 2):
        res.append(int(color[i * 2:i * 2 + 2], 16))
    return tuple(res)


def encode_skin(skin: Skin) -> str:
    """
    encodes skin to string representation
    :param skin: skin to save
    :return: string code
    """
    save = [
        skin.name,
        str(int(skin.transparent)),
        tuple_to_hex(skin.fill),
        "_".join([
            "/".join([
                ins.type,
                "*".join([str(x) + "+" + str(y) for x, y in ins.coords]),
                "*".join([str(size) for size in ins.size]),
                str(int(ins.closed_filled)),
                tuple_to_hex(ins.color)
            ])
            for ins in skin.instructions
        ])

    ]
    result = ",".join(save)
    return result


def decode_skin_safety_wrap(skin_string: str) -> Union[Skin, ValueError]:
    """
    wrap for decoding a skin
    :param skin_string: string encoded
    :return:
    """
    # noinspection PyBroadException
    try:
        return decode_skin(skin_string)
    except:
        return ValueError("Level string errored in decode.")


def decode_skin(skin_string: str) -> Skin:
    """
    decodes skin from a string
    :param skin_string:
    :return:
    """
    fields = skin_string.split(",")
    result = Skin(
        fields[0],
        bool(int(fields[1])),
        hex_to_tuple(fields[2]),
        []
    )
    if len(fields[3]) != 0:
        for instruction in fields[3].split("_"):
            instruction_fields = instruction.split("/")
            # noinspection PyTypeChecker
            result.instructions.append(Instruction(
                instruction_fields[0],
                [tuple(float(val) for val in coords.split("+")) for coords in instruction_fields[1].split("*")],
                [int(val) for val in instruction_fields[2].split("*")],
                bool(int(instruction_fields[3])),
                hex_to_tuple(instruction_fields[4])
            ))
    return result


if __name__ == "__main__":
    print(list(range(0, -3)))
    skin = Skin(
        "Pride",
        False,
        (255, 255, 255),
        [
            Instruction(
                "lines",
                [(0, 2), (40, 2)],
                [7],
                False,
                (228, 2, 3)
            ),
            Instruction(
                "lines",
                [(0, 9), (40, 9)],
                [7],
                False,
                (255, 139, 0)
            ),
            Instruction(
                "lines",
                [(0, 16), (40, 16)],
                [7],
                False,
                (254, 237, 0)
            ),
            Instruction(
                "lines",
                [(0, 23), (40, 23)],
                [7],
                False,
                (0, 128, 38)
            ),
            Instruction(
                "lines",
                [(0, 30), (40, 30)],
                [7],
                False,
                (0, 77, 255)
            ),
            Instruction(
                "lines",
                [(0, 37), (40, 37)],
                [7],
                False,
                (117, 6, 134)
            ),
        ]
    )
    str_skin = encode_skin(skin)
    print(str_skin)
    match = skin == decode_skin(str_skin)
    print(match)
    if match:
        print(f"Skin {skin.name} string copied to clipboard")
        copy(str_skin)
    else:
        print("Encode/decode did not match")
