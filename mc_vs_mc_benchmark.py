#!/usr/bin/env python3
"""
Benchmark: Monte Carlo AI (player 0, goes first) vs Monte Carlo AI (player 1, goes second).
Runs 1000 games with 3000 simulations per move decision.
"""

import sys
import time

from yoot import MonteCarloController, YutGame

NUM_GAMES = 1000
NUM_SIMS = 100

wins = {0: 0, 1: 0}
start = time.time()

for g in range(NUM_GAMES):
    game_start = time.time()
    game = YutGame(["MC0", "MC1"], 2)
    mc0 = MonteCarloController(game, 0, num_simulations=NUM_SIMS)
    mc1 = MonteCarloController(game, 1, num_simulations=NUM_SIMS)
    controllers = {0: mc0, 1: mc1}

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

    winner = game.rankings[0] if game.rankings else -1
    wins[winner] = wins.get(winner, 0) + 1
    elapsed = time.time() - game_start

    print(
        f"Game {g + 1:4d}: winner=MC{winner} turns={turn:3d} ({elapsed:.1f}s)  "
        f"Running: MC0={wins[0]} MC1={wins[1]}",
        flush=True,
    )

total_time = time.time() - start
print(f"\n{'=' * 60}")
print(f"FINAL RESULTS — {NUM_GAMES} games, {NUM_SIMS} sims/move")
print(f"{'=' * 60}")
print(f"  MC0 (goes first):  {wins[0]:4d} wins ({wins[0] / NUM_GAMES:.1%})")
print(f"  MC1 (goes second): {wins[1]:4d} wins ({wins[1] / NUM_GAMES:.1%})")
print(f"  Total time: {total_time / 3600:.1f} hours")
print(f"  Avg time per game: {total_time / NUM_GAMES:.1f}s")
print(f"{'=' * 60}")
