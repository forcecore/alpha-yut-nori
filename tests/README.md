# Yut Nori Test Suite

Comprehensive pytest test suite for the Yut Nori game engine.

## Running Tests

```bash
# Install pytest
uv pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_board.py

# Run specific test class
pytest tests/test_board.py::TestBoardLayout

# Run specific test
pytest tests/test_board.py::TestBoardLayout::test_board_constants
```

## Test Coverage

### test_board.py (18 tests)
Tests for board layout and movement logic:
- **TestBoardLayout**: Board constants, coordinates, counter-clockwise layout
- **TestBoardMovement**: Movement paths, entry positions, backward movement, validation
- **TestBoardRendering**: Board visualization and rendering
- **TestShortcutPaths**: Shortcut path selection at positions 5 and 10, path options

### test_yut_throw.py (6 tests)
Tests for yut stick throwing mechanics:
- Valid throw results
- Move values for each throw type
- Extra turn mechanics (Yut/Mo)
- Probability distribution (60% flat)
- Back Do mechanics

### test_piece_player.py (13 tests)
Tests for Piece and Player classes:
- **TestPiece**: Initialization, entry, movement, capture, finishing
- **TestPlayer**: Initialization, piece management, stacking, state queries

### test_game.py (27 tests)
Tests for main game engine:
- **TestGameInitialization**: Player setup, variable player counts, validation
- **TestGameMechanics**: Turn management, throwing phase
- **TestPieceEntry**: Entry with different throws, validation
- **TestPieceMovement**: Forward/backward movement, reaching goal
- **TestCaptureMechanics**: Capturing opponents, no self-capture
- **TestStackingMechanics**: Piece stacking, moving stacks together
- **TestWinCondition**: Win detection, partial completion
- **TestLegalMoves**: Legal move generation for entry and movement
- **TestGameState**: State tracking, history logging

## Test Statistics

- **Total Tests**: 65
- **Test Files**: 4
- **Test Classes**: 16
- **Coverage**: All major game mechanics including shortcut paths

## Key Test Areas

### Counter-Clockwise Board ✓
- Start at bottom-right (position 1)
- Move counter-clockwise: up → left → down → right
- Goal at position 20

### Entry Positions ✓
- Do (1) → position 1
- Gae (2) → position 2
- Geol (3) → position 3
- Yut (4) → position 4
- Mo (5) → position 5

### Yut Throw Probabilities ✓
- 60% flat probability per stick
- Mo: ~2.6%
- Do: ~11.5%, Back Do: ~3.8%
- Gae: ~34.6%
- Geol: ~34.6%
- Yut: ~13.0%

### Shortcut Paths ✓
- Position 5: Choice between outer (→6) and shortcut (→10)
- Position 10: Choice between outer (→11) and shortcut to goal (→20)
- Position 15: No choice, outer path only
- Shortcut diagonal from 5 continues through center (5→10→15)

### Game Mechanics ✓
- Variable player counts (2-6)
- Piece stacking (same player)
- Capture mechanics (opponent pieces)
- Backward movement (back Do)
- Win condition (all pieces home)
- Legal move generation
- State tracking

## Adding New Tests

1. Create test file: `test_<component>.py`
2. Import pytest and components:
   ```python
   import pytest
   from yoot import YutGame, Board, etc.
   ```
3. Organize tests in classes:
   ```python
   class TestFeatureName:
       def test_specific_behavior(self):
           # Arrange
           game = YutGame(["A", "B"], num_players=2)

           # Act
           result = game.some_method()

           # Assert
           assert result == expected_value
   ```
4. Run tests: `pytest tests/`

## Continuous Integration

To run tests in CI:
```bash
# Install dependencies
uv pip install -r requirements.txt

# Run tests with coverage
pytest tests/ -v --tb=short

# Generate coverage report (if pytest-cov installed)
pytest tests/ --cov=yoot --cov-report=html
```

## Test Markers

Tests can be marked for selective execution:

```python
@pytest.mark.slow
def test_long_running():
    pass

# Run only fast tests
pytest -m "not slow"
```

Available markers:
- `slow`: Long-running tests
- `integration`: Integration tests
