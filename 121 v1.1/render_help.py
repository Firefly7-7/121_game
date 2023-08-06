"""
helps with certain functions for drawing
"""


from pygame.surface import Surface
from pygame.draw import line, lines, polygon
from typing import Union


def sin(num: int) -> int:
    """
    gets a "sin" of an integer 0-3
    :param num: number to get sin of
    :return: -1, 0, 1
    """
    return num - 2 * max(num - 1, 0) + 2 * max(num - 3, 0)


def cos(num: int) -> int:
    """
    gets a "cos" of an integer
    :param num: number to get cos of
    :return: -1, 0, 1
    """
    return 1 - num + 2 * max(num - 2, 0)


def draw_arrow(
        block: Surface, direction: int, color: tuple[int, int, int], size: int, bars: int = 1
) -> None:
    """
    draws an arrow for a block
    :param block: block to draw on
    :param direction: direction to draw in (0 for up, 1 right, 2 down, 3 left)
    :param color: color of the arrow
    :param size: size of block to draw on
    :param bars: how many bars should the arrow have?
    :return: None (drawn directly onto the block)
    """
    for i in range(bars):
        offset = 3 * (i - bars / 2 + 0.5) * (size - 7.5) / 8 / bars
        line(
            block,
            color,
            (  # head side
                size / 2 + 2 * size / 16 * sin(direction) - offset * cos(direction),
                size / 2 - 2 * size / 16 * cos(direction) - offset * sin(direction)
            ),
            (  # butt side
                size / 2 - size / 4 * sin(direction) - offset * cos(direction),
                size / 2 + size / 4 * cos(direction) - offset * sin(direction)
            ),
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
    polygon(
        block,
        color,
        ((
             size / 2 + size / 8 * sin(direction) + size / 8 * cos(direction),
             size / 2 - size / 8 * cos(direction) - size / 8 * sin(direction)
         ), (
             size / 2 + size / 4 * sin(direction), size / 2 - size / 4 * cos(direction)
         ), (
             size / 2 + size / 8 * sin(direction) - size / 8 * cos(direction),
             size / 2 - size / 8 * cos(direction) + size / 8 * sin(direction)
         )),
        0
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