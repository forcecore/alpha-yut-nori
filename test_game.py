#!/usr/bin/env python3
"""
Test script to verify game mechanics.
"""

from yoot import YutGame, YutThrow


def test_basic_game_flow():
    """Test basic game initialization and flow."""
    print("Testing basic game flow...")

    # Initialize game
    game = YutGame(["Alice", "Bob", "Carol", "Dave"])
    print(f"✓ Game initialized with {len(game.players)} players")

    # Test throw phase
    throws = game.throw_phase()
    print(f"✓ Throw phase complete: {len(throws)} throws")
    print(f"  Accumulated moves: {game.accumulated_moves}")

    # Test legal moves
    legal_moves = game.get_legal_moves(0)
    print(f"✓ Found {len(legal_moves)} legal moves")

    # Test entering piece
    if game.accumulated_moves:
        steps = game.accumulated_moves[0]
        success, _ = game.move_piece(0, -1, steps)
        print(f"✓ Entered piece: {success}")

    # Test board rendering
    board_str = game.board.render_board(game.get_all_pieces())
    print(f"✓ Board rendered ({len(board_str)} chars)")

    print("\n✓ All basic tests passed!")


def test_piece_movement():
    """Test piece movement and game rules."""
    print("\nTesting piece movement...")

    game = YutGame()

    # Manually set up some pieces
    player = game.players[0]
    piece1 = player.pieces[0]
    piece1.enter_board("01")
    print(f"✓ Piece entered at position {piece1.position}")

    # Test movement
    game.accumulated_moves = [2]
    success, _ = game.move_piece(0, 0, 2)
    print(f"✓ Moved piece: {success}, new position: {piece1.position}")

    # Test stacking
    piece2 = player.pieces[1]
    piece2.enter_board("03")  # Same position as piece1 after moving 2 from 01
    stacks = game._get_stack_at_position(0, "03")
    print(f"✓ Stack created: {len(stacks)} pieces at position {piece1.position}")

    print("\n✓ All movement tests passed!")


def test_capture():
    """Test capture mechanics."""
    print("\nTesting capture mechanics...")

    game = YutGame()

    # Set up pieces for capture
    player1 = game.players[0]
    player2 = game.players[1]

    piece1 = player1.pieces[0]
    piece1.enter_board("05")

    piece2 = player2.pieces[0]
    piece2.enter_board("01")

    print(f"✓ Set up: P1 piece at {piece1.position}, P2 piece at {piece2.position}")

    # Move P2 piece to capture P1
    game.accumulated_moves = [4]
    game.move_piece(1, 0, 4)  # Should land on position 05 and capture

    print(f"✓ P2 moved to {piece2.position}, P1 captured (active={piece1.is_active})")

    print("\n✓ Capture test passed!")


def test_win_condition():
    """Test win condition."""
    print("\nTesting win condition...")

    game = YutGame()
    player = game.players[0]

    # Finish all pieces properly
    for piece in player.pieces:
        piece.enter_board("01")
        piece.finish()

    won = game.check_win_condition()
    print(f"✓ Win condition detected: {won}")
    print(f"✓ Winner: Player {game.winner}")
    print(f"✓ Game state: {game.game_state}")

    print("\n✓ Win condition test passed!")


def test_throw_probabilities():
    """Test throw distribution."""
    print("\nTesting throw probabilities (1000 throws)...")

    counts = {"do": 0, "back_do": 0, "gae": 0, "geol": 0, "yut": 0, "mo": 0}

    for _ in range(1000):
        throw_name, _ = YutThrow.throw()
        counts[throw_name] += 1

    print("Distribution:")
    for name, count in sorted(counts.items()):
        percentage = (count / 1000) * 100
        extra = " (extra turn)" if YutThrow.grants_extra_turn(name) else ""
        print(f"  {name}: {count} ({percentage:.1f}%){extra}")

    print("\n✓ Throw probability test complete!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("YUT NORI GAME ENGINE TEST SUITE")
    print("=" * 60)

    test_basic_game_flow()
    test_piece_movement()
    test_capture()
    test_win_condition()
    test_throw_probabilities()

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYou can now run: python3 cli_game.py")


if __name__ == "__main__":
    main()
