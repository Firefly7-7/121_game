"""
a module containing classes for various game structures
button
"""
from dataclasses import dataclass
from typing import Union, Callable, Any, Optional

from pygame.font import Font, SysFont
from pygame import Rect, Surface
from pygame.draw import rect
from pygame.mixer import music
from pygame.constants import USEREVENT


@dataclass()
class Button:
    """
    dataclass containing information for a button
    """
    click: Union[None, Callable]
    img: Surface
    text: str
    rect: Rect
    fill_color: Union[tuple[int, int, int], tuple[int, int, int, int], None] = None
    outline_color: Union[tuple[int, int, int], None] = None
    inflate_center: tuple[float, float] = (0.5, 0.5)
    outline_width: int = 1
    arguments: Union[None, dict[str, Any]] = None
    scale_factor: float = 1.25
    special_press: tuple = ()
    typing_instance: int = None


@dataclass()
class SpeakNode:
    """
    stop yelling at me
    """


@dataclass()
class SpeakNode:
    """
    holds a text message to speak
    """
    text: str
    next: Union[None, SpeakNode] = None


class QueueSpeech:
    """
    holds information for queued sounds for alerts
    """

    def __init__(self, speach: Callable):
        self.front = None
        self.back = None
        self.speach = speach
        self.speaking = False
        music.set_endevent(USEREVENT)
        # print("New Queuespeach instantiated")

    def add(self, text: str) -> None:
        """
        adds text to queue
        :param text:
        :return:
        """
        new = SpeakNode(text)
        if self.back is not None:
            self.back.next = new
        self.back = new

        # print(cls.front)
        if self.front is None:
            # print(f"saying {text}")
            self.front = self.back
            # print(cls.front)
            self.speak()

    def speak(self) -> None:
        """
        speaks
        :return:
        """
        # print("Speaking")
        self.speach(self.front.text)

    def next_speach(self) -> None:
        """
        goes to the next_
        :return:
        """
        # print("Next")
        if self.front is None:
            return
        self.front = self.front.next
        if self.front is None:
            self.back = None
        else:
            self.speak()


@dataclass()
class Alert:
    """"
    holds a single alert instance
    """


@dataclass()
class Alert:
    """
    holds a single alert instance
    """
    img: Surface
    last_tick: int
    height: int
    above: Union[Alert, None]
    y: int


class AlertHolder:
    """
    holds alerts for the game
    """

    def __init__(
            self,
            width: int,
            size: int,
            max_alerts: int,
            speed: int,
            speak: Callable,
            draw: Callable,
            border_buffer: int,
            lifespan: int
    ):
        self.text_size = size
        self.front_alert = None
        self.back_alert = None
        self.width = width
        self.max_alerts = max_alerts
        self.on_tick = 0
        self.decay = lifespan
        self.speed = speed
        self.speak = QueueSpeech(speak)
        self.draw = draw
        self.border_buffer = border_buffer

    def remove_last_alert(self) -> None:
        """
        removes the last/front alert from the queue
        :return:
        """
        self.front_alert = self.front_alert.above
        if self.front_alert is None:
            self.back_alert = None

    def add_alert(self, text: str, img: Surface = None) -> None:
        """
        adds an alert to the list
        :param text: text for the alert
        :param img: image that goes with display
        :return: None
        """
        if img is None:
            width = 0
            height = 0
        else:
            width, height = img.get_size()
            width += self.border_buffer
        self.speak.add(text)
        text_img = self.draw(
            text,
            self.text_size,
            max_line_pixels=self.width - width - self.border_buffer * 2,
            max_width=self.width - width - self.border_buffer * 2,
            text_align=0.5,
            max_lines=2,
            enforce_width=self.width - width - self.border_buffer * 2
        )
        height = max(height, text_img.get_height()) + self.border_buffer * 2
        surface = Surface((self.width, height))
        surface.fill((255, 255, 255))
        if img is not None:
            surface.blit(
                img,
                (self.border_buffer, self.border_buffer)
            )
        surface.blit(
            text_img,
            (self.border_buffer + width, self.border_buffer)
        )
        rect(
            surface,
            (0, 0, 0),
            Rect(
                (-1, -1),
                (self.width + 1, height + 1)
            ),
            round(self.border_buffer / 2)
        )
        alert = Alert(
            surface,
            self.on_tick + self.decay,
            height,
            None,
            -1 * height
        )
        if self.back_alert is not None:
            self.back_alert.y = 0
            self.back_alert.above = alert
        self.back_alert = alert
        if self.front_alert is None:
            self.front_alert = alert

    def tick(self) -> Union[Surface, None]:
        """
        ticks the alert system
        :return:
        """
        if self.front_alert is None:
            self.on_tick = 0
            return None
        self.on_tick += 1
        draw_queue = []
        boop = self.front_alert
        if self.on_tick >= boop.last_tick:
            boop.y -= self.speed
            if boop.y + boop.height < 0:
                self.remove_last_alert()
                boop = boop.above
                if boop is None:
                    self.on_tick = 0
                    return None
        i = 0
        while True:
            i += 1
            draw_queue.append((boop.img, boop.height, boop.y))
            if boop.above is None or i >= self.max_alerts:
                break
            else:
                boop = boop.above
        if not draw_queue:
            return None
        if self.on_tick < boop.last_tick:
            boop.y += self.speed
            if boop.y > 0:
                boop.y = 0
        height = 0
        for img, img_height, y in draw_queue:
            height += y + img_height
        surface = Surface((self.width, height))
        height = 0
        for img, img_height, y in reversed(draw_queue):
            height += y
            surface.blit(
                img,
                (0, height)
            )
            height += img_height
        return surface


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
    other: dict[int, Any] = ()
    link: Optional[int] = None


@dataclass()
class TypingData:
    """
    holds information about current typing target
    """
    typing: bool = False
    button_target: int = None
    text: str = ""
    instance: int = 0