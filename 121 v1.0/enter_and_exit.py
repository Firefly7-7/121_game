"""
class for entering and exiting level areas
"""

from utility import Utility
from pygame.transform import smoothscale


class EnterAndExit(Utility):
    """
    class holding enter and exit level functions
    """

    def enter_level_place(self) -> None:
        """
        enters level smoothly
        :return: None
        """
        scale = 40
        while self.place == "enter_level" and scale < 60:
            self.tick()
            scale += 0.5
            width, height = self.level_display.get_size()
            draw = smoothscale(self.level_display, (width * scale / 40, height * scale / 40))
            self.screen.blit(
                draw,
                (240 * 2 - width * scale / 80, 180 * 2 - height * scale / 80)
            )
        self.change_place("in_game")

    def exit_level_place(self) -> None:
        """
        enters level smoothly
        :return: None
        """
        scale = 60
        if self.after_game is None:
            self.after_game = "start"
        elif self.after_game == "export":
            self.after_game = "construction"
        while self.place == "exit_level" and scale > 40:
            self.tick()
            scale -= 0.5
            width, height = self.level_display.get_size()
            draw = smoothscale(self.level_display, (width * scale / 60, height * scale / 60))
            self.screen.blit(
                draw,
                (240 * 2 - width * scale / 120, 180 * 2 - height * scale / 120)
            )
        self.change_place(self.after_game)
