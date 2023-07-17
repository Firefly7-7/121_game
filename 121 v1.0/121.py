"""
main file for 121 game
"""

from start import Start
from options import Options
from level_select import LevelSelect
from enter_and_exit import EnterAndExit
from tutorial import Tutorial
from credits import Credits
from construction import Construction
from player_data import PlayerData, save_player_data
from achievements import Achievements


class Game(Start, Options, LevelSelect, EnterAndExit, Tutorial, Credits, Construction, Achievements):
    """
    class that runs the entire game
    init in utility
    """

    ran = False

    def main_game(self) -> None:
        """
        loop that handles travel between different locations
        :return: None
        """
        if self.ran:
            print("Don't do that?")
        self.ran = True
        try:
            while self.running:
                self.button_hover_keyed = -1
                self.buttons.clear()
                self.end_typing()
                if self.place == "testing":
                    self.testing_place()
                elif self.place == "start":
                    self.start_place()
                elif self.place == "options":
                    self.options_place()
                elif self.place == "level_select":
                    self.level_select_place()
                elif self.place == "construction":
                    self.construction_place()
                elif self.place == "enter_level":
                    self.enter_level_place()
                elif self.place == "exit_level":
                    self.exit_level_place()
                elif self.place == "in_game":
                    self.in_game_place()
                elif self.place == "credits":
                    self.credits_place()
                elif self.place == "tutorial":
                    self.tutorial_place()
                elif self.place == "export":
                    raise ValueError(f"Area '{self.place}' has not been prepared.")
                elif self.place == "achievements":
                    self.achievements_place()
                else:
                    raise ValueError(f"Area '{self.place}' does not exist.")
        finally:
            controls = dict()
            for control in self.controls:
                controls[control.name] = control.value
            player = PlayerData(
                self.level_on,
                self.levels[0],
                self.skin_using,
                self.skins,
                self.working_on,
                controls,
                self.achievements
            )
            save_player_data(player)

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


if __name__ == "__main__":
    Game().main_game()