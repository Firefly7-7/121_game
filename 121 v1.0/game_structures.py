"""
a module containing classes for various game structures
button
"""
from dataclasses import dataclass
from typing import Union, Callable, Any, Optional
from abc import ABC, abstractmethod

from pygame.font import Font, SysFont
from pygame.transform import scale
from pygame import Rect, Surface
from pygame.draw import rect
from pygame.mixer import music
from pygame.constants import USEREVENT


class ButtonHolderTemplate(ABC):
    """
    buttonholder abstract class
    """

    @abstractmethod
    def render_onto(self, onto: Surface, mouse_pos: tuple[int, int]) -> None:
        """
        draw onto a surface
        :return:
        """

    @abstractmethod
    def do_click(self, mouse_pos: tuple[int, int]) -> bool:
        """
        checks if mouse is on the button, and if so, recursively
        :return: whether or not to stop the check
        """

    @abstractmethod
    def do_key(self) -> bool:
        """
        checks if the holder is keyed, and if so, checks children
        :return: whether or not to stop the check
        """

    def special_key_click(self, key) -> None:
        """
        just runs it down all buttons if a key input triggered a special trigger
        :param key: what key to check for special presses
        :return:
        """

    @abstractmethod
    def iter_key(self) -> int:
        """
        if keyed, change to not keyed and return
        :return:
        0 = continue
        1 = stop and push to next
        2 = stop without pushing
        """

    @property
    @abstractmethod
    def keyed(self) -> bool:
        """
        if has been selected by special keyed button selection
        :return:
        """

    @abstractmethod
    def set_keyed(self) -> bool:
        """
        checks if possible to key, and does so if possible
        :return: if it could set to key
        """

    @abstractmethod
    def get_hover_keyed_text(self) -> Union[str, None]:
        """
        gets hover keyed text
        :return:
        """


class Button(ButtonHolderTemplate):
    """
    dataclass containing information for a button
    """

    def get_hover_keyed_text(self) -> Union[str, None]:
        """
        if keyed, return text, else None
        :return:
        """
        if self.keyed:
            return self.text
        return None

    @property
    def keyed(self):
        """
        if has been selected by special keyed button selection
        :return:
        """
        return self._keyed

    @keyed.setter
    def keyed(self, value):
        self._keyed = value

    def set_keyed(self) -> bool:
        """
        sets the button as keyed
        :return:
        """
        self.keyed = True
        return True

    def __init__(
            self,
            click: Union[None, Callable],
            img: Surface,
            text: str,
            _rect: Rect,
            fill_color: Union[tuple[int, int, int], tuple[int, int, int, int], None] = None,
            outline_color: Union[tuple[int, int, int], None] = None,
            inflate_center: tuple[float, float] = (0.5, 0.5),
            outline_width: int = 1,
            arguments: Union[None, dict[str, Any]] = None,
            scale_factor: float = 1.25,
            special_press: tuple = (),
            typing_instance: int = None
    ):
        """
        initialize a button
        :param click:
        :param img:
        :param text:
        :param _rect:
        :param fill_color:
        :param outline_color:
        :param inflate_center:
        :param outline_width:
        :param arguments:
        :param scale_factor:
        :param special_press:
        :param typing_instance:
        """
        self.click: Union[None, Callable] = click
        self.img: Surface = img
        self.text: str = text
        self.rect: Rect = _rect
        self.fill_color: Union[tuple[int, int, int], tuple[int, int, int, int], None] = fill_color
        self.outline_color: Union[tuple[int, int, int], None] = outline_color
        self.inflate_center: tuple[float, float] = inflate_center
        self.outline_width: int = outline_width
        self.arguments: Union[None, dict[str, Any]] = arguments
        self.scale_factor: float = scale_factor
        self.special_press: tuple = special_press
        self.typing_instance: int = typing_instance
        self.keyed = False

    @staticmethod
    def make_img_button(
            click: Union[None, callable],
            img: Surface,
            center: tuple[int, int],
            button_name: Union[str, None],
            inflate_center: tuple[float, float] = (0.5, 0.5),
            arguments: Union[None, dict[str, Any]] = None,
            scale_factor: float = 1.25,
            special_press: tuple = ()
    ):
        """
        creates a button with a given img provided as a surface
        :param click: click action
        :param img: image of button
        :param center: center of button
        :param button_name: text of the button
        :param inflate_center: where to inflate the button from
        :param arguments: click arguments
        :param scale_factor: how much the button inflates when moused over
        :param special_press: what controls can be used to press it
        :return: a formed button
        """
        return Button(
            click,
            img,
            button_name,
            img.get_rect(center=center),
            inflate_center=inflate_center,
            arguments=arguments,
            scale_factor=scale_factor,
            special_press=special_press,
            outline_width=0
        )

    def render_onto(self, onto: Surface, mouse_pos: tuple[int, int]) -> None:
        """
        draw onto a surface
        :return:
        """
        if self.click is not None and (self.rect.collidepoint(mouse_pos) or self.keyed):
            # mouse is over or keyed clicker is on

            # gets coordinates of button parts for scaling
            x, y = self.rect.topleft
            centerx, centery = self.rect.center
            width, height = centerx - x, centery - y
            new_centerx = centerx + width * (self.inflate_center[0] - 0.5) * -0.5
            new_centery = centery + height * (self.inflate_center[1] - 0.5) * -0.5

            new = scale(
                self.img,
                (width * 2 * self.scale_factor, height * 2 * self.scale_factor)
            )

            onto.blit(
                new,
                (new_centerx - width * self.scale_factor, new_centery - height * self.scale_factor)
            )
            if self.outline_width > 0:
                rect(
                    onto,
                    self.outline_color,
                    new.get_rect(center=(new_centerx, new_centery)).inflate(
                        1.75 * self.outline_width,
                        1.75 * self.outline_width
                    ),
                    width=self.outline_width
                )
        else:
            # not over
            onto.blit(self.img, self.rect)
            if self.outline_width > 0:
                rect(
                    onto,
                    self.outline_color,
                    self.rect.inflate(2 * self.outline_width, 2 * self.outline_width),
                    width=self.outline_width
                )

    def run_click(self) -> bool:
        """
        runs click event
        :return: if event occurred
        """
        if self.click is None:
            return False
        if self.arguments is None:
            self.click()
        else:
            self.click(**self.arguments)
        return True

    def do_click(self, mouse_pos: tuple[int, int]) -> bool:
        """
        checks if mouse is on the button when mouse button is pressed, and if so, recursively
        :return:
        """
        if self.rect.collidepoint(mouse_pos):
            return self.run_click()
        return False

    def do_key(self) -> bool:
        """
        checks if button is keyed, and if so, does click
        :return:
        """
        if self.keyed:
            self.run_click()
        return self.keyed

    def special_key_click(self, key) -> None:
        """
        ahhhh
        :return:
        """
        if isinstance(self.special_press, int):
            special_pressed = key == self.special_press
        else:
            special_pressed = key in self.special_press
        if special_pressed:
            self.run_click()

    def iter_key(self) -> int:
        """
        iterates which button is currently keyed
        :return:
        0 = continue
        1 = stop and push to next
        2 = stop without pushing
        """
        if self.keyed:
            self.keyed = False
            return 1
        return 0


class ButtonHolder(ButtonHolderTemplate):
    """
    holds a list of buttons or button holders
    """

    def get_hover_keyed_text(self) -> Union[str, None]:
        """
        if hover key is inside here, check for text to get it
        :return:
        """
        if self.keyed:
            for button in self.list:
                if button is None:
                    continue
                res = button.get_hover_keyed_text()
                if res is not None:
                    return res
        return None

    @property
    def keyed(self):
        """
        if has been selected by special keyed button selection
        :return:
        """
        return self._keyed

    def set_keyed(self, ) -> bool:
        """
        checks if can set as keyed based on children
        :return:
        """
        if not self.list:
            return False
        for button in self.list:
            if button.set_keyed():
                self.keyed = True
                return True
        return False

    def __init__(
            self,
            init_list: list[ButtonHolderTemplate] = None,
            background: Surface = None,
            _rect: Rect = None,
            fill_color: Union[tuple[int, int, int], tuple[int, int, int, int], None] = None,
            outline_color: Union[tuple[int, int, int], None] = None,
            outline_width: int = 0,
    ):
        """
        initializes
        """
        self.list = init_list
        if self.list is None:
            self.list = list()
        self.background = background
        self.rect = _rect
        self.fill_color = fill_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.keyed = False

    def adjust_mouse_pos(self, mouse_pos: tuple[int, int]) -> tuple[int, int]:
        """
        adjust mouse position passed based on the holder's rect
        :param mouse_pos:
        :return:
        """
        if self.rect is not None:
            return mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y
        return mouse_pos

    def render_onto(self, onto: Surface, mouse_pos: tuple[int, int]) -> None:
        """
        draws onto a surface
        :param onto:
        :param mouse_pos:
        :return:
        """
        mouse_pos = self.adjust_mouse_pos(mouse_pos)
        if self.background is None:
            for button in self.list:
                if button is None:
                    continue
                button.render_onto(onto, mouse_pos)
        else:
            self.background.fill(self.fill_color)
            for button in self.list:
                if button is None:
                    continue
                button.render_onto(self.background, mouse_pos)
            onto.blit(self.background, self.rect)
            if self.outline_width > 0:
                rect(
                    onto,
                    self.outline_color,
                    self.rect.inflate(2 * self.outline_width, 2 * self.outline_width),
                    width=self.outline_width
                )

    def do_click(self, mouse_pos: tuple[int, int]) -> bool:
        """
        checks if mouse is on the button when mouse button is pressed, and if so, recursively
        :return:
        """
        mouse_pos = self.adjust_mouse_pos(mouse_pos)
        if self.rect is None:
            click = True
        elif self.rect.collidepoint(mouse_pos):
            click = True
        else:
            return False
        if click:
            for button in self.list:
                if button is None:
                    continue
                if button.do_click(mouse_pos):
                    return True
        return False

    def do_key(self) -> bool:
        """
        presses special action key for keyed action selection (not special key press)
        :return:
        """
        if not self.keyed:
            return False
        for button in self.list:
            if button is None:
                continue
            if button.do_key():
                return True
        return True

    def special_key_click(self, key) -> None:
        """
        passes key press down the line
        :param key:
        :return:
        """
        for button in self.list:
            if button is None:
                continue
            button.special_key_click(key)

    def iter_key(self) -> int:
        """
        if keyed, push what
        :return:
        0 = continue
        1 = stop and push to next
        2 = stop without pushing
        """
        if not self.keyed:
            return 0
        res = 0
        for button in self.list:
            if button is None:
                continue
            match res:
                case 0:
                    res = button.iter_key()
                case 1:
                    if button.set_keyed():
                        return 2
                case 2:
                    return 2
        return res

    @keyed.setter
    def keyed(self, value):
        self._keyed = value

    def add_button(self, button: ButtonHolderTemplate):
        """
        adds a button to the list
        :param button:
        :return:
        """
        self.list.append(button)

    def __getitem__(self, index):
        return self.list[index]

    def __setitem__(self, index, value):
        if isinstance(self.list[index], ButtonHolder):
            keyed = self.list[index].keyed
        else:
            keyed = False
        self.list[index] = value
        if keyed:
            self.list[index].set_keyed()

    def __setslice__(self, i, j, sequence):
        self.list[i:j] = sequence

    def __delitem__(self, index):
        del self.list[index]

    def __delslice__(self, i, j):
        del self.list[i:j]

    def clear(self):
        """
        clears list
        :return:
        """
        self.list.clear()

    def __len__(self):
        return len(self.list)


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
    button_target: Button = None
    text: str = ""
    instance: int = 0