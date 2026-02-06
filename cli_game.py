#!/usr/bin/env python3
"""
CLI interface for playing Yut Nori.
"""

import os
from typing import Optional
from yoot import YutGame, HumanController, RandomController


def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def display_board(game: YutGame):
    """Display current board state."""
    print("\n" + "="*60)
    print("YUT NORI (윷놀이)")
    print("="*60 + "\n")

    # Show board
    print(game.board.render_board(game.get_all_pieces()))
    print()

    # Show player status
    print("\nPLAYER STATUS:")
    print("-" * 60)
    for player in game.players:
        active = len(player.get_active_pieces())
        finished = len(player.get_finished_pieces())
        waiting = len(player.get_inactive_pieces())

        marker = ">>> " if player.player_id == game.current_player_idx else "    "
        print(f"{marker}Player {player.player_id} ({player.name}): "
              f"On board: {active}, Finished: {finished}, Waiting: {waiting}")

        # Show positions of active pieces
        if active > 0:
            stacks = player.get_stacks()
            for pos, pieces in stacks.items():
                piece_ids = [p.piece_id for p in pieces]
                if len(pieces) == 1:
                    print(f"       - Piece {piece_ids[0]} at position {pos}")
                else:
                    print(f"       - Stack {piece_ids} at position {pos}")

    print("-" * 60)


def display_game_status(game: YutGame, current_player_id: Optional[int] = None, show_board: bool = True):
    """
    Display current game status for all players.

    Args:
        game: The game instance
        current_player_id: Optional player ID to highlight (shows piece positions)
        show_board: Whether to display the board visualization
    """
    print("\nCURRENT GAME STATUS:")
    print("-" * 60)

    for p in game.players:
        active = len(p.get_active_pieces())
        finished = len(p.get_finished_pieces())
        waiting = len(p.get_inactive_pieces())

        # Highlight current player
        marker = ">>> " if current_player_id is not None and p.player_id == current_player_id else "    "
        status_line = f"{marker}Player {p.player_id} ({p.name}): "
        status_line += f"On board: {active}, Finished: {finished}, Waiting: {waiting}"
        print(status_line)

        # Show positions of active pieces for current player
        if current_player_id is not None and p.player_id == current_player_id and active > 0:
            stacks = p.get_stacks()
            for pos, pieces in sorted(stacks.items()):
                piece_ids = [piece.piece_id for piece in pieces]
                if len(pieces) == 1:
                    print(f"         - Piece {piece_ids[0]} at position {pos}")
                else:
                    print(f"         - Stack {piece_ids} at position {pos}")

    print("-" * 60)

    # Display board visualization
    if show_board:
        print("\nBOARD:")
        print(game.board.render_board(game.get_all_pieces()))
        print()


def display_recent_moves(game: YutGame, count: int = 5):
    """Display recent move history."""
    if game.move_history:
        print("\nRECENT MOVES:")
        for move in game.move_history[-count:]:
            print(f"  {move}")
        print()


def get_player_names() -> tuple[list[str], int]:
    """Get number of players and their names from user."""
    print("Welcome to Yut Nori!")
    print("\n" + "="*60)

    # Get number of players
    while True:
        try:
            num_players_input = input("How many players? (2-6, default 4): ").strip()
            if not num_players_input:
                num_players = 4
                break
            num_players = int(num_players_input)
            if 2 <= num_players <= 6:
                break
            print("Please enter a number between 2 and 6.")
        except ValueError:
            print("Please enter a valid number.")

    print(f"\nEnter names for {num_players} players (press Enter for default names):\n")

    names = []
    for i in range(num_players):
        name = input(f"Player {i} name (default: Player {i}): ").strip()
        if not name:
            name = f"Player {i}"
        names.append(name)

    return names, num_players


def play_turn(game: YutGame, controller) -> bool:
    """
    Play a single turn for current player.

    Returns:
        True if game should continue, False to quit
    """
    player = game.get_current_player()
    is_human = isinstance(controller, HumanController)

    print(f"\n{'='*60}")
    print(f"{player.name}'s turn (Player {player.player_id})")
    print(f"{'='*60}\n")

    # Display current game status before turn
    display_game_status(game, player.player_id)
    print()

    # Throwing phase
    if is_human:
        print("Press Enter to throw yut sticks (or 'q' to quit)...")
        user_input = input().strip().lower()
        if user_input == 'q':
            return False

    throws = game.throw_phase()

    print(f"\nThrow results: ", end="")
    for throw_name, move_value in throws:
        print(f"{throw_name}({move_value}) ", end="")
    print()

    print(f"Accumulated moves: {game.accumulated_moves}")

    # Display game status after throw
    display_game_status(game, player.player_id)

    # Movement phase - use each accumulated move
    while game.accumulated_moves:
        display_recent_moves(game, count=3)

        print(f"\nRemaining moves: {game.accumulated_moves}")
        print(f"Available moves: {len(game.accumulated_moves)}\n")

        # Get legal moves
        legal_moves = game.get_legal_moves(player.player_id)

        if not legal_moves:
            print("No legal moves available. All remaining moves are forfeited.")
            game.accumulated_moves = []
            break

        # Ask controller to choose
        game_state = game.get_game_state()
        choice = controller.choose_move(game_state, legal_moves)

        if choice is None:
            print("Skipping remaining moves.")
            game.accumulated_moves = []
            break

        piece_id, steps = choice

        # Announce AI moves
        if not is_human:
            if piece_id == -1:
                print(f"  >> AI enters new piece with move {steps}")
            else:
                piece = player.get_piece_by_id(piece_id)
                print(f"  >> AI moves piece {piece_id} (at pos {piece.position}) with move {steps}")

        # Execute move
        success, captured = game.move_piece(player.player_id, piece_id, steps)

        if not success:
            print("Move failed. Try again.")
            continue

        # Capture grants bonus throw
        if captured:
            print("\n" + "="*60)
            print("CAPTURE! Bonus throw!")
            print("="*60)

            bonus_throws = game.throw_phase(is_bonus=True)
            print(f"\nBonus throw results: ", end="")
            for throw_name, move_value in bonus_throws:
                print(f"{throw_name}({move_value}) ", end="")
            print()
            print(f"All accumulated moves: {game.accumulated_moves}")

            # Display game status after bonus throw
            display_game_status(game, player.player_id)

        # Check win condition
        if game.check_win_condition():
            return True

    return True


def main():
    """Main game loop."""
    # Get player names and number
    player_names, num_players = get_player_names()

    # Initialize game
    game = YutGame(player_names, num_players)

    # Ask per-player: human or AI?
    controllers: dict[int, HumanController | RandomController] = {}
    any_human = False
    for i, name in enumerate(player_names):
        while True:
            choice = input(f"Is {name} human or AI? (h/a, default h): ").strip().lower()
            if choice in ('', 'h'):
                controllers[i] = HumanController(game, game.players[i])
                any_human = True
                break
            if choice == 'a':
                controllers[i] = RandomController()
                break
            print("Please enter 'h' or 'a'.")

    all_ai = not any_human

    print("\nStarting game...\n")
    input("Press Enter to begin...")

    # Main game loop
    while game.game_state == "playing":
        clear_screen()
        display_board(game)
        display_recent_moves(game, count=5)

        # Play turn
        controller = controllers[game.current_player_idx]
        should_continue = play_turn(game, controller)

        if not should_continue:
            print("\nGame ended by user.")
            break

        if game.game_state == "finished":
            clear_screen()
            display_board(game)
            display_recent_moves(game, count=10)
            print(f"\n{'='*60}")
            print(f"{game.players[game.winner].name} WINS!")
            print(f"{'='*60}\n")
            break

        # Next player
        game.next_turn()

        if game.game_state == "playing":
            if all_ai:
                input("Press Enter to continue to next turn...")
            else:
                print("\nPress Enter to continue to next player...")
                input()


if __name__ == "__main__":
    main()
