"""
contains class for start area
"""

from utility import Utility
from pygame.transform import smoothscale


class Start(Utility):
    """
    class for start area
    """

    def start_place(self) -> None:
        """
        handles start screen setup then initiates a loop that handles start screen
        :return: None
        """

        def title_click() -> None:
            """
            preserve the easter egg
            :return: None
            """
            work_list = list()
            for char in self.name:
                while int(char) >= len(work_list):
                    work_list.append(0)
                work_list[int(char) - 1] += 1
            self.name = ""
            for i in range(len(work_list)):
                if work_list[i] > 0:
                    self.name = str(work_list[i]) + str(i + 1) + self.name
            self.buttons[0] = self.make_text_button(
                self.name,
                self.fonts[100],
                title_click,
                (240 * 2, 100),
                (255, 255, 255),
                (0, 0, 0),
                5,
                arguments={}
            )

        self.add_button(self.make_text_button(
            self.name,
            self.fonts[100],
            title_click,
            (240 * 2, 100),
            (255, 255, 255),
            (0, 0, 0),
            5,
            arguments={}
        ))
        self.add_button(self.make_text_button(
            "Options",
            self.fonts[50],
            self.change_place,
            (0, 180 * 4),
            (255, 255, 255),
            (0, 0, 0),
            5,
            arguments={"place": "options"},
            y_align=1,
            x_align=0
        ))
        self.add_button(self.make_text_button(
            "Levels",
            self.fonts[100],
            self.change_place,
            (240 * 2, 180 * 4),
            (255, 255, 255),
            (0, 0, 0),
            5,
            arguments={"place": "level_select"},
            y_align=1,
            x_align=0.5,
            special_press="Play"
        ))

        player_img = smoothscale(self.player_img, (270, 270))

        while self.place == "start":
            self.tick()
            self.screen.blit(player_img, (240 * 2 - 135, 180 * 2 - 135))
            self.handle_buttons()
