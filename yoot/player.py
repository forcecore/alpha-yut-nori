"""
Player state management for Yut Nori.
"""

from typing import Dict, List

from .piece import Piece


class Player:
    """
    Represents a player in the game.

    Each player has 4 pieces and tracks their state.
    """

    NUM_PIECES = 4

    def __init__(self, player_id: int, name: str):
        self.player_id = player_id
        self.name = name
        self.pieces: List[Piece] = [
            Piece(piece_id=i, player_id=player_id) for i in range(self.NUM_PIECES)
        ]

    def get_active_pieces(self) -> List[Piece]:
        """Get all pieces currently on the board."""
        return [p for p in self.pieces if p.is_active]

    def get_finished_pieces(self) -> List[Piece]:
        """Get all pieces that reached the goal."""
        return [p for p in self.pieces if p.has_finished()]

    def get_inactive_pieces(self) -> List[Piece]:
        """Get pieces not yet entered on board."""
        return [p for p in self.pieces if not p.is_active and not p.has_finished()]

    def has_finished(self) -> bool:
        """Check if all pieces have reached the goal."""
        return len(self.get_finished_pieces()) == self.NUM_PIECES

    def get_stacks(self) -> Dict[str, List[Piece]]:
        """
        Group pieces by position (stacks).

        Returns:
            Dictionary mapping position to list of pieces at that position
        """
        stacks: Dict[str, List[Piece]] = {}
        for piece in self.get_active_pieces():
            pos = piece.position
            if pos is not None:
                if pos not in stacks:
                    stacks[pos] = []
                stacks[pos].append(piece)
        return stacks

    def get_piece_by_id(self, piece_id: int) -> Piece:
        """Get piece by its ID."""
        return self.pieces[piece_id]

    def can_enter_new_piece(self) -> bool:
        """Check if player has any pieces not yet on board."""
        return len(self.get_inactive_pieces()) > 0

    def __repr__(self):
        active = len(self.get_active_pieces())
        finished = len(self.get_finished_pieces())
        return f"Player(id={self.player_id}, name='{self.name}', active={active}, finished={finished})"
