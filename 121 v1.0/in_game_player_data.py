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
        self.pos = pos
        self.mom = [0, 0]
        self.block_record: set[BlockType] = set()
        self.scheduled: dict[tuple[int, int], tuple[int, int]] = dict()
        self.grounded: bool = False