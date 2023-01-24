"""
utility super-class
"""

import pygame
from game_structures import Button
from typing import Callable, Union, Any
from game_structures import ControlOption, FontHolder
from player_data import PlayerData
from os.path import exists
from os import listdir
from pickle import load, dump

# noinspection IncorrectFormatting
LEVEL_LIST = ("Baby Crawl", "Jump!", "Leap", "Danger!", "The Needle", "Gravity!", "Double Jump", "I Believe I can Fly", "Barriers", "Tap and Tap Again", "Sliding", "Hot Feet", "Gravity Collider", "Loop de loop", "Weird Jump", "Flip Flop", "The End...")


class Utility:
    """
    utility superclass.  Also the initialization function
    """

    def __init__(self) -> None:
        """
        loads player data and sets up the game with correct lists
        """

        self.buttons = list()
        self.button_names = list()
        self.button_hover_keyed = None
        self.button_hover_key = pygame.K_TAB

        if exists("player_data.pkl"):
            with open("player_data.pkl", "rb") as file:
                player_data = load(file)
        else:
            player_data = PlayerData(0, list(), list(), list(), dict())
        i = 0
        player_levels = {lvl[0] for lvl in player_data.level_list}
        easter_egg_levels = {c_lvl[:-4] for c_lvl in listdir("easter_eggs")}
        for lvl in LEVEL_LIST:
            if lvl in player_levels:
                while player_data.level_list[i][0] in easter_egg_levels:
                    i += 1
                if lvl != player_data.level_list[i][0]:
                    player_data.level_list.insert(i, (lvl, False))  # lvl name, completed
            else:
                player_data.level_list.insert(i, (lvl, False))  # lvl name, completed
            i += 1
        print(player_data.level_list)

        self.easter_eggs = player_data.easter_eggs

        self.level_display = None
        self.level_on = player_data.level_on
        self.levels = (player_data.level_list, [(c_lvl[:-4], False) for c_lvl in listdir("custom_levels")])
        self.level_data = None
        self.look_at = [min(len(self.levels[0]) - 1, self.level_on), 0]
        self.custom = 0
        self.after_game = None

        self.constructing = 0
        self.working_on = player_data.working_on

        self.player_img = pygame.surface.Surface((40, 40))
        self.player_img.fill((255, 255, 255))
        pygame.draw.rect(self.player_img, (0, 0, 0), pygame.rect.Rect(-1, -1, 41, 41), 6)

        # controls setup

        def add_control(
                name: str,
                default: Any,
                typ: str,
                args: Union[tuple[int, Any], None] = None,
                dependent: Union[tuple[int, Any], None] = None
        ) -> None:
            """
            adds control to controls list with default, type, args
            :param name: name of control
            :param default: default value of control
            :param typ: type of control
            :param args: any additional arguments needed for the option type
            :param dependent: what it is dependent on
            :return:
            """
            val = player_data.controls.get(name, default)
            self.controls.append(ControlOption(
                name,
                val,
                typ,
                args=args,
                dependent=dependent
            ))

        self.controls = []

        add_control("Jump", pygame.K_UP, "key")
        add_control("Right", pygame.K_RIGHT, "key")
        add_control("Left", pygame.K_LEFT, "key")
        add_control("Back", pygame.K_b, "key")
        add_control("Play", pygame.K_p, "key")
        add_control("Reset", pygame.K_r, "key")

        pygame.init()

        self.screen = pygame.display.set_mode(size=(240 * 4, 180 * 4))
        pygame.display.set_caption("121")

        self.clock = pygame.time.Clock()

        # pygame.font.init()
        self.fonts = FontHolder(pygame.font.get_fonts()[0])

        self.place = "start"

        self.pressed = pygame.key.get_pressed()

        self.running = True

        self.name = "121"

    def tick(self) -> None:
        """
        function that handles game clock and frame rate
        also handles some other actions that need to happen every frame
        :return: None
        """
        pygame.display.flip()
        self.clock.tick(60)
        self.screen.fill((255, 255, 255))
        self.pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.place = "ended"
                controls = dict()
                for control in self.controls:
                    controls[control.name] = control.value
                player = PlayerData(
                    self.level_on,
                    self.levels[0],
                    self.easter_eggs,
                    self.working_on,
                    controls
                )
                with open("player_data.pkl", "wb") as file:
                    dump(player, file)
                return

    def change_place(self, place) -> None:
        """
        here so that buttons make you able to change places
        :param place: new place
        :return: None
        """
        if place == "enter_level":
            self.after_game = self.place
        self.place = place

    def add_button(self, button: Union[Button, None]) -> None:
        """
        adds a button to the double list
        :param button: button to add
        :return: none
        """
        self.buttons.append(button)
        if button is None:
            self.button_names.append(None)
        else:
            self.button_names.append(button.text)

    def replace_button(self, index: int, button: Union[Button, None]) -> None:
        """
        replaces a button in the double list
        :param index: index to replace at
        :param button: button to change to
        :return:
        """
        self.buttons[index] = button
        if button is None:
            self.button_names[index] = None
        else:
            self.button_names[index] = button.text

    def make_text_button(
            self,
            text: str,
            font: pygame.font.Font,
            click: Union[Callable, None],
            center: tuple[int, int],
            background_color: Union[tuple[int, int, int], None] = (255, 255, 255),
            outline_color: tuple[int, int, int] = (0, 0, 0),
            border_width: int = 0,
            max_line_pixels: int = 0,
            max_line_words: int = 0,
            preserve_words: bool = True,
            text_align: float = 0,
            x_align: float = 0.5,
            y_align: float = 0.5,
            arguments: dict[str, Any] = None,
            special_press: Union[tuple[str], str] = ()
    ) -> Button:
        """
        creates a button object and adds it to handled list
        :param text: string
        :param font: font object to write the text in
        :param click: function called when the button is clicked
        :param center: coordinate centers of the button
        :param background_color: background color for the text
        :param outline_color: color used for text and border
        :param border_width: width of border for button
        :param max_line_pixels: maximum number of pixels in a line, 0 for disabled
        :param max_line_words: maximum number of words in a line, 0 for disabled
        :param preserve_words: whether or not to preserve words when considering max line pixels
        :param text_align: left (0) to right (1) alignment of text
        :param x_align: where the x value of 'center' is relative to the button, left (0), right (1).  Default center
        :param y_align: where the y value of 'center' is relative to the button, top (0), bottom (1).  Default center
        :param arguments: arguments to be used in the click action
        :param special_press: special keys that press button
        :return: a constructed button to be added to the list
        """
        text_surface = self.draw_text(
            text,
            font,
            background_color,
            outline_color,
            max_line_pixels,
            max_line_words,
            preserve_words,
            text_align
        )
        x, y = text_surface.get_size()
        if isinstance(special_press, str):
            special = self.get_special_click(special_press)
        else:
            special = tuple([self.get_special_click(name) for name in special_press])
        return Button(
            click,
            text_surface,
            text,
            pygame.Rect(center[0] - x_align * x, center[1] - y_align * y, x, y),
            background_color,
            outline_color,
            (x_align, y_align),
            border_width,
            arguments=arguments,
            special_press=special
        )

    @staticmethod
    def draw_text(
            text: str,
            font: pygame.font.Font,
            background_color: Union[tuple[int, int, int], None] = (255, 255, 255),
            outline_color: tuple[int, int, int] = (0, 0, 0),
            max_line_pixels: int = 0,
            max_line_words: int = 0,
            preserve_words: bool = True,
            text_align: float = 0
    ) -> pygame.surface.Surface:
        """
        draws text
        :param text: string
        :param font: font object to write the text in
        :param background_color: background color for the text
        :param outline_color: color used for text and border
        :param max_line_pixels: maximum number of pixels in a line, 0 for disabled
        :param max_line_words: maximum number of words in a line, 0 for disabled
        :param preserve_words: whether or not to preserve words when considering max line pixels
        :param text_align: left (0) to right (1) alignment of text
        :return: drawn text
        """
        lines = [""]
        word = ""
        words = 0
        for char in text + " ":
            if char == " ":
                if lines[-1] == "":
                    lines[-1] = word
                elif preserve_words and max_line_pixels > 0:
                    length = font.size(lines[-1] + " " + word)[0]
                    if length > max_line_pixels:
                        lines.append(word)
                        words = 0
                    else:
                        lines[-1] += " " + word
                else:
                    lines[-1] += " " + word
                word = ""
                words += 1
                if words >= max_line_words > 0:
                    words = 0
                    lines.append("")
            else:
                if not preserve_words and max_line_pixels > 0:
                    if lines[-1] != "":
                        length = font.size(word + char)[0]
                    else:
                        length = font.size(lines[-1] + " " + word + char)[0]
                    if length > max_line_pixels:
                        lines[-1] += word
                        lines.append("")
                        word = ""
                        words = 0
                word += char
        max_length = 0
        for i in range(len(lines)):
            lines[i] = font.render(lines[i], True, outline_color, background_color)
            max_length = max(max_length, lines[i].get_width())
        linesize = font.get_linesize()
        text_surface = pygame.Surface((max_length, linesize * len(lines)))
        if background_color is not None:
            text_surface.fill(background_color)
        for i in range(len(lines)):
            text_surface.blit(lines[i], (text_align * (max_length - lines[i].get_width()), i * linesize))
        return text_surface

    def handle_buttons(self) -> None:
        """
        engine to handle all buttons
        :return: none
        """
        keyed_pressed = False
        down = pygame.display.get_active() and pygame.mouse.get_pressed()[0]
        pos = pygame.mouse.get_pos()
        for i in range(len(self.buttons)):
            if self.buttons[i] is not None:
                self.handle_button(
                    self.buttons[i],
                    down,
                    self.buttons[i].rect.collidepoint(pos),
                    i == self.button_hover_keyed,
                    keyed_pressed
                )

    def handle_button(
            self,
            button: Button,
            mouse_down: bool,
            mouse_on: bool,
            keyed: bool,
            keyed_pressed: bool
    ) -> None:
        """
        handles a singular button
        :param button: button structure that is being handled
        :param mouse_down: if the mouse is currently clicking
        :param mouse_on: if the mouse is on the button
        :param keyed: if the keyed selection is on this button
        :param keyed_pressed: if the keyed button is pressed
        :return: None
        """
        self.draw_button(button, mouse_on, keyed)
        self.clicked_button(button, mouse_down, mouse_on, keyed, keyed_pressed)

    def draw_button(
            self,
            button: Button,
            mouse_on: bool,
            keyed: bool,
    ) -> None:
        """
        handles a singular button
        :param button: button structure that is being handled
        :param mouse_on: if the mouse is on the button
        :param keyed: if the keyed selection is on this button
        :return: None
        """
        if button.click is not None and (mouse_on or keyed):
            # mouse is over or keyed clicker is on

            # gets coordinates of button parts for scaling
            x, y = button.rect.topleft
            centerx, centery = button.rect.center
            width, height = centerx - x, centery - y
            new_centerx = centerx + width * (button.inflate_center[0] - 0.5) * -0.5
            new_centery = centery + height * (button.inflate_center[1] - 0.5) * -0.5

            new = pygame.transform.scale(
                button.img,
                (width * 2 * button.scale_factor, height * 2 * button.scale_factor)
            )

            self.screen.blit(
                new,
                (new_centerx - width * button.scale_factor, new_centery - height * button.scale_factor)
            )
            if button.outline_width > 0:
                pygame.draw.rect(
                    self.screen,
                    button.outline_color,
                    new.get_rect(center=(new_centerx, new_centery)).inflate(
                        1.75 * button.outline_width,
                        1.75 * button.outline_width
                    ),
                    width=button.outline_width
                )
        else:
            # not over
            self.screen.blit(button.img, button.rect)
            if button.outline_width > 0:
                pygame.draw.rect(
                    self.screen,
                    button.outline_color,
                    button.rect.inflate(2 * button.outline_width, 2 * button.outline_width),
                    width=button.outline_width
                )

    def clicked_button(
            self,
            button: Button,
            mouse_down: bool,
            mouse_on: bool,
            keyed: bool,
            keyed_pressed: bool
    ) -> None:
        """
        handles a singular button
        :param button: button structure that is being handled
        :param mouse_down: if the mouse is currently clicking
        :param mouse_on: if the mouse is on the button
        :param keyed: if the keyed selection is on this button
        :param keyed_pressed: if the keyed button is pressed
        :return: None
        """
        if button.click is not None:
            # if None in button.special_press:
            #     print(button.text, button.special_press)
            if isinstance(button.special_press, int):
                special_pressed = self.pressed[button.special_press]
            else:
                if None in button.special_press:
                    print(button.text)
                special_pressed = True in [self.pressed[click] for click in button.special_press]
            if (mouse_on and mouse_down) or (keyed and keyed_pressed) or special_pressed:
                button.down = True
            elif button.down:
                button.down = False
                if button.arguments is None:
                    button.click()
                else:
                    # noinspection PyCallingNonCallable
                    button.click(**button.arguments)

    def get_special_click(self, name: str) -> int:
        """
        gets special key for named press
        :param name: name of command
        :return: integer id of key to be used in commands
        """
        for con in self.controls:
            if con.name == name:
                return con.value