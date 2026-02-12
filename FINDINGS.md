# Yut Nori AI Experimental Findings

## Monte Carlo AI vs Random AI

**Setup**: Player 0 = Random, Player 1 = MC (100 sims/move), 1000 games total (500 per turn-order config).

| Config | MC Wins | Random Wins | MC Win Rate |
|--------|---------|-------------|-------------|
| Random first, MC second | 425 | 75 | 85.0% |
| MC first, Random second | 432 | 68 | 86.4% |
| **Overall** | **857** | **143** | **85.7%** |

MC dominates Random regardless of turn order. The ~14% Random win rate likely represents the irreducible luck factor from dice rolls.

## First-Mover Advantage (MC vs MC)

**Setup**: MC0 (first) vs MC1 (second), 100 sims/move, 1000 games.

| Player | Wins | Win Rate |
|--------|------|----------|
| MC0 (goes first) | 491 | 49.1% |
| MC1 (goes second) | 509 | 50.9% |

**No meaningful first-mover advantage.** The 1.8% gap is well within statistical noise (95% CI ~ +/-3% at 1000 games). Yut Nori's dice randomness completely levels the playing field regardless of turn order.

## MC Win Rate vs Simulation Count

**Setup**: Player 0 = Random, Player 1 = MC, 500 games per sim count.

| Sims | MC Wins | Win Rate | Time |
|------|---------|----------|------|
| 5 | 317/500 | 63.4% | 37s |
| 10 | 350/500 | 70.0% | 70s |
| 32 | 401/500 | 80.2% | 194s |
| 100 | 418/500 | 83.6% | 512s |
| 316 | 435/500 | 87.0% | 1410s |
| 1000 | 428/500 | 85.6% | 4207s |

**Key observations**:
- **5 to 32 sims**: Steep gains (63% to 80%). Even minimal search adds massive value.
- **32 to 316 sims**: Diminishing returns (80% to 87%).
- **316 to 1000 sims**: Flat / within noise (87% to 86%). No improvement, just 3x slower.
- **Sweet spot**: ~32-100 sims gives ~80-84% win rate at reasonable cost.
- **Ceiling**: ~85-87% appears to be the upper bound vs Random. The remaining ~13-15% is unwinnable due to dice luck.
