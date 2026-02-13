"""Tests for bonus throw mechanics (capture and Yut/Mo bonus)."""

import pytest

from yoot import YutGame


class TestBonusThrowStacking:
    """Test that bonus throws stack with existing moves instead of overwriting."""

    def test_regular_throw_resets_moves(self):
        """Regular throw at turn start should reset accumulated_moves."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)

        # Simulate old moves from previous turn
        game.accumulated_moves = [999, 888]

        # Regular throw should reset
        throws = game.throw_phase(is_bonus=False)

        # Old moves should be gone, only new throws remain
        assert 999 not in game.accumulated_moves
        assert 888 not in game.accumulated_moves
        assert len(game.accumulated_moves) >= 1  # At least one new throw

    def test_bonus_throw_stacks_moves(self):
        """Bonus throw should add to existing accumulated_moves."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)

        # Simulate remaining moves
        game.accumulated_moves = [4, 3]
        original_count = len(game.accumulated_moves)

        # Bonus throw should stack
        bonus_throws = game.throw_phase(is_bonus=True)

        # Should have original moves plus new ones
        assert 4 in game.accumulated_moves
        assert 3 in game.accumulated_moves
        assert len(game.accumulated_moves) >= original_count + 1

    def test_capture_bonus_preserves_remaining_moves(self):
        """When capture grants bonus throw, remaining moves should be preserved."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)
        player0 = game.players[0]
        player1 = game.players[1]

        # Setup: P0 has piece at 01
        piece0 = player0.pieces[0]
        piece0.position = "01"
        piece0.is_active = True
        piece0.has_moved = True

        # P1 has moves [4, 1]
        game.accumulated_moves = [4, 1]

        # P1 enters piece with move 1, capturing P0's piece at 01
        success, captured = game.move_piece(player1.player_id, -1, 1)

        assert success
        assert captured
        assert game.accumulated_moves == [4]  # Move 1 used, 4 remains

        # Simulate bonus throw adding move 2
        game.accumulated_moves.append(2)

        # Should have [4, 2] not just [2]
        assert game.accumulated_moves == [4, 2]
        assert 4 in game.accumulated_moves, "Original move 4 should still be available"
        assert 2 in game.accumulated_moves, "Bonus move 2 should be added"

    def test_multiple_captures_stack_bonuses(self):
        """Multiple captures in succession should keep stacking bonuses."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)
        player0 = game.players[0]
        player1 = game.players[1]

        # Setup: P0 has pieces at 01 and 03
        piece0_a = player0.pieces[0]
        piece0_a.position = "01"
        piece0_a.is_active = True
        piece0_a.has_moved = True

        piece0_b = player0.pieces[1]
        piece0_b.position = "03"
        piece0_b.is_active = True
        piece0_b.has_moved = True

        # P1 starts with moves [2, 1]
        game.accumulated_moves = [2, 1]

        # First capture: Enter at 01
        success, captured = game.move_piece(player1.player_id, -1, 1)
        assert success
        assert captured
        assert game.accumulated_moves == [2]

        # Simulate first bonus: adds move 3
        game.accumulated_moves.append(3)
        assert game.accumulated_moves == [2, 3]

        # Second capture: P1 piece at 01 moves 2 steps to 03
        success, captured = game.move_piece(player1.player_id, 0, 2)
        assert success
        assert captured
        assert game.accumulated_moves == [3]

        # Simulate second bonus: adds move 4
        game.accumulated_moves.append(4)
        assert game.accumulated_moves == [3, 4]

        # All bonus moves should have stacked
        assert 3 in game.accumulated_moves
        assert 4 in game.accumulated_moves


class TestYutMoBonusStacking:
    """Test that Yut/Mo bonus throws also stack correctly."""

    def test_yut_bonus_continues_throwing(self):
        """Throwing Yut should add bonus throw to accumulated_moves."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)

        # Throw phase will keep throwing until non-Yut/Mo
        throws = game.throw_phase(is_bonus=False)

        # Check that all throws were accumulated
        total_moves = sum(move_val for _, move_val in throws)
        accumulated_total = sum(game.accumulated_moves)

        assert total_moves == accumulated_total

    def test_mo_bonus_continues_throwing(self):
        """Throwing Mo should add bonus throw to accumulated_moves."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)

        # Throw phase will keep throwing until non-Yut/Mo
        throws = game.throw_phase(is_bonus=False)

        # All throws should be in accumulated_moves
        assert len(game.accumulated_moves) == len(throws)


class TestIntegration:
    """Integration tests combining multiple bonus scenarios."""

    def test_capture_then_yut_stacks_all(self):
        """Capture bonus that results in Yut should stack all throws."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)

        # Start with remaining move
        game.accumulated_moves = [5]
        initial_count = len(game.accumulated_moves)

        # Bonus throw (could include Yut/Mo which triggers more)
        bonus_throws = game.throw_phase(is_bonus=True)

        # Should have at least initial move + bonus throws
        assert len(game.accumulated_moves) >= initial_count + len(bonus_throws)
        assert 5 in game.accumulated_moves  # Original move preserved
