# =============================================================================
# test_board.py
# Tests for Member 1's board.py and wall.py
# Run this file directly: python test_board.py
# ALL tests should print PASSED. If any prints FAILED, fix the bug before
# handing off your code to the rest of the team.
# =============================================================================

# We need to adjust the import path since this test file is in the root
# but the game files are in the game/ folder
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.board import Board
from game.wall import Wall, get_cells_blocked_by_wall, walls_would_cross, walls_would_overlap


# ------------------------------------------------------------------
# Simple test helper
# ------------------------------------------------------------------

def test(name, condition):
    """Prints PASSED or FAILED for a test case."""
    status = "✅ PASSED" if condition else "❌ FAILED"
    print(f"  {status}: {name}")
    if not condition:
        # Make failures obvious
        print(f"           ^ THIS TEST FAILED — FIX BEFORE SHARING YOUR CODE")


# ==================================================================
# TEST GROUP 1: Board initialization
# ==================================================================
print("\n📋 GROUP 1: Board Initialization")

b = Board()
test("Board starts with no horizontal walls", len(b.horizontal_walls) == 0)
test("Board starts with no vertical walls", len(b.vertical_walls) == 0)
test("get_wall_count returns 0 on fresh board", b.get_wall_count() == 0)


# ==================================================================
# TEST GROUP 2: Horizontal wall placement — basic
# ==================================================================
print("\n📋 GROUP 2: Horizontal Wall Placement")

b = Board()
result = b.place_wall(3, 4, 'H')
test("Can place horizontal wall at (3,4)", result == True)
test("Wall is recorded in horizontal_walls set", (3, 4) in b.horizontal_walls)
test("get_wall_count is 1 after placing one wall", b.get_wall_count() == 1)

# Duplicate placement
result2 = b.place_wall(3, 4, 'H')
test("Cannot place duplicate horizontal wall at (3,4)", result2 == False)
test("Wall count is still 1 after failed duplicate", b.get_wall_count() == 1)

# Adjacent overlap (wall to the left)
b2 = Board()
b2.place_wall(3, 4, 'H')
result3 = b2.place_wall(3, 3, 'H')
test("Cannot place horizontal wall at (3,3) when (3,4) exists — left overlap", result3 == False)

# Adjacent overlap (wall to the right)
b3 = Board()
b3.place_wall(3, 4, 'H')
result4 = b3.place_wall(3, 5, 'H')
test("Cannot place horizontal wall at (3,5) when (3,4) exists — right overlap", result4 == False)

# Non-adjacent walls should be fine
b4 = Board()
b4.place_wall(3, 4, 'H')
result5 = b4.place_wall(3, 6, 'H')
test("Can place horizontal wall at (3,6) when (3,4) exists — no overlap", result5 == True)


# ==================================================================
# TEST GROUP 3: Vertical wall placement — basic
# ==================================================================
print("\n📋 GROUP 3: Vertical Wall Placement")

b = Board()
result = b.place_wall(3, 4, 'V')
test("Can place vertical wall at (3,4)", result == True)
test("Wall is recorded in vertical_walls set", (3, 4) in b.vertical_walls)

result2 = b.place_wall(3, 4, 'V')
test("Cannot place duplicate vertical wall at (3,4)", result2 == False)

# Adjacent overlap (wall above)
b2 = Board()
b2.place_wall(3, 4, 'V')
result3 = b2.place_wall(2, 4, 'V')
test("Cannot place vertical wall at (2,4) when (3,4) exists — upper overlap", result3 == False)

# Adjacent overlap (wall below)
b3 = Board()
b3.place_wall(3, 4, 'V')
result4 = b3.place_wall(4, 4, 'V')
test("Cannot place vertical wall at (4,4) when (3,4) exists — lower overlap", result4 == False)

# Non-adjacent vertical walls
b4 = Board()
b4.place_wall(3, 4, 'V')
result5 = b4.place_wall(5, 4, 'V')
test("Can place vertical wall at (5,4) when (3,4) exists — no overlap", result5 == True)


# ==================================================================
# TEST GROUP 4: Crossing walls
# ==================================================================
print("\n📋 GROUP 4: Crossing Walls")

b = Board()
b.place_wall(3, 4, 'H')
result = b.place_wall(3, 4, 'V')
test("Cannot place vertical wall at (3,4) when horizontal wall exists there — crossing", result == False)

b2 = Board()
b2.place_wall(3, 4, 'V')
result2 = b2.place_wall(3, 4, 'H')
test("Cannot place horizontal wall at (3,4) when vertical wall exists there — crossing", result2 == False)

b3 = Board()
b3.place_wall(3, 4, 'H')
result3 = b3.place_wall(3, 5, 'V')
test("Can place vertical wall at (3,5) when horizontal exists at (3,4) — no crossing", result3 == True)


# ==================================================================
# TEST GROUP 5: Out-of-bounds placement
# ==================================================================
print("\n📋 GROUP 5: Out-of-Bounds Placement")

b = Board()
test("Cannot place wall at row=8 (out of bounds)", b.place_wall(8, 4, 'H') == False)
test("Cannot place wall at col=8 (out of bounds)", b.place_wall(4, 8, 'H') == False)
test("Cannot place wall at row=-1 (out of bounds)", b.place_wall(-1, 4, 'H') == False)
test("Cannot place wall at col=-1 (out of bounds)", b.place_wall(4, -1, 'H') == False)
test("Can place wall at row=7 (boundary)", b.place_wall(7, 4, 'H') == True)
test("Can place wall at col=7 (boundary)", b.place_wall(4, 7, 'V') == True)
test("Can place wall at (0, 0)", b.place_wall(0, 0, 'H') == True)


# ==================================================================
# TEST GROUP 6: is_wall_between — horizontal walls
# ==================================================================
print("\n📋 GROUP 6: is_wall_between — Horizontal Walls")

b = Board()
b.place_wall(3, 4, 'H')
# This wall blocks downward movement at col 4 AND col 5 between rows 3 and 4

test("Wall at (3,4) blocks movement DOWN from (3,4) to (4,4)",
     b.is_wall_between((3, 4), (4, 4)) == True)

test("Wall at (3,4) blocks movement UP from (4,4) to (3,4)",
     b.is_wall_between((4, 4), (3, 4)) == True)

test("Wall at (3,4) blocks movement DOWN from (3,5) to (4,5)",
     b.is_wall_between((3, 5), (4, 5)) == True)

test("Wall at (3,4) blocks movement UP from (4,5) to (3,5)",
     b.is_wall_between((4, 5), (3, 5)) == True)

test("Wall at (3,4) does NOT block movement DOWN from (3,3) to (4,3)",
     b.is_wall_between((3, 3), (4, 3)) == False)

test("Wall at (3,4) does NOT block movement DOWN from (3,6) to (4,6)",
     b.is_wall_between((3, 6), (4, 6)) == False)

test("Wall at (3,4) does NOT block horizontal movement (3,4)→(3,5)",
     b.is_wall_between((3, 4), (3, 5)) == False)


# ==================================================================
# TEST GROUP 7: is_wall_between — vertical walls
# ==================================================================
print("\n📋 GROUP 7: is_wall_between — Vertical Walls")

b = Board()
b.place_wall(3, 4, 'V')
# This wall blocks rightward movement at row 3 AND row 4 between cols 4 and 5

test("Wall at (3,4)V blocks movement RIGHT from (3,4) to (3,5)",
     b.is_wall_between((3, 4), (3, 5)) == True)

test("Wall at (3,4)V blocks movement LEFT from (3,5) to (3,4)",
     b.is_wall_between((3, 5), (3, 4)) == True)

test("Wall at (3,4)V blocks movement RIGHT from (4,4) to (4,5)",
     b.is_wall_between((4, 4), (4, 5)) == True)

test("Wall at (3,4)V blocks movement LEFT from (4,5) to (4,4)",
     b.is_wall_between((4, 5), (4, 4)) == True)

test("Wall at (3,4)V does NOT block movement RIGHT from (2,4) to (2,5)",
     b.is_wall_between((2, 4), (2, 5)) == False)

test("Wall at (3,4)V does NOT block movement RIGHT from (5,4) to (5,5)",
     b.is_wall_between((5, 4), (5, 5)) == False)

test("Wall at (3,4)V does NOT block vertical movement (3,4)→(4,4)",
     b.is_wall_between((3, 4), (4, 4)) == False)


# ==================================================================
# TEST GROUP 8: remove_wall
# ==================================================================
print("\n📋 GROUP 8: Wall Removal")

b = Board()
b.place_wall(3, 4, 'H')
test("Wall exists before removal", b.is_wall_between((3, 4), (4, 4)) == True)

result = b.remove_wall(3, 4, 'H')
test("remove_wall returns True when wall exists", result == True)
test("Wall no longer blocks after removal", b.is_wall_between((3, 4), (4, 4)) == False)
test("Wall count is 0 after removal", b.get_wall_count() == 0)

result2 = b.remove_wall(3, 4, 'H')
test("remove_wall returns False when no wall exists", result2 == False)


# ==================================================================
# TEST GROUP 9: board.copy()
# ==================================================================
print("\n📋 GROUP 9: Board Copy")

b = Board()
b.place_wall(3, 4, 'H')
b.place_wall(5, 6, 'V')

b_copy = b.copy()
test("Copy has same horizontal walls", b_copy.horizontal_walls == b.horizontal_walls)
test("Copy has same vertical walls", b_copy.vertical_walls == b.vertical_walls)

# Modify copy — original should be unchanged
b_copy.place_wall(1, 1, 'H')
test("Adding wall to copy does NOT affect original", (1, 1) not in b.horizontal_walls)

b_copy.remove_wall(3, 4, 'H')
test("Removing wall from copy does NOT affect original", (3, 4) in b.horizontal_walls)


# ==================================================================
# TEST GROUP 10: get_all_walls and load_walls
# ==================================================================
print("\n📋 GROUP 10: Serialization (get_all_walls / load_walls)")

b = Board()
b.place_wall(2, 3, 'H')
b.place_wall(5, 1, 'V')

walls_data = b.get_all_walls()
test("get_all_walls returns a dict", isinstance(walls_data, dict))
test("get_all_walls has 'horizontal' key", 'horizontal' in walls_data)
test("get_all_walls has 'vertical' key", 'vertical' in walls_data)
test("horizontal list has 1 entry", len(walls_data['horizontal']) == 1)
test("vertical list has 1 entry", len(walls_data['vertical']) == 1)

# Restore into a new board
b2 = Board()
b2.load_walls(walls_data['horizontal'], walls_data['vertical'])
test("Loaded board blocks same movement as original",
     b2.is_wall_between((2, 3), (3, 3)) == True)
test("Loaded board has correct wall count", b2.get_wall_count() == 2)


# ==================================================================
# TEST GROUP 11: Wall dataclass
# ==================================================================
print("\n📋 GROUP 11: Wall Dataclass")

w = Wall(3, 4, 'H')
test("Wall.is_horizontal() returns True for H", w.is_horizontal() == True)
test("Wall.is_vertical() returns False for H", w.is_vertical() == False)
test("Wall.to_tuple() returns correct tuple", w.to_tuple() == (3, 4, 'H'))
test("Wall.is_valid_position() True for (3,4)", w.is_valid_position() == True)

w_bad = Wall(8, 4, 'H')
test("Wall.is_valid_position() False for (8,4) — out of bounds", w_bad.is_valid_position() == False)

w_dict = w.to_dict()
test("Wall.to_dict() returns correct dict", w_dict == {'row': 3, 'col': 4, 'orientation': 'H'})

w_restored = Wall.from_dict(w_dict)
test("Wall.from_dict() restores correctly", w_restored.row == 3 and w_restored.col == 4)

cells = get_cells_blocked_by_wall(Wall(3, 4, 'H'))
test("get_cells_blocked returns 2 pairs", len(cells) == 2)
test("First blocked pair is correct for H wall", cells[0] == ((3,4),(4,4)))
test("Second blocked pair is correct for H wall", cells[1] == ((3,5),(4,5)))


# ==================================================================
# TEST GROUP 12: get_all_valid_wall_positions
# ==================================================================
print("\n📋 GROUP 12: Valid Wall Position Enumeration")

b = Board()
positions = b.get_all_valid_wall_positions()
test("Empty board has 128 valid wall positions (64 H + 64 V)", len(positions) == 128)

b.place_wall(3, 4, 'H')
positions2 = b.get_all_valid_wall_positions()
# Placing (3,4,H) removes: (3,4,H), (3,3,H) overlap, (3,5,H) overlap, (3,4,V) cross
# That's 4 fewer positions
test("Placing one wall reduces valid positions by 3", len(positions2) == 125)


# ==================================================================
# TEST GROUP 13: board.reset()
# ==================================================================
print("\n📋 GROUP 13: Board Reset")

b = Board()
b.place_wall(0, 0, 'H')
b.place_wall(7, 7, 'V')
b.reset()
test("After reset, no horizontal walls", len(b.horizontal_walls) == 0)
test("After reset, no vertical walls", len(b.vertical_walls) == 0)
test("After reset, is_wall_between returns False everywhere",
     b.is_wall_between((0, 0), (1, 0)) == False)


# ==================================================================
# VISUAL DEBUG TEST
# ==================================================================
print("\n📋 BONUS: Visual Board Print Test")
print("(Check this manually — there should be walls shown below)")
b = Board()
b.place_wall(4, 4, 'H')   # horizontal wall in the middle
b.place_wall(2, 2, 'V')   # vertical wall top-left area
b.print_board()


# ==================================================================
# SUMMARY
# ==================================================================
print("\n" + "="*50)
print("All tests complete.")
print("If you see any ❌ FAILED above, fix that method in board.py")
print("before handing off your code to the team.")
print("="*50 + "\n")
