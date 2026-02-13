"""Tests for board.py - 29 position board with lookup-table movement."""

import pytest

from yoot.board import Board


class TestBoardPositions:
    """Test board position structure."""

    def test_has_20_outer_positions(self):
        """Board has 20 outer positions (00-19)."""
        assert len(Board.OUTER_POSITIONS) == 20
        assert Board.OUTER_POSITIONS[0] == "00"
        assert Board.OUTER_POSITIONS[19] == "19"

    def test_has_right_diagonal(self):
        """Board has right diagonal with 5 positions."""
        assert len(Board.RIGHT_DIAGONAL) == 5
        assert Board.RIGHT_DIAGONAL == ["aa", "bb", "cc", "pp", "qq"]

    def test_has_left_diagonal(self):
        """Board has left diagonal with 5 positions (cc shared)."""
        assert len(Board.LEFT_DIAGONAL) == 5
        assert Board.LEFT_DIAGONAL == ["xx", "yy", "cc", "uu", "vv"]

    def test_total_29_unique_positions(self):
        """Board has 29 unique positions total."""
        all_positions = set(
            Board.OUTER_POSITIONS + Board.RIGHT_DIAGONAL + Board.LEFT_DIAGONAL
        )
        assert len(all_positions) == 29  # 20 + 5 + 5 - 1 (cc shared)


class TestOuterPathMovement:
    """Test movement on outer path."""

    def test_move_from_00(self):
        board = Board()
        assert board.get_next_position("00", 1) == "01"
        assert board.get_next_position("00", 5) == "05"

    def test_exact_landing_at_00(self):
        """Can only land exactly at 00, cannot overshoot."""
        board = Board()
        assert board.get_next_position("19", 1) == "00"
        assert board.get_next_position("18", 2) == "00"
        assert board.get_next_position("15", 5) == "00"

    def test_overshoot_past_00(self):
        """Moves that would pass through 00 are invalid."""
        board = Board()
        assert board.get_next_position("19", 2) is None
        assert board.get_next_position("18", 3) is None
        assert board.get_next_position("16", 5) is None

    def test_middle_outer_path(self):
        board = Board()
        assert board.get_next_position("06", 4) == "10"
        assert board.get_next_position("11", 4) == "15"
        assert board.get_next_position("14", 5) == "19"


class TestShortcutTriggers:
    """Test shortcut detection."""

    def test_05_triggers_shortcut(self):
        board = Board()
        assert board.triggers_shortcut("05") is True

    def test_10_triggers_shortcut(self):
        board = Board()
        assert board.triggers_shortcut("10") is True

    def test_other_positions_dont_trigger(self):
        board = Board()
        assert board.triggers_shortcut("00") is False
        assert board.triggers_shortcut("03") is False
        assert board.triggers_shortcut("15") is False
        assert board.triggers_shortcut("cc") is False


class TestBranchCell05:
    """Cell 05 is the right-diagonal branch. Shortcut only on landing, not passing."""

    def test_landing_on_05(self):
        board = Board()
        assert board.get_next_position("04", 1) == "05"
        assert board.get_next_position("00", 5) == "05"

    def test_passing_through_05_stays_outer(self):
        """Passing through 05 on outer path stays on outer."""
        board = Board()
        assert board.get_next_position("04", 3) == "07"
        assert board.get_next_position("03", 5) == "08"
        assert board.get_next_position("02", 4) == "06"

    def test_from_05_takes_diagonal(self):
        """Starting from 05 always enters diagonal."""
        board = Board()
        assert board.get_next_position("05", 1) == "aa"
        assert board.get_next_position("05", 2) == "bb"
        assert board.get_next_position("05", 3) == "cc"
        assert board.get_next_position("05", 4) == "uu"
        assert board.get_next_position("05", 5) == "vv"


class TestBranchCell10:
    """Cell 10 is the left-diagonal branch. Shortcut only on landing, not passing."""

    def test_landing_on_10(self):
        board = Board()
        assert board.get_next_position("09", 1) == "10"
        assert board.get_next_position("08", 2) == "10"

    def test_passing_through_10_stays_outer(self):
        """Passing through 10 on outer path stays on outer."""
        board = Board()
        assert board.get_next_position("09", 3) == "12"
        assert board.get_next_position("08", 5) == "13"
        assert board.get_next_position("07", 4) == "11"

    def test_from_10_takes_diagonal(self):
        """Starting from 10 always enters diagonal."""
        board = Board()
        assert board.get_next_position("10", 1) == "xx"
        assert board.get_next_position("10", 2) == "yy"
        assert board.get_next_position("10", 3) == "cc"
        assert board.get_next_position("10", 4) == "pp"
        assert board.get_next_position("10", 5) == "qq"


class TestRightDiagonal:
    """Test movement on right diagonal: 05 -> aa -> bb -> cc -> uu -> vv -> 15."""

    def test_aa_movement(self):
        board = Board()
        assert board.get_next_position("aa", 1) == "bb"
        assert board.get_next_position("aa", 2) == "cc"
        assert board.get_next_position("aa", 3) == "uu"
        assert board.get_next_position("aa", 4) == "vv"
        assert board.get_next_position("aa", 5) == "15"

    def test_bb_movement(self):
        board = Board()
        assert board.get_next_position("bb", 1) == "cc"
        assert board.get_next_position("bb", 2) == "uu"
        assert board.get_next_position("bb", 3) == "vv"
        assert board.get_next_position("bb", 4) == "15"
        assert board.get_next_position("bb", 5) == "16"

    def test_uu_movement(self):
        board = Board()
        assert board.get_next_position("uu", 1) == "vv"
        assert board.get_next_position("uu", 2) == "15"
        assert board.get_next_position("uu", 3) == "16"

    def test_vv_exits_to_15(self):
        board = Board()
        assert board.get_next_position("vv", 1) == "15"
        assert board.get_next_position("vv", 2) == "16"


class TestLeftDiagonal:
    """Test movement on left diagonal: 10 -> xx -> yy -> cc -> pp -> qq -> 00."""

    def test_xx_movement(self):
        board = Board()
        assert board.get_next_position("xx", 1) == "yy"
        assert board.get_next_position("xx", 2) == "cc"
        assert board.get_next_position("xx", 3) == "pp"
        assert board.get_next_position("xx", 4) == "qq"
        assert board.get_next_position("xx", 5) == "00"

    def test_yy_movement(self):
        board = Board()
        assert board.get_next_position("yy", 1) == "cc"
        assert board.get_next_position("yy", 2) == "pp"
        assert board.get_next_position("yy", 3) == "qq"
        assert board.get_next_position("yy", 4) == "00"

    def test_pp_movement(self):
        board = Board()
        assert board.get_next_position("pp", 1) == "qq"
        assert board.get_next_position("pp", 2) == "00"
        assert board.get_next_position("pp", 3) is None

    def test_qq_exits_to_00(self):
        board = Board()
        assert board.get_next_position("qq", 1) == "00"
        assert board.get_next_position("qq", 2) is None


class TestCrossroadCC:
    """Cell cc is the center crossroad. From cc, always toward goal (pp -> qq -> 00)."""

    def test_cc_always_toward_goal(self):
        board = Board()
        assert board.get_next_position("cc", 1) == "pp"
        assert board.get_next_position("cc", 2) == "qq"
        assert board.get_next_position("cc", 3) == "00"
        assert board.get_next_position("cc", 4) is None

    def test_passing_through_cc_on_05_diagonal(self):
        """Pieces on 05-diagonal pass through cc toward uu/vv/15."""
        board = Board()
        assert board.get_next_position("aa", 3) == "uu"
        assert board.get_next_position("aa", 4) == "vv"
        assert board.get_next_position("bb", 2) == "uu"
        assert board.get_next_position("bb", 3) == "vv"

    def test_passing_through_cc_on_10_diagonal(self):
        """Pieces on 10-diagonal pass through cc toward pp/qq/00."""
        board = Board()
        assert board.get_next_position("xx", 3) == "pp"
        assert board.get_next_position("xx", 4) == "qq"
        assert board.get_next_position("yy", 2) == "pp"
        assert board.get_next_position("yy", 3) == "qq"


class TestBackwardMovement:
    """Test back-do (-1 step)."""

    def test_outer_path_backward(self):
        board = Board()
        assert board.get_next_position("05", -1) == "04"
        assert board.get_next_position("01", -1) == "00"
        assert board.get_next_position("10", -1) == "09"

    def test_backward_from_00_valid(self):
        board = Board()
        # Back-do from 00 goes to first option (19) by default
        assert board.get_next_position("00", -1) == "19"
        # Full list of back-do destinations from 00
        assert board.get_back_do_destinations("00") == ["19", "qq"]

    def test_diagonal_backward(self):
        board = Board()
        assert board.get_next_position("aa", -1) == "05"
        assert board.get_next_position("bb", -1) == "aa"
        assert board.get_next_position("xx", -1) == "10"
        assert board.get_next_position("qq", -1) == "pp"
        assert board.get_next_position("vv", -1) == "uu"


class TestEntryPositions:
    """Test piece entry positions based on throw values."""

    def test_entry_positions(self):
        assert Board.get_entry_position(1) == "01"
        assert Board.get_entry_position(2) == "02"
        assert Board.get_entry_position(3) == "03"
        assert Board.get_entry_position(4) == "04"
        assert Board.get_entry_position(5) == "05"


class TestFinishCondition:
    """Test finish detection at position 00."""

    def test_position_00_without_moving_is_not_finish(self):
        assert Board.is_finish_position("00", has_moved=False) is False

    def test_position_00_after_moving_is_finish(self):
        assert Board.is_finish_position("00", has_moved=True) is True

    def test_other_positions_are_not_finish(self):
        assert Board.is_finish_position("05", has_moved=True) is False
        assert Board.is_finish_position("10", has_moved=True) is False


class TestBoardRendering:
    """Test board visualization."""

    def test_render_empty_board(self):
        board = Board()
        rendered = board.render_board([])
        assert isinstance(rendered, str)
        assert "00" in rendered
        lines = [line for line in rendered.split("\n") if line or line == ""]
        assert len(lines) >= 11

    def test_render_with_pieces(self):
        from yoot import Piece

        board = Board()
        piece1 = Piece(0, 0)
        piece1.position = "01"
        piece1.is_active = True

        piece2 = Piece(1, 1)
        piece2.position = "10"
        piece2.is_active = True

        rendered = board.render_board([piece1, piece2])
        assert "P0" in rendered or "x" in rendered
        assert "P1" in rendered or "x" in rendered

    def test_is_valid_position(self):
        board = Board()
        assert board.is_valid_position("00")
        assert board.is_valid_position("19")
        assert board.is_valid_position("aa")
        assert board.is_valid_position("cc")
        assert not board.is_valid_position("zz")
        assert not board.is_valid_position("21")
