export class Board {
  static readonly NUM_POSITIONS = 29;
  static readonly START_POSITION = '00';
  static readonly GOAL_POSITION = '00';

  static readonly OUTER_POSITIONS: string[] = Array.from({ length: 20 }, (_, i) =>
    String(i).padStart(2, '0')
  );

  static readonly RIGHT_DIAGONAL = ['aa', 'bb', 'cc', 'pp', 'qq'];
  static readonly LEFT_DIAGONAL = ['xx', 'yy', 'cc', 'uu', 'vv'];

  static readonly ALL_POSITIONS = new Set([
    ...Board.OUTER_POSITIONS,
    ...Board.RIGHT_DIAGONAL,
    ...Board.LEFT_DIAGONAL,
  ]);

  static readonly DIAGONAL_CELLS = new Set([
    'aa', 'bb', 'cc', 'pp', 'qq', 'xx', 'yy', 'uu', 'vv',
  ]);

  static readonly MOVE_TABLE: Record<string, Record<number, string>> = {
    '00': { 1: '01', 2: '02', 3: '03', 4: '04', 5: '05' },
    '01': { 1: '02', 2: '03', 3: '04', 4: '05', 5: '06' },
    '02': { 1: '03', 2: '04', 3: '05', 4: '06', 5: '07' },
    '03': { 1: '04', 2: '05', 3: '06', 4: '07', 5: '08' },
    '04': { 1: '05', 2: '06', 3: '07', 4: '08', 5: '09' },
    '05': { 1: 'aa', 2: 'bb', 3: 'cc', 4: 'uu', 5: 'vv' },
    '06': { 1: '07', 2: '08', 3: '09', 4: '10', 5: '11' },
    '07': { 1: '08', 2: '09', 3: '10', 4: '11', 5: '12' },
    '08': { 1: '09', 2: '10', 3: '11', 4: '12', 5: '13' },
    '09': { 1: '10', 2: '11', 3: '12', 4: '13', 5: '14' },
    '10': { 1: 'xx', 2: 'yy', 3: 'cc', 4: 'pp', 5: 'qq' },
    '11': { 1: '12', 2: '13', 3: '14', 4: '15', 5: '16' },
    '12': { 1: '13', 2: '14', 3: '15', 4: '16', 5: '17' },
    '13': { 1: '14', 2: '15', 3: '16', 4: '17', 5: '18' },
    '14': { 1: '15', 2: '16', 3: '17', 4: '18', 5: '19' },
    '15': { 1: '16', 2: '17', 3: '18', 4: '19', 5: '00' },
    '16': { 1: '17', 2: '18', 3: '19', 4: '00' },
    '17': { 1: '18', 2: '19', 3: '00' },
    '18': { 1: '19', 2: '00' },
    '19': { 1: '00' },
    aa: { 1: 'bb', 2: 'cc', 3: 'uu', 4: 'vv', 5: '15' },
    bb: { 1: 'cc', 2: 'uu', 3: 'vv', 4: '15', 5: '16' },
    cc: { 1: 'pp', 2: 'qq', 3: '00' },
    pp: { 1: 'qq', 2: '00' },
    qq: { 1: '00' },
    xx: { 1: 'yy', 2: 'cc', 3: 'pp', 4: 'qq', 5: '00' },
    yy: { 1: 'cc', 2: 'pp', 3: 'qq', 4: '00' },
    uu: { 1: 'vv', 2: '15', 3: '16', 4: '17', 5: '18' },
    vv: { 1: '15', 2: '16', 3: '17', 4: '18', 5: '19' },
  };

  // Backward movement (back-do): list of possible previous positions.
  // Positions where two paths merge (00, cc, 15) have multiple destinations.
  static readonly BACK_DO: Record<string, string[]> = {
    '01': ['00'], '02': ['01'], '03': ['02'], '04': ['03'], '05': ['04'],
    '06': ['05'], '07': ['06'], '08': ['07'], '09': ['08'], '10': ['09'],
    '11': ['10'], '12': ['11'], '13': ['12'], '14': ['13'],
    '15': ['14', 'vv'],   // outer path OR right diagonal
    '16': ['15'], '17': ['16'], '18': ['17'], '19': ['18'],
    '00': ['19', 'qq'],   // outer path OR left diagonal
    aa: ['05'], bb: ['aa'],
    cc: ['bb', 'yy'],     // right diagonal OR left diagonal
    uu: ['cc'], vv: ['uu'],
    xx: ['10'], yy: ['xx'],
    pp: ['cc'], qq: ['pp'],
  };

  getNextPosition(currentPos: string, steps: number, allowOvershoot = false): string | null {
    if (steps === 0) return currentPos;
    if (steps === -1) {
      const dests = Board.BACK_DO[currentPos];
      return dests?.[0] ?? null;
    }
    const dest = Board.MOVE_TABLE[currentPos]?.[steps] ?? null;
    if (dest !== null) return dest;

    // Non-exact landing: if this position can reach 00 with a smaller step,
    // a larger step overshoots past 00 — piece exits immediately.
    if (allowOvershoot) {
      const entries = Board.MOVE_TABLE[currentPos];
      if (entries && Object.values(entries).includes('00')) {
        return 'EXIT';
      }
    }
    return null;
  }

  getBackDoDestinations(currentPos: string): string[] {
    return Board.BACK_DO[currentPos] ?? [];
  }

  triggersShortcut(position: string): boolean {
    return position === '05' || position === '10';
  }

  static getEntryPosition(steps: number): string {
    if (steps >= 1 && steps <= 5) return String(steps).padStart(2, '0');
    return '01';
  }

  static isFinishPosition(position: string, hasMoved: boolean): boolean {
    return position === '00' && hasMoved;
  }

  isValidPosition(position: string): boolean {
    return Board.ALL_POSITIONS.has(position);
  }
}
