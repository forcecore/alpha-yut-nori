#!/usr/bin/env python3
"""Test board display with pieces."""

from yoot import YutGame, Piece, Board

def test_board_display():
    """Test that pieces show up on board."""

    # Create game
    game = YutGame(player_names=["Alice", "Bob"], num_players=2)

    # Manually place some pieces for testing
    player0 = game.players[0]
    player1 = game.players[1]

    # Place Player 0's piece at position '01'
    piece0 = player0.pieces[0]
    piece0.position = '01'
    piece0.is_active = True
    piece0.has_moved = True

    # Place Player 1's piece at position '05'
    piece1 = player1.pieces[0]
    piece1.position = '05'
    piece1.is_active = True
    piece1.has_moved = True

    # Place another piece at position 'aa'
    piece2 = player0.pieces[1]
    piece2.position = 'aa'
    piece2.is_active = True
    piece2.has_moved = True

    print("Pieces placed:")
    print(f"  Piece 0 (P0): position={piece0.position}, active={piece0.is_active}")
    print(f"  Piece 1 (P1): position={piece1.position}, active={piece1.is_active}")
    print(f"  Piece 2 (P0): position={piece2.position}, active={piece2.is_active}")

    # Get all pieces
    all_pieces = game.get_all_pieces()
    print(f"\nTotal pieces passed to render: {len(all_pieces)}")
    print(f"Active pieces: {sum(1 for p in all_pieces if p.is_active)}")

    # Create piece map to debug
    piece_map = {}
    for piece in all_pieces:
        print(f"  Piece: player={piece.player_id}, pos={piece.position}, active={piece.is_active}")
        if piece.position and piece.is_active:
            pos = piece.position
            if pos not in piece_map:
                piece_map[pos] = []
            piece_map[pos].append(piece.player_id)

    print(f"\nPiece map: {piece_map}")

    # Render board
    print("\nRendered board:")
    print(game.board.render_board(all_pieces))

if __name__ == "__main__":
    test_board_display()
