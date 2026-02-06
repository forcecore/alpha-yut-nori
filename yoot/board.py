"""
Board representation and path logic for Yut Nori.

Based on traditional Korean Yut board with 29 positions:
- Outer circular path: 00-19 (20 positions)
- Right diagonal: aa, bb, cc, pp, qq (5 positions)
- Left diagonal: xx, yy, uu, vv (4 positions, cc is shared center)

Board layout (from cells.txt):
    10 09 08 07 06 05
       xx       aa
    11             04
         yy    bb
    12             03
           cc
    13             02
         uu   pp
    14             01
      vv        qq
    15 16 17 18 19 00

Diagonal paths (both go through cc, crossing at center):
  From 05: aa -> bb -> cc -> uu -> vv -> exits at 15 (continues outer)
  From 10: xx -> yy -> cc -> pp -> qq -> exits at 00 (goal)
  From cc: always pp -> qq -> 00 (toward goal)
"""

import re
from pathlib import Path
from typing import List, Optional


class Board:
    """
    Represents the Yut Nori game board with 29 positions.

    Position 00: START and GOAL (pieces must return here to win)
    Outer path (COUNTER-CLOCKWISE): 00 -> 01 -> 02 -> ... -> 19 -> 00

    Shortcuts activate when LANDING on 05 or 10:
    - Landing on 05 -> next move enters right diagonal (aa->bb->cc->uu->vv->15)
    - Landing on 10 -> next move enters left diagonal (xx->yy->cc->pp->qq->00)
    - Starting from cc -> always goes toward 00 (pp->qq->00)

    Movement is fully stateless -- just a dictionary lookup.
    """

    NUM_POSITIONS = 29
    START_POSITION = '00'
    GOAL_POSITION = '00'

    OUTER_POSITIONS = [f'{i:02d}' for i in range(20)]

    # Diagonal positions (physical groupings, used for rendering)
    RIGHT_DIAGONAL = ['aa', 'bb', 'cc', 'pp', 'qq']
    LEFT_DIAGONAL = ['xx', 'yy', 'cc', 'uu', 'vv']

    ALL_POSITIONS = set(OUTER_POSITIONS + RIGHT_DIAGONAL + LEFT_DIAGONAL)
    DIAGONAL_CELLS = {'aa', 'bb', 'cc', 'pp', 'qq', 'xx', 'yy', 'uu', 'vv'}

    # Forward movement: MOVE_TABLE[position][steps] = destination
    # Missing entries mean the move is invalid (overshoot past goal).
    MOVE_TABLE = {
        '00': {1: '01', 2: '02', 3: '03', 4: '04', 5: '05'},
        '01': {1: '02', 2: '03', 3: '04', 4: '05', 5: '06'},
        '02': {1: '03', 2: '04', 3: '05', 4: '06', 5: '07'},
        '03': {1: '04', 2: '05', 3: '06', 4: '07', 5: '08'},
        '04': {1: '05', 2: '06', 3: '07', 4: '08', 5: '09'},
        '05': {1: 'aa', 2: 'bb', 3: 'cc', 4: 'uu', 5: 'vv'},
        '06': {1: '07', 2: '08', 3: '09', 4: '10', 5: '11'},
        '07': {1: '08', 2: '09', 3: '10', 4: '11', 5: '12'},
        '08': {1: '09', 2: '10', 3: '11', 4: '12', 5: '13'},
        '09': {1: '10', 2: '11', 3: '12', 4: '13', 5: '14'},
        '10': {1: 'xx', 2: 'yy', 3: 'cc', 4: 'pp', 5: 'qq'},
        '11': {1: '12', 2: '13', 3: '14', 4: '15', 5: '16'},
        '12': {1: '13', 2: '14', 3: '15', 4: '16', 5: '17'},
        '13': {1: '14', 2: '15', 3: '16', 4: '17', 5: '18'},
        '14': {1: '15', 2: '16', 3: '17', 4: '18', 5: '19'},
        '15': {1: '16', 2: '17', 3: '18', 4: '19', 5: '00'},
        '16': {1: '17', 2: '18', 3: '19', 4: '00'},
        '17': {1: '18', 2: '19', 3: '00'},
        '18': {1: '19', 2: '00'},
        '19': {1: '00'},
        'aa': {1: 'bb', 2: 'cc', 3: 'uu', 4: 'vv', 5: '15'},
        'bb': {1: 'cc', 2: 'uu', 3: 'vv', 4: '15', 5: '16'},
        'cc': {1: 'pp', 2: 'qq', 3: '00'},
        'pp': {1: 'qq', 2: '00'},
        'qq': {1: '00'},
        'xx': {1: 'yy', 2: 'cc', 3: 'pp', 4: 'qq', 5: '00'},
        'yy': {1: 'cc', 2: 'pp', 3: 'qq', 4: '00'},
        'uu': {1: 'vv', 2: '15', 3: '16', 4: '17', 5: '18'},
        'vv': {1: '15', 2: '16', 3: '17', 4: '18', 5: '19'},
    }

    # Backward movement (back-do): BACK_TABLE[position] = previous position
    # 00 is not in the table -> backward from 00 is invalid.
    BACK_TABLE = {
        '01': '00', '02': '01', '03': '02', '04': '03', '05': '04',
        '06': '05', '07': '06', '08': '07', '09': '08', '10': '09',
        '11': '10', '12': '11', '13': '12', '14': '13', '15': '14',
        '16': '15', '17': '16', '18': '17', '19': '18',
        'aa': '05', 'bb': 'aa', 'cc': 'bb',
        'uu': 'cc', 'vv': 'uu',
        'xx': '10', 'yy': 'xx',
        'pp': 'cc', 'qq': 'pp',
    }

    def __init__(self):
        """Initialize the board."""
        self._load_board_template()

    def _load_board_template(self):
        """Load board template from cells.txt file."""
        current_file = Path(__file__)
        project_root = current_file.parent.parent
        cells_file = project_root / 'cells.txt'

        if cells_file.exists():
            self.board_template = cells_file.read_text()
        else:
            self.board_template = """10 09 08  07 06 05
   xx        aa
11              04
      yy  bb
12              03
        cc
13              02
      uu  pp
14              01
   vv        qq
15 16 17  18 19 00"""

    def get_next_position(self, current_pos: str, steps: int) -> Optional[str]:
        """
        Look up next position from current position.

        Args:
            current_pos: Current position ('00'-'19' or diagonal letters)
            steps: Number of steps to move (1-5, or -1 for back do)

        Returns:
            Next position string, or None if move is invalid (overshoot)
        """
        if steps == 0:
            return current_pos
        if steps == -1:
            return self.BACK_TABLE.get(current_pos)
        return self.MOVE_TABLE.get(current_pos, {}).get(steps)

    def triggers_shortcut(self, position: str) -> bool:
        """Check if landing on this position triggers a diagonal shortcut."""
        return position in ('05', '10')

    def is_on_diagonal(self, position: str) -> bool:
        """Check if position is on a diagonal path."""
        return position in self.DIAGONAL_CELLS

    def render_board(self, pieces: List) -> str:
        """
        Create board visualization by replacing positions with pieces.

        Args:
            pieces: List of Piece objects to display

        Returns:
            Board string with colored pieces
        """
        COLORS = {
            0: '\033[91m',  # Red
            1: '\033[94m',  # Blue
            2: '\033[92m',  # Green
            3: '\033[93m',  # Yellow
        }
        RESET = '\033[0m'

        board_str = self.board_template

        piece_map = {}
        for piece in pieces:
            if piece.position and piece.is_active:
                pos = piece.position
                if pos not in piece_map:
                    piece_map[pos] = []
                piece_map[pos].append(piece.player_id)

        all_positions = self.OUTER_POSITIONS + self.RIGHT_DIAGONAL + self.LEFT_DIAGONAL

        for position in all_positions:
            if position in piece_map:
                players = piece_map[position]

                if len(players) == 1:
                    player_id = players[0]
                    color = COLORS.get(player_id, '')
                    replacement = f'{color}P{player_id}{RESET}'
                else:
                    player_id = players[0]
                    color = COLORS.get(player_id, '')
                    replacement = f'{color}x{len(players)}{RESET}'

                pattern = r'\b' + re.escape(position) + r'\b'
                board_str = re.sub(pattern, replacement, board_str)

        return board_str

    def is_valid_position(self, position: str) -> bool:
        """Check if position is valid."""
        return position in self.ALL_POSITIONS

    @staticmethod
    def get_entry_position(steps: int) -> str:
        """Get entry position based on throw value."""
        if 1 <= steps <= 5:
            return f'{steps:02d}'
        return '01'

    @staticmethod
    def is_finish_position(position: str, has_moved: bool) -> bool:
        """Check if piece finishes at this position."""
        return position == '00' and has_moved
