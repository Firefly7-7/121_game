"""
module that draws the level based on level data
"""

from pygame.surface import Surface
from pygame.draw import line, lines, polygon, circle
from pygame.transform import smoothscale
from pygame.font import Font
from math import floor
from block_data import Block
from typing import Union
from constants import BLOCK_FILLS, BARRIER_COLORS


def draw_level(
        dimensions: tuple[int, int],
        gravity: tuple[int, float],
        blocks: dict[tuple[int, int], Block],
        links: list[list[tuple[int, int]]],
        players: list[tuple[Union[int, float], Union[int, float]]],
        player_img: Surface,
        font: Font,
        scale: int = 60
) -> Surface:
    """
    draws a level to a surface
    :param dimensions: dimension data
    :param gravity: gravity data, (direction, strength)
    :param blocks: block data to draw
    :param links: link data
    :param players: player data
    :param player_img: pygame surface player image
    :param font: font to write with
    :param scale: how big
    :return: a drawn surface to display
    """
    x, y = dimensions
    # print(dimensions)
    drawn = Surface((x * scale + floor(scale / 20), y * scale + floor(scale / 20)))
    drawn.fill((255, 255, 255))
    for coordinates, block in blocks.items():
        drawn.blit(
            draw_block(block, gravity[0], font, scale),
            ((coordinates[0] - 1) * scale, (y - coordinates[1]) * scale)
        )
        # print(coordinates)
    for i in range(x + 1):
        line(drawn, (0, 0, 0), (i * scale, 0), (i * scale, y * scale), floor(scale / 10))
    for i in range(y + 1):
        line(drawn, (0, 0, 0), (0, i * scale), (x * scale, i * scale), floor(scale / 10))
    player = smoothscale(player_img, (scale * 3 / 4, scale * 3 / 4))
    for px, py in players:
        drawn.blit(
            player,
            (
                (px - 30) * (scale / 30) - scale * 3 / 8 + floor(scale / 40),
                (360 - py) * (scale / 30) - scale * 3 / 8 + floor(scale / 40)
            )
        )
    return drawn


def sin(num: int) -> float:
    """
    gets a "sin" of an integer 0-3
    :param num: number to get sin of
    :return: -1, 0, 1
    """
    return num - 2 * max(num - 1, 0) + 2 * max(num - 3, 0)


def cos(num: int) -> float:
    """
    gets a "cos" of an integer
    :param num: number to get cos of
    :return: -1, 0, 1
    """
    return 1 - num + 2 * max(num - 2, 0)


def draw_arrow(
        block: Surface, direction: int, color: tuple[int, int, int], size: int
) -> None:
    """
    draws an arrow for a block
    :param block: block to draw on
    :param direction: direction to draw in (0 for up, 1 right, 2 down, 3 left)
    :param color: color of the arrow
    :param size: size of block to draw on
    :return: None (drawn directly onto the block)
    """
    line(
        block,
        color,
        (size / 2 + size / 4 * sin(direction), size / 2 - size / 4 * cos(direction)),
        (size / 2 - size / 4 * sin(direction), size / 2 + size / 4 * cos(direction)),
        round(size / 12)
    )
    lines(
        block,
        color,
        True,
        ((
             size / 2 + size / 8 * sin(direction) + size / 8 * cos(direction),
             size / 2 - size / 8 * cos(direction) - size / 8 * sin(direction)
         ), (
             size / 2 + size / 4 * sin(direction), size / 2 - size / 4 * cos(direction)
         ), (
             size / 2 + size / 8 * sin(direction) - size / 8 * cos(direction),
             size / 2 - size / 8 * cos(direction) + size / 8 * sin(direction)
         )),
        round(size / 12)
    )


def draw_block(block: Block, gravity: int, font: Font, scale: int = 60) -> Surface:
    """
    draws a single block onto a surface
    :param block: block data
    :param gravity: integer for direction of gravity (0-3)
    :param font: font to write with
    :param scale: what size to use
    :return: drawn surface
    """
    res = Surface((scale, scale))
    # back
    res.fill(BLOCK_FILLS.get(block.type, (255, 255, 255)))
    # arrow
    if "rotation" in block.other:
        # noinspection PyTypeChecker
        draw_arrow(
            res,
            (block.other["rotation"] - (1 - block.other["grav_locked"]) * gravity) % 4,
            tuple([(1 - block.other["grav_locked"]) * 255] * 3),
            scale
        )
    # block specific
    if block.type == "repel":
        if block.other["mode"] == 1:
            lines(
                res,
                (255, 255, 255),
                True,
                (
                    (scale / 2, scale / 4),
                    (scale * 3 / 4, scale / 2),
                    (scale / 2, scale * 3 / 4),
                    (scale / 4, scale / 2)
                ),
                round(scale / 6)
            )
        else:
            line(
                res,
                (255, 255, 255),
                (scale / 2, scale / 4),
                (scale / 2, scale * 3 / 4),
                round(scale / 6)
            )
            line(
                res,
                (255, 255, 255),
                (scale / 4, scale / 2),
                (scale * 3 / 4, scale / 2),
                round(scale / 12)
            )
    elif block.type == "gravity":
        if block.other["type"] == "set":
            res.blit(
                smoothscale(
                    font.render(
                        "=+-x/"[block.other["mode"]] + str(clean_decimal(block.other["value"])),
                        True,
                        (0, 0, 0),
                        None
                    ),
                    (scale * 3 / 4, scale * 3 / 4)
                ),
                (scale / 8, scale / 8)
            )
    elif block.type == "easter egg":
        lines(
            res,
            (255, 230, 0),
            True,
            ((scale / 2, scale / 4), (scale * 3 / 4, scale / 2), (scale / 2, scale * 3 / 4), (scale / 4, scale / 2)),
            round(scale / 6)
        )
    elif block.type == "activator":
        res.blit(
            smoothscale(
                font.render(
                    str(clean_decimal(block.other["delay"])),
                    True,
                    (128, 128, 128),
                    None
                ),
                (scale * 3 / 4, scale * 3 / 4)
            ),
            (scale / 8, scale / 8)
        )
    elif block.type == "coin":
        polygon(
            res,
            (128, 84, 0),
            ((scale / 2, scale / 4), (scale * 3 / 4, scale / 2), (scale / 2, scale * 3 / 4), (scale / 4, scale / 2)),
            0
        )
        polygon(
            res,
            (255, 168, 0),
            ((scale / 2, scale / 4), (scale * 3 / 4, scale / 2), (scale / 2, scale * 3 / 4), (scale / 4, scale / 2)),
            round(scale / 6)
        )
    elif block.type == "msg":
        res.blit(
            smoothscale(
                font.render(
                    "MSG",
                    True,
                    (128, 128, 128),
                    None
                ),
                (scale * 3 / 4, scale * 3 / 4)
            ),
            (scale / 8, scale / 8)
        )
    # barriers
    # if block.barriers:
    #     print(block.barriers)
    barrier_destination = ((scale, 0), (scale, scale), (0, scale), (0, 0))
    for barrier_type, grav_lock, barriers in block.barriers:
        for i in range(4):
            if barriers[i]:
                line(
                    res,
                    BARRIER_COLORS[barrier_type][grav_lock],
                    barrier_destination[i - 1 - grav_lock * gravity],
                    barrier_destination[i - grav_lock * gravity],
                    round(scale * 0.285)
                )
    # links
    if "link" in block.other:
        circle(res, degree_to_rgb(block.other["link"] * 54), (scale / 4, scale / 4), scale / 12)
    return res


def degree_to_rgb(hue: int) -> tuple[int, int, int]:
    """
    converts d hue at 100 saturation and value to rgb values
    :param hue: 0-360
    :return: RGB tuple
    """
    return (
        max(min(255, round(510 - 4.25 * hue)), 0, min(round(4.25 * hue - 1020), 255)),
        max(min(round(4.25 * hue), 255, round(1020 - 4.25 * hue)), 0),
        max(0, min(round(4.25 * hue - 510), 255, round(1530 - 4.25 * hue)))
    )


def clean_decimal(num: float) -> Union[int, float]:
    """
    cleans decimal points off a number
    :param num: float number
    :return: decimal points cleaned
    """
    if round(num) == num:
        return round(num)
    return num