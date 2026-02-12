export class Piece {
  pieceId: number;
  playerId: number;
  position: string | null = null;
  isActive = false;
  hasMoved = false;

  constructor(pieceId: number, playerId: number) {
    this.pieceId = pieceId;
    this.playerId = playerId;
  }

  enterBoard(entryPosition: string): void {
    this.position = entryPosition;
    this.isActive = true;
    this.hasMoved = true;
  }

  moveTo(position: string): void {
    this.position = position;
    this.hasMoved = true;
  }

  finish(): void {
    this.position = null;
    this.isActive = false;
  }

  capture(): void {
    this.position = null;
    this.isActive = false;
    this.hasMoved = false;
  }

  hasFinished(): boolean {
    return !this.isActive && this.hasMoved && this.position === null;
  }

  clone(): Piece {
    const p = new Piece(this.pieceId, this.playerId);
    p.position = this.position;
    p.isActive = this.isActive;
    p.hasMoved = this.hasMoved;
    return p;
  }
}
