#!/usr/bin/env python3
"""
Benchmark: Random AI vs Monte Carlo AI.
500 games with Random as player 0, 500 games with Random as player 1.
"""

import time

from yoot import MonteCarloController, RandomController, YutGame

NUM_GAMES_PER_CONFIG = 500
NUM_SIMS = 100


def run_games(random_idx, mc_idx, num_games):
    wins = {"random": 0, "mc": 0}
    for g in range(num_games):
        game_start = time.time()
        names = [""] * 2
        names[random_idx] = "Random"
        names[mc_idx] = "MC"
        game = YutGame(names, 2)
        controllers = {
            random_idx: RandomController(),
            mc_idx: MonteCarloController(game, mc_idx, num_simulations=NUM_SIMS),
        }

        turn = 0
        while game.game_state == "playing" and turn < 500:
            pid = game.current_player_idx
            ctrl = controllers[pid]
            game.throw_phase()
            while game.accumulated_moves:
                legal = game.get_legal_moves(pid)
                if not legal:
                    game.accumulated_moves = []
                    break
                choice = ctrl.choose_move(game.get_game_state(), legal)
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
                game.check_win_condition()
                if game.game_state != "playing":
                    break
            if game.game_state == "finished":
                break
            game.next_turn()
            turn += 1

        winner_name = game.players[game.rankings[0]].name if game.rankings else "?"
        if game.rankings and game.rankings[0] == mc_idx:
            wins["mc"] += 1
        else:
            wins["random"] += 1
        elapsed = time.time() - game_start

        print(
            f"  Game {g + 1:3d}: winner={winner_name:6s} turns={turn:3d} ({elapsed:.1f}s)  "
            f"Running: MC={wins['mc']} Random={wins['random']}",
            flush=True,
        )
    return wins


start = time.time()

print("=" * 60)
print("CONFIG 1: Random=Player0 (first), MC=Player1 (second)")
print("=" * 60)
wins1 = run_games(random_idx=0, mc_idx=1, num_games=NUM_GAMES_PER_CONFIG)

print()
print("=" * 60)
print("CONFIG 2: MC=Player0 (first), Random=Player1 (second)")
print("=" * 60)
wins2 = run_games(random_idx=1, mc_idx=0, num_games=NUM_GAMES_PER_CONFIG)

total_time = time.time() - start
total_mc = wins1["mc"] + wins2["mc"]
total_random = wins1["random"] + wins2["random"]
total_games = NUM_GAMES_PER_CONFIG * 2

print()
print("=" * 60)
print(f"FINAL RESULTS — {total_games} games, {NUM_SIMS} sims/move")
print("=" * 60)
print(
    f"  Config 1 (Random first, MC second): MC={wins1['mc']} Random={wins1['random']}  MC win rate: {wins1['mc'] / NUM_GAMES_PER_CONFIG:.1%}"
)
print(
    f"  Config 2 (MC first, Random second):  MC={wins2['mc']} Random={wins2['random']}  MC win rate: {wins2['mc'] / NUM_GAMES_PER_CONFIG:.1%}"
)
print(
    f"  Overall:                              MC={total_mc} Random={total_random}  MC win rate: {total_mc / total_games:.1%}"
)
print(f"  Total time: {total_time / 3600:.1f} hours")
print("=" * 60)
