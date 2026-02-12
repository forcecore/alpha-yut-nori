import type { ThrowName, ThrowResult } from './types';

export class YutThrow {
  static readonly THROW_NAMES: Record<number, ThrowName> = {
    1: 'do',
    2: 'gae',
    3: 'geol',
    4: 'yut',
    0: 'mo',
  };

  static readonly MOVE_VALUES: Record<ThrowName, number> = {
    do: 1,
    back_do: -1,
    gae: 2,
    geol: 3,
    yut: 4,
    mo: 5,
  };

  static readonly EXTRA_TURN_THROWS: Set<ThrowName> = new Set(['yut', 'mo']);

  static readonly FLAT_PROBABILITY = 0.6;

  static readonly KOREAN_NAMES: Record<ThrowName, string> = {
    do: '도',
    back_do: '빽도',
    gae: '개',
    geol: '걸',
    yut: '윷',
    mo: '모',
  };

  static throw(): ThrowResult {
    const sticks = Array.from({ length: 4 }, () => Math.random() < YutThrow.FLAT_PROBABILITY);
    const flatCount = sticks.filter(Boolean).length;

    let name = YutThrow.THROW_NAMES[flatCount];

    // Special case: if Do (1 flat), check if it's the back Do stick
    if (name === 'do') {
      const flatIdx = sticks.indexOf(true);
      if (flatIdx === 0) {
        name = 'back_do';
      }
    }

    return {
      name,
      value: YutThrow.MOVE_VALUES[name],
      sticks,
    };
  }

  static grantsExtraTurn(throwName: ThrowName): boolean {
    return YutThrow.EXTRA_TURN_THROWS.has(throwName);
  }

  static getMoveValue(throwName: ThrowName): number {
    return YutThrow.MOVE_VALUES[throwName];
  }
}
