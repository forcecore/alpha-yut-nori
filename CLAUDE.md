# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Yut Nori (윷놀이) — a traditional Korean board game with two implementations:

1. **Python CLI** (`yoot/` + `cli_game.py`) — original engine with text-based interface
2. **TypeScript Web** (`yoot-web/`) — browser GUI with SVG board, click-to-play, and AI opponents

## Commands

### Python CLI

```bash
python3 cli_game.py                 # play the game
pytest                              # run tests (configured in pytest.ini)
pytest tests/test_board.py          # single file
pytest -k test_name                 # single test by name
```

No build step. No external dependencies for the game itself; only `pytest` for testing.

### TypeScript Web (`yoot-web/`)

```bash
cd yoot-web
pnpm install                        # install dependencies (uses pnpm, not npm)
pnpm dev                            # dev server with hot reload (http://localhost:5173)
pnpm build                          # type-check + production build → dist/
pnpm preview                        # preview production build locally
```

Add `?fast` to the URL (e.g. `http://localhost:5173/?fast`) to skip animations for quick debugging. There is also a "Fast mode" checkbox on the setup screen.

## Architecture

### Web app (`yoot-web/`)

Vanilla TypeScript + Vite, no framework. All client-side, served from GitHub Pages (`base: '/yoot/'`).

- **`src/engine/`** — 1:1 port of the Python engine (board, piece, player, yutThrow, game). Same position system, same move tables. `game.clone()` for MC simulations (shares Board, clones players).
- **`src/controller/`** — `PlayerController` interface (async). `HumanController` (Promise resolved by UI clicks), `RandomController` ("AI Easy"), `MonteCarloController` ("AlphaYutNori", 100 rollouts).
- **`src/ui/gameUI.ts`** — Event-driven state machine: setup → throwing → selecting_piece → selecting_move → animating → game_over. Manages all DOM updates, keyboard shortcuts (QWER for pieces, N for new piece, Space to throw, 0 to skip).
- **`src/ui/boardRenderer.ts`** — SVG 600x600 board. Three layers: static (lines/nodes), highlight (destination glow, exit indicator), piece (active + reserve). Layer order swaps during destination selection for click priority.
- **`src/ui/throwAnimation.ts`** — Yut stick throw animation with tumble effect. Flat sticks are light, round sticks are dark with X marks.
- **`src/ui/constants.ts`** — Position coordinates, board edges, player colors, PIECE_KEYS (`['Q','W','E','R']`), reserve positions with stack direction.
- **`src/style.css`** — Dark theme, responsive layout, SVG animations (capture burst, game over rays, exit indicator spin).

### Core engine (`yoot/` package — Python)

- **board.py** — Stateless board with 29 positions. All movement is a dictionary lookup (`MOVE_TABLE[pos][steps]`). Backward moves use `BACK_TABLE`. Loads `cells.txt` at project root for ASCII rendering.
- **piece.py** — Single piece (말). Tracks `position` (str or None), `is_active`, `has_moved`. The `has_moved` flag distinguishes "at start" from "returned to 00 to finish".
- **player.py** — Owns 4 Piece objects. Provides active/finished/inactive queries and stack grouping.
- **yut_throw.py** — Simulates throwing 4 biased sticks (60% flat). Special case: stick index 0 being the only flat → back_do (-1 step).
- **game.py** — `YutGame` orchestrates turns. Key flow: `throw_phase()` → `get_legal_moves()` → `move_piece()` → `check_win_condition()` → `next_turn()`. Captures grant bonus throws. Stacked pieces at the same position move together.
- **controller.py** — `PlayerController` ABC with `choose_move(game_state, legal_moves) -> (piece_id, steps) | None`. Implementations: `HumanController` (interactive CLI), `RandomController`, `MonteCarloController` (rollout simulations via deepcopy).

### CLI (`cli_game.py`)

Top-level script. Asks for player count/names, assigns controller type per player (human/random/MC), then runs the game loop calling `play_turn()` per player.

## Board Position System

Positions are **2-char strings**: outer path `'00'`-`'19'`, diagonals `'aa'`, `'bb'`, `'cc'`, `'pp'`, `'qq'`, `'xx'`, `'yy'`, `'uu'`, `'vv'`.

- `'00'` is both START and GOAL. Pieces at `'00'` with `has_moved=True` exit on their next move (any step value).
- Landing on `'05'` or `'10'` **automatically** triggers diagonal shortcuts on the next move (not player choice).
- From `'05'`: aa→bb→cc→uu→vv→15 (exits to outer path).
- From `'10'`: xx→yy→cc→pp→qq→00 (straight to goal).
- From `'cc'`: always pp→qq→00 (toward goal).
- Entry position varies by throw: Do→`'01'`, Gae→`'02'`, Geol→`'03'`, Yut→`'04'`, Mo→`'05'`.
- `piece_id = -1` in legal moves means "enter a new piece".

## Key Design Decisions

- Board movement is fully stateless — `MOVE_TABLE` encodes all shortcut routing, no runtime path tracking needed.
- `MonteCarloController._clone_game()` shares the `Board` object (immutable lookup tables) to avoid file I/O on deepcopy.
- Game supports rankings (not just first-place winner) — play continues until one player remains.
