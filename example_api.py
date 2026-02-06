#!/usr/bin/env python3
"""
Example demonstrating the Yut Nori game engine API.

This shows how to use the game engine programmatically
(useful for AI/RL agent development).
"""

from yoot import YutGame


def simulate_simple_game():
    """
    Simulate a simple automated game where each player
    makes the first available legal move.
    """
    print("Simulating automated Yut Nori game...")
    print("="*60)

    # Initialize game
    game = YutGame(["Alice", "Bob", "Carol", "Dave"])
    print(f"Game started with {len(game.players)} players\n")

    turn_count = 0
    max_turns = 100  # Prevent infinite games

    # Main game loop
    while game.game_state == "playing" and turn_count < max_turns:
        turn_count += 1
        player = game.get_current_player()

        print(f"\nTurn {turn_count}: {player.name}'s turn")
        print("-" * 60)

        # Throw phase
        throws = game.throw_phase()
        print(f"Throws: {[f'{name}({val})' for name, val in throws]}")
        print(f"Accumulated moves: {game.accumulated_moves}")

        # Make moves until no moves left
        moves_made = 0
        while game.accumulated_moves:
            legal_moves = game.get_legal_moves(player.player_id)

            if not legal_moves:
                print(f"  No legal moves available. Forfeiting {game.accumulated_moves}")
                game.accumulated_moves = []
                break

            # Take first legal move (simple strategy)
            piece_id, steps, destination = legal_moves[0]

            piece_str = "New piece" if piece_id == -1 else f"Piece {piece_id}"
            dest_str = "GOAL" if destination == -1 or destination == 28 else f"pos {destination}"

            print(f"  Move {moves_made + 1}: {piece_str} by {steps} spaces to {dest_str}")

            # Execute move
            success = game.move_piece(player.player_id, piece_id, steps)

            if not success:
                print(f"    ERROR: Move failed!")
                break

            moves_made += 1

            # Check for win
            if game.check_win_condition():
                break

        print(f"  Total moves made: {moves_made}")

        # Show player status
        active = len(player.get_active_pieces())
        finished = len(player.get_finished_pieces())
        print(f"  Status: {active} on board, {finished} finished")

        # Check if game ended
        if game.game_state == "finished":
            break

        # Next player
        game.next_turn()

    # Game over
    print("\n" + "="*60)
    if game.winner is not None:
        winner = game.players[game.winner]
        print(f"🎉 {winner.name} wins after {turn_count} turns!")
    else:
        print(f"Game ended after {turn_count} turns (max limit reached)")

    print("="*60)

    # Show final statistics
    print("\nFinal Statistics:")
    for player in game.players:
        finished = len(player.get_finished_pieces())
        active = len(player.get_active_pieces())
        waiting = len(player.get_inactive_pieces())
        print(f"  {player.name}: {finished} finished, {active} active, {waiting} waiting")


def demonstrate_api_features():
    """
    Demonstrate various API features and state inspection.
    """
    print("\n\nDemonstrating API Features")
    print("="*60)

    game = YutGame()

    # 1. Inspect initial state
    print("\n1. Initial Game State:")
    state = game.get_game_state()
    print(f"   Current player: {state['current_player']}")
    print(f"   Game state: {state['game_state']}")
    print(f"   Players: {len(state['players'])}")

    # 2. Throw and show moves
    print("\n2. Throw Phase:")
    throws = game.throw_phase()
    for throw_name, move_value in throws:
        print(f"   Threw {throw_name}: {move_value} spaces")

    # 3. Get legal moves
    print("\n3. Legal Moves:")
    legal_moves = game.get_legal_moves(0)
    print(f"   Found {len(legal_moves)} legal moves")
    for piece_id, steps, dest in legal_moves[:3]:  # Show first 3
        print(f"   - Piece {piece_id}, {steps} steps -> position {dest}")

    # 4. Execute a move
    if legal_moves:
        print("\n4. Execute Move:")
        piece_id, steps, dest = legal_moves[0]
        success = game.move_piece(0, piece_id, steps)
        print(f"   Move executed: {success}")

    # 5. Inspect player state
    print("\n5. Player State:")
    player = game.players[0]
    print(f"   Active pieces: {len(player.get_active_pieces())}")
    print(f"   Finished pieces: {len(player.get_finished_pieces())}")
    print(f"   Can enter new piece: {player.can_enter_new_piece()}")

    # 6. Board rendering
    print("\n6. Board Visualization:")
    print(game.board.render_board(game.get_all_pieces()))

    # 7. Move history
    print("\n7. Move History:")
    for move in game.move_history[-5:]:
        print(f"   {move}")


def main():
    """Run examples."""
    # Run automated game simulation
    simulate_simple_game()

    # Show API features
    demonstrate_api_features()

    print("\n" + "="*60)
    print("Examples complete!")
    print("="*60)


if __name__ == "__main__":
    main()
