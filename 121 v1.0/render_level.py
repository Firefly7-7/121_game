"""
module that draws the level based on level data
"""

from pygame.surface import Surface
from pygame.draw import line, lines, polygon, circle
from pygame.transform import smoothscale
from pygame.font import Font
from math import floor
from block_data import *
from typing import Union
from constants import BARRIER_COLORS


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


def draw_block(block: Block, gravity: int, font: Font, scale: int = 60) -> Surface:
    """
    draws a single block onto a surface
    :param block: block data
    :param gravity: integer for direction of gravity (0-3)
    :param font: font to write with
    :param scale: what size to use
    :return: drawn surface
    """
    res = block.type.render(block.other, gravity, font, scale)
    if res is None:
        res = Surface((scale, scale))
        res.fill((255, 255, 255))
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
        circle(res, (0, 0, 0), (scale / 4, scale / 4), scale / 16 + 1)
        circle(res, degree_to_rgb(block.other["link"] * 54), (scale / 4, scale / 4), scale / 16)
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