import type { PlayerController } from './controller';
import type { GameState, LegalMove } from '../engine/types';

export class RandomController implements PlayerController {
  async chooseMove(_gameState: GameState, legalMoves: LegalMove[]): Promise<{ pieceId: number; steps: number }> {
    const move = legalMoves[Math.floor(Math.random() * legalMoves.length)];
    return { pieceId: move.pieceId, steps: move.steps };
  }
}
