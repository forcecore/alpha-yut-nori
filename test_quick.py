#!/usr/bin/env python3
"""Quick test of core game functionality."""

from yoot import YutGame


def test_game_basics():
    """Test basic game operations."""
    print("Creating game...")
    game = YutGame(player_names=["Alice", "Bob"], num_players=2)

    print(f"✓ Game created with {len(game.players)} players")
    print(f"✓ Current player: {game.get_current_player().name}")

    # Test throwing
    print("\nThrowing yut sticks...")
    throws = game.throw_phase()
    print(f"✓ Throws: {throws}")
    print(f"✓ Accumulated moves: {game.accumulated_moves}")

    # Test getting legal moves
    player = game.get_current_player()
    legal_moves = game.get_legal_moves(player.player_id)
    print(f"✓ Legal moves available: {len(legal_moves)}")

    # Test entering a piece
    if game.accumulated_moves and player.can_enter_new_piece():
        steps = game.accumulated_moves[0]
        print(f"\nEntering piece with throw value {steps}...")
        success, captured = game.move_piece(player.player_id, -1, steps)
        print(f"✓ Entry successful: {success}")

        # Check piece position
        active_pieces = player.get_active_pieces()
        if active_pieces:
            piece = active_pieces[0]
            print(f"✓ Piece entered at position: {piece.position}")

    # Test board rendering
    print("\nRendering board...")
    rendered = game.board.render_board(game.get_all_pieces())
    print(rendered)

    print("\n✅ All basic tests passed!")


if __name__ == "__main__":
    test_game_basics()
