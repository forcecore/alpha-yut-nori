"""
Main game engine for Yut Nori.
"""

from typing import Dict, List, Optional, Tuple

from .board import Board
from .piece import Piece
from .player import Player
from .yut_throw import YutThrow


class YutGame:
    """
    Main game engine managing game state and rules.
    """

    def __init__(self, player_names: Optional[List[str]] = None, num_players: int = 4):
        if num_players < 2 or num_players > 6:
            raise ValueError("Number of players must be between 2 and 6")

        if player_names is None:
            player_names = [f"Player {i}" for i in range(num_players)]

        if len(player_names) != num_players:
            raise ValueError(f"Must provide exactly {num_players} player names")

        self.board = Board()
        self.num_players = num_players
        self.players = [Player(i, name) for i, name in enumerate(player_names)]
        self.current_player_idx = 0
        self.game_state = "playing"
        self.winner: Optional[int] = None  # first player to finish (back-compat)
        self.rankings: List[int] = []  # player_ids in finish order
        self.accumulated_moves: List[int] = []
        self.move_history: List[str] = []

    def get_current_player(self) -> Player:
        """Get the current player whose turn it is."""
        return self.players[self.current_player_idx]

    def throw_phase(self, is_bonus: bool = False) -> List[Tuple[str, int]]:
        """
        Execute throwing phase for current turn.
        Keep throwing until no Yut/Mo is rolled.
        """
        throws = []

        if not is_bonus:
            self.accumulated_moves = []

        while True:
            throw_name, move_value = YutThrow.throw()
            throws.append((throw_name, move_value))
            self.accumulated_moves.append(move_value)

            bonus_msg = " (bonus)" if is_bonus else ""
            self.log_move(
                f"{self.get_current_player().name} threw {throw_name} ({move_value} spaces){bonus_msg}"
            )

            if not YutThrow.grants_extra_turn(throw_name):
                break

        return throws

    def get_legal_moves(self, player_id: int) -> List[Tuple[int, int, str]]:
        """
        Get all legal moves for a player with current accumulated moves.

        Returns:
            List of (piece_id, steps, destination) tuples
            piece_id = -1 means entering a new piece
        """
        player = self.players[player_id]
        legal_moves = []

        for piece in player.get_active_pieces():
            for steps in self.accumulated_moves:
                if steps == -1:
                    for dest in self.board.get_back_do_destinations(piece.position):
                        legal_moves.append((piece.piece_id, steps, dest))
                else:
                    dest = self.board.get_next_position(piece.position, steps)
                    if dest is not None:
                        legal_moves.append((piece.piece_id, steps, dest))

        # Check if new piece can enter
        if player.can_enter_new_piece() and self.accumulated_moves:
            for steps in self.accumulated_moves:
                if 1 <= steps <= 5:
                    entry_pos = f"{steps:02d}"
                    legal_moves.append((-1, steps, entry_pos))

        return legal_moves

    def move_piece(
        self, player_id: int, piece_id: int, steps: int, destination: str | None = None
    ) -> tuple[bool, bool]:
        """
        Execute a single piece movement.

        Returns:
            Tuple of (success, captured)
        """
        player = self.players[player_id]

        # Handle entering new piece
        if piece_id == -1:
            if not player.can_enter_new_piece():
                return False, False
            if steps not in self.accumulated_moves:
                return False, False
            if not (1 <= steps <= 5):
                return False, False

            entry_position = f"{steps:02d}"
            new_piece = player.get_inactive_pieces()[0]
            new_piece.enter_board(entry_position)
            self.accumulated_moves.remove(steps)

            shortcut = self.board.triggers_shortcut(entry_position)
            if shortcut:
                self.log_move(
                    f"{player.name} entered new piece (Piece {new_piece.piece_id}) at position {entry_position} (shortcut position)"
                )
            else:
                self.log_move(
                    f"{player.name} entered new piece (Piece {new_piece.piece_id}) at position {entry_position}"
                )

            captured = self.check_capture(player_id, new_piece.position)
            return True, captured

        # Handle moving existing piece
        piece = player.get_piece_by_id(piece_id)

        if not piece.is_active:
            return False, False

        if steps not in self.accumulated_moves:
            return False, False

        current_pos = piece.position

        # Special case: at 00 with has_moved → piece exits the board (but not on back-do)
        if current_pos == "00" and piece.has_moved and steps != -1:
            stack = self._get_stack_at_position(player_id, current_pos)
            piece_str = (
                f"Piece {piece_id}" if len(stack) == 1 else f"Stack (x{len(stack)})"
            )

            for stacked_piece in stack:
                stacked_piece.finish()

            self.accumulated_moves.remove(steps)
            self.log_move(f"{player.name}'s {piece_str} exited the board!")
            return True, False

        # For back-do with explicit destination, use it directly
        if steps == -1 and destination is not None:
            valid = self.board.get_back_do_destinations(current_pos)
            if destination not in valid:
                return False, False
            new_pos = destination
        else:
            new_pos = self.board.get_next_position(current_pos, steps)

        if new_pos is None:
            return False, False

        # Get all pieces in stack at current position
        stack = self._get_stack_at_position(player_id, current_pos)

        # Move all pieces in stack
        for stacked_piece in stack:
            stacked_piece.move_to(new_pos)

        self.accumulated_moves.remove(steps)

        piece_str = f"Piece {piece_id}" if len(stack) == 1 else f"Stack (x{len(stack)})"

        if new_pos == "00":
            self.log_move(
                f"{player.name} moved {piece_str} {steps} spaces to position 00 (at goal - next move exits)"
            )
        elif self.board.triggers_shortcut(new_pos):
            self.log_move(
                f"{player.name} moved {piece_str} {steps} spaces to {new_pos} (shortcut position - next move uses diagonal)"
            )
        else:
            self.log_move(
                f"{player.name} moved {piece_str} {steps} spaces to {new_pos}"
            )

        captured = self.check_capture(player_id, new_pos)

        return True, captured

    def _get_stack_at_position(self, player_id: int, position: str) -> List[Piece]:
        """Get all pieces of a player at a specific position."""
        player = self.players[player_id]
        return [p for p in player.get_active_pieces() if p.position == position]

    def check_capture(self, player_id: int, position: str) -> bool:
        """Check if a piece at position captures opponent pieces."""

        captured_any = False

        for other_player in self.players:
            if other_player.player_id == player_id:
                continue

            captured_pieces = [
                p for p in other_player.get_active_pieces() if p.position == position
            ]

            if captured_pieces:
                captured_any = True
                for piece in captured_pieces:
                    piece.capture()
                    self.log_move(
                        f"{self.players[player_id].name} captured "
                        f"{other_player.name}'s Piece {piece.piece_id}!"
                    )

        return captured_any

    def check_win_condition(self) -> bool:
        """Check if any player has newly finished. Game ends when only one remains."""
        changed = False
        for player in self.players:
            if player.has_finished() and player.player_id not in self.rankings:
                self.rankings.append(player.player_id)
                place = len(self.rankings)
                self.log_move(f"{player.name} finishes in place #{place}!")
                if self.winner is None:
                    self.winner = player.player_id
                changed = True

        # Game over when all but one player have finished
        remaining = [p for p in self.players if p.player_id not in self.rankings]
        if len(remaining) <= 1:
            if remaining:
                self.rankings.append(remaining[0].player_id)
            self.game_state = "finished"
            return True

        return changed

    def next_turn(self):
        """Advance to next player's turn, skipping finished players."""
        for _ in range(self.num_players):
            self.current_player_idx = (self.current_player_idx + 1) % self.num_players
            if self.current_player_idx not in self.rankings:
                break
        self.accumulated_moves = []

    def log_move(self, message: str):
        """Add entry to move history."""
        self.move_history.append(message)

    def get_game_state(self) -> Dict:
        """Get current game state as dictionary."""
        return {
            "current_player": self.current_player_idx,
            "game_state": self.game_state,
            "winner": self.winner,
            "rankings": self.rankings.copy(),
            "accumulated_moves": self.accumulated_moves.copy(),
            "players": [
                {
                    "id": p.player_id,
                    "name": p.name,
                    "active_pieces": len(p.get_active_pieces()),
                    "finished_pieces": len(p.get_finished_pieces()),
                    "pieces": [
                        {
                            "id": piece.piece_id,
                            "position": piece.position,
                            "is_active": piece.is_active,
                        }
                        for piece in p.pieces
                    ],
                }
                for p in self.players
            ],
            "move_history": self.move_history[-10:],
        }

    def get_all_pieces(self) -> List[Piece]:
        """Get all pieces from all players for board rendering."""
        pieces = []
        for player in self.players:
            pieces.extend(player.pieces)
        return pieces
