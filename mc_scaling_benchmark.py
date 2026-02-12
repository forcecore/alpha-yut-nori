#!/usr/bin/env python3
"""
Benchmark: MC win rate vs simulation count.
Player 0 = Random, Player 1 = MC. 500 games per sim count.
"""

import time
from yoot import YutGame, RandomController, MonteCarloController

SIM_COUNTS = [5, 10, 32, 100, 316, 1000]
NUM_GAMES = 500


def run_games(num_sims, num_games):
    mc_wins = 0
    for g in range(num_games):
        game = YutGame(['Random', 'MC'], 2)
        controllers = {
            0: RandomController(),
            1: MonteCarloController(game, 1, num_simulations=num_sims),
        }

        turn = 0
        while game.game_state == 'playing' and turn < 500:
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
                if game.game_state != 'playing':
                    break
            if game.game_state == 'finished':
                break
            game.next_turn()
            turn += 1

        if game.rankings and game.rankings[0] == 1:
            mc_wins += 1

        if (g + 1) % 100 == 0:
            print(f"    sims={num_sims:4d}  game {g+1:3d}/{num_games}  MC wins so far: {mc_wins}", flush=True)

    return mc_wins


start = time.time()
results = []

print("=" * 60)
print("MC WIN RATE SCALING EXPERIMENT")
print(f"Player 0 = Random, Player 1 = MC, {NUM_GAMES} games each")
print("=" * 60)

for num_sims in SIM_COUNTS:
    t0 = time.time()
    print(f"\nRunning sims={num_sims} ...", flush=True)
    mc_wins = run_games(num_sims, NUM_GAMES)
    elapsed = time.time() - t0
    win_rate = mc_wins / NUM_GAMES
    results.append((num_sims, mc_wins, win_rate, elapsed))
    print(f"  Done: MC wins {mc_wins}/{NUM_GAMES} = {win_rate:.1%}  ({elapsed:.0f}s)", flush=True)

total_time = time.time() - start

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  {'Sims':>6s}  {'MC Wins':>8s}  {'Win Rate':>9s}  {'Time':>8s}")
print(f"  {'----':>6s}  {'-------':>8s}  {'--------':>9s}  {'----':>8s}")
for num_sims, mc_wins, win_rate, elapsed in results:
    print(f"  {num_sims:6d}  {mc_wins:5d}/500  {win_rate:8.1%}  {elapsed:7.0f}s")
print(f"  Total time: {total_time/3600:.1f} hours")
print("=" * 60)
