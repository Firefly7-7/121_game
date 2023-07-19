"""
utility super-class
"""

import pygame
from pygame.constants import USEREVENT
from pygame.surface import Surface
from game_structures import Button, TypingData, AlertHolder
from typing import Callable, Union, Any
from game_structures import ControlOption, FontHolder
from player_data import load_player_data, empty_player_data
from os.path import exists
from os import listdir
from sys import argv
from constants import LEVEL_LIST, EASTER_EGG_LEVELS, BLOCK_LIST, DEFAULT_SKINS, BASE_ACHIEVEMENTS, ADMIN_BLOCKS
from gtts import gTTS
from aiogtts import aiogTTS
from io import BytesIO
from multiprocessing.pool import ThreadPool as Pool
from skin_management import draw_skin
from block_data import Block, Blocks
from platform import system
from subprocess import Popen, call
from level_data import LevelWrap
from level_management import make_blank_level
import asyncio
from showinfm import show_in_file_manager
import logging
import traceback

# from pyperclip import paste


class Utility:
    """
    utility superclass.  Also the initialization function
    """

    def __init__(self) -> None:
        """
        loads player data and sets up the game with correct lists
        """

        self.buttons: list[[Button]] = list()
        self.button_names: list[[str]] = list()
        self.button_hover_keyed = -1
        self.button_hover_next_key = pygame.K_TAB
        self.button_hover_press_key = pygame.K_RETURN

        print(argv[0][len(argv[0]) - 6:])
        if len(argv) == 2 and argv[1] == "admin":
            self.admin = True
            for block in ADMIN_BLOCKS:
                BLOCK_LIST.append(block)
        else:
            self.admin = False

        if exists("player_data.dat"):
            player_data = load_player_data()
        else:
            player_data = empty_player_data()
        easter_egg_levels = set(EASTER_EGG_LEVELS)
        existing_lvls = {c_lvl[:-4] for c_lvl in listdir("premade_levels")}.union(easter_egg_levels)
        for i in range(len(player_data.level_list) - 1, -1, -1):
            if player_data.level_list[i][0] not in existing_lvls:
                del player_data.level_list[i]
        player_levels = {lvl[0] for lvl in player_data.level_list}
        i = 0
        for lvl in LEVEL_LIST:
            if lvl not in existing_lvls:
                print(lvl)
                continue
            if lvl not in player_levels:
                player_data.level_list.insert(i, (lvl, False))  # lvl name, completed
                if i < player_data.level_on:
                    player_data.level_on += 1
            while player_data.level_list[i][0] in easter_egg_levels:
                i += 1
                # if lvl != player_data.level_list[i][0]:
                #     player_data.level_list.insert(i, (lvl, False))  # lvl name, completed
            i += 1

        self.achievements = set(player_data.achievements)

        self.skin_using = player_data.skin
        if "Default" not in player_data.skins:
            player_data.skins["Default"] = DEFAULT_SKINS["Default"]
        self.skins = player_data.skins

        self.level_display = None
        self.level_on = player_data.level_on
        self.levels = (player_data.level_list, [(c_lvl[:-4], False) for c_lvl in listdir("custom_levels")])
        self.level_data: LevelWrap = None
        self.look_at = [min(len(self.levels[0]) - 1, self.level_on), 0]
        self.custom = 0
        self.after_game = None

        self.constructing = 0
        self.working_on = player_data.working_on

        self.player_img = draw_skin(self.skins[self.skin_using])

        # controls setup

        def add_control(
                name: str,
                default: Any,
                typ: str,
                args: Union[list[Any], None] = None,
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
        self.control_edit = None

        add_control("Jump", pygame.K_UP, "key")
        add_control("Right", pygame.K_RIGHT, "key")
        add_control("Left", pygame.K_LEFT, "key")
        add_control("Back", pygame.K_b, "key")
        add_control("Play", pygame.K_p, "key")
        add_control("Reset", pygame.K_r, "key")
        add_control("Font", 0, "click_through", pygame.font.get_fonts())  # 6
        add_control("Tab Navigation", True, "bool")
        add_control("TTS", True, "bool")
        add_control("Death Timer", 1, "range", [0, 2.1, 0.1])  # 9

        self.fonts = FontHolder(self.controls[6].args[self.controls[6].value])
        self.keyed = self.controls[7].value
        self.tts = self.controls[8].value
        self.last_spoken = ""

        pygame.mixer.pre_init(8000, size=-16, channels=1)

        pygame.init()

        self.screen = pygame.display.set_mode(size=(240 * 4, 180 * 4))
        pygame.display.set_caption("121")

        self.clock = pygame.time.Clock()

        self.place = "start"

        self.pressed = pygame.key.get_pressed()

        self.running = True

        self.name = "121"

        self.typing = TypingData()
        pygame.key.set_repeat(500, 125)

        self.alerts = AlertHolder(
            width=512,
            size=20,
            max_alerts=5,
            speed=10,
            speak=self.speak,
            draw=self.draw_text,
            border_buffer=5,
            lifespan=300
        )

        # # makes opening directories cross-platform
        # if system() == "Windows" or system() == "Darwin":
        #     def open_directory(args: list[str]) -> None:
        #         """
        #         opens directory, windows version
        #         :param args: parts of path
        #         :return:
        #         """
        #         Popen(["explorer", "\\".join(args)])
        # elif system() == "MacOS":
        #     def open_directory(args: list[str]) -> None:
        #         """
        #         opens directory, windows version
        #         :param args: parts of path
        #         :return:
        #         """
        #         call(["open", "\\".join(args)])
        # else:
        #     def open_directory(args: list[str]) -> None:
        #         """
        #         tries to open using general attempt, but if errors puts out an alert
        #         :param args:
        #         :return:
        #         """
        #         try:
        #             Popen(["xdg-open", "\\".join(args)])
        #         except:
        #             cls.alerts.add_alert(f"Sorry, the game doesn't support opening folders in '{system()}'.  Contact the developer.")
        # cls.open_directory = open_directory

        logging.basicConfig(filename="errors.log",
                            format='%(asctime)s\n%(message)s',
                            filemode='a')

    def open_directory(self, args: list[str]) -> None:
        """
        tries to open a directory
        :return:
        """
        show_in_file_manager("\\".join(args))

    def start_typing(self, start_text: str = "", button_index: int = None) -> TypingData:
        """
        begins typing, output in cls.text
        :param start_text: what starting text is
        :param button_index: what button editing
        :return: typing instance
        """
        # print(f"Start typing with '{start_text}'")
        self.typing = TypingData(
            typing=True,
            text=start_text,
            button_target=button_index,
            instance=self.typing.instance + 1
        )
        if button_index is not None:
            self.buttons[button_index].typing_instance = self.typing.instance
        return self.typing

    def end_typing(self) -> str:
        """
        ends typing
        :return: string typed
        """
        self.typing = TypingData(
            typing=False,
            text=self.typing.text
        )
        return self.typing.text

    def speak(self, text: str) -> None:
        """
        wrapper to make asynchronous speach work
        :param text: text to read
        :return: none
        """
        if self.tts:
            asyncio.get_event_loop().run_until_complete(asynchronous_speak(text))

    def rewrite_button(
            self,
            new_text: str,
            index: int,
            font: int,
            center: tuple[int, int],
            instance: int = None,
            others: list[tuple[int, float, float, int, int]] = (),
            max_line_pixels: int = 0,
            max_width: int = 0,
            y_align: int = 0.5,
            x_align: int = 0.5,
            override_button_name: str = None
    ) -> None:
        """
        change text of target button to new string.  Also moves buttons around
        as described
        :param new_text: new text to change it to
        :param index: integer index of button to keep track of
        :param font: font size of it
        :param center: center of the button to orient around
        :param instance: typing instance
        :param others: a list of other buttons to update positions of, with information
        integer: button index
        float: offset x by width
        float: offset y by height
        integer: static x offset
        integer: static y offset
        :param max_line_pixels: maximum pixels in a line
        :param max_width: maximum width of the button
        :param y_align: designate where to orient x from
        :param x_align: designate where to orient y from
        :param override_button_name: override the button name if any
        :return: None
        """
        if instance is not None and self.buttons[index].typing_instance != instance:
            return
        new_img = self.draw_text(new_text, font, max_line_pixels=max_line_pixels, preserve_words=True)
        width = new_img.get_width()
        if width > max_width > 0:
            new_img = self.draw_text(
                new_text,
                round(font * max_width / width),
                max_line_pixels=round(max_line_pixels * max_width / width),
                preserve_words=True
            )
            width = new_img.get_width()
        height = new_img.get_height()
        self.buttons[index].img = new_img
        if override_button_name is None:
            override_button_name = new_text
        self.button_names[index] = override_button_name
        self.buttons[index].rect = new_img.get_rect(topleft=(
            center[0] - x_align * new_img.get_width(),
            center[1] - y_align * new_img.get_height()
        ))
        for other_index, offset_width, offset_height, offset_x, offset_y in others:
            if self.buttons[other_index] is None:
                continue
            self.buttons[other_index].rect.center = (
                center[0] + offset_width * width + offset_x,
                center[1] + offset_height * height + offset_y
            )

    def write_button_text(
            self,
            index: int,
            font: int,
            max_characters: int = 0,
            min_characters: int = 0,
            others: list[tuple[int, float, float, int, int]] = (),
            max_line_pixels: int = 0,
            max_width: int = 0,
            prepend: str = "",
            append: str = "",
            start_text: str = None,
            callback: Callable = None,
            y_align: int = 0.5,
            x_align: int = 0.5
    ) -> None:
        """
        edits a button's text, given an index.  Wrapper for interior async function
        :param index: integer index of button to keep track of
        :param font: font size of it
        :param max_characters: max characters in a line (0 if no max)
        :param min_characters: minimum characters in a line
        :param others: a list of other buttons to update positions of, with information
        integer: button index
        float: offset x by width
        float: offset y by height
        integer: static x offset
        integer: static y offset
        :param max_line_pixels: maximum pixels in a line
        :param max_width: maximum width of the button
        :param prepend: prepend string
        :param append: append string
        :param start_text: if None, uses button name as start
        :param callback: function called when the function completes
        :param y_align: designate where to orient x from
        :param x_align: designate where to orient y from
        :return: None
        """

        def async_write_button_text() -> str:
            """
            asynchronously edits level name on display
            :return: final string value
            """

            nonlocal start_text
            if start_text is None:
                start_text = self.button_names[index]
            current = start_text

            x = self.buttons[index].rect.left + x_align * self.buttons[index].rect.width
            y = self.buttons[index].rect.top + y_align * self.buttons[index].rect.height

            instance = self.start_typing(current, index)

            self.rewrite_button(prepend + current + "_" + append, index, font, (x, y), instance.instance, others, max_line_pixels, max_width, y_align, x_align, start_text)

            try:
                while self.typing.instance == instance.instance:
                    if instance.text != current:
                        if len(instance.text) > max_characters > 0:
                            current = instance.text[0:max_characters]
                            if "\n" in instance.text[max_characters:]:
                                self.rewrite_button(prepend + current + append, index, font, (x, y), instance.instance, others, max_line_pixels, max_width, y_align, start_text)
                                self.end_typing()
                                break
                            instance.text = current
                        current = instance.text
                        if min_characters <= len(current):
                            if len(current) > 0 and current[-1] == "\n":
                                self.rewrite_button(prepend + current[:-1] + append, index, font, (x, y), instance.instance, others, max_line_pixels, max_width, y_align, x_align, start_text)
                                self.end_typing()
                                current = current[:-1]
                                break
                        if "\n" in current:
                            instance.text = current[:current.index("\n")]
                            current = instance.text
                        self.rewrite_button(prepend + current + "_" + append, index, font, (x, y), instance.instance, others, max_line_pixels, max_width, y_align, x_align, start_text)
            finally:
                if len(current) > max_characters > 0 or min_characters > len(current):
                    result = start_text
                else:
                    result = current
                if self.buttons[index] is not None and self.buttons[index].typing_instance == instance.instance:
                    self.rewrite_button(prepend + result + append, index, font, (x, y), instance.instance, others, max_line_pixels, max_width, y_align, x_align)
                    self.buttons[index].typing_instance = None
                return result

        if self.buttons[index] is not None and self.buttons[index].typing_instance is not None:
            return
        pool = Pool(1)
        if callback is None:
            pool.apply_async(async_write_button_text)
        else:
            pool.apply_async(async_write_button_text, callback=callback)

    def tick(self) -> None:
        """
        function that handles game clock and frame rate
        also handles some other actions that need to happen every frame
        :return: string of typed characters
        """
        self.handle_buttons()
        alert_img = self.alerts.tick()
        if alert_img is not None:
            self.screen.blit(
                alert_img,
                (240 * 2 - self.alerts.width / 2, 0)
            )
        pygame.display.flip()
        self.clock.tick(60)
        self.screen.fill((255, 255, 255))
        self.pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.place = "ended"
            elif event.type == pygame.KEYDOWN:
                if self.typing.typing:
                    if event.key == pygame.K_RETURN:
                        self.typing.text += "\n"
                    elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                        if self.typing.text != "":
                            self.typing.text = self.typing.text[:-1]
                    else:
                        self.typing.text += event.unicode
                        # print(event.key, event.mod, pygame.KMOD_CTRL)
                elif self.control_edit is None:
                    if event.key == self.button_hover_next_key:
                        # print("Button keyed")
                        self.button_hover_keyed += 1
                        if self.button_hover_keyed >= len(self.buttons):
                            self.button_hover_keyed = 0
                        # noinspection IncorrectFormatting
                        while self.buttons[self.button_hover_keyed] is None or self.buttons[self.button_hover_keyed].text is None:
                            self.button_hover_keyed += 1
                            if self.button_hover_keyed >= len(self.buttons):
                                self.button_hover_keyed = -1
                                break
                        if self.button_hover_keyed >= 0 and self.tts:
                            self.speak(self.buttons[self.button_hover_keyed].text)
                        continue
                    for button in self.buttons:
                        if button is None:
                            continue
                        special_pressed = False
                        if isinstance(button.special_press, int):
                            special_pressed = event.key == button.special_press
                        else:
                            for click in button.special_press:
                                if event.key == click:
                                    special_pressed = True
                                    break
                        if special_pressed:
                            if button.arguments is None:
                                button.click()
                            else:
                                # noinspection PyCallingNonCallable
                                button.click(**button.arguments)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in self.buttons:
                        if button is None:
                            continue
                        if button.rect.collidepoint(event.pos):
                            if button.click is None:
                                pass
                            elif button.arguments is None:
                                button.click()
                            else:
                                button.click(**button.arguments)
                            break
            elif event.type == USEREVENT:
                self.alerts.speak.next_speach()

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
    ) -> Button:
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

    def make_text_button(
            self,
            text: str,
            font: int,
            click: Union[Callable, None],
            center: tuple[int, int],
            background_color: Union[tuple[int, int, int], tuple[int, int, int, int], None] = (255, 255, 255, 255),
            outline_color: tuple[int, int, int] = (0, 0, 0),
            border_width: int = 0,
            max_line_pixels: int = 0,
            max_line_words: int = 0,
            max_width: int = 0,
            preserve_words: bool = True,
            text_align: float = 0,
            x_align: float = 0.5,
            y_align: float = 0.5,
            arguments: dict[str, Any] = None,
            special_press: Union[tuple[str], str] = (),
            override_text: str = None,
            max_lines: int = 0,
            enforce_width: int = 0
    ) -> Button:
        """
        creates a button object and adds it to handled list
        :param text: string
        :param font: size of the font object
        :param click: function called when the button is clicked
        :param center: coordinate centers of the button
        :param background_color: background color for the text
        :param outline_color: color used for text and border
        :param border_width: width of border for button
        :param max_line_pixels: maximum number of pixels in a line, 0 for disabled
        :param max_line_words: maximum number of words in a line, 0 for disabled
        :param max_width: maximum width of object.  Scales to be inside of it, if not already.  0 for disabled.
        :param preserve_words: whether or not to preserve words when considering max line pixels
        :param text_align: left (0) to right (1) alignment of text
        :param x_align: where the x value of 'center' is relative to the button, left (0), right (1).  Default center
        :param y_align: where the y value of 'center' is relative to the button, top (0), bottom (1).  Default center
        :param arguments: arguments to be used in the click action
        :param special_press: special keys that press button
        :param override_text: overrides text for tts
        :return: a constructed button to be added to the list
        """
        text_surface = self.draw_text(
            text,
            font,
            background_color,
            outline_color,
            max_line_pixels,
            max_line_words,
            max_width,
            preserve_words,
            text_align,
            max_lines=max_lines,
            enforce_width=enforce_width,
        )
        x, y = text_surface.get_size()
        if isinstance(special_press, str):
            special = self.get_special_click(special_press)
        else:
            special = tuple([self.get_special_click(name) for name in special_press])
        if text == "<":
            text = "Left"
        elif text == ">":
            text = "Right"
        if override_text is None:
            override_text = text
        return Button(
            click,
            text_surface,
            override_text,
            pygame.Rect(center[0] - x_align * x, center[1] - y_align * y, x, y),
            background_color,
            outline_color,
            (x_align, y_align),
            border_width,
            arguments=arguments,
            special_press=special
        )

    def draw_text(
            self,
            text: str,
            font: int,
            background_color: Union[tuple[int, int, int], tuple[int, int, int, int], None] = (255, 255, 255, 255),
            outline_color: tuple[int, int, int] = (0, 0, 0),
            max_line_pixels: int = 0,
            max_line_words: int = 0,
            max_width: int = 0,
            preserve_words: bool = True,
            text_align: float = 0,
            max_lines: int = 0,
            enforce_width: int = 0
    ) -> pygame.surface.Surface:
        """
        draws text
        :param text: string
        :param font: font size
        :param background_color: background color for the text
        :param outline_color: color used for text and border
        :param max_line_pixels: maximum number of pixels in a line, 0 for disabled
        :param max_line_words: maximum number of words in a line, 0 for disabled
        :param max_width: maximum pixels in line, scales down to match
        :param preserve_words: whether or not to preserve words when considering max line pixels
        :param text_align: left (0) to right (1) alignment of text
        :param max_lines: maximum lines in the text display
        :param enforce_width: enforce a width for the display
        :return: drawn text
        """
        lines = [""]
        word = ""
        words = 0
        draw_font = self.fonts[font]
        for char in text + " ":
            if char == "\n":
                if word != "":
                    if lines[-1] == "":
                        lines[-1] = word
                    else:
                        lines[-1] += " " + word
                    word = ""
                if len(lines) == max_lines:
                    if draw_font.size(lines[-1] + "...")[0] > max_line_pixels:
                        backstep = -1
                        while draw_font.size(lines[-1][:backstep] + "...")[0] > max_line_pixels:
                            backstep -= 1
                            if backstep >= len(lines[-1]):
                                break
                        lines[-1] = lines[-1][:backstep] + "..."
                    else:
                        lines[-1] += "..."
                    break
                else:
                    lines.append("")
                words = 0
            elif char == " ":
                if lines[-1] == "":
                    lines[-1] = word
                elif preserve_words and max_line_pixels > 0:
                    if lines[-1] == "":
                        length = draw_font.size(word)
                    else:
                        length = draw_font.size(lines[-1] + " " + word)[0]
                    if length > max_line_pixels:
                        if len(lines) == max_lines:
                            if draw_font.size(lines[-1] + "...")[0] > max_line_pixels:
                                backstep = -1
                                while draw_font.size(lines[-1][:backstep] + "...")[0] > max_line_pixels:
                                    backstep -= 1
                                    if backstep >= len(lines[-1]):
                                        break
                                lines[-1] = lines[-1][:backstep] + "..."
                            else:
                                lines[-1] += "..."
                            break
                        else:
                            lines.append(word)
                        words = 0
                    else:
                        if lines[-1] == "":
                            lines[-1] = word
                        else:
                            lines[-1] += " " + word
                else:
                    if lines[-1] == "":
                        lines[-1] = word
                    else:
                        lines[-1] += " " + word
                word = ""
                words += 1
                if words >= max_line_words > 0:
                    words = 0
                    if len(lines) == max_lines:
                        if draw_font.size(lines[-1] + "...")[0] > max_line_pixels:
                            backstep = -1
                            while draw_font.size(lines[-1][:backstep] + "...")[0] > max_line_pixels:
                                backstep -= 1
                                if backstep >= len(lines[-1]):
                                    break
                            lines[-1] = lines[-1][:backstep] + "..."
                        else:
                            lines[-1] += "..."
                        break
                    else:
                        lines.append("")
            else:
                if max_line_pixels > 0:
                    if lines[-1] == "":
                        length = draw_font.size(word + char)[0]
                    else:
                        length = draw_font.size(lines[-1] + " " + word + char)[0]
                    if length > max_line_pixels:
                        if len(lines) == max_lines:
                            if lines[-1] == "":
                                lines[-1] = word
                            else:
                                lines[-1] += " " + word
                            if draw_font.size(lines[-1] + "...")[0] > max_line_pixels:
                                backstep = -1
                                while draw_font.size(lines[-1][:backstep] + "...")[0] > max_line_pixels:
                                    backstep -= 1
                                    if backstep >= len(lines[-1]):
                                        break
                                lines[-1] = lines[-1][:backstep] + "..."
                            else:
                                lines[-1] += "..."
                            break
                        else:
                            if not preserve_words:
                                lines[-1] += word
                                word = ""
                            lines.append("")
                        words = 0
                word += char
        if max_width > 0:
            max_length = 0
            for line in lines:
                max_length = max(max_length, draw_font.size(line)[0])
            if max_length > max_width:
                draw_font = self.fonts[font * max_width / max_length]
        if enforce_width == 0:
            max_length = 0
            for i in range(len(lines)):
                lines[i] = draw_font.render(lines[i], True, outline_color, None)
                max_length = max(max_length, lines[i].get_width())
        else:
            max_length = enforce_width
            for i in range(len(lines)):
                lines[i] = draw_font.render(lines[i], True, outline_color, None)
        linesize = draw_font.get_linesize()
        text_surface = pygame.Surface((max_length, linesize * len(lines)), pygame.SRCALPHA)
        if background_color is not None:
            text_surface.fill(background_color)
        for i in range(len(lines)):
            text_surface.blit(lines[i], (text_align * (max_length - lines[i].get_width()), i * linesize))
        return text_surface

    def blit_text(
            self,
            text: str,
            font: int,
            x: int,
            y: int,
            background_color: Union[tuple[int, int, int], tuple[int, int, int, int], None] = (255, 255, 255, 255),
            outline_color: tuple[int, int, int] = (0, 0, 0),
            max_line_pixels: int = 0,
            max_line_words: int = 0,
            max_width: int = 0,
            preserve_words: bool = True,
            text_align: float = 0,
            centerx: float = 0.5,
            centery: float = 0.5,
            surface: pygame.surface.Surface = None
    ) -> None:
        """
        draws text
        :param text: string
        :param font: font size
        :param x:
        :param y:
        :param background_color: background color for the text
        :param outline_color: color used for text and border
        :param max_line_pixels: maximum number of pixels in a line, 0 for disabled
        :param max_line_words: maximum number of words in a line, 0 for disabled
        :param max_width: maximum pixels in line, scales down to match
        :param preserve_words: whether or not to preserve words when considering max line pixels
        :param text_align: left (0) to right (1) alignment of text
        :param centerx: where centered
        :param centery: where centered
        :param surface: what to draw it on (if not the screen)
        :return: None
        """
        text = self.draw_text(
            text,
            font,
            background_color,
            outline_color,
            max_line_pixels,
            max_line_words,
            max_width,
            preserve_words,
            text_align
        )
        if surface is None:
            surface = self.screen
        width, height = text.get_size()
        surface.blit(text, (x - centerx * width, y - centery * height))

    def handle_buttons(self) -> None:
        """
        engine to handle all buttons
        :return: none
        """
        pos = pygame.mouse.get_pos()
        for i in range(len(self.buttons)):
            if self.buttons[i] is not None:
                self.handle_button(
                    self.buttons[i],
                    self.buttons[i].rect.collidepoint(pos),
                    i == self.button_hover_keyed
                )

    def handle_button(
            self,
            button: Button,
            mouse_on: bool,
            keyed: bool,
    ) -> None:
        """
        handles a singular button
        whoops, was originally distributing click and draw, but eh
        :param button: button structure that is being handled
        :param mouse_on: if the mouse is on the button
        :param keyed: if the keyed selection is on this button
        :return: None
        """
        self.draw_button(button, mouse_on, keyed)

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

    def give_achievement(self, achievement_name: str, previous: set[str] = None) -> None:
        """
        gives an achievement to the player
        :param achievement_name: the name of the achievement
        :param previous: previous achievements gotten to prevent infinite recursion
        :return: nothing
        """
        if previous is None:
            previous = set()
        if achievement_name in self.achievements:
            self.alerts.add_alert(f"You have already collected achievement '{achievement_name}'.")
        else:
            self.alerts.add_alert(
                f"Achievement '{achievement_name}' unlocked!  {BASE_ACHIEVEMENTS[achievement_name].description}")
        self.achievements.add(achievement_name)
        achievement = BASE_ACHIEVEMENTS[achievement_name]
        previous.add(achievement_name)
        for skin in achievement.skins:
            if skin not in self.skins:
                self.give_skin(skin)
        for level in achievement.easter_egg_levels:
            if level in {lvl[0] for lvl in self.levels[0]}:
                self.give_level(level)
        for nest_achievement, conditions in achievement.nest_achievements:
            if nest_achievement in previous:
                continue
            got = True
            if self.skin_using not in conditions.get("skins", [self.skin_using]):
                got = False
            if not conditions.get("achievements", set()).issubset(self.achievements):
                got = False
            if got:
                self.give_achievement(nest_achievement, previous)

    def give_skin(self, skin_name: str) -> None:
        """
        gives a skin to the player
        :param skin_name: the name of the skin
        :return: nothing
        """
        if skin_name in self.skins:
            self.alerts.add_alert(f"You have already collected skin '{skin_name}'.")
        else:
            self.alerts.add_alert(f"Skin '{skin_name}' unlocked!", draw_skin(
                DEFAULT_SKINS[skin_name]
            ))
        self.skins[skin_name] = DEFAULT_SKINS[skin_name]

    def give_level(self, level_name: str) -> None:
        """
        gives an achievement to the player
        :param level_name: the name of the level
        :return: nothing
        """
        if level_name in {lvl[0] for lvl in self.levels[0]}:
            self.alerts.add_alert(f"You have already collected easter egg level '{level_name}'.")
        else:
            self.alerts.add_alert(f"Easter egg level '{level_name}' unlocked!", LevelWrap(make_blank_level()).draw_block(
                Block(
                    Blocks.easter_egg,
                    []
                ),
                self.fonts[30],
                60
            ))
            self.levels[0].insert(
                self.look_at[0],
                (level_name, False)
            )
            self.look_at[0] += 1
            self.level_on += 1

    def get_special_click(self, name: str) -> int:
        """
        gets special key for named press
        :param name: name of command
        :return: integer id of key to be used in commands
        """
        for con in self.controls:
            if con.name == name:
                return con.value

    def log_error(self, exc: Exception) -> None:
        """
        logs an error.  Requires there to be an error.
        :return:
        """
        stack: traceback.StackSummary = traceback.extract_tb(exc.__traceback__)
        if not self.admin:
            root = argv[0][:len(argv[0]) - 6].replace("/", "\\")
            for frame in stack:
                if frame.filename.startswith(root):
                    frame.filename = frame.filename[len(root):]
                else:
                    frame.filename = "<filename outside of program, obscured for privacy>"
        logging.error("".join(traceback.format_list(stack)))

    def check_pressed(self, key: int) -> bool:
        """
        checks if a key is pressed using pygame key constant
        :param key: what key
        :return: is it pressed?
        """
        return self.pressed[key]


async def asynchronous_speak(text: str) -> None:
    """
    asynchronous speak method using google text to speach
    :param text: text to read
    :return: none
    """
    mp3_fp = BytesIO()
    try:
        tts = aiogTTS()
        await tts.write_to_fp(text, mp3_fp)
        mp3_fp.seek(0)
        pygame.mixer.music.load(mp3_fp, "mp3")
        pygame.mixer.music.play()
    except:
        return