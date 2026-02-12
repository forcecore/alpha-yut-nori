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

      const rect = document.createElementNS(SVG_NS, 'rect');
      rect.setAttribute('x', String(x));
      rect.setAttribute('y', String(y));
      rect.setAttribute('width', String(stickWidth));
      rect.setAttribute('height', String(stickHeight));
      rect.classList.add('yut-stick');
      rect.classList.add(result.sticks[i] ? 'flat' : 'round');

      // Stagger the animation
      rect.style.animationDelay = `${i * 0.1}s`;
      rect.classList.add('stick-tumbling');

      this.throwSvg.appendChild(rect);
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
