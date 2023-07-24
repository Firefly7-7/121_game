"""
contains class for options area
"""

import pygame
from utility import Utility
from typing import Union
from constants import KEY_CONSTANTS
from copy import deepcopy
from game_structures import ControlOption
from math import log10


class Options(Utility):
    """
    class for options place
    """

    # noinspection PyAttributeOutsideInit
    def options_place(self) -> None:
        """
        runs while in options/controls area
        :return: None
        """

        self.editing_controls = list()

        def load_area() -> None:
            """
            loads the area with saved settings
            :return:
            """
            self.buttons.clear()
            self.add_button(self.make_text_button(
                "Back",
                50,
                self.change_place,
                (0, 180 * 4),
                (255, 255, 255),
                (0, 0, 0),
                5,
                arguments={"place": "start"},
                y_align=1,
                x_align=0,
                special_press="Back"
            ))
            self.add_button(self.make_text_button(
                "Apply",
                50,
                apply_changes,
                (0, 0),
                (255, 255, 255),
                (0, 0, 0),
                5,
                y_align=0,
                x_align=0,
                special_press="Play"
            ))
            self.add_button(self.make_text_button(
                "Revert",
                50,
                revert_changes,
                (240 * 4, 0),
                (255, 255, 255),
                (0, 0, 0),
                5,
                y_align=0,
                x_align=1,
                special_press="Reset"
            ))

            self.control_edit = None
            self.editing_controls = deepcopy(self.controls)
            for index, load_control in enumerate(self.editing_controls):
                load_control.button_index = len(self.buttons)
                if load_control.typ == "key":
                    self.add_button(self.make_text_button(
                        f"{load_control.name}: {pygame.key.name(load_control.value)}",
                        50,
                        key_control,
                        (0, 0),
                        (255, 255, 255),
                        (0, 0, 0),
                        5,
                        arguments={"index": index}
                    ))
                elif load_control.typ == "click_through":
                    self.add_button(self.make_text_button(
                        f"{load_control.name}: {load_control.args[load_control.value]}",
                        50,
                        click_through_on,
                        (0, 0),
                        (255, 255, 255),
                        (0, 0, 0),
                        5,
                        arguments={"index": index}
                    ))
                    self.add_button(self.make_text_button(
                        "<",
                        50,
                        click_through_change,
                        (0, 0),
                        (255, 255, 255),
                        (0, 0, 0),
                        5,
                        arguments={"index": index, "change": -1}
                    ))
                    self.add_button(self.make_text_button(
                        ">",
                        50,
                        click_through_change,
                        (0, 0),
                        (255, 255, 255),
                        (0, 0, 0),
                        5,
                        arguments={"index": index, "change": 1}
                    ))
                elif load_control.typ == "bool":
                    self.add_button(self.make_text_button(
                        f"{load_control.name}: {load_control.value}",
                        50,
                        bool_control,
                        (0, 0),
                        (255, 255, 255),
                        (0, 0, 0),
                        5,
                        arguments={"index": index}
                    ))
                elif load_control.typ == "range":
                    self.add_button(self.make_text_button(
                        f"{load_control.name}: {round(load_control.value, -1 * round(log10(load_control.args[2])))}",
                        50,
                        None,
                        (0, 0),
                        (255, 255, 255),
                        (0, 0, 0),
                        5
                    ))
                    self.add_button(self.make_text_button(
                        "<",
                        50,
                        range_change,
                        (0, 0),
                        (255, 255, 255),
                        (0, 0, 0),
                        5,
                        arguments={"index": index, "change": -1}
                    ))
                    self.add_button(self.make_text_button(
                        ">",
                        50,
                        range_change,
                        (0, 0),
                        (255, 255, 255),
                        (0, 0, 0),
                        5,
                        arguments={"index": index, "change": 1}
                    ))
                else:
                    raise TypeError(f"Incorrect controls type {load_control.typ}")

        def save_changes() -> None:
            """
            saves new controls and loads with new values
            :return:
            """
            self.controls = deepcopy(self.editing_controls)
            for save_control in self.editing_controls:
                if save_control.name == "Font":
                    self.fonts.new_fonts(save_control.args[save_control.value])
                elif save_control.name == "TTS":
                    self.tts = save_control.value

        def revert_changes() -> None:
            """
            reloads area and makes an alert
            :return:
            """
            load_area()
            self.alerts.add_alert("Settings reverted!")

        def apply_changes() -> None:
            """
            applies changes inside of options menu
            :return:
            """
            save_changes()
            load_area()
            self.alerts.add_alert("Settings updated!")

        def reset_control_change() -> None:
            """
            resets a load_control load_control
            :return: no
            """
            self.end_typing()
            if self.control_edit is None:
                return
            if self.editing_controls[self.control_edit].typ == "key":
                self.replace_button(self.editing_controls[self.control_edit].button_index, self.make_text_button(
                    f"{self.editing_controls[self.control_edit].name}: {pygame.key.name(self.editing_controls[self.control_edit].value)}",
                    50,
                    key_control,
                    (0, 0),
                    (255, 255, 255),
                    (0, 0, 0),
                    5,
                    arguments={"index": self.control_edit}
                ))
            elif self.editing_controls[self.control_edit].typ == "click_through":
                self.replace_button(self.editing_controls[self.control_edit].button_index, self.make_text_button(
                    f"{self.editing_controls[self.control_edit].name}: {self.editing_controls[self.control_edit].args[self.editing_controls[self.control_edit].value]}",
                    50,
                    click_through_on,
                    (0, 0),
                    (255, 255, 255),
                    (0, 0, 0),
                    5,
                    arguments={"index": self.control_edit}
                ))
            self.control_edit = None

        def key_control(index: int) -> None:
            """
            changes value for a load_control based on a click
            :param index: index of load_control in controls list
            :return: None
            """
            cont = self.editing_controls[index]
            reset_control_change()
            self.control_edit = index
            self.replace_button(cont.button_index, self.make_text_button(
                f"{cont.name}: <press a key>",
                50,
                key_control,
                (0, 0),
                (192, 192, 192),
                (0, 0, 0),
                5,
                arguments={"index": index}
            ))
            if self.tts:
                self.speak("Press a key")

        def click_through_on(index: int) -> None:
            """
            clicking on a click through
            :param index: load_control index looking at
            :return: no
            """
            cont = self.editing_controls[index]
            reset_control_change()
            self.start_typing()
            self.control_edit = index
            self.replace_button(cont.button_index, self.make_text_button(
                f"{cont.name}: <search>",
                50,
                reset_control_change,
                (0, 0),
                (192, 192, 192),
                (0, 0, 0),
                5
            ))
            if self.tts:
                self.speak("search")

        def click_through_change(index: int, change: int) -> None:
            """
            changes a click-through value forwards or backwards
            :param index:
            :param change:
            :return:
            """
            cont = self.editing_controls[index]
            reset_control_change()
            cont.value = (cont.value + change) % len(cont.args)
            self.replace_button(cont.button_index, self.make_text_button(
                f"{cont.name}: {cont.args[cont.value]}",
                50,
                click_through_on,
                (0, 0),
                (255, 255, 255),
                (0, 0, 0),
                5,
                arguments={"index": index}
            ))
            if self.tts:
                self.speak(cont.args[cont.value])

        def range_change(index: int, change: int) -> None:
            """
            changes a click-through value forwards or backwards
            :param index:
            :param change:
            :return:
            """
            cont = self.editing_controls[index]
            reset_control_change()
            cont.value = (cont.value + change * cont.args[2]) % (cont.args[1] - cont.args[0]) + cont.args[0]
            self.replace_button(cont.button_index, self.make_text_button(
                f"{cont.name}: {round(cont.value, -1 * round(log10(cont.args[2])))}",
                50,
                None,
                (0, 0),
                (255, 255, 255),
                (0, 0, 0),
                5
            ))
            if self.tts:
                self.speak(cont.value)

        def bool_control(index: int) -> None:
            """
            changes value of a boolean control at an index
            :param index:
            :return:
            """
            cont = self.editing_controls[index]
            cont.value = not cont.value
            self.replace_button(cont.button_index, self.make_text_button(
                f"{cont.name}: {cont.value}",
                50,
                bool_control,
                (0, 0),
                (255, 255, 255),
                (0, 0, 0),
                5,
                arguments={"index": index}
            ))
            if self.tts:
                self.speak(str(cont.value))

        def visible(contr: ControlOption) -> bool:
            """
            finds if a load_control is visible
            :param contr: load_control looking at
            :return: boolean
            """
            if contr.dependent is None:
                return True
            elif isinstance(contr.dependent[1], type(self.editing_controls[contr.dependent[0]].value)):
                return False
            elif contr.dependent[1] == self.editing_controls[contr.dependent[0]].value:
                return True
            else:
                return False

        load_area()

        top = 0

        while self.place == "options":
            self.tick()
            on = top
            if self.control_edit is None:
                pass
            elif self.editing_controls[self.control_edit].typ == "key":
                pressed = pygame.key.get_pressed()
                if pressed.count(True) == 1:
                    for const in KEY_CONSTANTS:
                        if pressed[const]:
                            self.editing_controls[self.control_edit].value = const
                            break
                    self.replace_button(self.editing_controls[self.control_edit].button_index, self.make_text_button(
                        f"{self.editing_controls[self.control_edit].name}: {pygame.key.name(self.editing_controls[self.control_edit].value)}",
                        50,
                        key_control,
                        (0, 0),
                        (255, 255, 255),
                        (0, 0, 0),
                        5,
                        arguments={"index": self.control_edit}
                    ))
                    # noinspection PyAttributeOutsideInit
                    self.control_edit = None
            elif self.editing_controls[self.control_edit].typ == "click_through":
                if self.typing.text != "":
                    if self.typing.text[-1] == "\n":
                        match = get_first_match(self.typing.text[:-1], self.editing_controls[self.control_edit].args)
                        if match is None:
                            self.start_typing()
                            self.replace_button(
                                self.editing_controls[self.control_edit].button_index,
                                self.make_text_button(
                                    f"{self.editing_controls[self.control_edit].name}: <search>",
                                    50,
                                    reset_control_change,
                                    (0, 0),
                                    (192, 192, 192),
                                    (0, 0, 0),
                                    5
                                )
                            )
                        else:
                            self.end_typing()
                            self.replace_button(
                                self.editing_controls[self.control_edit].button_index,
                                self.make_text_button(
                                    f"{self.editing_controls[self.control_edit].name}: {self.editing_controls[self.control_edit].args[match]}",
                                    50,
                                    click_through_on,
                                    (0, 0),
                                    (255, 255, 255),
                                    (0, 0, 0),
                                    5,
                                    arguments={"index": self.control_edit}
                                )
                            )
                            if self.tts:
                                self.speak(self.editing_controls[self.control_edit].args[match])
                            self.editing_controls[self.control_edit].value = match
                            self.control_edit = None
                    else:
                        match = get_first_match(self.typing.text, self.editing_controls[self.control_edit].args)
                        if match is None:
                            self.replace_button(
                                self.editing_controls[self.control_edit].button_index,
                                self.make_text_button(
                                    f"{self.editing_controls[self.control_edit].name}: <no match found>",
                                    50,
                                    reset_control_change,
                                    (0, 0),
                                    (192, 192, 192),
                                    (0, 0, 0),
                                    5
                                )
                            )
                            if self.tts:
                                self.speak("No match found")
                        else:
                            self.replace_button(
                                self.editing_controls[self.control_edit].button_index,
                                self.make_text_button(
                                    f"{self.editing_controls[self.control_edit].name}: {self.editing_controls[self.control_edit].args[match]}_",
                                    50,
                                    reset_control_change,
                                    (0, 0),
                                    (192, 192, 192),
                                    (0, 0, 0),
                                    5
                                )
                            )
                            if self.tts:
                                self.speak(self.editing_controls[self.control_edit].args[match])
            for button in self.buttons[3:]:
                button.rect.center = (0, 180 * 5)
            pos = pygame.mouse.get_pos()
            for i in range(10):
                if on >= len(self.editing_controls):
                    break
                while not visible(self.editing_controls[on]):
                    on += 1
                    if on >= len(self.editing_controls):
                        break
                if on >= len(self.editing_controls):
                    break
                self.buttons[self.editing_controls[on].button_index].rect.midtop = (480, 20 + i * 70)
                if self.editing_controls[on].typ == "click_through":
                    width = self.buttons[self.editing_controls[on].button_index].rect.width / 2
                    if self.buttons[self.editing_controls[on].button_index].rect.collidepoint(pos) or self.editing_controls[on].button_index == self.button_hover_keyed:
                        width *= self.buttons[self.editing_controls[on].button_index].scale_factor
                    self.buttons[self.editing_controls[on].button_index + 1].rect.topright = (480 - width - 20, 20 + i * 70)
                    self.buttons[self.editing_controls[on].button_index + 2].rect.topleft = (480 + width + 20, 20 + i * 70)
                elif self.editing_controls[on].typ == "range":
                    width = self.buttons[self.editing_controls[on].button_index].rect.width / 2
                    self.buttons[self.editing_controls[on].button_index + 1].rect.topright = (480 - width - 20, 20 + i * 70)
                    self.buttons[self.editing_controls[on].button_index + 2].rect.topleft = (480 + width + 20, 20 + i * 70)
                on += 1
        for control in self.editing_controls:
            if control.name == "Font":
                self.fonts.new_fonts(control.args[control.value])
            control.button_index = None
        if self.place == "refresh":
            self.place = "options"


def get_first_match(substring: str, strings: list[str]) -> Union[int, None]:
    """
    finds first string in a list with a matching substring
    :param substring: searching for
    :param strings: searching through
    :return: first instance
    """
    for i, string in enumerate(strings):
        if substring in string:
            return i
    return None