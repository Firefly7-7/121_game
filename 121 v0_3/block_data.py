"""
data for blocks
"""
from dataclasses import dataclass
from typing import Any


@dataclass()
class Block:
    """
    dataclass containing block data
    """
    type: str  # type of main block
    barriers: list[  # list of barriers
        tuple[  # single barrier object
            str,  # name of type
            bool,  # if gravity locked (False if does not move with gravity, True if does)
            tuple[  # tuple of if sides are there
                bool,  # 0, up
                bool,  # 1, right
                bool,  # 2, down
                bool  # 3, left
            ]
        ]
    ]
    other: dict[str, Any] = ()  # dictionary containing any extra tags the block needs