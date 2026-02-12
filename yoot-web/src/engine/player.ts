import { Piece } from './piece';

export class Player {
  static readonly NUM_PIECES = 4;

  playerId: number;
  name: string;
  pieces: Piece[];

  constructor(playerId: number, name: string) {
    this.playerId = playerId;
    this.name = name;
    this.pieces = Array.from(
      { length: Player.NUM_PIECES },
      (_, i) => new Piece(i, playerId)
    );
  }

  getActivePieces(): Piece[] {
    return this.pieces.filter(p => p.isActive);
  }

  getFinishedPieces(): Piece[] {
    return this.pieces.filter(p => p.hasFinished());
  }

  getInactivePieces(): Piece[] {
    return this.pieces.filter(p => !p.isActive && !p.hasFinished());
  }

  hasFinished(): boolean {
    return this.getFinishedPieces().length === Player.NUM_PIECES;
  }

  getStacks(): Map<string, Piece[]> {
    const stacks = new Map<string, Piece[]>();
    for (const piece of this.getActivePieces()) {
      if (piece.position !== null) {
        const list = stacks.get(piece.position);
        if (list) {
          list.push(piece);
        } else {
          stacks.set(piece.position, [piece]);
        }
      }
    }
    return stacks;
  }

  getPieceById(pieceId: number): Piece {
    return this.pieces[pieceId];
  }

  canEnterNewPiece(): boolean {
    return this.getInactivePieces().length > 0;
  }

  clone(): Player {
    const p = new Player(this.playerId, this.name);
    p.pieces = this.pieces.map(piece => piece.clone());
    return p;
  }
}
