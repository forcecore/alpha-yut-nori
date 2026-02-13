#!/usr/bin/env python3
"""Play 3 games with MCTS output visible to diagnose behavior."""

from yoot import MCTSController, MonteCarloController, YutGame


def play_game(game_num: int) -> int:
    mcts_pid = 0
    mc_pid = 1

    game = YutGame(["MCTS", "MC"], 2)
    controllers = {
        mcts_pid: MCTSController(game, mcts_pid, num_iterations=100),
        mc_pid: MonteCarloController(game, mc_pid, num_simulations=100),
    }

    for turn in range(500):
        if game.game_state != "playing":
            break

        pid = game.current_player_idx
        ctrl = controllers[pid]
        game.throw_phase()

        move_num = 0
        while game.accumulated_moves:
            legal = game.get_legal_moves(pid)
            if not legal:
                game.accumulated_moves = []
                break

            if pid == mcts_pid:
                print(
                    f"  [Turn {turn}, Move {move_num}] accumulated={game.accumulated_moves}, {len(legal)} legal moves"
                )

            choice = ctrl.choose_move(game.get_game_state(), legal)

            if choice is None:
                if pid == mcts_pid:
                    print(f"  >>> MCTS chose SKIP")
                game.accumulated_moves = []
                break

            piece_id, steps = choice
            if pid == mcts_pid:
                print(f"  >>> MCTS chose piece={piece_id} steps={steps}")

            success, captured = game.move_piece(pid, piece_id, steps)
            if not success:
                game.accumulated_moves = []
                break
            if captured:
                game.throw_phase(is_bonus=True)
            if game.check_win_condition():
                break
            move_num += 1

        if game.game_state == "finished":
            break
        game.next_turn()

    winner = game.rankings[0] if game.rankings else -1
    label = "MCTS" if winner == mcts_pid else "MC"
    print(f"\n=== Game {game_num}: {label} wins ===\n")
    return winner


for i in range(3):
    print(f"\n{'=' * 60}\nGAME {i + 1}\n{'=' * 60}")
    play_game(i + 1)
