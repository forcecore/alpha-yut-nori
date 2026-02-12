export type Position = string; // '00'-'19', 'aa', 'bb', 'cc', 'pp', 'qq', 'xx', 'yy', 'uu', 'vv'

export type ThrowName = 'do' | 'back_do' | 'gae' | 'geol' | 'yut' | 'mo';

export interface ThrowResult {
  name: ThrowName;
  value: number;
  sticks: boolean[]; // true = flat, false = round (for animation)
}

export interface LegalMove {
  pieceId: number; // -1 = enter new piece
  steps: number;
  destination: string;
}

export interface PieceState {
  id: number;
  position: string | null;
  isActive: boolean;
  hasMoved: boolean;
}

export interface PlayerState {
  id: number;
  name: string;
  activePieces: number;
  finishedPieces: number;
  pieces: PieceState[];
}

export interface GameState {
  currentPlayer: number;
  gameState: 'playing' | 'finished';
  winner: number | null;
  rankings: number[];
  accumulatedMoves: number[];
  players: PlayerState[];
  moveHistory: string[];
}

export interface MoveResult {
  success: boolean;
  captured: boolean;
}
