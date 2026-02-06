# Quick Start Guide - Yut Nori

## Installation & Testing

```bash
# Navigate to project directory
cd yoot

# Run test suite to verify everything works
python3 test_game.py

# Start playing!
python3 cli_game.py
```

## How to Play

1. **Setup**: Choose number of players (2-6), then enter names (or press Enter for defaults)

2. **Each Turn**:
   - Press Enter to throw yut sticks
   - If you throw Yut (윷) or Mo (모), you get extra throws automatically
   - All throws accumulate (e.g., Mo→Yut→Gae gives you [5,4,2] moves)

3. **Making Moves**:
   - Choose which piece to move or enter a new piece
   - Use accumulated moves in any order
   - Pieces stack when landing on your own pieces
   - Capture opponents by landing on their pieces

4. **Winning**: First player to get all 4 pieces to the goal wins!

## Throw Results

Yut sticks are unfair coins - each has 60% chance of landing flat side up!

- **Do (도)**: 1 space forward (~11.5%)
- **Back Do (빽도)**: 1 space BACKWARDS (~3.8% - one stick is special!)
- **Gae (개)**: 2 spaces (~34.6% - most common!)
- **Geol (걸)**: 3 spaces (~34.6% - most common!)
- **Yut (윷)**: 4 spaces + throw again (~13% - bonus throw!)
- **Mo (모)**: 5 spaces + throw again (~2.6% - very rare!)

## Tips

- Stack your pieces to move them together
- Landing on opponent pieces sends them back to start
- You can take shortcuts through the center
- Must land exactly on goal (excess moves wasted)

## Example Game Session

```
$ python3 cli_game.py

Welcome to Yut Nori!
============================================================
How many players? (2-6, default 4): 4

Enter names for 4 players (press Enter for default names):

Player 0 name (default: Player 0): Alice
Player 1 name (default: Player 1): Bob
Player 2 name (default: Player 2): Carol
Player 3 name (default: Player 3): Dave

Starting game...

Press Enter to begin...
```

## Project Structure

```
yoot/
├── yoot/              # Core game engine
│   ├── board.py       # Board logic
│   ├── piece.py       # Piece class
│   ├── player.py      # Player management
│   ├── yut_throw.py   # Throw mechanics
│   └── game.py        # Main engine
├── cli_game.py        # Play the game!
├── test_game.py       # Test suite
└── README.md          # Full documentation
```

## Next Steps

- Play a full game with friends
- Read README.md for API documentation
- Extend the engine for RL agents
- Build a GUI version

Enjoy playing Yut Nori! 🎲
