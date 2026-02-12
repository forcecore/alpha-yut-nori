import { YutGame } from '../engine/game';
import { YutThrow } from '../engine/yutThrow';
import { BoardRenderer } from './boardRenderer';
import { ThrowAnimation } from './throwAnimation';
import { HumanController } from '../controller/humanController';
import { RandomController } from '../controller/randomController';
import { MonteCarloController } from '../controller/mcController';
import type { PlayerController, ControllerType } from '../controller/controller';
import type { LegalMove, ThrowResult } from '../engine/types';
import { PLAYER_COLORS, PIECE_KEYS } from './constants';

type Phase = 'setup' | 'throwing' | 'selecting_piece' | 'selecting_move' | 'animating' | 'game_over';

interface PlayerConfig {
  name: string;
  type: ControllerType;
}

export class GameUI {
  private game!: YutGame;
  private renderer!: BoardRenderer;
  private throwAnim!: ThrowAnimation;
  private controllers: PlayerController[] = [];
  private controllerTypes: ControllerType[] = [];
  private phase: Phase = 'setup';
  private fast: boolean;

  // Selection state
  private selectedPieceId: number | null = null;
  private currentLegalMoves: LegalMove[] = [];
  private currentThrows: ThrowResult[] = [];

  constructor(fast = false) {
    this.fast = fast;
  }

  // DOM elements
  private setupOverlay!: HTMLElement;
  private gameContainer!: HTMLElement;
  private helpOverlay!: HTMLElement;
  private playerStatus!: HTMLElement;
  private movesList!: HTMLElement;
  private historyLog!: HTMLElement;
  private actionButtons!: HTMLElement;
  private statusMessage!: HTMLElement;

  init(): void {
    this.setupOverlay = document.getElementById('setup-overlay')!;
    this.gameContainer = document.getElementById('game-container')!;
    this.helpOverlay = document.getElementById('help-overlay')!;
    this.playerStatus = document.getElementById('player-status')!;
    this.movesList = document.getElementById('moves-list')!;
    this.historyLog = document.getElementById('history-log')!;
    this.actionButtons = document.getElementById('action-buttons')!;
    this.statusMessage = document.getElementById('status-message')!;

    this.setupPlayerConfigUI();
    this.setupEventListeners();
  }

  private setupPlayerConfigUI(): void {
    const countSelect = document.getElementById('player-count') as HTMLSelectElement;
    const configsDiv = document.getElementById('player-configs')!;
    const defaultNames = ['Alice', 'Bob', 'Charlie', 'Diana'];

    const renderConfigs = () => {
      const count = Number(countSelect.value);
      configsDiv.innerHTML = '';
      for (let i = 0; i < count; i++) {
        const div = document.createElement('div');
        div.className = 'player-config';
        div.style.borderColor = PLAYER_COLORS[i];
        div.innerHTML = `
          <input type="text" value="${defaultNames[i]}" data-player="${i}" class="player-name-input" placeholder="Player ${i + 1}" />
          <select data-player="${i}" class="player-type-select">
            <option value="human"${i === 0 ? ' selected' : ''}>Human</option>
            <option value="random"${i >= 1 && i < 2 ? ' selected' : ''}>Random AI</option>
            <option value="mc"${i >= 2 ? ' selected' : ''}>MC AI</option>
          </select>
        `;
        // Default: first player human, rest random
        const select = div.querySelector('select')!;
        if (i === 0) select.value = 'human';
        else select.value = 'random';
        configsDiv.appendChild(div);
      }
    };

    countSelect.addEventListener('change', renderConfigs);
    renderConfigs();

    document.getElementById('start-btn')!.addEventListener('click', () => {
      const count = Number(countSelect.value);
      const configs: PlayerConfig[] = [];
      for (let i = 0; i < count; i++) {
        const nameInput = configsDiv.querySelector(`input[data-player="${i}"]`) as HTMLInputElement;
        const typeSelect = configsDiv.querySelector(`select[data-player="${i}"]`) as HTMLSelectElement;
        configs.push({
          name: nameInput.value || `Player ${i}`,
          type: typeSelect.value as ControllerType,
        });
      }
      this.startGame(configs);
    });
  }

  private setupEventListeners(): void {
    // Help toggle
    document.getElementById('help-btn')!.addEventListener('click', () => this.toggleHelp());
    document.getElementById('help-close-btn')!.addEventListener('click', () => this.toggleHelp());
    document.getElementById('settings-btn')!.addEventListener('click', () => this.returnToSetup());

    // Keyboard
    document.addEventListener('keydown', (e) => this.handleKeydown(e));
  }

  private handleKeydown(e: KeyboardEvent): void {
    // Help
    if (e.key === '?') {
      e.preventDefault();
      this.toggleHelp();
      return;
    }

    if (this.phase === 'throwing') {
      if (e.key === ' ' || e.key === 'Enter') {
        e.preventDefault();
        this.performThrow();
      }
    } else if (this.phase === 'selecting_piece') {
      const pieceKeyMap: Record<string, number> = { q: 0, w: 1, e: 2, r: 3 };
      const pieceIdx = pieceKeyMap[e.key.toLowerCase()];
      if (pieceIdx !== undefined) {
        e.preventDefault();
        this.trySelectPieceByIndex(pieceIdx);
      } else if (e.key === 'n' || e.key === 'N') {
        e.preventDefault();
        this.tryEnterNewPiece();
      } else if (e.key === '0') {
        e.preventDefault();
        this.skipRemainingMoves();
      }
    } else if (this.phase === 'selecting_move') {
      if (e.key === 'Escape') {
        e.preventDefault();
        this.backToPieceSelection();
      }
      // QWER to select move values
      const moveKeyMap: Record<string, number> = { q: 0, w: 1, e: 2, r: 3 };
      const moveIdx = moveKeyMap[e.key.toLowerCase()];
      if (moveIdx !== undefined) {
        const moveButtons = this.actionButtons.querySelectorAll('.btn-move') as NodeListOf<HTMLButtonElement>;
        if (moveIdx < moveButtons.length) {
          e.preventDefault();
          moveButtons[moveIdx].click();
        }
      }
    }
  }

  private toggleHelp(): void {
    this.helpOverlay.classList.toggle('hidden');
  }

  private returnToSetup(): void {
    this.gameContainer.classList.add('hidden');
    this.setupOverlay.classList.remove('hidden');
    this.phase = 'setup';
  }

  private startGame(configs: PlayerConfig[]): void {
    const names = configs.map(c => c.name);
    this.game = new YutGame(names, configs.length);

    // Create controllers
    this.controllers = [];
    this.controllerTypes = [];
    for (let i = 0; i < configs.length; i++) {
      this.controllerTypes.push(configs[i].type);
      switch (configs[i].type) {
        case 'human':
          this.controllers.push(new HumanController());
          break;
        case 'random':
          this.controllers.push(new RandomController());
          break;
        case 'mc':
          this.controllers.push(new MonteCarloController(this.game, i, 100));
          break;
      }
    }

    // Show game, hide setup
    this.setupOverlay.classList.add('hidden');
    this.gameContainer.classList.remove('hidden');

    // Initialize renderer
    const svg = document.getElementById('board-svg') as unknown as SVGSVGElement;
    svg.innerHTML = '';
    this.renderer = new BoardRenderer(svg);
    this.throwAnim = new ThrowAnimation();

    // Set up piece click handler
    this.renderer.onPieceClick((playerId, pieceId) => {
      if (this.phase === 'selecting_piece' && playerId === this.game.currentPlayerIdx) {
        this.selectPiece(pieceId);
      }
    });

    this.renderer.onNewPieceClick(() => {
      if (this.phase === 'selecting_piece') {
        this.tryEnterNewPiece();
      }
    });

    this.renderer.onPositionClick((position) => {
      if (this.phase === 'selecting_move' && this.selectedPieceId !== null) {
        // Find moves that land on this destination
        const matchingMoves = this.getMovesForPiece(this.selectedPieceId)
          .filter(m => m.destination === position);
        if (matchingMoves.length > 0) {
          this.executeMove(matchingMoves[0].pieceId, matchingMoves[0].steps);
        }
      }
    });

    this.updateDisplay();
    this.startTurn();
  }

  private async startTurn(): Promise<void> {
    if (this.game.gameState === 'finished') {
      this.showGameOver();
      return;
    }

    const player = this.game.getCurrentPlayer();
    const isHuman = this.controllerTypes[this.game.currentPlayerIdx] === 'human';

    this.phase = 'throwing';
    this.updateDisplay();

    if (isHuman) {
      this.setStatus(`${player.name}'s turn — click Throw or press Space`);
      this.showThrowButton();
    } else {
      this.setStatus(`${player.name} (AI) is throwing...`);
      this.clearActions();
      await this.delay(300);
      // AI uses performThrow too so animation plays
      this.phase = 'throwing';
      await this.performThrow();
    }
  }

  private showThrowButton(): void {
    this.actionButtons.innerHTML = '';
    const btn = document.createElement('button');
    btn.className = 'btn btn-primary';
    btn.textContent = 'Throw (Space)';
    btn.addEventListener('click', () => this.performThrow());
    this.actionButtons.appendChild(btn);
  }

  private async performThrow(): Promise<void> {
    if (this.phase !== 'throwing') return;
    this.phase = 'animating';
    this.clearActions();

    const throws = this.game.throwPhase();
    this.currentThrows = throws;

    // Animate each throw
    if (!this.fast) {
      for (const t of throws) {
        await this.throwAnim.animate(t);
      }
      this.throwAnim.hide();
    }

    this.updateDisplay();
    await this.startMovePhase();
  }

  private async startMovePhase(): Promise<void> {
    while (this.game.accumulatedMoves.length > 0) {
      const playerId = this.game.currentPlayerIdx;
      const legalMoves = this.game.getLegalMoves(playerId);
      this.currentLegalMoves = legalMoves;

      if (legalMoves.length === 0) {
        this.game.accumulatedMoves = [];
        break;
      }

      const isHuman = this.controllerTypes[playerId] === 'human';

      if (isHuman) {
        this.phase = 'selecting_piece';
        this.showPieceSelection(legalMoves);
        this.updateDisplay();

        const controller = this.controllers[playerId] as HumanController;
        const move = await controller.chooseMove(this.game.getGameState(), legalMoves);

        if (move === null) {
          // Skip
          this.game.accumulatedMoves = [];
          break;
        }

        const { captured } = this.game.movePiece(playerId, move.pieceId, move.steps);
        this.renderer.clearHighlights();
        this.updateDisplay();
        await this.delay(300);

        if (captured) {
          this.addHistory('Capture! Bonus throw!', true);
          if (!this.fast) await this.renderer.showCaptureEffect();
          this.phase = 'throwing';
          this.updateDisplay();

          this.setStatus(`${this.game.getCurrentPlayer().name} captured — bonus throw!`);
          if (isHuman) {
            this.showThrowButton();
            // Wait for the human to throw
            await new Promise<void>(resolve => {
              const origPerformThrow = this.performThrow.bind(this);
              this.performThrow = async () => {
                this.performThrow = origPerformThrow;
                if (this.phase !== 'throwing') return;
                this.phase = 'animating';
                this.clearActions();

                const bonusThrows = this.game.throwPhase(true);
                if (!this.fast) {
                  for (const t of bonusThrows) {
                    await this.throwAnim.animate(t);
                  }
                  this.throwAnim.hide();
                }
                this.updateDisplay();
                resolve();
              };
            });
          } else {
            this.game.throwPhase(true);
            this.updateDisplay();
          }
        }

        if (this.game.checkWinCondition()) {
          this.updateDisplay();
          if (this.game.gameState === 'finished') {
            this.showGameOver();
            return;
          }
        }
      } else {
        // AI turn
        this.phase = 'animating';
        this.setStatus(`${this.game.getCurrentPlayer().name} (AI) is thinking...`);
        this.clearActions();

        const controller = this.controllers[playerId];
        const move = await controller.chooseMove(this.game.getGameState(), legalMoves);

        if (move === null) {
          this.game.accumulatedMoves = [];
          break;
        }

        await this.delay(300);
        const { captured } = this.game.movePiece(playerId, move.pieceId, move.steps);
        this.updateDisplay();
        await this.delay(400);

        if (captured) {
          this.addHistory('Capture! Bonus throw!', true);
          if (!this.fast) await this.renderer.showCaptureEffect();
          const bonusThrows = this.game.throwPhase(true);
          if (!this.fast) {
            for (const t of bonusThrows) {
              await this.throwAnim.animate(t);
            }
            this.throwAnim.hide();
          }
          this.updateDisplay();
        }

        if (this.game.checkWinCondition()) {
          this.updateDisplay();
          if (this.game.gameState === 'finished') {
            this.showGameOver();
            return;
          }
        }
      }
    }

    // Turn done
    if (this.game.gameState === 'finished') {
      this.showGameOver();
      return;
    }

    this.game.nextTurn();
    this.updateDisplay();
    await this.delay(300);
    this.startTurn();
  }

  private showPieceSelection(legalMoves: LegalMove[]): void {
    const player = this.game.getCurrentPlayer();

    // Get unique piece IDs that have moves
    const pieceIds = new Set(legalMoves.map(m => m.pieceId));
    const hasNewPiece = pieceIds.has(-1);
    const activePieceIds = new Set([...pieceIds].filter(id => id !== -1));

    // Highlight pieces on board
    this.renderer.highlightPieces(player.playerId, activePieceIds, hasNewPiece);

    // Show action buttons
    this.actionButtons.innerHTML = '';

    if (hasNewPiece) {
      const btn = document.createElement('button');
      btn.className = 'btn';
      btn.textContent = 'New Piece (N)';
      btn.addEventListener('click', () => this.tryEnterNewPiece());
      this.actionButtons.appendChild(btn);
    }

    const skipBtn = document.createElement('button');
    skipBtn.className = 'btn';
    skipBtn.textContent = 'Skip (0)';
    skipBtn.addEventListener('click', () => this.skipRemainingMoves());
    this.actionButtons.appendChild(skipBtn);

    this.setStatus(
      `${player.name}'s turn — select a piece (moves: ${this.game.accumulatedMoves.join(', ')})`
    );
  }

  private selectPiece(pieceId: number): void {
    this.selectedPieceId = pieceId;
    this.phase = 'selecting_move';

    const moves = this.getMovesForPiece(pieceId);
    this.showMoveSelection(pieceId, moves);
  }

  private getMovesForPiece(pieceId: number): LegalMove[] {
    return this.currentLegalMoves.filter(m => m.pieceId === pieceId);
  }

  private showMoveSelection(pieceId: number, moves: LegalMove[]): void {
    const player = this.game.getCurrentPlayer();
    const piece = pieceId === -1 ? null : player.getPieceById(pieceId);

    // Show selection bracket on chosen piece and highlight destinations
    this.renderer.clearHighlights();
    if (pieceId !== -1) {
      this.renderer.selectPiece(player.playerId, pieceId);
    }
    const dests = new Set(moves.map(m => m.destination));
    this.renderer.highlightDestinations(dests);

    // Show move buttons
    this.actionButtons.innerHTML = '';

    for (let mi = 0; mi < moves.length; mi++) {
      const move = moves[mi];
      let destStr: string;
      if (pieceId !== -1 && piece?.position === '00' && piece.hasMoved) {
        destStr = 'EXIT';
      } else if (move.destination === '00') {
        destStr = 'GOAL';
      } else {
        destStr = move.destination;
        if (this.game.board.triggersShortcut(move.destination)) {
          destStr += ' (shortcut)';
        }
      }

      const keyHint = PIECE_KEYS[mi] ?? '';
      const btn = document.createElement('button');
      btn.className = 'btn btn-move';
      btn.textContent = `[${keyHint}] ${move.steps} → ${destStr}`;
      btn.addEventListener('click', () => this.executeMove(move.pieceId, move.steps));
      this.actionButtons.appendChild(btn);
    }

    const backBtn = document.createElement('button');
    backBtn.className = 'btn';
    backBtn.textContent = 'Back (Esc)';
    backBtn.addEventListener('click', () => this.backToPieceSelection());
    this.actionButtons.appendChild(backBtn);

    const label = pieceId === -1 ? 'new piece' : `Piece ${PIECE_KEYS[pieceId] ?? pieceId}`;
    this.setStatus(`${player.name} — choose move for ${label}`);
  }

  private executeMove(pieceId: number, steps: number): void {
    if (this.phase !== 'selecting_move') return;
    this.phase = 'animating';
    this.renderer.clearHighlights();
    this.clearActions();

    const controller = this.controllers[this.game.currentPlayerIdx];
    if (controller instanceof HumanController) {
      controller.submitMove(pieceId, steps);
    }
  }

  private trySelectPieceByIndex(index: number): void {
    const player = this.game.getCurrentPlayer();
    const active = player.getActivePieces();
    if (index < active.length) {
      this.selectPiece(active[index].pieceId);
    }
  }

  private tryEnterNewPiece(): void {
    if (this.phase !== 'selecting_piece') return;
    const moves = this.currentLegalMoves.filter(m => m.pieceId === -1);
    if (moves.length > 0) {
      this.selectedPieceId = -1;
      this.phase = 'selecting_move';
      this.showMoveSelection(-1, moves);
    }
  }

  private skipRemainingMoves(): void {
    if (this.phase !== 'selecting_piece') return;
    this.phase = 'animating';
    this.renderer.clearHighlights();
    this.clearActions();

    const controller = this.controllers[this.game.currentPlayerIdx];
    if (controller instanceof HumanController) {
      controller.submitSkip();
    }
  }

  private backToPieceSelection(): void {
    if (this.phase !== 'selecting_move') return;
    this.selectedPieceId = null;
    this.phase = 'selecting_piece';
    this.renderer.clearHighlights();
    this.showPieceSelection(this.currentLegalMoves);
    this.updateDisplay();
  }

  private showGameOver(): void {
    this.phase = 'game_over';
    this.renderer.clearHighlights();

    const rankings = this.game.rankings.map(pid => ({
      name: this.game.players[pid].name,
      color: PLAYER_COLORS[pid],
    }));
    this.renderer.showGameOverEffect(rankings);

    this.actionButtons.innerHTML = '';
    const btn = document.createElement('button');
    btn.className = 'btn btn-primary';
    btn.textContent = 'New Game';
    btn.addEventListener('click', () => this.returnToSetup());
    this.actionButtons.appendChild(btn);

    this.setStatus('');
  }

  private updateDisplay(): void {
    this.updatePlayerStatus();
    this.updateMovesDisplay();
    this.updateHistory();
    this.renderer.updatePieces(this.game.getAllPieces(), this.game.players);
  }

  private updatePlayerStatus(): void {
    const medals = ['\u{1F947}', '\u{1F948}', '\u{1F949}'];
    const rankings = this.game.rankings;
    const numPlayers = this.game.players.length;

    // Sort: still playing first (by playerId), then finished (by rank order)
    const sorted = [...this.game.players].sort((a, b) => {
      const aRank = rankings.indexOf(a.playerId);
      const bRank = rankings.indexOf(b.playerId);
      const aFinished = aRank !== -1;
      const bFinished = bRank !== -1;
      if (aFinished !== bFinished) return aFinished ? 1 : -1;
      if (aFinished) return aRank - bRank;
      return a.playerId - b.playerId;
    });

    let html = '<h3>Players</h3>';
    for (const player of sorted) {
      const isCurrent = player.playerId === this.game.currentPlayerIdx;
      const color = PLAYER_COLORS[player.playerId];
      const finished = player.getFinishedPieces().length;
      const rankIdx = rankings.indexOf(player.playerId);
      const isFinished = rankIdx !== -1;
      const isLast = rankIdx === numPlayers - 1;
      const medal = (isFinished && !isLast) ? (medals[rankIdx] ?? '') : '';
      const typeLabel = this.controllerTypes[player.playerId] === 'human' ? '' :
        ` (${this.controllerTypes[player.playerId].toUpperCase()})`;

      html += `
        <div class="player-status-item ${isCurrent ? 'current' : ''}" style="${isFinished ? 'opacity:0.5' : ''}">
          <span class="player-dot" style="background:${color}"></span>
          <span class="player-name">${medal}${medal ? ' ' : ''}${player.name}${typeLabel}</span>
          <span class="player-score">${finished}/4</span>
        </div>
      `;
    }
    this.playerStatus.innerHTML = html;
  }

  private updateMovesDisplay(): void {
    const moves = this.game.accumulatedMoves;
    if (moves.length === 0) {
      this.movesList.textContent = 'No moves';
      return;
    }
    this.movesList.innerHTML = moves
      .map(m => `<span class="btn btn-small btn-move">${m > 0 ? '+' : ''}${m}</span>`)
      .join(' ');
  }

  private updateHistory(): void {
    const history = this.game.moveHistory.slice(-15);
    this.historyLog.innerHTML = history
      .map(entry => {
        const isCapture = entry.includes('captured');
        return `<div class="history-entry${isCapture ? ' capture' : ''}">${entry}</div>`;
      })
      .join('');
    this.historyLog.scrollTop = this.historyLog.scrollHeight;
  }

  private addHistory(text: string, isCapture = false): void {
    const div = document.createElement('div');
    div.className = `history-entry${isCapture ? ' capture' : ''}`;
    div.textContent = text;
    this.historyLog.appendChild(div);
    this.historyLog.scrollTop = this.historyLog.scrollHeight;
  }

  private setStatus(text: string): void {
    this.statusMessage.textContent = text;
  }

  private clearActions(): void {
    this.actionButtons.innerHTML = '';
  }

  private delay(ms: number): Promise<void> {
    if (this.fast) ms = Math.min(ms, 50);
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
