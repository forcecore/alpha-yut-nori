import { Board } from './board';
import { Player } from './player';
import { Piece } from './piece';
import { YutThrow } from './yutThrow';
import type { GameState, LegalMove, MoveResult, ThrowResult } from './types';

export class YutGame {
  board: Board;
  numPlayers: number;
  players: Player[];
  currentPlayerIdx: number;
  gameState: 'playing' | 'finished';
  winner: number | null;
  rankings: number[];
  accumulatedMoves: number[];
  moveHistory: string[];

  constructor(playerNames?: string[], numPlayers = 4) {
    if (numPlayers < 2 || numPlayers > 6) {
      throw new Error('Number of players must be between 2 and 6');
    }

    const names = playerNames ?? Array.from({ length: numPlayers }, (_, i) => `Player ${i}`);
    if (names.length !== numPlayers) {
      throw new Error(`Must provide exactly ${numPlayers} player names`);
    }

    this.board = new Board();
    this.numPlayers = numPlayers;
    this.players = names.map((name, i) => new Player(i, name));
    this.currentPlayerIdx = 0;
    this.gameState = 'playing';
    this.winner = null;
    this.rankings = [];
    this.accumulatedMoves = [];
    this.moveHistory = [];
  }

  getCurrentPlayer(): Player {
    return this.players[this.currentPlayerIdx];
  }

  throwPhase(isBonus = false): ThrowResult[] {
    const throws: ThrowResult[] = [];

    if (!isBonus) {
      this.accumulatedMoves = [];
    }

    while (true) {
      const result = YutThrow.throw();
      throws.push(result);
      this.accumulatedMoves.push(result.value);

      const bonusMsg = isBonus ? ' (bonus)' : '';
      this.logMove(
        `${this.getCurrentPlayer().name} threw ${result.name} (${result.value} spaces)${bonusMsg}`
      );

      if (!YutThrow.grantsExtraTurn(result.name)) break;
    }

    return throws;
  }

  getLegalMoves(playerId: number): LegalMove[] {
    const player = this.players[playerId];
    const moves: LegalMove[] = [];

    for (const piece of player.getActivePieces()) {
      // Special case: at 00 with hasMoved → any move value exits the board (except back-do)
      if (piece.position === '00' && piece.hasMoved) {
        for (const steps of this.accumulatedMoves) {
          if (steps === -1) {
            for (const dest of this.board.getBackDoDestinations('00')) {
              moves.push({ pieceId: piece.pieceId, steps, destination: dest });
            }
          } else {
            moves.push({ pieceId: piece.pieceId, steps, destination: 'EXIT' });
          }
        }
        continue;
      }
      for (const steps of this.accumulatedMoves) {
        if (steps === -1) {
          for (const dest of this.board.getBackDoDestinations(piece.position!)) {
            moves.push({ pieceId: piece.pieceId, steps, destination: dest });
          }
        } else {
          const dest = this.board.getNextPosition(piece.position!, steps);
          if (dest !== null) {
            moves.push({ pieceId: piece.pieceId, steps, destination: dest });
          }
        }
      }
    }

    // Check if new piece can enter
    if (player.canEnterNewPiece() && this.accumulatedMoves.length > 0) {
      for (const steps of this.accumulatedMoves) {
        if (steps >= 1 && steps <= 5) {
          const entryPos = String(steps).padStart(2, '0');
          moves.push({ pieceId: -1, steps, destination: entryPos });
        }
      }
    }

    return moves;
  }

  movePiece(playerId: number, pieceId: number, steps: number, destination?: string): MoveResult {
    const player = this.players[playerId];

    // Handle entering new piece
    if (pieceId === -1) {
      if (!player.canEnterNewPiece()) return { success: false, captured: false };
      if (!this.accumulatedMoves.includes(steps)) return { success: false, captured: false };
      if (steps < 1 || steps > 5) return { success: false, captured: false };

      const entryPosition = String(steps).padStart(2, '0');
      const newPiece = player.getInactivePieces()[0];
      newPiece.enterBoard(entryPosition);
      this.removeAccumulatedMove(steps);

      const shortcut = this.board.triggersShortcut(entryPosition);
      if (shortcut) {
        this.logMove(
          `${player.name} entered new piece (Piece ${newPiece.pieceId}) at position ${entryPosition} (shortcut position)`
        );
      } else {
        this.logMove(
          `${player.name} entered new piece (Piece ${newPiece.pieceId}) at position ${entryPosition}`
        );
      }

      const captured = this.checkCapture(playerId, newPiece.position!);
      return { success: true, captured };
    }

    // Handle moving existing piece
    const piece = player.getPieceById(pieceId);
    if (!piece.isActive) return { success: false, captured: false };
    if (!this.accumulatedMoves.includes(steps)) return { success: false, captured: false };

    const currentPos = piece.position!;

    // Special case: at 00 with hasMoved → piece exits the board (but not on back-do)
    if (currentPos === '00' && piece.hasMoved && steps !== -1) {
      const stack = this.getStackAtPosition(playerId, currentPos);
      const pieceStr = stack.length === 1 ? `Piece ${pieceId}` : `Stack (x${stack.length})`;

      for (const stacked of stack) {
        stacked.finish();
      }

      this.removeAccumulatedMove(steps);
      this.logMove(`${player.name}'s ${pieceStr} exited the board!`);
      return { success: true, captured: false };
    }

    // For back-do with explicit destination, use it directly
    let newPos: string | null;
    if (steps === -1 && destination) {
      const valid = this.board.getBackDoDestinations(currentPos);
      if (!valid.includes(destination)) return { success: false, captured: false };
      newPos = destination;
    } else {
      newPos = this.board.getNextPosition(currentPos, steps);
    }
    if (newPos === null) return { success: false, captured: false };

    // Get all pieces in stack at current position
    const stack = this.getStackAtPosition(playerId, currentPos);

    // Move all pieces in stack
    for (const stacked of stack) {
      stacked.moveTo(newPos);
    }

    this.removeAccumulatedMove(steps);

    const pieceStr = stack.length === 1 ? `Piece ${pieceId}` : `Stack (x${stack.length})`;

    if (newPos === '00') {
      this.logMove(
        `${player.name} moved ${pieceStr} ${steps} spaces to position 00 (at goal - next move exits)`
      );
    } else if (this.board.triggersShortcut(newPos)) {
      this.logMove(
        `${player.name} moved ${pieceStr} ${steps} spaces to ${newPos} (shortcut position - next move uses diagonal)`
      );
    } else {
      this.logMove(`${player.name} moved ${pieceStr} ${steps} spaces to ${newPos}`);
    }

    const captured = this.checkCapture(playerId, newPos);
    return { success: true, captured };
  }

  getStackAtPosition(playerId: number, position: string): Piece[] {
    const player = this.players[playerId];
    return player.getActivePieces().filter(p => p.position === position);
  }

  checkCapture(playerId: number, position: string): boolean {
    let capturedAny = false;

    for (const otherPlayer of this.players) {
      if (otherPlayer.playerId === playerId) continue;

      const capturedPieces = otherPlayer.getActivePieces().filter(p => p.position === position);
      if (capturedPieces.length > 0) {
        capturedAny = true;
        for (const piece of capturedPieces) {
          piece.capture();
          this.logMove(
            `${this.players[playerId].name} captured ${otherPlayer.name}'s Piece ${piece.pieceId}!`
          );
        }
      }
    }

    return capturedAny;
  }

  checkWinCondition(): boolean {
    let changed = false;
    for (const player of this.players) {
      if (player.hasFinished() && !this.rankings.includes(player.playerId)) {
        this.rankings.push(player.playerId);
        const place = this.rankings.length;
        this.logMove(`${player.name} finishes in place #${place}!`);
        if (this.winner === null) {
          this.winner = player.playerId;
        }
        changed = true;
      }
    }

    // Game over when all but one player have finished
    const remaining = this.players.filter(p => !this.rankings.includes(p.playerId));
    if (remaining.length <= 1) {
      if (remaining.length === 1) {
        this.rankings.push(remaining[0].playerId);
      }
      this.gameState = 'finished';
      return true;
    }

    return changed;
  }

  nextTurn(): void {
    for (let i = 0; i < this.numPlayers; i++) {
      this.currentPlayerIdx = (this.currentPlayerIdx + 1) % this.numPlayers;
      if (!this.rankings.includes(this.currentPlayerIdx)) break;
    }
    this.accumulatedMoves = [];
  }

  logMove(message: string): void {
    this.moveHistory.push(message);
  }

  getGameState(): GameState {
    return {
      currentPlayer: this.currentPlayerIdx,
      gameState: this.gameState,
      winner: this.winner,
      rankings: [...this.rankings],
      accumulatedMoves: [...this.accumulatedMoves],
      players: this.players.map(p => ({
        id: p.playerId,
        name: p.name,
        activePieces: p.getActivePieces().length,
        finishedPieces: p.getFinishedPieces().length,
        pieces: p.pieces.map(piece => ({
          id: piece.pieceId,
          position: piece.position,
          isActive: piece.isActive,
          hasMoved: piece.hasMoved,
        })),
      })),
      moveHistory: this.moveHistory.slice(-10),
    };
  }

  getAllPieces(): Piece[] {
    return this.players.flatMap(p => p.pieces);
  }

  clone(): YutGame {
    const game = Object.create(YutGame.prototype) as YutGame;
    game.board = this.board; // shared — stateless lookup tables
    game.numPlayers = this.numPlayers;
    game.players = this.players.map(p => p.clone());
    game.currentPlayerIdx = this.currentPlayerIdx;
    game.gameState = this.gameState;
    game.winner = this.winner;
    game.rankings = [...this.rankings];
    game.accumulatedMoves = [...this.accumulatedMoves];
    game.moveHistory = []; // don't clone history for simulations
    return game;
  }

  private removeAccumulatedMove(steps: number): void {
    const idx = this.accumulatedMoves.indexOf(steps);
    if (idx !== -1) this.accumulatedMoves.splice(idx, 1);
  }
}
