"""
Game piece representation for Yut Nori.
"""

from typing import Optional


class Piece:
    """
    Represents a single game piece (말).

    Attributes:
        piece_id: Unique identifier for this piece within the player (0-3)
        player_id: Which player owns this piece (0-3)
        position: Current board position (string: '00'-'19', 'aa'-'qq', 'xx'-'vv')
                  None = not entered yet
        is_active: Whether piece is currently on board and moveable
        has_moved: Whether piece has started moving (to distinguish 00 start vs finish)
    """

    def __init__(self, piece_id: int, player_id: int):
        self.piece_id = piece_id
        self.player_id = player_id
        self.position: Optional[str] = None
        self.is_active = False
        self.has_moved = False

    def enter_board(self, entry_position: str):
        """Place piece on board."""
        self.position = entry_position
        self.is_active = True
        self.has_moved = True

    def move_to(self, position: str):
        """Move piece to a new position."""
        self.position = position
        self.has_moved = True

    def finish(self):
        """Mark piece as finished (returned to 00 after going around)."""
        self.position = None
        self.is_active = False

    def capture(self):
        """Remove piece from board (captured by opponent)."""
        self.position = None
        self.is_active = False
        self.has_moved = False

    def has_finished(self) -> bool:
        """Check if piece has reached the goal (finished)."""
        return not self.is_active and self.has_moved and self.position is None

    def __repr__(self):
        return f"Piece(P{self.player_id}#{self.piece_id}, pos={self.position})"
