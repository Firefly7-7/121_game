"""
holds credits class
"""

from utility import Utility
import pygame


class Credits(Utility):
    """
    handles credits area.
    """

    # noinspection SpellCheckingInspection
    def credits_place(self) -> None:
        """
        handles rendering and showing credits
        :return: None
        """
        self.add_button(self.make_text_button(
            "Back",
            50,
            self.change_place,
            (0, 0),
            (255, 255, 255),
            (0, 0, 0),
            5,
            arguments={"place": "start"},
            y_align=0,
            x_align=0,
            special_press="Back"
        ))
        credits_text = (
            """
            Main Developer:
            Fractal
            
            Mac Developer:
            PLx22
            
            Level Designers:
            Ishililly (Creator of 'The End...')
            
            Play Testers:
            Ishililly, Eva, Walkdoge
            """
        )
        self.add_button(self.make_text_button(
            credits_text,
            32,
            None,
            (240 * 2, 180 * 2),
            text_align=0.5,
            max_line_pixels=240 * 3,
            preserve_words=True,
            x_align=0.5,
            y_align=0.5,
            border_width=0
        ))
        if self.tts:
            self.speak(credits_text)
        while self.place == "credits":
            self.tick()