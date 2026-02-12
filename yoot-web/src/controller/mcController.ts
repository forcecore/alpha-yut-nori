import type { PlayerController } from './controller';
import type { GameState, LegalMove } from '../engine/types';
import { YutGame } from '../engine/game';

export class MonteCarloController implements PlayerController {
  private game: YutGame;
  private playerId: number;
  private numSimulations: number;

  static readonly MAX_ROLLOUT_TURNS = 200;

  constructor(game: YutGame, playerId: number, numSimulations = 100) {
    this.game = game;
    this.playerId = playerId;
    this.numSimulations = numSimulations;
  }

  async chooseMove(_gameState: GameState, legalMoves: LegalMove[]): Promise<{ pieceId: number; steps: number }> {
    // Deduplicate: stacked pieces at same position produce identical outcomes
    const seen = new Map<string, number>(); // key -> pieceId
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

    if (candidates.length === 1) return candidates[0];

    const results: { move: { pieceId: number; steps: number }; winRate: number }[] = [];

    for (const move of candidates) {
      let wins = 0;
      for (let i = 0; i < this.numSimulations; i++) {
        wins += this.simulate(move.pieceId, move.steps);
      }
      results.push({ move, winRate: wins / this.numSimulations });
    }

    results.sort((a, b) => b.winRate - a.winRate);

    console.log(`[MC] Evaluating ${results.length} moves (${this.numSimulations} sims each):`);
    for (const { move, winRate } of results) {
      const marker = move === results[0].move ? ' <<' : '';
      console.log(`  piece=${move.pieceId} steps=${move.steps}: ${(winRate * 100).toFixed(1)}%${marker}`);
    }

    return results[0].move;
  }

  private simulate(pieceId: number, steps: number): number {
    const sim = this.game.clone();
    const playerId = this.playerId;
    const targetRankIdx = sim.rankings.length;

    const { success, captured } = sim.movePiece(playerId, pieceId, steps);
    if (!success) return 0;

    if (captured) sim.throwPhase(true);

    sim.checkWinCondition();
    if (sim.rankings.length > targetRankIdx) {
      return sim.rankings[targetRankIdx] === playerId ? 1 : 0;
    }

    this.playRemainingMoves(sim, playerId);

    if (sim.rankings.length > targetRankIdx) {
      return sim.rankings[targetRankIdx] === playerId ? 1 : 0;
    }

    if (sim.gameState !== 'playing') return 0;

    sim.nextTurn();

    for (let t = 0; t < MonteCarloController.MAX_ROLLOUT_TURNS; t++) {
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
