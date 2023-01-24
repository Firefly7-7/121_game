"""
main file for 121 game
"""

from start import Start
from options import Options
from level_select import LevelSelect
from enter_and_exit import EnterAndExit
from in_game import InGame

BLOCK_LIST = ()


class Game(Start, Options, LevelSelect, EnterAndExit, InGame):
    """
    class that runs the entire game
    init in utility
    """

    def main_game(self) -> None:
        """
        loop that handles travel between different locations
        :return: None
        """
        while self.running:
            self.buttons.clear()
            if self.place == "testing":
                self.testing_place()
            elif self.place == "start":
                self.start_place()
            elif self.place == "options":
                self.options_place()
            elif self.place == "level_select":
                self.level_select_place()
            elif self.place == "construction":
                raise ValueError("Construction area has not been made yet.")
            elif self.place == "instructions":
                raise ValueError("Instruction area has not been made yet.")
            elif self.place == "enter_level":
                self.enter_level_place()
            elif self.place == "exit_level":
                self.exit_level_place()
            elif self.place == "in_game":
                self.in_game_place()
            else:
                raise ValueError(f"Area '{self.place}' does not exist.")

    def testing_place(self) -> None:
        self.buttons.append(self.make_text_button(
            "testing",
            self.fonts[100],
            self.change_place,
            (200, 100),
            (255, 255, 255),
            (0, 0, 0),
            20,
            arguments={"place": "start"}
        ))
        while self.place == "testing":
            self.tick()
            self.handle_buttons()


Game().main_game()