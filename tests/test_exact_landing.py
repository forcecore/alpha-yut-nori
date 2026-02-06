"""Tests for exact landing requirement at goal (00)."""

from yoot import Board


class TestExactLandingAtGoal:
    """Pieces heading toward 00 must land exactly, cannot overshoot."""

    def test_from_cc(self):
        """From cc: cc -> pp -> qq -> 00. Beyond 3 steps is overshoot."""
        board = Board()
        assert board.get_next_position('cc', 1) == 'pp'
        assert board.get_next_position('cc', 2) == 'qq'
        assert board.get_next_position('cc', 3) == '00'
        assert board.get_next_position('cc', 4) is None
        assert board.get_next_position('cc', 5) is None

    def test_from_qq(self):
        """From qq: one step to 00. Beyond is overshoot."""
        board = Board()
        assert board.get_next_position('qq', 1) == '00'
        assert board.get_next_position('qq', 2) is None
        assert board.get_next_position('qq', 3) is None

    def test_from_pp(self):
        """From pp: pp -> qq -> 00. Beyond 2 steps is overshoot."""
        board = Board()
        assert board.get_next_position('pp', 1) == 'qq'
        assert board.get_next_position('pp', 2) == '00'
        assert board.get_next_position('pp', 3) is None

    def test_from_outer_path(self):
        """Outer path positions near 00 must land exactly."""
        board = Board()
        assert board.get_next_position('19', 1) == '00'
        assert board.get_next_position('19', 2) is None

        assert board.get_next_position('18', 2) == '00'
        assert board.get_next_position('18', 3) is None

        assert board.get_next_position('16', 4) == '00'
        assert board.get_next_position('16', 5) is None


class TestDiagonalExitTo15:
    """Right diagonal exits to 15 and continues on outer path (no exact landing at 15)."""

    def test_from_vv(self):
        """vv exits to 15, then continues on outer."""
        board = Board()
        assert board.get_next_position('vv', 1) == '15'
        assert board.get_next_position('vv', 2) == '16'
        assert board.get_next_position('vv', 5) == '19'

    def test_from_uu(self):
        """uu -> vv -> 15, then continues on outer."""
        board = Board()
        assert board.get_next_position('uu', 1) == 'vv'
        assert board.get_next_position('uu', 2) == '15'
        assert board.get_next_position('uu', 3) == '16'
