"""
MCTS (Monte Carlo Tree Search) controller for Yut Nori.

Builds a search tree within the current player's turn, exploring
different move sequences (including skip) via UCB1 selection.
"""

import copy
import math
import random

from .controller import PlayerController


class MCTSNode:
    """A node in the MCTS tree. Each node = a game state with remaining accumulated_moves."""

    __slots__ = ('game', 'player_id', 'parent', 'children',
                 'untried_actions', 'action', 'visits', 'wins')

    def __init__(self, game, player_id, parent=None, action=None):
        self.game = game
        self.player_id = player_id
        self.parent = parent
        self.children = []
        self.action = action  # (piece_id, steps) or None (skip)
        self.visits = 0
        self.wins = 0.0
        self.untried_actions = None  # lazily computed

    def get_untried_actions(self):
        if self.untried_actions is not None:
            return self.untried_actions

        if not self.game.accumulated_moves:
            self.untried_actions = []
            return self.untried_actions

        legal = self.game.get_legal_moves(self.player_id)
        if not legal:
            self.untried_actions = []
            return self.untried_actions

        # Deduplicate: stacked pieces at same position produce identical outcomes
        seen = {}
        for pid, steps, _dest in legal:
            if pid == -1:
                key = ('entry', steps)
            else:
                pos = self.game.players[self.player_id].get_piece_by_id(pid).position
                key = (pos, steps)
            if key not in seen:
                seen[key] = pid

        actions: list[tuple[int, int] | None] = [(pid, steps) for (_, steps), pid in seen.items()]

        # Only allow skip when a piece is on a late-game position
        skip_positions = {'xx', 'yy', 'cc', 'pp', 'qq', '15', '16', '17', '18', '19'}
        player = self.game.players[self.player_id]
        if any(p.position in skip_positions for p in player.get_active_pieces()):
            actions.append(None)

        self.untried_actions = actions
        return self.untried_actions

    def is_terminal(self):
        """Terminal if no moves left or game finished."""
        return (not self.game.accumulated_moves or
                self.game.game_state != 'playing' or
                self.game.check_win_condition())

    def ucb1(self, c=1.414):
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + c * math.sqrt(math.log(self.parent.visits) / self.visits)

    def best_child(self):
        return max(self.children, key=lambda ch: ch.ucb1())

    def most_visited_child(self):
        return max(self.children, key=lambda ch: ch.visits)


class MCTSController(PlayerController):
    """MCTS AI — builds a search tree within the current turn."""

    MAX_ROLLOUT_TURNS = 200

    def __init__(self, game, player_id, num_iterations=1000):
        self.game = game
        self.player_id = player_id
        self.num_iterations = num_iterations
        self._reuse_root = None

    def choose_move(self, game_state: dict, legal_moves: list) -> tuple[int, int] | None:
        # Deduplicate candidates
        seen = {}
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
            self._reuse_root = None
            return candidates[0]

        # Try to reuse saved subtree from previous move in this turn
        root = None
        prior_visits = 0
        if self._reuse_root is not None:
            if self._reuse_root.game.accumulated_moves == list(self.game.accumulated_moves):
                root = self._reuse_root
                prior_visits = root.visits
                root.parent = None
            self._reuse_root = None

        if root is None:
            root = MCTSNode(self._clone_game(), self.player_id)

        for _ in range(self.num_iterations):
            node = self._select(root)
            child = self._expand(node)
            score = self._simulate(child)
            self._backpropagate(child, score)

        # Pick most-visited root child
        if not root.children:
            self._reuse_root = None
            return candidates[0]

        best = root.most_visited_child()

        # Save subtree for potential reuse on next call within this turn
        if best.action is not None:
            self._reuse_root = best
        else:
            self._reuse_root = None

        # Log tree stats
        reuse_str = f" (reused {prior_visits} prior visits)" if prior_visits else ""
        print(f"  [MCTS] {self.num_iterations} iterations{reuse_str}, {len(root.children)} root children:")
        ranked = sorted(root.children, key=lambda c: c.visits, reverse=True)
        for ch in ranked:
            wr = ch.wins / ch.visits if ch.visits > 0 else 0
            action_str = 'skip' if ch.action is None else f'piece={ch.action[0]} steps={ch.action[1]}'
            marker = ' <<' if ch is best else ''
            print(f"    {action_str}: {ch.visits} visits, {wr:.1%} winrate{marker}")

        return best.action

    def _select(self, node):
        """Descend tree via UCB1 until we find a node with untried actions or a terminal."""
        while not node.is_terminal():
            untried = node.get_untried_actions()
            if untried:
                return node
            if not node.children:
                return node
            node = node.best_child()
        return node

    def _expand(self, node):
        """Add one untried child."""
        untried = node.get_untried_actions()
        if not untried or node.is_terminal():
            return node

        action = untried.pop()
        child_game = self._clone_from(node.game)

        if action is None:
            # Skip: clear accumulated moves
            child_game.accumulated_moves = []
        else:
            piece_id, steps = action
            success, captured = child_game.move_piece(self.player_id, piece_id, steps)
            if not success:
                # Invalid move — return parent for rollout
                return node
            if captured:
                child_game.throw_phase(is_bonus=True)
            child_game.check_win_condition()

        child = MCTSNode(child_game, self.player_id, parent=node, action=action)
        node.children.append(child)
        return child

    def _simulate(self, node):
        """Random rollout from node to game end."""
        sim = self._clone_from(node.game)
        player_id = self.player_id
        target_rank_idx = len(sim.rankings)

        # Check if already won
        if len(sim.rankings) > target_rank_idx:
            return 1.0 if sim.rankings[target_rank_idx] == player_id else 0.0

        # Consume remaining moves randomly (no skip in random rollout)
        self._play_remaining_moves(sim, player_id)

        if len(sim.rankings) > target_rank_idx:
            return 1.0 if sim.rankings[target_rank_idx] == player_id else 0.0

        if sim.game_state != 'playing':
            return 0.0

        # Full random playout
        sim.next_turn()

        for _ in range(self.MAX_ROLLOUT_TURNS):
            if sim.game_state != 'playing':
                break

            current_pid = sim.current_player_idx
            sim.throw_phase()
            self._play_remaining_moves(sim, current_pid)

            if len(sim.rankings) > target_rank_idx:
                return 1.0 if sim.rankings[target_rank_idx] == player_id else 0.0

            sim.next_turn()

        if len(sim.rankings) > target_rank_idx:
            return 1.0 if sim.rankings[target_rank_idx] == player_id else 0.0

        return self._heuristic_score(sim)

    def _backpropagate(self, node, score):
        while node is not None:
            node.visits += 1
            node.wins += score
            node = node.parent

    def _clone_game(self):
        """Deepcopy the live game, sharing the Board to avoid file I/O."""
        board = self.game.board
        self.game.board = None
        sim = copy.deepcopy(self.game)
        self.game.board = board
        sim.board = board
        return sim

    def _clone_from(self, game):
        """Deepcopy an already-cloned game, sharing the Board."""
        board = game.board
        game.board = None
        sim = copy.deepcopy(game)
        game.board = board
        sim.board = board
        return sim

    def _play_remaining_moves(self, sim, player_id):
        """Consume all accumulated_moves with random legal choices (no skip)."""
        while sim.accumulated_moves:
            legal = sim.get_legal_moves(player_id)
            if not legal:
                sim.accumulated_moves = []
                break

            pid, steps, _dest = random.choice(legal)
            success, captured = sim.move_piece(player_id, pid, steps)

            if not success:
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
