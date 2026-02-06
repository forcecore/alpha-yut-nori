"""Tests for crossroad behavior in game context (game engine integration)."""

from yoot import YutGame


class TestCrossroadInGame:
    """Test crossroad movement in actual game scenarios."""

    def test_piece_passes_through_cc_on_05_diagonal(self):
        """Piece on 05-diagonal correctly passes through cc toward uu."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)
        player = game.players[0]

        piece = player.pieces[0]
        piece.position = 'aa'
        piece.is_active = True
        piece.has_moved = True

        # aa -> bb -> cc -> uu
        game.accumulated_moves = [3]
        success, _ = game.move_piece(player.player_id, 0, 3)
        assert success
        assert piece.position == 'uu'

    def test_piece_passes_through_cc_on_10_diagonal(self):
        """Piece on 10-diagonal correctly passes through cc toward pp."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)
        player = game.players[0]

        piece = player.pieces[0]
        piece.position = 'xx'
        piece.is_active = True
        piece.has_moved = True

        # xx -> yy -> cc -> pp
        game.accumulated_moves = [3]
        success, _ = game.move_piece(player.player_id, 0, 3)
        assert success
        assert piece.position == 'pp'

    def test_piece_at_cc_moves_toward_goal(self):
        """Piece starting at cc always moves toward 00 (pp -> qq -> 00)."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)
        player = game.players[0]

        piece = player.pieces[0]
        piece.position = 'cc'
        piece.is_active = True
        piece.has_moved = True

        game.accumulated_moves = [1]
        success, _ = game.move_piece(player.player_id, 0, 1)
        assert success
        assert piece.position == 'pp'

    def test_right_diagonal_exits_to_15(self):
        """Right diagonal piece exits to outer path at 15."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)
        player = game.players[0]

        piece = player.pieces[0]
        piece.position = 'vv'
        piece.is_active = True
        piece.has_moved = True

        game.accumulated_moves = [1]
        game.move_piece(player.player_id, 0, 1)
        assert piece.position == '15'

    def test_left_diagonal_exits_to_00(self):
        """Left diagonal piece exits to goal at 00."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)
        player = game.players[0]

        piece = player.pieces[0]
        piece.position = 'qq'
        piece.is_active = True
        piece.has_moved = True

        game.accumulated_moves = [1]
        game.move_piece(player.player_id, 0, 1)
        assert piece.position == '00'

    def test_full_right_diagonal_traversal(self):
        """Piece traverses: 05 -> aa -> bb -> cc -> uu -> vv -> 15."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)
        player = game.players[0]

        piece = player.pieces[0]
        piece.position = '05'
        piece.is_active = True
        piece.has_moved = True

        # 05 -> uu (4 steps)
        game.accumulated_moves = [4]
        game.move_piece(player.player_id, 0, 4)
        assert piece.position == 'uu'

        # uu -> vv
        game.accumulated_moves = [1]
        game.move_piece(player.player_id, 0, 1)
        assert piece.position == 'vv'

        # vv -> 15
        game.accumulated_moves = [1]
        game.move_piece(player.player_id, 0, 1)
        assert piece.position == '15'

    def test_full_left_diagonal_traversal(self):
        """Piece traverses: 10 -> xx -> yy -> cc -> pp -> qq -> 00."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)
        player = game.players[0]

        piece = player.pieces[0]
        piece.position = '10'
        piece.is_active = True
        piece.has_moved = True

        # 10 -> pp (4 steps)
        game.accumulated_moves = [4]
        game.move_piece(player.player_id, 0, 4)
        assert piece.position == 'pp'

        # pp -> qq
        game.accumulated_moves = [1]
        game.move_piece(player.player_id, 0, 1)
        assert piece.position == 'qq'

        # qq -> 00
        game.accumulated_moves = [1]
        game.move_piece(player.player_id, 0, 1)
        assert piece.position == '00'


class TestOuterPathNoFalseShortcuts:
    """Test that passing through 05/10 on outer path does NOT take diagonal."""

    def test_passing_through_05_stays_outer(self):
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)
        player = game.players[0]

        piece = player.pieces[0]
        piece.position = '03'
        piece.is_active = True
        piece.has_moved = True

        game.accumulated_moves = [3]
        game.move_piece(player.player_id, 0, 3)
        assert piece.position == '06'

    def test_passing_through_10_stays_outer(self):
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)
        player = game.players[0]

        piece = player.pieces[0]
        piece.position = '08'
        piece.is_active = True
        piece.has_moved = True

        game.accumulated_moves = [3]
        game.move_piece(player.player_id, 0, 3)
        assert piece.position == '11'

    def test_landing_on_05_takes_diagonal_next(self):
        """Landing on 05 means next move takes diagonal."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)
        player = game.players[0]

        piece = player.pieces[0]
        piece.position = '04'
        piece.is_active = True
        piece.has_moved = True

        # Land on 05
        game.accumulated_moves = [1]
        game.move_piece(player.player_id, 0, 1)
        assert piece.position == '05'

        # Next move from 05 takes diagonal
        game.accumulated_moves = [1]
        game.move_piece(player.player_id, 0, 1)
        assert piece.position == 'aa'

    def test_landing_on_10_takes_diagonal_next(self):
        """Landing on 10 means next move takes diagonal."""
        game = YutGame(player_names=["Alice", "Bob"], num_players=2)
        player = game.players[0]

        piece = player.pieces[0]
        piece.position = '09'
        piece.is_active = True
        piece.has_moved = True

        # Land on 10
        game.accumulated_moves = [1]
        game.move_piece(player.player_id, 0, 1)
        assert piece.position == '10'

        # Next move from 10 takes diagonal
        game.accumulated_moves = [1]
        game.move_piece(player.player_id, 0, 1)
        assert piece.position == 'xx'
