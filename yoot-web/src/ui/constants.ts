// Board layout in a 600x600 SVG viewBox
// Traditional Yut board: square outer path with two crossing diagonals

const S = 600; // viewBox size
const M = 60;  // margin
const W = S - 2 * M; // inner width

// Outer corners
const TL = { x: M, y: M };         // position 10
const TR = { x: S - M, y: M };     // position 05
const BR = { x: S - M, y: S - M }; // position 00
const BL = { x: M, y: S - M };     // position 15
const CENTER = { x: S / 2, y: S / 2 }; // position cc

function lerp(a: { x: number; y: number }, b: { x: number; y: number }, t: number) {
  return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t };
}

// Outer path positions (counter-clockwise on the board visual)
// Right side: 00(BR) -> 01 -> 02 -> 03 -> 04 -> 05(TR)
// Top side: 05(TR) -> 06 -> 07 -> 08 -> 09 -> 10(TL)
// Left side: 10(TL) -> 11 -> 12 -> 13 -> 14 -> 15(BL)
// Bottom side: 15(BL) -> 16 -> 17 -> 18 -> 19 -> 00(BR)

export const POSITION_COORDS: Record<string, { x: number; y: number }> = {
  // Right edge: BR -> TR (bottom to top)
  '00': BR,
  '01': lerp(BR, TR, 1 / 5),
  '02': lerp(BR, TR, 2 / 5),
  '03': lerp(BR, TR, 3 / 5),
  '04': lerp(BR, TR, 4 / 5),
  '05': TR,

  // Top edge: TR -> TL (right to left)
  '06': lerp(TR, TL, 1 / 5),
  '07': lerp(TR, TL, 2 / 5),
  '08': lerp(TR, TL, 3 / 5),
  '09': lerp(TR, TL, 4 / 5),
  '10': TL,

  // Left edge: TL -> BL (top to bottom)
  '11': lerp(TL, BL, 1 / 5),
  '12': lerp(TL, BL, 2 / 5),
  '13': lerp(TL, BL, 3 / 5),
  '14': lerp(TL, BL, 4 / 5),
  '15': BL,

  // Bottom edge: BL -> BR (left to right)
  '16': lerp(BL, BR, 1 / 5),
  '17': lerp(BL, BR, 2 / 5),
  '18': lerp(BL, BR, 3 / 5),
  '19': lerp(BL, BR, 4 / 5),

  // Right diagonal: 05(TR) -> aa -> bb -> cc -> uu -> vv -> 15(BL)
  aa: lerp(TR, CENTER, 1 / 3),
  bb: lerp(TR, CENTER, 2 / 3),
  cc: CENTER,
  uu: lerp(CENTER, BL, 1 / 3),
  vv: lerp(CENTER, BL, 2 / 3),

  // Left diagonal: 10(TL) -> xx -> yy -> cc -> pp -> qq -> 00(BR)
  xx: lerp(TL, CENTER, 1 / 3),
  yy: lerp(TL, CENTER, 2 / 3),
  pp: lerp(CENTER, BR, 1 / 3),
  qq: lerp(CENTER, BR, 2 / 3),
};

// Lines connecting adjacent positions on the board
export const BOARD_EDGES: [string, string][] = [
  // Right edge
  ['00', '01'], ['01', '02'], ['02', '03'], ['03', '04'], ['04', '05'],
  // Top edge
  ['05', '06'], ['06', '07'], ['07', '08'], ['08', '09'], ['09', '10'],
  // Left edge
  ['10', '11'], ['11', '12'], ['12', '13'], ['13', '14'], ['14', '15'],
  // Bottom edge
  ['15', '16'], ['16', '17'], ['17', '18'], ['18', '19'], ['19', '00'],
  // Right diagonal (05 -> center -> 15)
  ['05', 'aa'], ['aa', 'bb'], ['bb', 'cc'], ['cc', 'uu'], ['uu', 'vv'], ['vv', '15'],
  // Left diagonal (10 -> center -> 00)
  ['10', 'xx'], ['xx', 'yy'], ['yy', 'cc'], ['cc', 'pp'], ['pp', 'qq'], ['qq', '00'],
];

// Special positions get larger circles
export const CORNER_POSITIONS = new Set(['00', '05', '10', '15', 'cc']);

export const NODE_RADIUS = 16;
export const CORNER_RADIUS = 22;
export const PIECE_RADIUS = 13;

export const PLAYER_COLORS = ['#e74c3c', '#3498db', '#2ecc71', '#f1c40f'];
export const PLAYER_COLORS_LIGHT = ['#f5a6a6', '#a6d4f5', '#a6f5c4', '#f5e6a6'];

// Key labels for pieces (displayed on board and in UI)
export const PIECE_KEYS = ['Q', 'W', 'E', 'R'];

// Reserve (home) positions for inactive pieces, outside the board per player
// stackDir: -1 = stack upward (bottom players), +1 = stack downward (top players)
export const RESERVE_POSITIONS: { x: number; y: number; stackDir: number }[] = [
  { x: S - 20, y: S - 20, stackDir: -1 },  // P0: bottom-right
  { x: S - 20, y: 20, stackDir: 1 },        // P1: top-right
  { x: 20, y: 20, stackDir: 1 },            // P2: top-left
  { x: 20, y: S - 20, stackDir: -1 },       // P3: bottom-left
];
