#!/usr/bin/env python3
"""Simulate MCTS vs Monte Carlo: 500 games each side going first."""

import sys
import io
from yoot import YutGame, MonteCarloController, MCTSController


def play_game(mcts_player_id: int) -> int:
    """Play one game, return winner player_id."""
    mc_player_id = 1 - mcts_player_id
    names = [None, None]
    names[mcts_player_id] = "MCTS"
    names[mc_player_id] = "MC"

    game = YutGame(names, 2)

    controllers = {}
    controllers[mcts_player_id] = MCTSController(game, mcts_player_id, num_iterations=1000)
    controllers[mc_player_id] = MonteCarloController(game, mc_player_id, num_simulations=100)

    max_turns = 500
    for _ in range(max_turns):
        if game.game_state != "playing":
            break

        pid = game.current_player_idx
        ctrl = controllers[pid]

        game.throw_phase()

        while game.accumulated_moves:
            legal = game.get_legal_moves(pid)
            if not legal:
                game.accumulated_moves = []
                break

            game_state = game.get_game_state()
            choice = ctrl.choose_move(game_state, legal)

            if choice is None:
                game.accumulated_moves = []
                break

            piece_id, steps = choice
            success, captured = game.move_piece(pid, piece_id, steps)
            if not success:
                game.accumulated_moves = []
                break

            if captured:
                game.throw_phase(is_bonus=True)

            if game.check_win_condition():
                break

        if game.game_state == "finished":
            break

        game.next_turn()

    if game.rankings:
        return game.rankings[0]
    return -1  # draw/timeout


def main():
    # Suppress print output from controllers
    real_stdout = sys.stdout

    mcts_wins = 0
    mc_wins = 0
    draws = 0

    total = 1000

    for i in range(total):
        mcts_is_p0 = (i % 2 == 0)
        mcts_pid = 0 if mcts_is_p0 else 1

        sys.stdout = io.StringIO()
        winner = play_game(mcts_pid)
        sys.stdout = real_stdout

        if winner == mcts_pid:
            mcts_wins += 1
        elif winner == 1 - mcts_pid:
            mc_wins += 1
        else:
            draws += 1

        if True:
            phase = "MCTS=P0" if mcts_is_p0 else "MCTS=P1"
            print(f"  [{phase}] Game {i+1}/{total}: MCTS {mcts_wins} - MC {mc_wins} (draws: {draws})")

    print()
    print("=" * 50)
    print(f"FINAL RESULTS ({total} games)")
    print(f"  MCTS wins: {mcts_wins} ({mcts_wins/total:.1%})")
    print(f"  MC   wins: {mc_wins} ({mc_wins/total:.1%})")
    print(f"  Draws:     {draws}")
    print("=" * 50)


if __name__ == "__main__":
    main()
