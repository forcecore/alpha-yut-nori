import type { GameState, LegalMove } from '../engine/types';

export interface PlayerController {
  chooseMove(
    gameState: GameState,
    legalMoves: LegalMove[]
  ): Promise<{ pieceId: number; steps: number } | null>;
}

export type ControllerType = 'human' | 'random' | 'mc' | 'mcts';
