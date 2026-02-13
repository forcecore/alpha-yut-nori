import type { PlayerController } from './controller';
import type { GameState, LegalMove } from '../engine/types';

export class HumanController implements PlayerController {
  private resolveMove: ((move: { pieceId: number; steps: number; destination?: string } | null) => void) | null = null;

  chooseMove(_gameState: GameState, _legalMoves: LegalMove[]): Promise<{ pieceId: number; steps: number; destination?: string } | null> {
    return new Promise(resolve => {
      this.resolveMove = resolve;
    });
  }

  submitMove(pieceId: number, steps: number, destination?: string): void {
    this.resolveMove?.({ pieceId, steps, destination });
    this.resolveMove = null;
  }

  submitSkip(): void {
    this.resolveMove?.(null);
    this.resolveMove = null;
  }
}
