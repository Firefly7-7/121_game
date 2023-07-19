"""
handles data for in game player data
"""


from block_data import BlockType
from copy import copy
from game_structures import Collision


class InGamePlayer:
    """
    handles data for player entities in game
    """

    def __init__(
            self,
            pos: list[int, int]
    ):
        """
        create a player entity
        """
        self.pos: list[int, float] = pos
        self.mom: list[int, float] = [0, 0]
        self.block_record: set[BlockType] = set()
        self.collision_record: tuple[list[Collision]] = tuple()
        self.scheduled: dict[tuple[int, int], tuple[int, int]] = dict()
        self.grounded: bool = False
        self.stop: bool = False
        self.corrected: bool = False


class InGamePlayerInBetween:
    """
    handles data in
    """

    def __init__(
            self,
            player: InGamePlayer
    ):
        """
        generates pared down player for this
        :param player:
        """
        self.pos = copy(player.pos)
        self.mom = [player.mom[0] / 2, player.mom[1] / 2]