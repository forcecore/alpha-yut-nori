"""
Player controllers for Yut Nori — ABC plus human and AI implementations.
"""

import random
from abc import ABC, abstractmethod


class PlayerController(ABC):
    """Abstract base for all player controllers (human, random, RL, MCTS, …)."""

    @abstractmethod
    def choose_move(self, game_state: dict, legal_moves: list) -> tuple[int, int] | None:
        """
        Pick one move from legal_moves.

        Args:
            game_state: dict from game.get_game_state()
            legal_moves: list of (piece_id, steps, dest) from game.get_legal_moves()

        Returns:
            (piece_id, steps) to execute, or None to skip remaining moves
        """


class RandomController(PlayerController):
    """Baseline AI — picks moves uniformly at random."""

    def choose_move(self, game_state: dict, legal_moves: list) -> tuple[int, int]:
        piece_id, steps, _dest = random.choice(legal_moves)
        return piece_id, steps


class HumanController(PlayerController):
    """
    Interactive CLI controller — two-step menu (pick piece, pick move value).

    Needs access to the game and player objects for display purposes (stack info,
    shortcut previews, etc.).
    """

    def __init__(self, game, player):
        self.game = game
        self.player = player

    def choose_move(self, game_state: dict, legal_moves: list) -> tuple[int, int] | None:
        """Two-step interactive input loop extracted from cli_game.py."""
        while True:
            # STEP 1: Choose piece
            print("STEP 1: Choose piece to move:")
            print("-" * 40)

            piece_options = {}  # piece_id -> [(steps, dest), ...]
            for piece_id, steps, dest in legal_moves:
                if piece_id not in piece_options:
                    piece_options[piece_id] = []
                piece_options[piece_id].append((steps, dest))

            option_idx = 1
            piece_map = {}

            for piece_id in sorted(piece_options.keys()):
                if piece_id == -1:
                    print(f"  {option_idx}. Enter new piece")
                    piece_map[option_idx] = -1
                    option_idx += 1
                else:
                    piece = self.player.get_piece_by_id(piece_id)
                    stack_size = len(self.game._get_stack_at_position(self.player.player_id, piece.position))
                    stack_str = f" [Stack x{stack_size}]" if stack_size > 1 else ""
                    print(f"  {option_idx}. Piece {piece_id}{stack_str} (at pos {piece.position})")
                    piece_map[option_idx] = piece_id
                    option_idx += 1

            print(f"  0. Skip remaining moves")
            print()

            # Get piece choice
            try:
                piece_choice = int(input("Select piece: ").strip())
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if piece_choice == 0:
                print("Skipping remaining moves.")
                return None

            if piece_choice not in piece_map:
                print("Invalid choice. Try again.")
                continue

            selected_piece_id = piece_map[piece_choice]

            # STEP 2: Choose move value
            print(f"\nSTEP 2: Choose move value:")
            print("-" * 40)

            move_options = piece_options[selected_piece_id]
            move_map = {}
            option_idx = 1

            for steps, dest in move_options:
                if selected_piece_id != -1:
                    piece = self.player.get_piece_by_id(selected_piece_id)
                    if piece.position == '00' and piece.has_moved:
                        dest_str = "EXIT (finish)"
                    else:
                        dest_str = "GOAL" if dest == '00' else f"pos {dest}"
                        if self.game.board.triggers_shortcut(dest):
                            dest_str += " (diagonal shortcut)"
                else:
                    dest_str = f"pos {dest}"
                    if self.game.board.triggers_shortcut(dest):
                        dest_str += " (diagonal shortcut)"

                print(f"  {option_idx}. Use move {steps} (→ {dest_str})")
                move_map[option_idx] = (steps, dest)
                option_idx += 1

            print(f"  0. Go back to piece selection")
            print()

            # Get move choice
            try:
                move_choice = int(input("Select move: ").strip())
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if move_choice == 0:
                print("Going back...")
                continue

            if move_choice not in move_map:
                print("Invalid choice. Try again.")
                continue

            steps, _dest = move_map[move_choice]
            return selected_piece_id, steps
