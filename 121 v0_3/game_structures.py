"""
a module containing classes for various game structures
button
"""
from dataclasses import dataclass
from typing import Union, Callable, Any

from pygame.font import Font, SysFont
from pygame import Rect, Surface


@dataclass()
class Button:
    """
    dataclass containing information for a button
    """
    click: Union[None, Callable]
    img: Surface
    text: str
    rect: Rect
    fill_color: Union[tuple[int, int, int], tuple[int, int, int, int], None]
    outline_color: tuple[int, int, int]
    inflate_center: tuple[float, float]
    outline_width: int = 1
    arguments: Union[None, dict[str, Any]] = None
    scale_factor: float = 1.25
    special_press: tuple = ()


class FontHolder:
    """
    class to hold required fonts dynamically
    """

    def __init__(self, name: str) -> None:
        self.fonts = dict()
        self.font_name = name

    def new_fonts(self, name) -> None:
        """
        change font in the holder
        :param name: name of new font
        :return: None
        """
        self.font_name = name
        self.fonts.clear()

    def __getitem__(self, key: Union[int, float]) -> Font:
        """
        gets item from holder
        :param key: size to look for
        :return: Font object
        """
        if key not in self.fonts.keys():
            self.fonts[key] = SysFont(self.font_name, int(key))
        return self.fonts[key]


@dataclass()
class ControlOption:
    """
    a control option for the control menu
    """
    name: str
    value: Any
    typ: str
    button_index: int = None
    args: Union[list[Any], None] = None
    dependent: Union[tuple[int, Any], None] = None


@dataclass(frozen=True)
class Collision:
    """
    holds information for a collision
    assumes that it is in a dictionary and type is already known
    """
    direction: int
    local: bool = False
    coordinates: tuple[int, int] = ()
    other: dict[str, Any] = ()