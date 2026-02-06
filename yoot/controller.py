"""
Player controllers for Yut Nori — ABC plus human and AI implementations.
"""

import copy
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


class MonteCarloController(PlayerController):
    """Monte Carlo Tree Search AI — evaluates moves via random rollout simulations."""

    MAX_ROLLOUT_TURNS = 200

    def __init__(self, game, player_id, num_simulations=3000):
        self.game = game
        self.player_id = player_id
        self.num_simulations = num_simulations

    def choose_move(self, game_state: dict, legal_moves: list) -> tuple[int, int]:
        # Deduplicate: stacked pieces at the same position produce identical outcomes,
        # so group by (position_or_entry, steps) and keep one representative piece_id.
        seen = {}  # (position_key, steps) -> piece_id
        for pid, steps, _dest in legal_moves:
            if pid == -1:
                key = ('entry', steps)
            else:
                pos = self.game.players[self.player_id].get_piece_by_id(pid).position
                key = (pos, steps)
            if key not in seen:
                seen[key] = pid
        candidates = [(pid, steps) for (_, steps), pid in seen.items()]

        if len(candidates) == 1:
            return candidates[0]

        results = []
        for piece_id, steps in candidates:
            wins = sum(
                self._simulate(piece_id, steps)
                for _ in range(self.num_simulations)
            )
            win_rate = wins / self.num_simulations
            results.append(((piece_id, steps), win_rate))

        results.sort(key=lambda r: r[1], reverse=True)

        print(f"  [MC] Evaluating {len(results)} moves ({self.num_simulations} sims each):")
        for (pid, st), wr in results:
            marker = " <<" if (pid, st) == results[0][0] else ""
            print(f"    piece={pid} steps={st}: {wr:.1%}{marker}")

        return results[0][0]

    def _simulate(self, piece_id: int, steps: int) -> float:
        """Run one random rollout. Win = finishing at the next available rank."""
        sim = self._clone_game()
        player_id = self.player_id
        # "Winning" means being the next player to finish (best achievable rank)
        target_rank_idx = len(sim.rankings)

        # Apply the candidate move
        success, captured = sim.move_piece(player_id, piece_id, steps)
        if not success:
            return 0.0

        if captured:
            sim.throw_phase(is_bonus=True)

        sim.check_win_condition()
        if len(sim.rankings) > target_rank_idx:
            return 1.0 if sim.rankings[target_rank_idx] == player_id else 0.0

        # Consume remaining accumulated_moves with random play
        self._play_remaining_moves(sim, player_id)

        if len(sim.rankings) > target_rank_idx:
            return 1.0 if sim.rankings[target_rank_idx] == player_id else 0.0

        if sim.game_state != "playing":
            return 0.0

        # Full random playout
        sim.next_turn()

        for _ in range(self.MAX_ROLLOUT_TURNS):
            if sim.game_state != "playing":
                break

            current_pid = sim.current_player_idx
            sim.throw_phase()

            self._play_remaining_moves(sim, current_pid)

            # Someone took the next rank — check if it was us
            if len(sim.rankings) > target_rank_idx:
                return 1.0 if sim.rankings[target_rank_idx] == player_id else 0.0

            sim.next_turn()

        if len(sim.rankings) > target_rank_idx:
            return 1.0 if sim.rankings[target_rank_idx] == player_id else 0.0

        return self._heuristic_score(sim)

    def _clone_game(self):
        """Deepcopy the game, sharing the Board to avoid file I/O."""
        board = self.game.board
        self.game.board = None
        sim = copy.deepcopy(self.game)
        self.game.board = board
        sim.board = board
        return sim

    def _play_remaining_moves(self, sim, player_id):
        """Consume all accumulated_moves with random legal choices."""
        while sim.accumulated_moves:
            legal = sim.get_legal_moves(player_id)
            if not legal:
                sim.accumulated_moves = []
                break

            pid, steps, _dest = random.choice(legal)
            success, captured = sim.move_piece(player_id, pid, steps)

            if not success:
                # Shouldn't happen, but avoid infinite loop
                sim.accumulated_moves = []
                break

            if captured:
                sim.throw_phase(is_bonus=True)

            if sim.check_win_condition():
                break

    def _heuristic_score(self, sim) -> float:
        """Score an unfinished game: ratio of finished pieces with a bonus for leading."""
        my_finished = len(sim.players[self.player_id].get_finished_pieces())
        score = my_finished / 4.0

        best_opponent = max(
            len(p.get_finished_pieces())
            for p in sim.players
            if p.player_id != self.player_id
        )

        if my_finished > best_opponent:
            score += 0.1

        return score
