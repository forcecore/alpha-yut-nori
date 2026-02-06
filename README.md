# Yut Nori (윷놀이) Game Engine

A Python implementation of the traditional Korean board game Yut Nori, playable via command line interface with eventual support for reinforcement learning agents.

## Game Overview

Yut Nori is a traditional Korean board game played with 4 wooden sticks and pieces on a cross-shaped board. Players race to move all their pieces around the board and reach the goal first.

### Key Rules

- **2-6 Players**: Each player has 4 pieces (말). Game supports 2 to 6 players.
- **Yut Sticks**: Throw 4 sticks to determine movement (sticks are biased - 60% chance of landing flat side up)
  - **Do (도)**: 1 flat stick → move 1 space (~11.5% probability)
  - **Back Do (빽도)**: 1 flat (if the "back Do" stick) → move 1 space BACKWARDS (~3.8% probability)
  - **Gae (개)**: 2 flat → move 2 spaces (~34.6% probability - most common!)
  - **Geol (걸)**: 3 flat → move 3 spaces (~34.6% probability - most common!)
  - **Yut (윷)**: 4 flat → move 4 spaces + throw again (~13% probability)
  - **Mo (모)**: 0 flat → move 5 spaces + throw again (~2.6% probability - very rare!)

- **Board**: Cross-shaped with 21 positions (counter-clockwise from bottom-right)
  - Outer circular path: 1→2→...→20
  - Two diagonal shortcuts through center:
    - At position 5: Choose outer (→6) OR shortcut (→10 center)
    - At position 10: Choose outer (→11) OR shortcut (→20 goal)
  - Must land exactly on goal

- **Special Mechanics**:
  - **Bonus throws**: Yut and Mo grant additional throws
  - **Move accumulation**: All throws in a turn accumulate (e.g., Mo→Yut→Gae = [5,4,2])
  - **Stacking**: Own pieces can stack and move together
  - **Captures**: Landing on opponent captures them (returns to start)
  - **Win condition**: First to get all 4 pieces to goal

## Installation

```bash
# Clone or download this repository
cd yoot

# No dependencies needed for base game - uses Python standard library only
python3 cli_game.py

# For development and testing
uv pip install pytest
pytest tests/  # Run test suite
```

## Usage

### Playing the Game

```bash
# Run the CLI game
python3 cli_game.py
```

### Game Flow

1. Enter player names (or use defaults)
2. Each turn:
   - Press Enter to throw yut sticks
   - Throws continue automatically on Yut/Mo
   - Use accumulated moves one at a time
   - Choose which piece to move or enter new piece
   - Captures happen automatically
3. First player to finish all 4 pieces wins

### Controls

- **Enter**: Throw yut sticks / Continue
- **Number keys**: Select piece or action
- **0**: Skip remaining moves
- **q**: Quit game during throw phase

## Project Structure

```
yoot/
├── yoot/                # Core game engine package
│   ├── __init__.py      # Package exports
│   ├── board.py         # Board representation and paths
│   ├── piece.py         # Game piece class
│   ├── player.py        # Player state management
│   ├── yut_throw.py     # Yut stick throwing logic
│   └── game.py          # Main game engine
├── cli_game.py          # CLI interface for human play
├── requirements.txt     # Dependencies (minimal)
└── README.md            # This file
```

## Game Engine API

### Basic Usage

```python
from yoot import YutGame

# Initialize game with 4 players (default)
game = YutGame(["Alice", "Bob", "Carol", "Dave"])

# Or with a different number of players
game = YutGame(["Alice", "Bob", "Carol"], num_players=3)

# Game loop
while game.game_state == "playing":
    # Throw phase - accumulates all throws
    throws = game.throw_phase()

    # Get legal moves for current player
    player = game.get_current_player()
    legal_moves = game.get_legal_moves(player.player_id)

    # Make moves
    for piece_id, steps, dest in legal_moves:
        game.move_piece(player.player_id, piece_id, steps)

        if game.check_win_condition():
            break

    # Next player
    game.next_turn()

print(f"Winner: {game.players[game.winner].name}")
```

### Key Classes

#### `YutGame`
Main game engine managing game state.

**Methods**:
- `throw_phase()`: Execute throwing phase, returns list of throws
- `get_legal_moves(player_id)`: Get valid moves for player
- `move_piece(player_id, piece_id, steps)`: Execute move
- `check_win_condition()`: Check if game is over
- `get_game_state()`: Get complete game state dict

#### `Board`
Board representation and path logic.

**Methods**:
- `get_next_position(current_pos, steps)`: Calculate destination
- `get_valid_moves(position, steps)`: Get valid destinations
- `render_board(pieces)`: ASCII art representation

#### `Player`
Player state management.

**Methods**:
- `get_active_pieces()`: Pieces on board
- `get_finished_pieces()`: Pieces at goal
- `get_stacks()`: Grouped pieces by position
- `has_finished()`: Check if won

## Board Layout

```
Position numbering:

    5 --- 10 --- 15        (Top row)
    |      |      |
    |      |      |
    1      |     20        (Sides)
    |      |      |
    |      |      |
  Start   28    Goal       (Bottom)
```

Paths:
- **Outer path**: 1 → 2 → 3 → 4 → 5 → 6 → ... → 10 → 11 → ... → 20 (goal)
- **Shortcut at position 5**: 5 → 10 → 15 → 16 → ... → 20
  - At position 5, player chooses: outer (→6) OR shortcut diagonal (→10)
- **Shortcut at position 10**: 10 → 20 (direct to goal)
  - At position 10, player chooses: outer (→11) OR shortcut diagonal (→20)
- **Position 15**: No choice, continues on outer path only

## Future Enhancements

- [ ] RL environment wrapper (OpenAI Gym interface)
- [ ] GUI version (pygame/tkinter)
- [ ] Network multiplayer
- [ ] Game replay/save system
- [ ] AI opponents with different strategies
- [ ] Tournament mode

## Development

### Running Tests

```bash
# Install pytest
uv pip install pytest

# Run full test suite (59 tests)
pytest tests/ -v

# Run specific test file
pytest tests/test_board.py

# Run with coverage
pytest tests/ --cov=yoot --cov-report=html
```

**Test Coverage**: 65 tests covering:
- Board layout and counter-clockwise movement
- Shortcut path selection at positions 5 and 10
- Yut throw mechanics and probabilities
- Piece and player management
- Game mechanics (entry, movement, capture, stacking)
- Win conditions and state tracking

See [tests/README.md](tests/README.md) for detailed test documentation.

### Manual Testing

```bash
# Play the game
python3 cli_game.py

# Test edge cases:
# - Piece stacking
# - Captures
# - Yut/Mo consecutive throws
# - Path selection at intersections
# - Exact landing on goal
```

### Code Style

- Python 3.8+ with type hints
- No external dependencies for core game
- Let programs crash instead of try-catch
- Use early returns

## License

MIT License

## Credits

Yut Nori is a traditional Korean board game with centuries of history.
This implementation is for educational and entertainment purposes.
