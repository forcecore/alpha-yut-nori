"""
Tests for main game engine.
"""

import pytest
from yoot import YutGame, Board


class TestGameInitialization:
    """Test game initialization."""

    def test_game_with_default_players(self):
        """Test game with default player names."""
        game = YutGame()
        assert len(game.players) == 4
        assert game.num_players == 4
        assert game.current_player_idx == 0
        assert game.game_state == "playing"

    def test_game_with_custom_players(self):
        """Test game with custom player names."""
        names = ["Alice", "Bob", "Carol", "Dave"]
        game = YutGame(names)
        assert len(game.players) == 4
        for i, name in enumerate(names):
            assert game.players[i].name == name

    def test_game_with_variable_player_count(self):
        """Test game with different numbers of players."""
        # 2 players
        game2 = YutGame(["A", "B"], num_players=2)
        assert len(game2.players) == 2

        # 3 players
        game3 = YutGame(["A", "B", "C"], num_players=3)
        assert len(game3.players) == 3

        # 6 players
        game6 = YutGame(None, num_players=6)
        assert len(game6.players) == 6

    def test_invalid_player_count(self):
        """Test invalid player count raises error."""
        with pytest.raises(ValueError):
            YutGame(num_players=1)

        with pytest.raises(ValueError):
            YutGame(num_players=7)

    def test_mismatched_names_and_count(self):
        """Test error when names don't match count."""
        with pytest.raises(ValueError):
            YutGame(["A", "B"], num_players=3)


class TestGameMechanics:
    """Test game mechanics."""

    def test_get_current_player(self):
        """Test getting current player."""
        game = YutGame(["A", "B"], num_players=2)
        assert game.get_current_player().name == "A"
        game.next_turn()
        assert game.get_current_player().name == "B"

    def test_next_turn(self):
        """Test turn advancement."""
        game = YutGame(["A", "B", "C"], num_players=3)
        assert game.current_player_idx == 0
        game.next_turn()
        assert game.current_player_idx == 1
        game.next_turn()
        assert game.current_player_idx == 2
        game.next_turn()
        assert game.current_player_idx == 0  # Wrap around

    def test_throw_phase(self):
        """Test throwing phase."""
        game = YutGame(["A", "B"], num_players=2)
        throws = game.throw_phase()

        assert len(throws) >= 1  # At least one throw
        assert len(game.accumulated_moves) >= 1

        # Check all throws are valid
        for throw_name, move_value in throws:
            assert throw_name in ['do', 'back_do', 'gae', 'geol', 'yut', 'mo']


class TestPieceEntry:
    """Test piece entry mechanics."""

    def test_enter_piece_with_do(self):
        """Test entering piece with Do (1)."""
        game = YutGame(["A", "B"], num_players=2)
        game.accumulated_moves = [1]

        success, _ = game.move_piece(0, -1, 1)
        assert success

        piece = game.players[0].pieces[0]
        assert piece.position == '01'
        assert piece.is_active

    def test_enter_piece_with_different_throws(self):
        """Test pieces enter at correct positions for different throws."""
        # Test each throw type separately with fresh games
        throw_positions = {1: '01', 2: '02', 3: '03', 4: '04', 5: '05'}

        for throw_value, expected_pos in throw_positions.items():
            game = YutGame(["A", "B"], num_players=2)
            game.accumulated_moves = [throw_value]
            success, _ = game.move_piece(0, -1, throw_value)

            assert success
            # Check the first entered piece has correct position
            entered_piece = game.players[0].get_active_pieces()[0]
            assert entered_piece.position == expected_pos

    def test_cannot_enter_without_inactive_pieces(self):
        """Test cannot enter when all pieces are active."""
        game = YutGame(["A", "B"], num_players=2)

        # Enter all pieces
        for i in range(4):
            game.players[0].pieces[i].enter_board('01')

        game.accumulated_moves = [1]
        success, _ = game.move_piece(0, -1, 1)
        assert not success


class TestPieceMovement:
    """Test piece movement."""

    def test_move_piece_forward(self):
        """Test moving piece forward."""
        game = YutGame(["A", "B"], num_players=2)

        # Enter piece
        game.players[0].pieces[0].enter_board('01')

        # Move it
        game.accumulated_moves = [3]
        success, _ = game.move_piece(0, 0, 3)

        assert success
        assert game.players[0].pieces[0].position == '04'

    def test_move_piece_backward(self):
        """Test moving piece backward (back Do)."""
        game = YutGame(["A", "B"], num_players=2)

        # Enter piece at position 05
        game.players[0].pieces[0].enter_board('05')

        # Move backward
        game.accumulated_moves = [-1]
        success, _ = game.move_piece(0, 0, -1)

        assert success
        assert game.players[0].pieces[0].position == '04'

    def test_move_to_goal(self):
        """Test piece finishing at goal (two-step process)."""
        game = YutGame(["A", "B"], num_players=2)

        # Place piece at 19
        piece = game.players[0].pieces[0]
        piece.position = '19'
        piece.is_active = True
        piece.has_moved = True

        # Step 1: Move to 00 (lands at goal)
        game.accumulated_moves = [1]
        success, _ = game.move_piece(0, 0, 1)

        assert success
        assert piece.position == '00'
        assert piece.is_active  # Still on board

        # Step 2: Any move from 00 causes piece to exit
        game.accumulated_moves = [1]
        success, _ = game.move_piece(0, 0, 1)

        assert success
        assert not piece.is_active
        assert piece.has_finished()


class TestCaptureMechanics:
    """Test capture mechanics."""

    def test_capture_opponent_piece(self):
        """Test capturing opponent's piece."""
        game = YutGame(["A", "B"], num_players=2)

        # Place opponent piece
        game.players[1].pieces[0].enter_board('05')

        # Move our piece to same position
        game.players[0].pieces[0].enter_board('02')
        game.accumulated_moves = [3]
        success, captured = game.move_piece(0, 0, 3)

        # Move should succeed and indicate capture
        assert success
        assert captured

        # Opponent piece should be captured
        assert not game.players[1].pieces[0].is_active
        assert game.players[1].pieces[0].position is None

    def test_no_capture_same_player(self):
        """Test pieces of same player don't capture each other."""
        game = YutGame(["A", "B"], num_players=2)

        # Place two pieces of same player
        game.players[0].pieces[0].enter_board('05')
        game.players[0].pieces[1].enter_board('02')

        # Move second piece to same position as first
        game.accumulated_moves = [3]
        success, captured = game.move_piece(0, 1, 3)

        # Should not indicate capture (just stacking)
        assert success
        assert not captured

        # Both pieces should still be active (stacking)
        assert game.players[0].pieces[0].is_active
        assert game.players[0].pieces[1].is_active
        assert game.players[0].pieces[0].position == '05'
        assert game.players[0].pieces[1].position == '05'

    def test_capture_returns_bonus_flag(self):
        """Test that capture returns True for bonus throw."""
        game = YutGame(["A", "B"], num_players=2)

        # Place opponent piece at position 03
        game.players[1].pieces[0].enter_board('03')

        # Enter our piece and move to capture
        game.players[0].pieces[0].enter_board('01')
        game.accumulated_moves = [2]

        success, captured = game.move_piece(0, 0, 2)

        assert success
        assert captured  # Should grant bonus throw


class TestStackingMechanics:
    """Test piece stacking."""

    def test_stack_same_player_pieces(self):
        """Test stacking pieces from same player."""
        game = YutGame(["A", "B"], num_players=2)

        # Place two pieces at same position
        game.players[0].pieces[0].enter_board('05')
        game.players[0].pieces[1].enter_board('05')

        stack = game._get_stack_at_position(0, '05')
        assert len(stack) == 2

    def test_move_stack_together(self):
        """Test stacked pieces move together."""
        game = YutGame(["A", "B"], num_players=2)

        # Create stack at a non-shortcut position
        game.players[0].pieces[0].enter_board('03')
        game.players[0].pieces[1].enter_board('03')

        # Move stack
        game.accumulated_moves = [2]
        game.move_piece(0, 0, 2)  # Returns (success, captured) tuple

        # Both pieces should have moved
        assert game.players[0].pieces[0].position == '05'
        assert game.players[0].pieces[1].position == '05'


class TestWinCondition:
    """Test win condition."""

    def test_win_when_all_pieces_finished(self):
        """Test player wins when all pieces reach goal."""
        game = YutGame(["A", "B"], num_players=2)

        # Properly finish all pieces
        for piece in game.players[0].pieces:
            piece.enter_board('01')
            piece.finish()

        game.check_win_condition()

        assert game.game_state == "finished"
        assert game.winner == 0

    def test_no_win_with_partial_pieces(self):
        """Test no win when not all pieces finished."""
        game = YutGame(["A", "B"], num_players=2)

        # Finish 3 pieces
        for i in range(3):
            game.players[0].pieces[i].enter_board('01')
            game.players[0].pieces[i].finish()

        result = game.check_win_condition()

        assert not result
        assert game.game_state == "playing"
        assert game.winner is None


class TestLegalMoves:
    """Test legal move generation."""

    def test_get_legal_moves_entry(self):
        """Test legal moves include piece entry options."""
        game = YutGame(["A", "B"], num_players=2)
        game.accumulated_moves = [1, 2, 3]

        legal_moves = game.get_legal_moves(0)

        # Should have entry options for each move value
        entry_moves = [m for m in legal_moves if m[0] == -1]
        assert len(entry_moves) == 3

    def test_get_legal_moves_movement(self):
        """Test legal moves for piece movement."""
        game = YutGame(["A", "B"], num_players=2)

        # Enter a piece
        game.players[0].pieces[0].enter_board('05')
        game.accumulated_moves = [2, 3]

        legal_moves = game.get_legal_moves(0)

        # Should have moves for the active piece
        piece_moves = [m for m in legal_moves if m[0] == 0]
        assert len(piece_moves) >= 2

    def test_no_legal_moves(self):
        """Test when no legal moves available."""
        game = YutGame(["A", "B"], num_players=2)

        # No pieces and no moves
        game.accumulated_moves = []
        legal_moves = game.get_legal_moves(0)

        assert len(legal_moves) == 0


class TestGameState:
    """Test game state management."""

    def test_get_game_state(self):
        """Test getting game state."""
        game = YutGame(["A", "B"], num_players=2)
        state = game.get_game_state()

        assert 'current_player' in state
        assert 'game_state' in state
        assert 'winner' in state
        assert 'accumulated_moves' in state
        assert 'players' in state
        assert len(state['players']) == 2

    def test_game_state_tracking(self):
        """Test game state changes are tracked."""
        game = YutGame(["A", "B"], num_players=2)

        initial_state = game.get_game_state()
        assert initial_state['game_state'] == 'playing'

        # Enter a piece
        game.accumulated_moves = [1]
        game.move_piece(0, -1, 1)  # Returns (success, captured) tuple

        new_state = game.get_game_state()
        assert new_state['players'][0]['active_pieces'] == 1

    def test_move_history(self):
        """Test move history is recorded."""
        game = YutGame(["A", "B"], num_players=2)

        game.log_move("Test move 1")
        game.log_move("Test move 2")

        assert len(game.move_history) == 2
        assert "Test move 1" in game.move_history
