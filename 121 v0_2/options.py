"""
contains class for options area
"""

import pygame
from utility import Utility

# noinspection IncorrectFormatting
KEY_CONSTANTS = (pygame.K_BACKSPACE, pygame.K_TAB, pygame.K_CLEAR, pygame.K_RETURN, pygame.K_PAUSE, pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_EXCLAIM, pygame.K_QUOTEDBL, pygame.K_HASH, pygame.K_DOLLAR, pygame.K_AMPERSAND, pygame.K_QUOTE, pygame.K_LEFTPAREN, pygame.K_RIGHTPAREN, pygame.K_ASTERISK, pygame.K_PLUS, pygame.K_COMMA, pygame.K_MINUS, pygame.K_PERIOD, pygame.K_SLASH, pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_COLON, pygame.K_SEMICOLON, pygame.K_LESS, pygame.K_EQUALS, pygame.K_GREATER, pygame.K_QUESTION, pygame.K_AT, pygame.K_LEFTBRACKET, pygame.K_BACKSLASH, pygame.K_RIGHTBRACKET, pygame.K_CARET, pygame.K_UNDERSCORE, pygame.K_BACKQUOTE, pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r, pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z, pygame.K_DELETE, pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9, pygame.K_KP_PERIOD, pygame.K_KP_DIVIDE, pygame.K_KP_MULTIPLY, pygame.K_KP_MINUS, pygame.K_KP_PLUS, pygame.K_KP_ENTER, pygame.K_KP_EQUALS, pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_INSERT, pygame.K_HOME, pygame.K_END, pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5, pygame.K_F6, pygame.K_F7, pygame.K_F8, pygame.K_F9, pygame.K_F10, pygame.K_F11, pygame.K_F12, pygame.K_F13, pygame.K_F14, pygame.K_F15, pygame.K_NUMLOCK, pygame.K_CAPSLOCK, pygame.K_SCROLLOCK, pygame.K_RSHIFT, pygame.K_LSHIFT, pygame.K_RCTRL, pygame.K_LCTRL, pygame.K_RALT, pygame.K_LALT, pygame.K_RMETA, pygame.K_LMETA, pygame.K_LSUPER, pygame.K_RSUPER, pygame.K_MODE, pygame.K_HELP, pygame.K_PRINT, pygame.K_SYSREQ, pygame.K_BREAK, pygame.K_MENU, pygame.K_POWER, pygame.K_EURO, pygame.K_AC_BACK)


class Options(Utility):
    """
    class for options place
    """

    def options_place(self) -> None:
        """
        runs while in options/controls area
        :return: None
        """

        self.add_button(self.make_text_button(
            "Back",
            self.fonts[50],
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

        # noinspection PyAttributeOutsideInit
        self.key_edit = None

        def control_iter(index) -> None:
            """
            changes value for a control based on a click
            :param index: index of control in controls list
            :return: None
            """
            # TODO change control buttons to main list
            cont = self.controls[index]
            if self.key_edit is not None:
                self.controls[self.key_edit].button = self.make_text_button(
                    f"{self.controls[self.key_edit].name}: {pygame.key.name(self.controls[self.key_edit].value)}",
                    self.fonts[50],
                    control_iter,
                    (0, 0),
                    (255, 255, 255),
                    (0, 0, 0),
                    5,
                    arguments={"index": self.key_edit}
                )
                self.key_edit = None
            if cont.typ == "key":
                self.key_edit = index
                cont.button = self.make_text_button(
                    f"{cont.name}: <press a key>",
                    self.fonts[50],
                    control_iter,
                    (0, 0),
                    (192, 192, 192),
                    (0, 0, 0),
                    5,
                    arguments={"index": index}
                )
            elif cont.typ == "click_through":
                if cont.value == len(cont.args):
                    cont.value = 0
                else:
                    cont.value += 1
                cont.button = self.make_text_button(
                    f"{cont.name}: {cont.args[cont.value]}",
                    self.fonts[50],
                    control_iter,
                    (0, 0),
                    (255, 255, 255),
                    (0, 0, 0),
                    5,
                    arguments={"index": index}
                )

        def visible(contr) -> bool:
            """
            finds if a control is visible
            :param contr: control looking at
            :return: boolean
            """
            if contr.dependent is None:
                return True
            elif type(contr.dependent[1]) != type(self.controls[contr.dependent[0]].value):
                return False
            elif contr.dependent[1] == self.controls[contr.dependent[0]].value:
                return True
            else:
                return False

        for i, control in enumerate(self.controls):
            if control.typ == "key":
                val = pygame.key.name(control.value)
            else:
                val = control.value
            control.button = self.make_text_button(
                f"{control.name}: {val}",
                self.fonts[50],
                control_iter,
                (0, 0),
                (255, 255, 255),
                (0, 0, 0),
                5,
                arguments={"index": i}
            )

        top = 0

        while self.place == "options":
            self.tick()
            on = top

            down = pygame.display.get_active() and pygame.mouse.get_pressed()[0]
            pos = pygame.mouse.get_pos()

            if self.key_edit is not None:
                pressed = pygame.key.get_pressed()
                if pressed.count(True) == 1:
                    for const in KEY_CONSTANTS:
                        if pressed[const]:
                            self.controls[self.key_edit].value = const
                            break
                    self.controls[self.key_edit].button = self.make_text_button(
                        f"{self.controls[self.key_edit].name}: {pygame.key.name(self.controls[self.key_edit].value)}",
                        self.fonts[50],
                        control_iter,
                        (0, 0),
                        (255, 255, 255),
                        (0, 0, 0),
                        5,
                        arguments={"index": self.key_edit}
                    )
                    # noinspection PyAttributeOutsideInit
                    self.key_edit = None

            for i in range(8):
                if on >= len(self.controls):
                    break
                while not visible(self.controls[on]):
                    on += 1
                    if on >= len(self.controls):
                        break
                self.controls[on].button.rect.midtop = (480, 20 + i * 70)
                self.handle_button(
                    self.controls[on].button,
                    down,
                    self.controls[on].button.rect.collidepoint(pos),
                    i == self.button_hover_keyed,
                    False  # TODO actually do the keyed thingy
                )
                on += 1
            self.handle_buttons()
        for control in self.controls:
            control.button = None
        del self.key_edit