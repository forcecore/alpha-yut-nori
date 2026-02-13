"""
Tests for Piece and Player classes.
"""

import pytest

from yoot import Piece, Player


class TestPiece:
    """Test Piece class."""

    def test_piece_initialization(self):
        """Test piece is created with correct initial state."""
        piece = Piece(piece_id=0, player_id=1)
        assert piece.piece_id == 0
        assert piece.player_id == 1
        assert piece.position is None
        assert not piece.is_active

    def test_enter_board(self):
        """Test piece entering board."""
        piece = Piece(0, 0)
        piece.enter_board("05")
        assert piece.position == "05"
        assert piece.is_active
        assert piece.has_moved

    def test_move_to(self):
        """Test piece movement."""
        piece = Piece(0, 0)
        piece.enter_board("01")
        piece.move_to("05")
        assert piece.position == "05"
        assert piece.is_active

    def test_move_to_goal(self):
        """Test piece finishing at goal."""
        piece = Piece(0, 0)
        piece.enter_board("01")
        piece.finish()
        assert piece.position is None
        assert not piece.is_active
        assert piece.has_finished()

    def test_capture(self):
        """Test piece capture."""
        piece = Piece(0, 0)
        piece.enter_board("05")
        piece.capture()
        assert piece.position is None
        assert not piece.is_active
        assert not piece.has_moved  # Reset on capture

    def test_has_finished(self):
        """Test checking if piece finished."""
        piece = Piece(0, 0)
        assert not piece.has_finished()

        # Just setting position to None is not enough
        piece.position = None
        assert not piece.has_finished()

        # Must finish properly
        piece.enter_board("01")
        piece.finish()
        assert piece.has_finished()


class TestPlayer:
    """Test Player class."""

    def test_player_initialization(self):
        """Test player is created with correct initial state."""
        player = Player(player_id=0, name="Alice")
        assert player.player_id == 0
        assert player.name == "Alice"
        assert len(player.pieces) == 4
        assert all(p.player_id == 0 for p in player.pieces)

    def test_get_active_pieces(self):
        """Test getting active pieces."""
        player = Player(0, "Alice")
        assert len(player.get_active_pieces()) == 0

        player.pieces[0].enter_board("01")
        player.pieces[1].enter_board("05")
        assert len(player.get_active_pieces()) == 2

    def test_get_finished_pieces(self):
        """Test getting finished pieces."""
        player = Player(0, "Alice")
        assert len(player.get_finished_pieces()) == 0

        player.pieces[0].enter_board("01")
        player.pieces[0].finish()
        assert len(player.get_finished_pieces()) == 1

    def test_get_inactive_pieces(self):
        """Test getting inactive pieces."""
        player = Player(0, "Alice")
        assert len(player.get_inactive_pieces()) == 4

        player.pieces[0].enter_board("01")
        assert len(player.get_inactive_pieces()) == 3

    def test_has_finished(self):
        """Test checking if player has won."""
        player = Player(0, "Alice")
        assert not player.has_finished()

        # Finish all pieces
        for piece in player.pieces:
            piece.enter_board("01")
            piece.finish()
        assert player.has_finished()

    def test_get_stacks(self):
        """Test getting piece stacks."""
        player = Player(0, "Alice")
        player.pieces[0].enter_board("05")
        player.pieces[1].enter_board("05")
        player.pieces[2].enter_board("10")

        stacks = player.get_stacks()
        assert "05" in stacks
        assert len(stacks["05"]) == 2
        assert "10" in stacks
        assert len(stacks["10"]) == 1

    def test_get_piece_by_id(self):
        """Test getting piece by ID."""
        player = Player(0, "Alice")
        piece = player.get_piece_by_id(2)
        assert piece.piece_id == 2
        assert piece.player_id == 0

    def test_can_enter_new_piece(self):
        """Test checking if player can enter new piece."""
        player = Player(0, "Alice")
        assert player.can_enter_new_piece()

        # Enter all pieces
        for piece in player.pieces:
            piece.enter_board("01")
        assert not player.can_enter_new_piece()
