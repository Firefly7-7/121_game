"""
contains class for start area
"""

from utility import Utility
from pygame.transform import smoothscale
from webbrowser import open_new_tab
from skin_management import draw_skin


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
            if self.name == "24132231":
                self.give_achievement("14233221")
            elif self.name == "14233221":
                self.change_place("achievements")
                return
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
                100,
                title_click,
                (240 * 2, 100),
                (255, 255, 255),
                (0, 0, 0),
                5,
                arguments={}
            )

        skins = tuple(self.skins.keys())

        def change_skin(direction: int) -> None:
            """
            changes what skin the player is using
            :param direction: direction going (-1 back left through list, 1 right through list)
            :return: none
            """
            nonlocal player_img
            self.skin_using = skins[(skins.index(self.skin_using) + direction) % len(skins)]
            self.player_img = draw_skin(self.skins[self.skin_using])
            player_img = smoothscale(self.player_img, (270, 270))
            self.replace_button(8, self.make_text_button(
                self.skin_using,
                40,
                self.change_place,
                (240 * 2, 180 * 2 + 135 + 10),
                (255, 255, 255),
                (0, 0, 0),
                5,
                arguments={"place": "level_select"},
                y_align=0,
                x_align=0.5,
            ))

        self.add_button(self.make_text_button(
            self.name,
            100,
            title_click,
            (240 * 2, 100),
            (255, 255, 255),
            (0, 0, 0),
            5,
            arguments={}
        ))  # 0
        self.add_button(self.make_text_button(
            "Options",
            50,
            self.change_place,
            (0, 180 * 4),
            (255, 255, 255),
            (0, 0, 0),
            5,
            max_width=220,
            arguments={"place": "options"},
            y_align=1,
            x_align=0
        ))  # 1
        self.add_button(self.make_text_button(
            "Tutorial",
            50,
            self.change_place,
            (240 * 4, 180 * 4),
            (255, 255, 255),
            (0, 0, 0),
            5,
            max_width=220,
            arguments={"place": "tutorial"},
            y_align=1,
            x_align=1,
        ))  # 2
        self.add_button(self.make_text_button(
            "Levels",
            100,
            self.change_place,
            (240 * 2, 180 * 4),
            (255, 255, 255),
            (0, 0, 0),
            5,
            arguments={"place": "level_select"},
            y_align=1,
            x_align=0.5,
            special_press="Play",
            max_width=350
        ))  # 3
        self.add_button(self.make_text_button(
            "Open Scratch version",
            20,
            open_new_tab,
            (0, 0),
            (255, 255, 255),
            (0, 0, 0),
            5,
            arguments={"url": "https://scratch.mit.edu/projects/631515625/"},
            y_align=0,
            x_align=0,
        ))  # 4
        self.add_button(self.make_text_button(
            "Open Github",
            20,
            open_new_tab,
            (0, self.buttons[-1].rect.height + 5),
            (255, 255, 255),
            (0, 0, 0),
            5,
            arguments={"url": "https://github.com/Firefly7-7/121_game"},
            y_align=0,
            x_align=0,
        ))  # 5
        self.add_button(self.make_text_button(
            "Discord",
            20,
            open_new_tab,
            (0, self.buttons[-2].rect.height + self.buttons[-1].rect.height + 10),
            (255, 255, 255),
            (0, 0, 0),
            5,
            arguments={"url": "https://discord.gg/ETVgSDB5VW"},
            y_align=0,
            x_align=0,
        ))  # 6
        self.add_button(self.make_text_button(
            "Credits",
            20,
            self.change_place,
            (240 * 4, 0),
            (255, 255, 255),
            (0, 0, 0),
            5,
            arguments={"place": "credits"},
            y_align=0,
            x_align=1,
        ))  # 7
        if len(skins) > 1:
            self.add_button(self.make_text_button(
                self.skin_using,
                40,
                None,
                (240 * 2, 180 * 2 + 135 + 10),
                (255, 255, 255),
                (0, 0, 0),
                5,
                y_align=0,
                x_align=0.5
            ))  # 8
            self.add_button(self.make_text_button(
                "<",
                50,
                change_skin,
                (240 * 2 - 135 - 10, 180 * 2),
                (255, 255, 255),
                (0, 0, 0),
                5,
                arguments={"direction": -1},
                y_align=0.5,
                x_align=1,
                special_press="Left"
            ))  # 9
            self.add_button(self.make_text_button(
                ">",
                50,
                change_skin,
                (240 * 2 + 135 + 10, 180 * 2),
                (255, 255, 255),
                (0, 0, 0),
                5,
                arguments={"direction": 1},
                y_align=0.5,
                x_align=0,
                special_press="Right"
            ))  # 10

        player_img = smoothscale(self.player_img, (270, 270))

        while self.place == "start":
            self.tick()
            self.screen.blit(player_img, (240 * 2 - 135, 180 * 2 - 135))
