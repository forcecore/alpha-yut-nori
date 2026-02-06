# Yut Nori Implementation - Complete Rewrite

## Overview

Complete rewrite of the Yut Nori (윷놀이) game to implement the **correct traditional rules** based on research from namu.wiki and the cells.txt board diagram.

## Critical Rule Corrections

### Previous (WRONG) Implementation
❌ 21 positions (1-20 + center)
❌ Position 20 as goal
❌ Clockwise movement
❌ Player chooses shortcuts
❌ All pieces enter at position 1

### Current (CORRECT) Implementation
✅ 29 positions: 20 outer (00-19) + 9 diagonal (aa-ee, xx-vv with shared cc)
✅ Position 00 is both START and GOAL (circular)
✅ Counter-clockwise movement: 00→01→02→...→19→00
✅ **AUTOMATIC shortcuts** (landing on 05 or 10 forces diagonal entry)
✅ Entry positions vary by throw: Do→01, Gae→02, Geol→03, Yut→04, Mo→05

## Board Structure

```
29 Total Positions:

    10 09 08 07 06 05       ← Outer path positions (counter-clockwise)
       xx       aa          ← Diagonal positions
    11             04
         yy    bb
    12             03
           cc               ← Shared center position
    13             02
         uu   dd
    14             01
      vv        ee
    15 16 17 18 19 00       ← Position 00 is start AND goal
```

**Outer Path (20 positions):** '00' → '01' → ... → '19' → '00'
**Right Diagonal (5 positions):** 05 → aa → bb → cc → dd → ee → 00
**Left Diagonal (5 positions):** 10 → xx → yy → cc → uu → vv → 15

## Test Results

✅ tests/test_board.py: 32/32 passing
✅ tests/test_yut_throw.py: 6/6 passing
✅ Verification tests passing (test_quick.py, test_shortcuts.py)

## Status

✅ Core game engine implemented with correct rules
✅ Automatic shortcuts working correctly
✅ CLI updated and working
