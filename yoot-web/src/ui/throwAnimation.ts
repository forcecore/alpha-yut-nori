import type { ThrowResult } from '../engine/types';
import { YutThrow } from '../engine/yutThrow';

const SVG_NS = 'http://www.w3.org/2000/svg';

export class ThrowAnimation {
  private throwArea: HTMLElement;
  private throwSvg: SVGSVGElement;
  private throwResult: HTMLElement;

  constructor() {
    this.throwArea = document.getElementById('throw-area')!;
    this.throwSvg = document.getElementById('throw-svg') as unknown as SVGSVGElement;
    this.throwResult = document.getElementById('throw-result')!;
  }

  async animate(result: ThrowResult): Promise<void> {
    this.throwArea.classList.remove('hidden');
    this.throwResult.textContent = '';

    // Clear previous sticks
    while (this.throwSvg.firstChild) {
      this.throwSvg.removeChild(this.throwSvg.firstChild);
    }

    // Draw 4 sticks with staggered animation
    const stickWidth = 20;
    const stickHeight = 70;
    const gap = 50;
    const startX = (300 - (4 * stickWidth + 3 * gap)) / 2;

    for (let i = 0; i < 4; i++) {
      const x = startX + i * (stickWidth + gap);
      const y = 25;
      const isFlat = result.sticks[i];

      const g = document.createElementNS(SVG_NS, 'g');
      g.style.animationDelay = `${i * 0.1}s`;
      g.classList.add('stick-tumbling');

      // Stick body
      const rect = document.createElementNS(SVG_NS, 'rect');
      rect.setAttribute('x', String(x));
      rect.setAttribute('y', String(y));
      rect.setAttribute('width', String(stickWidth));
      rect.setAttribute('height', String(stickHeight));
      rect.classList.add('yut-stick');
      rect.classList.add(isFlat ? 'flat' : 'round');
      g.appendChild(rect);

      // Round side: draw 3 X marks
      if (!isFlat) {
        const cx = x + stickWidth / 2;
        const xSize = 4;
        const positions = [y + 17, y + 35, y + 53]; // top, mid, bottom
        for (const py of positions) {
          const cross = document.createElementNS(SVG_NS, 'g');
          cross.classList.add('stick-x-mark');
          const l1 = document.createElementNS(SVG_NS, 'line');
          l1.setAttribute('x1', String(cx - xSize));
          l1.setAttribute('y1', String(py - xSize));
          l1.setAttribute('x2', String(cx + xSize));
          l1.setAttribute('y2', String(py + xSize));
          const l2 = document.createElementNS(SVG_NS, 'line');
          l2.setAttribute('x1', String(cx + xSize));
          l2.setAttribute('y1', String(py - xSize));
          l2.setAttribute('x2', String(cx - xSize));
          l2.setAttribute('y2', String(py + xSize));
          cross.appendChild(l1);
          cross.appendChild(l2);
          g.appendChild(cross);
        }
      }

      this.throwSvg.appendChild(g);
    }

    // Wait for animation to complete
    await new Promise(resolve => setTimeout(resolve, 600));

    // Show result text
    const korean = YutThrow.KOREAN_NAMES[result.name];
    const color = result.value >= 4 ? '#ffeb3b' : result.value === -1 ? '#e74c3c' : '#fff';
    this.throwResult.innerHTML = `<span style="color:${color}">${result.name} ${korean} (${result.value > 0 ? '+' : ''}${result.value})</span>`;

    // Keep visible briefly
    await new Promise(resolve => setTimeout(resolve, 800));
  }

  hide(): void {
    this.throwArea.classList.add('hidden');
  }
}
