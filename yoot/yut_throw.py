"""
Yut stick throwing mechanics.
"""

import random
from typing import Tuple


class YutThrow:
    """
    Handles yut stick throwing simulation.

    Four sticks are thrown, each can land flat or round side up.
    """

    # Throw results mapped to Korean names
    THROW_NAMES = {
        1: "do",  # 도 (1 flat)
        2: "gae",  # 개 (2 flat)
        3: "geol",  # 걸 (3 flat)
        4: "yut",  # 윷 (4 flat)
        0: "mo",  # 모 (0 flat, all round)
    }

    # Move values for each throw
    MOVE_VALUES = {
        "do": 1,
        "back_do": -1,  # 빽도 - backwards Do
        "gae": 2,
        "geol": 3,
        "yut": 4,
        "mo": 5,
    }

    # Throws that grant extra turn
    EXTRA_TURN_THROWS = {"yut", "mo"}

    # Probability of each stick landing flat side up
    # Real yut sticks are biased - flat side lands up MORE often than convex side
    # Research shows approximately 60% probability of flat side up
    FLAT_PROBABILITY = 0.6  # 60% chance flat side up, 40% convex side up

    @staticmethod
    def throw() -> Tuple[str, int]:
        """
        Simulate throwing 4 yut sticks.

        One stick is designated as "back Do" - if Do is thrown and that
        stick is the flat one, it's back Do (move backwards).

        Yut sticks are unfair coins: 60% chance of landing flat side up.

        Returns:
            Tuple of (throw_name, move_value)
        """
        # Simulate which sticks land flat (0-3 indices)
        sticks = [
            1 if random.random() < YutThrow.FLAT_PROBABILITY else 0 for _ in range(4)
        ]
        flat_count = sum(sticks)

        throw_name = YutThrow.THROW_NAMES[flat_count]

        # Special case: if Do (1 flat), check if it's the back Do stick
        if throw_name == "do":
            # Find which stick is flat (0-3)
            flat_stick_idx = sticks.index(1)
            # Stick 0 is designated as the "back Do" stick
            if flat_stick_idx == 0:
                throw_name = "back_do"

        move_value = YutThrow.MOVE_VALUES[throw_name]

        return throw_name, move_value

    @staticmethod
    def grants_extra_turn(throw_name: str) -> bool:
        """Check if throw grants another turn."""
        return throw_name in YutThrow.EXTRA_TURN_THROWS

    @staticmethod
    def get_move_value(throw_name: str) -> int:
        """Get movement value for a throw result."""
        return YutThrow.MOVE_VALUES[throw_name]
