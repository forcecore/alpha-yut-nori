import { Piece } from '../engine/piece';
import { Player } from '../engine/player';
import {
  POSITION_COORDS,
  BOARD_EDGES,
  CORNER_POSITIONS,
  NODE_RADIUS,
  CORNER_RADIUS,
  PIECE_RADIUS,
  PLAYER_COLORS,
  PIECE_KEYS,
  RESERVE_POSITIONS,
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

  updatePieces(allPieces: Piece[], players?: Player[]): void {
    // Clear piece layer
    while (this.pieceLayer.firstChild) {
      this.pieceLayer.removeChild(this.pieceLayer.firstChild);
    }

    // Draw reserve (inactive) pieces for each player
    if (players) {
      this.drawReserves(players);
    }

    // Group active pieces by position and player
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

  private drawReserves(players: Player[]): void {
    const STACK_GAP = 8;
    const RESERVE_PIECE_RADIUS = 11;

    for (const player of players) {
      const inactive = player.getInactivePieces();
      if (inactive.length === 0) continue;

      const base = RESERVE_POSITIONS[player.playerId];
      if (!base) continue;

      for (let si = 0; si < inactive.length; si++) {
        const piece = inactive[si];
        const cx = base.x;
        const cy = base.y + si * STACK_GAP * base.stackDir;

        const g = document.createElementNS(SVG_NS, 'g');
        g.classList.add('piece-group', 'reserve-piece');
        g.style.transform = `translate(${cx}px, ${cy}px)`;
        g.dataset.playerId = String(player.playerId);
        g.dataset.pieceId = String(piece.pieceId);
        g.dataset.reserve = 'true';

        g.addEventListener('click', (e) => {
          e.stopPropagation();
          this.onNewPieceClickCb?.();
        });

        const circle = document.createElementNS(SVG_NS, 'circle');
        circle.setAttribute('cx', '0');
        circle.setAttribute('cy', '0');
        circle.setAttribute('r', String(RESERVE_PIECE_RADIUS));
        circle.classList.add('piece-circle');
        circle.style.fill = PLAYER_COLORS[player.playerId] ?? '#888';
        circle.style.opacity = '0.6';
        g.appendChild(circle);

        // Label on topmost piece only — show "N" (matches hotkey)
        if (si === inactive.length - 1) {
          const label = document.createElementNS(SVG_NS, 'text');
          label.setAttribute('x', '0');
          label.setAttribute('y', '0');
          label.classList.add('piece-label');
          label.style.opacity = '0.8';
          label.textContent = 'N';
          g.appendChild(label);
        }

        this.pieceLayer.appendChild(g);
      }
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

  selectPiece(playerId: number, pieceId: number): void {
    // Draw RTS-style [ ] brackets around the selected piece
    const groups = this.pieceLayer.querySelectorAll('.piece-group');
    for (const g of groups) {
      const gEl = g as SVGGElement;
      if (Number(gEl.dataset.playerId) === playerId && Number(gEl.dataset.pieceId) === pieceId) {
        const s = PIECE_RADIUS + 6; // half-size of bracket box
        const corner = 6; // length of bracket arms

        const path = document.createElementNS(SVG_NS, 'path');
        path.setAttribute('d', [
          // top-left bracket
          `M${-s},${-s + corner} L${-s},${-s} L${-s + corner},${-s}`,
          // top-right bracket
          `M${s - corner},${-s} L${s},${-s} L${s},${-s + corner}`,
          // bottom-right bracket
          `M${s},${s - corner} L${s},${s} L${s - corner},${s}`,
          // bottom-left bracket
          `M${-s + corner},${s} L${-s},${s} L${-s},${s - corner}`,
        ].join(' '));
        path.classList.add('selection-bracket');
        gEl.appendChild(path);
        break;
      }
    }
  }

  highlightDestinations(destKeys: Map<string, string>): void {
    // Move highlight layer above pieces so destination clicks take priority
    this.svg.appendChild(this.highlightLayer);

    for (const [pos, key] of destKeys) {
      if (pos === 'EXIT') {
        // Draw arced exit arrow from cell 00
        this.drawExitArrow(key);
        continue;
      }

      const coord = POSITION_COORDS[pos];
      if (!coord) continue;

      const g = document.createElementNS(SVG_NS, 'g');
      g.style.cursor = 'pointer';
      g.addEventListener('click', () => {
        this.onPositionClickCb?.(pos);
      });

      const circle = document.createElementNS(SVG_NS, 'circle');
      circle.setAttribute('cx', String(coord.x));
      circle.setAttribute('cy', String(coord.y));
      circle.setAttribute('r', String(CORNER_RADIUS));
      circle.classList.add('dest-highlight');
      circle.dataset.destPosition = pos;
      g.appendChild(circle);

      // Key label
      if (key) {
        const label = document.createElementNS(SVG_NS, 'text');
        label.setAttribute('x', String(coord.x + CORNER_RADIUS + 8));
        label.setAttribute('y', String(coord.y));
        label.classList.add('dest-key-label');
        label.textContent = key;
        g.appendChild(label);
      }

      this.highlightLayer.appendChild(g);
    }
  }

  private drawExitArrow(key: string): void {
    const origin = POSITION_COORDS['00'];
    const cx = origin.x;
    const cy = origin.y;

    const g = document.createElementNS(SVG_NS, 'g');
    g.classList.add('exit-indicator');
    g.style.cursor = 'pointer';
    g.addEventListener('click', () => {
      this.onPositionClickCb?.('EXIT');
    });

    // Rotating rays around position 00
    const raysGroup = document.createElementNS(SVG_NS, 'g');
    raysGroup.classList.add('exit-rays-group');
    raysGroup.style.transformOrigin = `${cx}px ${cy}px`;

    const numRays = 8;
    const innerR = CORNER_RADIUS + 6;
    const outerR = CORNER_RADIUS + 22;
    for (let i = 0; i < numRays; i++) {
      const angle = (i / numRays) * Math.PI * 2;
      const line = document.createElementNS(SVG_NS, 'line');
      line.setAttribute('x1', String(cx + Math.cos(angle) * innerR));
      line.setAttribute('y1', String(cy + Math.sin(angle) * innerR));
      line.setAttribute('x2', String(cx + Math.cos(angle) * outerR));
      line.setAttribute('y2', String(cy + Math.sin(angle) * outerR));
      line.classList.add('exit-ray');
      raysGroup.appendChild(line);
    }
    g.appendChild(raysGroup);

    // Label above
    const label = document.createElementNS(SVG_NS, 'text');
    label.setAttribute('x', String(cx));
    label.setAttribute('y', String(cy - CORNER_RADIUS - 26));
    label.classList.add('dest-key-label');
    label.style.textAnchor = 'middle';
    label.textContent = key ? `[${key}] EXIT` : 'EXIT';
    g.appendChild(label);

    this.highlightLayer.appendChild(g);
  }

  clearHighlights(): void {
    while (this.highlightLayer.firstChild) {
      this.highlightLayer.removeChild(this.highlightLayer.firstChild);
    }
    // Restore default layer order: highlight below pieces
    this.svg.insertBefore(this.highlightLayer, this.pieceLayer);

    // Remove highlight rings and selection brackets from piece groups
    for (const el of this.pieceLayer.querySelectorAll('.highlight-ring, .selection-bracket')) {
      el.remove();
    }
  }

  showCaptureEffect(): Promise<void> {
    const cx = 300;
    const cy = 300;

    const overlay = document.createElementNS(SVG_NS, 'g');
    overlay.classList.add('capture-effect');

    // Burst rays
    const numRays = 12;
    for (let i = 0; i < numRays; i++) {
      const angle = (i / numRays) * Math.PI * 2;
      const line = document.createElementNS(SVG_NS, 'line');
      line.setAttribute('x1', String(cx));
      line.setAttribute('y1', String(cy));
      line.setAttribute('x2', String(cx + Math.cos(angle) * 120));
      line.setAttribute('y2', String(cy + Math.sin(angle) * 120));
      line.classList.add('capture-ray');
      overlay.appendChild(line);
    }

    // Glow circle
    const glow = document.createElementNS(SVG_NS, 'circle');
    glow.setAttribute('cx', String(cx));
    glow.setAttribute('cy', String(cy));
    glow.setAttribute('r', '60');
    glow.classList.add('capture-glow');
    overlay.appendChild(glow);

    // Text
    const text = document.createElementNS(SVG_NS, 'text');
    text.setAttribute('x', String(cx));
    text.setAttribute('y', String(cy - 8));
    text.classList.add('capture-text');
    text.textContent = 'CAPTURE!';
    overlay.appendChild(text);

    const subtext = document.createElementNS(SVG_NS, 'text');
    subtext.setAttribute('x', String(cx));
    subtext.setAttribute('y', String(cy + 20));
    subtext.classList.add('capture-subtext');
    subtext.textContent = 'BONUS THROW';
    overlay.appendChild(subtext);

    this.svg.appendChild(overlay);

    return new Promise(resolve => {
      setTimeout(() => {
        overlay.remove();
        resolve();
      }, 1200);
    });
  }

  showGameOverEffect(rankings: { name: string; color: string }[]): void {
    const cx = 300;
    const cy = 300;

    const overlay = document.createElementNS(SVG_NS, 'g');
    overlay.classList.add('gameover-effect');

    // Dark backdrop
    const backdrop = document.createElementNS(SVG_NS, 'rect');
    backdrop.setAttribute('x', '0');
    backdrop.setAttribute('y', '0');
    backdrop.setAttribute('width', '600');
    backdrop.setAttribute('height', '600');
    backdrop.classList.add('gameover-backdrop');
    overlay.appendChild(backdrop);

    // Burst rays (gold)
    const numRays = 16;
    for (let i = 0; i < numRays; i++) {
      const angle = (i / numRays) * Math.PI * 2;
      const line = document.createElementNS(SVG_NS, 'line');
      line.setAttribute('x1', String(cx));
      line.setAttribute('y1', String(cy - 30));
      line.setAttribute('x2', String(cx + Math.cos(angle) * 200));
      line.setAttribute('y2', String(cy - 30 + Math.sin(angle) * 200));
      line.classList.add('gameover-ray');
      overlay.appendChild(line);
    }

    // Title
    const title = document.createElementNS(SVG_NS, 'text');
    title.setAttribute('x', String(cx));
    title.setAttribute('y', String(cy - 100));
    title.classList.add('gameover-title');
    title.textContent = 'GAME OVER';
    overlay.appendChild(title);

    // Rankings — last place gets no medal
    const allMedals = ['\u{1F947}', '\u{1F948}', '\u{1F949}'];
    for (let i = 0; i < rankings.length; i++) {
      const r = rankings[i];
      const isLast = i === rankings.length - 1;
      const medal = isLast ? '' : (allMedals[i] ?? '');
      const y = cy - 40 + i * 42;

      const row = document.createElementNS(SVG_NS, 'text');
      row.setAttribute('x', String(cx));
      row.setAttribute('y', String(y));
      row.classList.add('gameover-rank');
      row.style.fill = r.color;
      row.style.animationDelay = `${0.3 + i * 0.2}s`;
      row.textContent = `#${i + 1}  ${medal} ${r.name}`;
      overlay.appendChild(row);
    }

    this.svg.appendChild(overlay);
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
