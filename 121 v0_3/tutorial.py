"""
holds tutorial information
"""

from in_game import InGame
from level_management import decode_safety_wrap
from pygame.key import name


class Tutorial(InGame):
    """
    tutorial class
    """

    # noinspection SpellCheckingInspection
    def tutorial_place(self) -> None:
        """
        runs tutorial place
        :return: None
        """

        def single_level(level_string: str, welcome_message: str) -> None:
            """
            runs a single level.  You can never escape!
            :return: None
            """
            if not self.running:
                return
            self.place = "in_game"
            self.won = False
            self.level_data = decode_safety_wrap(level_string)
            self.in_game_place(welcome_message, False)

        single_level(
            "3oStartoppnn|||ttpnn",
            f"Reach the goal block by pressing {name(self.controls[1].value)}.  Controls can be customized in the options menu later."
        )
        single_level(
            "3xTutorial1oppnn|t|ttpn↚p?These message blocks can give important information.t↯nn",
            f"Try running into that msg block in the middle."
        )
        single_level(
            "3xTutorial2oppnn|t|tt↯n|↠tpnn",
            "Sometimes messages will show up here automatically."
        )
        single_level(
            "3xTutorial3oppnn|t|ttpn>q1+Bouncy Castlet↯pn",
            "At the top is an Easter Egg block.  None of them are necessary to complete or play the game.  You can't reach it."
        )
        single_level(
            "3xTutorial4opptt|0a|n↬tnnatn↬t|naan↬ttn↯onnn↬tan↯↯nnn↬tona↣n↬t↯na0n↬tqna↛n↬t↛n↯xnnn↬txna+n↬t↠n|ttp|+p↠Oh.  How?n↬tpnn",
            "On the bottom is a variety of the blocks that exist in this game.  Each has a different function.  You can't touch them here."
        )
        single_level(
            "3↯Finishoppnn|t||nt|o|ntnt|a|atotoa↯o↯aq↯qo↛↯↛qxqx↛↠↛p↛↠qpqx↯↠↯p↯↛oxo↠opoqa↛axa↠apa↯tqt↛txt↠tpto|onanqn↯n↯|q|↛|↛nxnx|↠|↠npnp||ttpxn",
            f"You need to jump! ({name(self.controls[0].value)})\n\nContinue playing the game to learn more."
        )
        if self.running:
            self.place = "start"