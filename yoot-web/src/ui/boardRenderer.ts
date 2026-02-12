import { Piece } from '../engine/piece';
import {
  POSITION_COORDS,
  BOARD_EDGES,
  CORNER_POSITIONS,
  NODE_RADIUS,
  CORNER_RADIUS,
  PIECE_RADIUS,
  PLAYER_COLORS,
  PIECE_KEYS,
} from './constants';

const SVG_NS = 'http://www.w3.org/2000/svg';

interface PieceGroup {
  playerId: number;
  pieces: Piece[];
  position: string;
}

export class BoardRenderer {
  private svg: SVGSVGElement;
  private staticLayer: SVGGElement;
  private pieceLayer: SVGGElement;
  private highlightLayer: SVGGElement;

  private onPieceClickCb: ((playerId: number, pieceId: number) => void) | null = null;
  private onPositionClickCb: ((position: string) => void) | null = null;
  private onNewPieceClickCb: (() => void) | null = null;

  constructor(svgElement: SVGSVGElement) {
    this.svg = svgElement;
    this.staticLayer = this.createGroup('static-layer');
    this.highlightLayer = this.createGroup('highlight-layer');
    this.pieceLayer = this.createGroup('piece-layer');

    this.svg.appendChild(this.staticLayer);
    this.svg.appendChild(this.highlightLayer);
    this.svg.appendChild(this.pieceLayer);

    this.drawStaticBoard();
  }

  private createGroup(id: string): SVGGElement {
    const g = document.createElementNS(SVG_NS, 'g');
    g.id = id;
    return g;
  }

  private drawStaticBoard(): void {
    // Draw edges (lines)
    for (const [a, b] of BOARD_EDGES) {
      const ca = POSITION_COORDS[a];
      const cb = POSITION_COORDS[b];
      const line = document.createElementNS(SVG_NS, 'line');
      line.setAttribute('x1', String(ca.x));
      line.setAttribute('y1', String(ca.y));
      line.setAttribute('x2', String(cb.x));
      line.setAttribute('y2', String(cb.y));
      line.classList.add('board-line');
      this.staticLayer.appendChild(line);
    }

    // Draw nodes (circles) and labels
    for (const [pos, coord] of Object.entries(POSITION_COORDS)) {
      const isCorner = CORNER_POSITIONS.has(pos);
      const r = isCorner ? CORNER_RADIUS : NODE_RADIUS;

      const circle = document.createElementNS(SVG_NS, 'circle');
      circle.setAttribute('cx', String(coord.x));
      circle.setAttribute('cy', String(coord.y));
      circle.setAttribute('r', String(r));
      circle.classList.add('board-node');
      if (isCorner) circle.classList.add('corner');
      circle.dataset.position = pos;

      circle.addEventListener('click', () => {
        this.onPositionClickCb?.(pos);
      });

      this.staticLayer.appendChild(circle);

      // Label
      const label = document.createElementNS(SVG_NS, 'text');
      label.setAttribute('x', String(coord.x));
      label.setAttribute('y', String(coord.y + r + 12));
      label.classList.add('board-label');
      label.textContent = pos;
      this.staticLayer.appendChild(label);
    }

    // Special markers for START/GOAL at 00
    const pos00 = POSITION_COORDS['00'];
    const startLabel = document.createElementNS(SVG_NS, 'text');
    startLabel.setAttribute('x', String(pos00.x));
    startLabel.setAttribute('y', String(pos00.y));
    startLabel.classList.add('board-label');
    startLabel.style.fontSize = '9px';
    startLabel.style.fill = '#aaa';
    startLabel.textContent = 'START';
    this.staticLayer.appendChild(startLabel);
  }

  updatePieces(allPieces: Piece[]): void {
    // Clear piece layer
    while (this.pieceLayer.firstChild) {
      this.pieceLayer.removeChild(this.pieceLayer.firstChild);
    }

    // Group pieces by position and player
    const groups = new Map<string, PieceGroup[]>();

    for (const piece of allPieces) {
      if (!piece.isActive || piece.position === null) continue;
      const key = piece.position;
      if (!groups.has(key)) groups.set(key, []);
      const posGroups = groups.get(key)!;

      let group = posGroups.find(g => g.playerId === piece.playerId);
      if (!group) {
        group = { playerId: piece.playerId, pieces: [], position: piece.position };
        posGroups.push(group);
      }
      group.pieces.push(piece);
    }

    // Draw each group
    for (const [position, posGroups] of groups) {
      const coord = POSITION_COORDS[position];
      if (!coord) continue;

      // Offset multiple player groups at same position (x-offset between players)
      const numGroups = posGroups.length;
      posGroups.forEach((group, gi) => {
        const groupOffsetX = numGroups > 1
          ? (gi - (numGroups - 1) / 2) * 28
          : 0;

        // Draw each piece in the stack with a y-offset so they look stacked
        const stackSize = group.pieces.length;
        const STACK_OFFSET_Y = -8; // pixels between stacked pieces

        for (let si = 0; si < stackSize; si++) {
          const piece = group.pieces[si];
          const cx = coord.x + groupOffsetX;
          const cy = coord.y + si * STACK_OFFSET_Y;

          const g = document.createElementNS(SVG_NS, 'g');
          g.classList.add('piece-group');
          g.style.transform = `translate(${cx}px, ${cy}px)`;
          g.dataset.playerId = String(group.playerId);
          g.dataset.pieceId = String(piece.pieceId);
          g.dataset.position = position;

          g.addEventListener('click', (e) => {
            e.stopPropagation();
            this.onPieceClickCb?.(group.playerId, group.pieces[0].pieceId);
          });

          // Circle
          const circle = document.createElementNS(SVG_NS, 'circle');
          circle.setAttribute('cx', '0');
          circle.setAttribute('cy', '0');
          circle.setAttribute('r', String(PIECE_RADIUS));
          circle.classList.add('piece-circle');
          circle.style.fill = PLAYER_COLORS[group.playerId] ?? '#888';
          g.appendChild(circle);

          // Label on topmost piece only
          if (si === stackSize - 1) {
            const label = document.createElementNS(SVG_NS, 'text');
            label.setAttribute('x', '0');
            label.setAttribute('y', '0');
            label.classList.add('piece-label');
            label.textContent = PIECE_KEYS[piece.pieceId] ?? String(piece.pieceId);
            g.appendChild(label);
          }

          this.pieceLayer.appendChild(g);
        }
      });
    }
  }

  highlightPieces(playerId: number, pieceIds: Set<number>, hasNewPiece: boolean): void {
    this.clearHighlights();

    // Highlight active pieces
    const groups = this.pieceLayer.querySelectorAll('.piece-group');
    for (const g of groups) {
      const gEl = g as SVGGElement;
      const pid = Number(gEl.dataset.playerId);
      const pieceId = Number(gEl.dataset.pieceId);
      if (pid === playerId && pieceIds.has(pieceId)) {
        const ring = document.createElementNS(SVG_NS, 'circle');
        ring.setAttribute('cx', '0');
        ring.setAttribute('cy', '0');
        ring.setAttribute('r', String(PIECE_RADIUS + 5));
        ring.classList.add('highlight-ring');
        gEl.insertBefore(ring, gEl.firstChild);
      }
    }

    // Highlight new piece option on the side panel (handled by gameUI)
  }

  highlightDestinations(positions: Set<string>): void {
    for (const pos of positions) {
      const coord = POSITION_COORDS[pos];
      if (!coord) continue;

      const circle = document.createElementNS(SVG_NS, 'circle');
      circle.setAttribute('cx', String(coord.x));
      circle.setAttribute('cy', String(coord.y));
      circle.setAttribute('r', String(CORNER_RADIUS));
      circle.classList.add('dest-highlight');
      circle.dataset.destPosition = pos;
      circle.style.cursor = 'pointer';
      circle.addEventListener('click', () => {
        this.onPositionClickCb?.(pos);
      });
      this.highlightLayer.appendChild(circle);
    }
  }

  clearHighlights(): void {
    while (this.highlightLayer.firstChild) {
      this.highlightLayer.removeChild(this.highlightLayer.firstChild);
    }
    // Remove highlight rings from piece groups
    for (const ring of this.pieceLayer.querySelectorAll('.highlight-ring')) {
      ring.remove();
    }
  }

  onPieceClick(cb: (playerId: number, pieceId: number) => void): void {
    this.onPieceClickCb = cb;
  }

  onPositionClick(cb: (position: string) => void): void {
    this.onPositionClickCb = cb;
  }

  onNewPieceClick(cb: () => void): void {
    this.onNewPieceClickCb = cb;
  }

  triggerNewPieceClick(): void {
    this.onNewPieceClickCb?.();
  }
}
