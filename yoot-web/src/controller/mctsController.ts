import type { PlayerController } from './controller';
import type { GameState, LegalMove } from '../engine/types';
import { YutGame } from '../engine/game';

type Action = { pieceId: number; steps: number } | null;

class MCTSNode {
  game: YutGame;
  playerId: number;
  parent: MCTSNode | null;
  children: MCTSNode[];
  untriedActions: Action[] | null;
  action: Action;
  visits: number;
  wins: number;

  constructor(game: YutGame, playerId: number, parent: MCTSNode | null = null, action: Action = null) {
    this.game = game;
    this.playerId = playerId;
    this.parent = parent;
    this.children = [];
    this.action = action;
    this.visits = 0;
    this.wins = 0;
    this.untriedActions = null; // lazily computed
  }

  getUntriedActions(): Action[] {
    if (this.untriedActions !== null) return this.untriedActions;

    if (this.game.accumulatedMoves.length === 0) {
      this.untriedActions = [];
      return this.untriedActions;
    }

    const legal = this.game.getLegalMoves(this.playerId);
    if (legal.length === 0) {
      this.untriedActions = [];
      return this.untriedActions;
    }

    // Deduplicate: stacked pieces at same position produce identical outcomes
    const seen = new Map<string, number>();
    for (const { pieceId, steps } of legal) {
      let key: string;
      if (pieceId === -1) {
        key = `entry:${steps}`;
      } else {
        const pos = this.game.players[this.playerId].getPieceById(pieceId).position;
        key = `${pos}:${steps}`;
      }
      if (!seen.has(key)) seen.set(key, pieceId);
    }

    const actions: Action[] = [];
    for (const [key, pieceId] of seen) {
      const steps = Number(key.split(':')[1]);
      actions.push({ pieceId, steps });
    }

    // Only allow skip when a piece is on a late-game position
    const skipPositions = new Set(['xx', 'yy', 'cc', 'pp', 'qq', '15', '16', '17', '18', '19']);
    const player = this.game.players[this.playerId];
    if (player.getActivePieces().some(p => skipPositions.has(p.position!))) {
      actions.push(null);
    }

    this.untriedActions = actions;
    return this.untriedActions;
  }

  isTerminal(): boolean {
    return (
      this.game.accumulatedMoves.length === 0 ||
      this.game.gameState !== 'playing' ||
      this.game.checkWinCondition()
    );
  }

  ucb1(c = 1.414): number {
    if (this.visits === 0) return Infinity;
    return (this.wins / this.visits) + c * Math.sqrt(Math.log(this.parent!.visits) / this.visits);
  }

  bestChild(): MCTSNode {
    let best = this.children[0];
    let bestScore = best.ucb1();
    for (let i = 1; i < this.children.length; i++) {
      const score = this.children[i].ucb1();
      if (score > bestScore) {
        bestScore = score;
        best = this.children[i];
      }
    }
    return best;
  }

  mostVisitedChild(): MCTSNode {
    let best = this.children[0];
    for (let i = 1; i < this.children.length; i++) {
      if (this.children[i].visits > best.visits) {
        best = this.children[i];
      }
    }
    return best;
  }
}

export class MCTSController implements PlayerController {
  private game: YutGame;
  private playerId: number;
  private numIterations: number;
  private reuseRoot: MCTSNode | null = null;

  static readonly MAX_ROLLOUT_TURNS = 200;

  constructor(game: YutGame, playerId: number, numIterations = 1000) {
    this.game = game;
    this.playerId = playerId;
    this.numIterations = numIterations;
  }

  private movesMatch(a: number[], b: number[]): boolean {
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) {
      if (a[i] !== b[i]) return false;
    }
    return true;
  }

  async chooseMove(_gameState: GameState, legalMoves: LegalMove[]): Promise<{ pieceId: number; steps: number } | null> {
    // Deduplicate candidates
    const seen = new Map<string, number>();
    for (const { pieceId, steps } of legalMoves) {
      let key: string;
      if (pieceId === -1) {
        key = `entry:${steps}`;
      } else {
        const pos = this.game.players[this.playerId].getPieceById(pieceId).position;
        key = `${pos}:${steps}`;
      }
      if (!seen.has(key)) seen.set(key, pieceId);
    }

    const candidates: { pieceId: number; steps: number }[] = [];
    for (const [key, pieceId] of seen) {
      const steps = Number(key.split(':')[1]);
      candidates.push({ pieceId, steps });
    }

    if (candidates.length === 1) {
      this.reuseRoot = null;
      return candidates[0];
    }

    // Try to reuse saved subtree from previous move in this turn
    let root: MCTSNode | null = null;
    let priorVisits = 0;
    if (this.reuseRoot !== null) {
      if (this.movesMatch(this.reuseRoot.game.accumulatedMoves, this.game.accumulatedMoves)) {
        root = this.reuseRoot;
        priorVisits = root.visits;
        root.parent = null;
      }
      this.reuseRoot = null;
    }

    if (root === null) {
      root = new MCTSNode(this.game.clone(), this.playerId);
    }

    for (let i = 0; i < this.numIterations; i++) {
      const node = this.select(root);
      const child = this.expand(node);
      const score = this.simulate(child);
      this.backpropagate(child, score);
    }

    if (root.children.length === 0) {
      this.reuseRoot = null;
      return candidates[0];
    }

    const best = root.mostVisitedChild();

    // Save subtree for potential reuse on next call within this turn
    this.reuseRoot = best.action !== null ? best : null;

    // Log tree stats
    const reuseStr = priorVisits ? ` (reused ${priorVisits} prior visits)` : '';
    const ranked = [...root.children].sort((a, b) => b.visits - a.visits);
    console.log(`[MCTS] ${this.numIterations} iterations${reuseStr}, ${root.children.length} root children:`);
    for (const ch of ranked) {
      const wr = ch.visits > 0 ? ch.wins / ch.visits : 0;
      const actionStr = ch.action === null ? 'skip' : `piece=${ch.action.pieceId} steps=${ch.action.steps}`;
      const marker = ch === best ? ' <<' : '';
      console.log(`  ${actionStr}: ${ch.visits} visits, ${(wr * 100).toFixed(1)}% winrate${marker}`);
    }

    return best.action;
  }

  private select(node: MCTSNode): MCTSNode {
    while (!node.isTerminal()) {
      const untried = node.getUntriedActions();
      if (untried.length > 0) return node;
      if (node.children.length === 0) return node;
      node = node.bestChild();
    }
    return node;
  }

  private expand(node: MCTSNode): MCTSNode {
    const untried = node.getUntriedActions();
    if (untried.length === 0 || node.isTerminal()) return node;

    const action = untried.pop()!;
    const childGame = node.game.clone();

    if (action === null) {
      childGame.accumulatedMoves = [];
    } else {
      const { success, captured } = childGame.movePiece(this.playerId, action.pieceId, action.steps);
      if (!success) return node;
      if (captured) childGame.throwPhase(true);
      childGame.checkWinCondition();
    }

    const child = new MCTSNode(childGame, this.playerId, node, action);
    node.children.push(child);
    return child;
  }

  private simulate(node: MCTSNode): number {
    const sim = node.game.clone();
    const playerId = this.playerId;
    const targetRankIdx = sim.rankings.length;

    if (sim.rankings.length > targetRankIdx) {
      return sim.rankings[targetRankIdx] === playerId ? 1 : 0;
    }

    this.playRemainingMoves(sim, playerId);

    if (sim.rankings.length > targetRankIdx) {
      return sim.rankings[targetRankIdx] === playerId ? 1 : 0;
    }

    if (sim.gameState !== 'playing') return 0;

    sim.nextTurn();

    for (let t = 0; t < MCTSController.MAX_ROLLOUT_TURNS; t++) {
      if (sim.gameState !== 'playing') break;

      const currentPid = sim.currentPlayerIdx;
      sim.throwPhase();
      this.playRemainingMoves(sim, currentPid);

      if (sim.rankings.length > targetRankIdx) {
        return sim.rankings[targetRankIdx] === playerId ? 1 : 0;
      }

      sim.nextTurn();
    }

    if (sim.rankings.length > targetRankIdx) {
      return sim.rankings[targetRankIdx] === playerId ? 1 : 0;
    }

    return this.heuristicScore(sim);
  }

  private backpropagate(node: MCTSNode | null, score: number): void {
    while (node !== null) {
      node.visits += 1;
      node.wins += score;
      node = node.parent;
    }
  }

  private playRemainingMoves(sim: YutGame, playerId: number): void {
    while (sim.accumulatedMoves.length > 0) {
      const legal = sim.getLegalMoves(playerId);
      if (legal.length === 0) {
        sim.accumulatedMoves = [];
        break;
      }

      const pick = legal[Math.floor(Math.random() * legal.length)];
      const { success, captured } = sim.movePiece(playerId, pick.pieceId, pick.steps);

      if (!success) {
        sim.accumulatedMoves = [];
        break;
      }

      if (captured) sim.throwPhase(true);
      if (sim.checkWinCondition()) break;
    }
  }

  private heuristicScore(sim: YutGame): number {
    const myFinished = sim.players[this.playerId].getFinishedPieces().length;
    let score = myFinished / 4.0;

    let bestOpponent = 0;
    for (const p of sim.players) {
      if (p.playerId !== this.playerId) {
        bestOpponent = Math.max(bestOpponent, p.getFinishedPieces().length);
      }
    }

    if (myFinished > bestOpponent) score += 0.1;
    return score;
  }
}
