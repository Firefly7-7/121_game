"""
displays achievements for players
"""

from utility import Utility
from constants import BASE_ACHIEVEMENTS


class Achievements(Utility):
    """
    displays achievements for players to view
    """

    def achievements_place(self) -> None:
        """
        displays achievements place
        :return: nothing
        """

        self.buttons.add_button(self.make_text_button(
            "Back",
            20,
            self.change_place,
            (0, 0),
            (255, 255, 255),
            (0, 0, 0),
            5,
            arguments={"place": "start"},
            y_align=0,
            x_align=0,
            special_press="Back"
        ))  # 0

        line_height = 0
        lines = 0
        index = 0

        def change_index(change: int) -> None:
            """
            changes index looking at in displaying_achievement selection menu
            :param change:
            :return:
            """
            nonlocal index
            if change < 0:
                if index == 0:
                    return
            elif change > 0:
                if index >= len(self.achievements) - lines:
                    return
            index += change
            down = 0.5
            if index > 0:
                self.buttons[4 + index].rect.midleft = (240 * 4 + 20, 0)
            for i in range(index, min(index + lines, len(self.achievements))):
                down += 1
                self.buttons[5 + i].rect.y = 60 + down * line_height
                self.buttons[5 + i].rect.x = 0
            if index + lines < len(self.achievements):
                self.buttons[5 + index + lines].rect.midleft = (240 * 4 + 20, 0)

        self.buttons.add_button(self.make_text_button(
            "Up",
            20,
            change_index,
            (0, 60),
            max_lines=1,
            max_line_pixels=240 + 120 - 20,
            enforce_width=240 + 120 - 20,
            border_width=5,
            text_align=0.5,
            x_align=0,
            arguments={"change": -1}
        ))  # 1 up
        self.buttons.add_button(self.make_text_button(
            "Down",
            20,
            change_index,
            (0, 180 * 4 - 20),
            max_lines=1,
            max_line_pixels=240 + 120 - 20,
            enforce_width=240 + 120 - 20,
            border_width=5,
            text_align=0.5,
            x_align=0,
            arguments={"change": 1}
        ))  # 2 down

        self.buttons.add_button(None)  # 3 looking at name
        self.buttons.add_button(None)  # 4 looking at description/data

        def display_achievement(achievement_name: str) -> None:
            """
            puts an displaying_achievement's data to the display
            :param achievement_name: name of the displaying_achievement
            :return: none
            """
            self.buttons[3] = self.make_text_button(
                achievement_name,
                32,
                None,
                (240 * 4 - 240 - 60, 0),
                y_align=0,
                border_width=5,
                enforce_width=240 * 2 + 120,
                max_line_pixels=240 * 2 + 120,
                text_align=0.5,
                x_align=0.5
            )
            displaying_achievement = BASE_ACHIEVEMENTS[achievement_name]
            text = [displaying_achievement.description]
            if displaying_achievement.easter_egg_levels != ():
                text.append("\nGave levels:")
                for level in displaying_achievement.easter_egg_levels:
                    text.append(level)
            if displaying_achievement.skins != ():
                text.append("\nGave skins:")
                for skin in displaying_achievement.skins:
                    text.append(skin)
            if displaying_achievement.nest_achievements != ():
                text.append("\nCan give nested achievements:")
                for nested_achievement, *args in displaying_achievement.nest_achievements:
                    text.append(nested_achievement)
            self.buttons[4] = self.make_text_button(
                "\n".join(text),
                20,
                None,
                y_align=0,
                border_width=5,
                enforce_width=240 * 2 + 120 - 20,
                max_line_pixels=240 * 2 + 120 - 20,
                preserve_words=True,
                text_align=0,
                x_align=1,
                center=(240 * 4 - 10, self.buttons[3].rect.height + 10)
            )

        for achievement in self.achievements:  # 5+ look at displaying_achievement buttons
            self.buttons.add_button(self.make_text_button(
                achievement,
                20,
                display_achievement,
                (240 * 4 + 20, 0),
                x_align=0,
                text_align=0,
                max_lines=1,
                max_line_pixels=240 + 120 - 30,
                enforce_width=240 + 120 - 30,
                border_width=5,
                arguments={"achievement_name": achievement}
            ))

        line_height = self.buttons[1].rect.height + 10
        lines = (180 * 4 - 30 - 50) // line_height - 2
        index = 0

        change_index(0)

        while self.place == "achievements":
            self.tick()