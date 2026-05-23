"""
move_logic.py
-------------
Pure-logic module (no GUI dependencies) that answers three questions:

  1. get_valid_moves(pawn_pos, opponent_pos, board)
        → list of (row, col) the pawn can legally move to this turn.

  2. bfs_path_exists(start, goal_row, board, opponent_pos)
        → True if there is at least one path from *start* to any cell
          on *goal_row*, treating walls AND the opponent pawn as obstacles.
          Used to validate wall placements (both players must keep a path).

  3. bfs_distance(start, goal_row, board)
        → Shortest number of pawn moves from *start* to *goal_row*
          ignoring the opponent pawn.  Used by the AI heuristic.

Coordinate system
-----------------
  (row, col), 0-indexed, row 0 = top, row 8 = bottom.
  Player 1 starts (8,4) → goal_row=0.
  Player 2 starts (0,4) → goal_row=8.

Board parameter
---------------
  Any object that exposes:
      board.is_wall_between((r1, c1), (r2, c2)) → bool
"""

from __future__ import annotations
from collections import deque
from typing import List, Optional, Tuple

BOARD_SIZE = 9
Position = Tuple[int, int]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _in_bounds(r: int, c: int) -> bool:
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def _orthogonal_neighbors(r: int, c: int) -> List[Position]:
    """All in-bounds orthogonal neighbours of (r, c)."""
    candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
    return [(nr, nc) for nr, nc in candidates if _in_bounds(nr, nc)]


def _can_step(r1: int, c1: int, r2: int, c2: int, board) -> bool:
    """True if a pawn on (r1,c1) can step to adjacent (r2,c2) (no wall)."""
    return not board.is_wall_between((r1, c1), (r2, c2))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_valid_moves(
    pawn_pos: Position,
    opponent_pos: Position,
    board,
) -> List[Position]:
    """Return all legal destination squares for the pawn at *pawn_pos*.

    Rules implemented
    -----------------
    * Normal step  – move to any of the four orthogonal neighbours that is
                     not blocked by a wall and is not occupied by the opponent.
    * Straight jump – when the neighbour IS the opponent and there is no wall
                      behind the opponent, jump straight over.
    * Diagonal jump – when the straight jump is blocked (wall behind opponent
                      or board edge), the pawn may jump diagonally to either
                      side of the opponent (if not wall-blocked).

    Parameters
    ----------
    pawn_pos     : (row, col) of the pawn that wants to move.
    opponent_pos : (row, col) of the other player's pawn.
    board        : Board instance (must have is_wall_between).

    Returns
    -------
    Sorted list of unique (row, col) destinations (sorted for determinism).
    """
    pr, pc = pawn_pos
    or_, oc = opponent_pos
    moves: set = set()

    for nr, nc in _orthogonal_neighbors(pr, pc):
        if not _can_step(pr, pc, nr, nc, board):
            continue  # wall blocks this edge

        if (nr, nc) != opponent_pos:
            # Normal step – destination is free
            moves.add((nr, nc))
        else:
            # Neighbour is occupied by the opponent → jump logic
            dr = nr - pr
            dc = nc - pc
            jump_r = nr + dr   # square directly behind opponent
            jump_c = nc + dc

            if (_in_bounds(jump_r, jump_c)
                    and _can_step(nr, nc, jump_r, jump_c, board)):
                # Straight jump over the opponent
                moves.add((jump_r, jump_c))
            else:
                # Straight jump blocked: try diagonal jumps
                # Perpendicular directions
                if dr == 0:  # opponent is left/right → diagonals are up/down
                    for side_r, side_c in [(nr - 1, nc), (nr + 1, nc)]:
                        if (_in_bounds(side_r, side_c)
                                and _can_step(nr, nc, side_r, side_c, board)):
                            moves.add((side_r, side_c))
                else:        # opponent is up/down → diagonals are left/right
                    for side_r, side_c in [(nr, nc - 1), (nr, nc + 1)]:
                        if (_in_bounds(side_r, side_c)
                                and _can_step(nr, nc, side_r, side_c, board)):
                            moves.add((side_r, side_c))

    return sorted(moves)


def bfs_path_exists(
    start: Position,
    goal_row: int,
    board,
    opponent_pos: Optional[Position] = None,
) -> bool:
    """Return True if a path exists from *start* to any cell on *goal_row*.

    Walls block movement as normal.  If *opponent_pos* is provided that
    cell is treated as impassable (used when validating wall placements so
    we don't count a route that passes through the opponent's pawn).

    Parameters
    ----------
    start        : (row, col) starting cell.
    goal_row     : target row (0 or 8).
    board        : Board instance.
    opponent_pos : optional (row, col) to treat as an extra obstacle.

    Returns
    -------
    bool
    """
    if start[0] == goal_row:
        return True

    visited = {start}
    queue = deque([start])

    while queue:
        r, c = queue.popleft()

        for nr, nc in _orthogonal_neighbors(r, c):
            if (nr, nc) in visited:
                continue
            if opponent_pos and (nr, nc) == opponent_pos:
                continue
            if board.is_wall_between((r, c), (nr, nc)):
                continue

            if nr == goal_row:
                return True

            visited.add((nr, nc))
            queue.append((nr, nc))

    return False


def bfs_distance(
    start: Position,
    goal_row: int,
    board,
) -> int:
    """Return the shortest pawn-move distance from *start* to *goal_row*.

    Walls are respected; the opponent pawn is ignored (used by AI
    heuristics that compare distances independently).

    Returns
    -------
    int  – minimum moves required, or a very large number if unreachable
           (should not happen in a legal game state, but guards the AI).
    """
    if start[0] == goal_row:
        return 0

    visited = {start}
    queue = deque([(start, 0)])

    while queue:
        (r, c), dist = queue.popleft()

        for nr, nc in _orthogonal_neighbors(r, c):
            if (nr, nc) in visited:
                continue
            if board.is_wall_between((r, c), (nr, nc)):
                continue

            new_dist = dist + 1
            if nr == goal_row:
                return new_dist

            visited.add((nr, nc))
            queue.append(((nr, nc), new_dist))

    return 10 ** 9   # unreachable (illegal game state)


# ===========================================================================
# Tests — run with: python pathfinder.py
# ===========================================================================

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from board import Board
    from pawn import Pawn

    _results = []

    def check(name, condition, extra=""):
        status = "PASS" if condition else "FAIL"
        _results.append((name, condition))
        tag = f"  (got {extra})" if extra else ""
        print(f"  [{status}] {name}{tag}")

    def section(title):
        print(f"\n{'='*60}\n  {title}\n{'='*60}")

    def empty_board():
        return Board()

    # -----------------------------------------------------------------------
    section("1. Pawn class")
    # -----------------------------------------------------------------------
    p1 = Pawn(start_pos=(8, 4), goal_row=0, player_id=1)
    check("p1 initial position", p1.position == (8, 4))
    check("p1 row property", p1.row == 8)
    check("p1 col property", p1.col == 4)
    check("p1 goal_row", p1.goal_row == 0)
    check("p1 walls_remaining default 10", p1.walls_remaining == 10)
    check("p1 has_won() is False at start", not p1.has_won())
    check("p1 has_walls() is True", p1.has_walls())
    p1.move_to((0, 4))
    check("p1 has_won() after moving to goal row", p1.has_won())
    p1.move_to((8, 4))
    p1.place_wall()
    check("place_wall decrements count", p1.walls_remaining == 9)
    p_no_walls = Pawn(start_pos=(0, 4), goal_row=8, player_id=2, walls=0)
    check("has_walls() False when 0 walls", not p_no_walls.has_walls())
    try:
        p_no_walls.place_wall()
        check("place_wall raises on 0 walls", False)
    except ValueError:
        check("place_wall raises on 0 walls", True)
    check("__repr__ runs", "Pawn" in repr(p1))

    # -----------------------------------------------------------------------
    section("2. Normal steps (no jump involved)")
    # -----------------------------------------------------------------------
    board = empty_board()
    moves = get_valid_moves((4, 4), (0, 0), board)
    check("Centre has 4 moves", len(moves) == 4, moves)
    check("Centre moves correct", set(moves) == {(3,4),(5,4),(4,3),(4,5)})

    moves = get_valid_moves((0, 0), (8, 8), board)
    check("Top-left corner has 2 moves", len(moves) == 2, moves)
    check("Corner moves correct", set(moves) == {(1,0),(0,1)})

    # H wall at (5,4) blocks (5,4)<->(6,4) and (5,5)<->(6,5)
    # To block downward step from (4,4) to (5,4) we need H wall at (4,4)
    board2 = empty_board()
    board2.place_wall(4, 4, 'H')  # blocks (4,4)->(5,4)
    moves = get_valid_moves((4, 4), (0, 0), board2)
    check("Wall blocks downward step from (4,4)", (5,4) not in moves, moves)
    check("Other three directions still open", {(3,4),(4,3),(4,5)}.issubset(set(moves)))

    # -----------------------------------------------------------------------
    section("3. Straight jump over opponent")
    # -----------------------------------------------------------------------
    board = empty_board()
    moves = get_valid_moves((5, 4), (4, 4), board)
    check("Straight jump UP included", (3,4) in moves, moves)
    check("Opponent square NOT in moves", (4,4) not in moves)

    moves = get_valid_moves((3, 4), (4, 4), board)
    check("Straight jump DOWN included", (5,4) in moves, moves)

    moves = get_valid_moves((4, 5), (4, 4), board)
    check("Straight jump LEFT included", (4,3) in moves, moves)

    moves = get_valid_moves((4, 3), (4, 4), board)
    check("Straight jump RIGHT included", (4,5) in moves, moves)

    moves = get_valid_moves((1, 4), (0, 4), board)
    check("Straight jump blocked by top edge", (-1,4) not in moves, moves)

    # -----------------------------------------------------------------------
    section("4. Diagonal jump (straight blocked by wall)")
    # -----------------------------------------------------------------------
    # H wall at (3,4) blocks (3,4)<->(4,4) and (3,5)<->(4,5)
    # Pawn (5,4), opponent (4,4): straight jump needs (3,4) which is blocked
    board = empty_board()
    board.place_wall(3, 4, 'H')   # blocks (3,4)<->(4,4)
    check("Wall correctly blocks (3,4)->(4,4)", board.is_wall_between((3,4),(4,4)))

    moves = get_valid_moves((5, 4), (4, 4), board)
    check("Diagonal LEFT (4,3) available when straight blocked", (4,3) in moves, moves)
    check("Diagonal RIGHT (4,5) available when straight blocked", (4,5) in moves, moves)
    check("Straight jump (3,4) NOT available", (3,4) not in moves, moves)

    # V wall at (3,5) blocks (3,5)<->(3,6) and (4,5)<->(4,6)
    # To block (4,4)<->(4,5) we need V wall at (4,4)
    board2 = empty_board()
    board2.place_wall(4, 4, 'V')    # blocks (4,4)<->(4,5) and (5,4)<->(5,5)
    moves = get_valid_moves((4, 3), (4, 4), board2)
    check("Diagonal UP (3,4) available", (3,4) in moves, moves)
    check("Diagonal DOWN (5,4) available", (5,4) in moves, moves)
    check("Straight jump (4,5) NOT available", (4,5) not in moves, moves)

    # Straight blocked + left diagonal also blocked
    board3 = empty_board()
    board3.place_wall(3, 4, 'H')  # blocks straight jump (3,4) from opponent (4,4)
    board3.place_wall(4, 3, 'V')    # blocks left diagonal: (4,3)<->(4,4)
    moves = get_valid_moves((5, 4), (4, 4), board3)
    check("Only right diagonal (4,5) when left also blocked",
          (4,5) in moves and (4,3) not in moves, moves)

    # Both diagonals blocked too
    board4 = empty_board()
    board4.place_wall(3, 4, 'H')  # blocks straight
    board4.place_wall(4, 3, 'V')    # blocks left diagonal (4,3)<->(4,4)
    board4.place_wall(4, 4, 'V')    # blocks right diagonal (4,4)<->(4,5)
    moves = get_valid_moves((5, 4), (4, 4), board4)
    check("No jump when straight + both diagonals blocked",
          (3,4) not in moves and (4,3) not in moves and (4,5) not in moves, moves)

    board5 = empty_board()
    moves = get_valid_moves((1, 4), (0, 4), board5)
    check("Edge-blocked straight -> diagonal left (0,3) available", (0,3) in moves, moves)
    check("Edge-blocked straight -> diagonal right (0,5) available", (0,5) in moves, moves)

    # -----------------------------------------------------------------------
    section("5. bfs_path_exists")
    # -----------------------------------------------------------------------
    board = empty_board()
    check("P1 path exists on empty board", bfs_path_exists((8,4), 0, board))
    check("P2 path exists on empty board", bfs_path_exists((0,4), 8, board))
    check("Already at goal row -> True", bfs_path_exists((0,4), 0, board))

    # Full barrier across row 4/5 boundary using 4 H walls covering all 9 columns
    # H wall at (r,c) blocks cols c and c+1. Place at cols 0,2,4,6 = segs 0-7.
    # Col 8 edge: H wall at (4,7) covers cols 7 and 8 — but (4,6) already covers 6,7.
    # Use (4,0),(4,2),(4,4),(4,6) for cols 0-7, then manually cover col 8.
    board_blocked = empty_board()
    for col in range(0, 8, 2):
        board_blocked.place_wall(4, col, 'H')
    board_blocked.horizontal_walls.add((4, 8))   # manually plug last column edge
    check("Path blocked by full horizontal wall",
          not bfs_path_exists((8,4), 0, board_blocked))

    board_obs = empty_board()
    for col in range(0, 8, 2):
        board_obs.place_wall(4, col, 'H')
    board_obs.horizontal_walls.add((4, 8))
    check("Path blocked with opponent obstacle",
          not bfs_path_exists((8,4), 0, board_obs, opponent_pos=(6,4)))

    # -----------------------------------------------------------------------
    section("6. bfs_distance")
    # -----------------------------------------------------------------------
    board = empty_board()
    check("P1 distance on empty board == 8",
          bfs_distance((8,4), 0, board) == 8, bfs_distance((8,4),0,board))
    check("P2 distance on empty board == 8",
          bfs_distance((0,4), 8, board) == 8, bfs_distance((0,4),8,board))
    check("Distance when already at goal == 0", bfs_distance((0,4), 0, board) == 0)
    check("Distance when 1 step away == 1", bfs_distance((1,4), 0, board) == 1)

    board_full = empty_board()
    for col in range(0, 8, 2):
        board_full.place_wall(2, col, 'H')
    board_full.horizontal_walls.add((2, 8))
    d = bfs_distance((4,4), 0, board_full)
    check("Full barrier at row 2 forces detour (distance > 4)", d > 4, d)

    # -----------------------------------------------------------------------
    section("Summary")
    passed = sum(1 for _, ok in _results if ok)
    total = len(_results)
    print(f"\n  {passed}/{total} tests passed")
    if passed == total:
        print("\n  All tests passed!")
    else:
        failed = [name for name, ok in _results if not ok]
        print(f"\n  Failed: {failed}")