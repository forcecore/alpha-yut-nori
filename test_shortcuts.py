#!/usr/bin/env python3
"""Test automatic shortcuts in the game."""

from yoot import YutGame

def test_automatic_shortcuts():
    """Test that shortcuts trigger automatically."""
    game = YutGame(player_names=["Alice", "Bob"], num_players=2)
    player = game.get_current_player()

    print("Testing automatic shortcuts (correct behavior)...\n")

    # Test 1: Enter piece with Mo (5) - should LAND on 05
    print("TEST 1: Enter with Mo (5) - LANDS on 05")
    print("-" * 50)
    game.accumulated_moves = [5]

    success, captured = game.move_piece(player.player_id, -1, 5)
    piece = player.get_active_pieces()[0]

    print(f"Entry successful: {success}")
    print(f"Piece position: {piece.position}")
    print(f"Expected: position='05' (shortcut trigger)")

    assert piece.position == '05', f"Expected '05', got {piece.position}"
    print("PASS: Piece lands on shortcut trigger position\n")

    # Test 1b: Next move from 05 MUST use diagonal
    print("TEST 1b: Move from 05 with 1 step - MUST use diagonal (05 -> aa)")
    print("-" * 50)

    game.accumulated_moves = [1]
    success, captured = game.move_piece(player.player_id, 0, 1)

    print(f"Move successful: {success}")
    print(f"Piece position: {piece.position}")
    print(f"Expected: position='aa'")

    assert piece.position == 'aa', f"Expected 'aa', got {piece.position}"
    print("PASS: Next move from shortcut position uses diagonal\n")

    # Test 2: Move piece to land on 10
    print("TEST 2: Land on 10 (left diagonal trigger)")
    print("-" * 50)

    piece2 = player.pieces[1]
    piece2.position = '09'
    piece2.is_active = True
    piece2.has_moved = True

    game.accumulated_moves = [1]
    success, captured = game.move_piece(player.player_id, 1, 1)

    print(f"Move successful: {success}")
    print(f"Piece position: {piece2.position}")
    print(f"Expected: position='10'")

    assert piece2.position == '10', f"Expected '10', got {piece2.position}"
    print("PASS: Piece lands on shortcut trigger position\n")

    # Test 2b: Next move from 10 MUST use diagonal
    print("TEST 2b: Move from 10 with 1 step - MUST use diagonal (10 -> xx)")
    print("-" * 50)

    game.accumulated_moves = [1]
    success, captured = game.move_piece(player.player_id, 1, 1)

    print(f"Move successful: {success}")
    print(f"Piece position: {piece2.position}")
    print(f"Expected: position='xx'")

    assert piece2.position == 'xx', f"Expected 'xx', got {piece2.position}"
    print("PASS: Next move from shortcut position uses diagonal\n")

    # Test 3: Move on right diagonal
    print("TEST 3: Move on right diagonal (aa -> cc)")
    print("-" * 50)

    game.accumulated_moves = [2]
    success, captured = game.move_piece(player.player_id, 0, 2)

    print(f"Move successful: {success}")
    print(f"Piece position: {piece.position}")
    print(f"Expected: position='cc'")

    assert piece.position == 'cc', f"Expected 'cc', got {piece.position}"
    print("PASS: Movement along right diagonal\n")

    # Test 4: From cc, move toward goal
    print("TEST 4: From cc, move toward goal (cc -> pp)")
    print("-" * 50)

    game.accumulated_moves = [1]
    success, captured = game.move_piece(player.player_id, 0, 1)

    print(f"Move successful: {success}")
    print(f"Piece position: {piece.position}")
    print(f"Expected: position='pp'")

    assert piece.position == 'pp', f"Expected 'pp', got {piece.position}"
    print("PASS: cc moves toward goal\n")

    print("="*50)
    print("ALL AUTOMATIC SHORTCUT TESTS PASSED!")
    print("="*50)

if __name__ == "__main__":
    test_automatic_shortcuts()
