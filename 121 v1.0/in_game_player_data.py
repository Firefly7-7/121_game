"""
handles data for in game player data
"""


from block_data import BlockType


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
        self.scheduled: dict[tuple[int, int], tuple[int, int]] = dict()
        self.grounded: bool = False
        self.stop: bool = False
        self.corrected: bool = False