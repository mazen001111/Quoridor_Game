"""
ai_player.py
------------
Public entry point + shared utilities for the Quoridor AI opponent.

Difficulty modes live in their own modules:
  • ai_easy.py   — Greedy BFS follower
  • ai_medium.py — Minimax + Alpha-Beta, depth 3
  • ai_hard.py   — Minimax + Alpha-Beta + Iterative Deepening, depth 5

Public interface
----------------
    from ai_player import get_ai_action

    action = get_ai_action(game_manager)
    # Returns one of:
    #   ("move", (row, col))
    #   ("wall", row, col, orientation)

Integration with game_manager.py
---------------------------------
    from ai_player import get_ai_action

    def handle_ai_turn(self):
        if not self.is_ai_turn():
            return False
        action = get_ai_action(self)
        if action[0] == "move":
            return self.handle_pawn_move(action[1])
        elif action[0] == "wall":
            _, r, c, ori = action
            return self.handle_wall_placement(r, c, ori)
        return False

Coordinate system
-----------------
  (row, col), 0-indexed.  Row 0 = top, row 8 = bottom.
  AI is always Player 2:  starts (0,4), goal_row = 8.
  Human is Player 1:      starts (8,4), goal_row = 0.
"""

from __future__ import annotations
import math
from typing import Optional, Tuple, List

from game.pathfinder import bfs_distance, bfs_path_exists, get_valid_moves
from game.board import Board
from game.pawn import Pawn


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
Action   = Tuple   # ("move", pos) or ("wall", r, c, ori)
Position = Tuple[int, int]

# ---------------------------------------------------------------------------
# Shared Minimax constants (imported by ai_medium.py and ai_hard.py)
# ---------------------------------------------------------------------------
INF = math.inf


# ===========================================================================
# Public entry point
# ===========================================================================

def get_ai_action(game_manager) -> Action:
    """
    Return the best action for the AI (Player 2) given the current game state.

    Parameters
    ----------
    game_manager : GameManager
        The live game manager object. We only READ from it; we never mutate it.

    Returns
    -------
    ("move", (row, col))            — move the pawn
    ("wall", row, col, orientation) — place a wall
    """
    # Import here to avoid circular imports and keep each module self-contained
    from ai_easy   import easy_action
    from ai_medium import medium_action
    from ai_hard   import hard_action

    difficulty = (game_manager.ai_difficulty or "easy").lower()
    state = _GameState.from_manager(game_manager)

    if difficulty == "easy":
        return easy_action(state)
    elif difficulty == "medium":
        return medium_action(state)
    else:  # "hard"
        return hard_action(state)


# ===========================================================================
# Lightweight game-state snapshot used by all search trees
# ===========================================================================

class _GameState:
    """
    A minimal, copyable game state for the Minimax search tree.

    The search tree must create thousands of hypothetical game states without
    touching the real GameManager, Board, or Pawn objects. This class is a
    fast, self-contained snapshot.

    Attributes
    ----------
    board       : Board (copied)
    ai_pos      : (row, col)  — AI pawn position  (Player 2)
    human_pos   : (row, col)  — Human pawn position (Player 1)
    ai_walls    : int         — walls remaining for the AI
    human_walls : int         — walls remaining for the human
    ai_goal     : int         — goal row for AI (8)
    human_goal  : int         — goal row for human (0)
    """

    __slots__ = (
        "board", "ai_pos", "human_pos",
        "ai_walls", "human_walls", "ai_goal", "human_goal"
    )

    def __init__(self, board, ai_pos, human_pos,
                 ai_walls, human_walls, ai_goal=8, human_goal=0):
        self.board       = board
        self.ai_pos      = ai_pos
        self.human_pos   = human_pos
        self.ai_walls    = ai_walls
        self.human_walls = human_walls
        self.ai_goal     = ai_goal
        self.human_goal  = human_goal

    @classmethod
    def from_manager(cls, gm) -> "_GameState":
        """Build a snapshot from the live GameManager."""
        ai    = gm.pawns[2]
        human = gm.pawns[1]
        return cls(
            board       = gm.board.copy(),
            ai_pos      = ai.position,
            human_pos   = human.position,
            ai_walls    = ai.walls_remaining,
            human_walls = human.walls_remaining,
            ai_goal     = ai.goal_row,
            human_goal  = human.goal_row,
        )

    def copy(self) -> "_GameState":
        return _GameState(
            board       = self.board.copy(),
            ai_pos      = self.ai_pos,
            human_pos   = self.human_pos,
            ai_walls    = self.ai_walls,
            human_walls = self.human_walls,
            ai_goal     = self.ai_goal,
            human_goal  = self.human_goal,
        )

    # ------------------------------------------------------------------
    # Terminal checks
    # ------------------------------------------------------------------

    def ai_won(self) -> bool:
        return self.ai_pos[0] == self.ai_goal

    def human_won(self) -> bool:
        return self.human_pos[0] == self.human_goal

    def is_terminal(self) -> bool:
        return self.ai_won() or self.human_won()

    # ------------------------------------------------------------------
    # Move generators
    # ------------------------------------------------------------------

    def get_ai_pawn_moves(self) -> List[Position]:
        return get_valid_moves(self.ai_pos, self.human_pos, self.board)

    def get_human_pawn_moves(self) -> List[Position]:
        return get_valid_moves(self.human_pos, self.ai_pos, self.board)

    # ------------------------------------------------------------------
    # State transitions (return new _GameState, never mutate self)
    # ------------------------------------------------------------------

    def apply_ai_move(self, dest: Position) -> "_GameState":
        s = self.copy()
        s.ai_pos = dest
        return s

    def apply_human_move(self, dest: Position) -> "_GameState":
        s = self.copy()
        s.human_pos = dest
        return s

    def apply_ai_wall(self, r: int, c: int, ori: str) -> "_GameState":
        s = self.copy()
        s.board.place_wall(r, c, ori)
        s.ai_walls -= 1
        return s

    def apply_human_wall(self, r: int, c: int, ori: str) -> "_GameState":
        s = self.copy()
        s.board.place_wall(r, c, ori)
        s.human_walls -= 1
        return s

    # ------------------------------------------------------------------
    # Path validation (used after simulating wall placement)
    # ------------------------------------------------------------------

    def both_paths_exist(self) -> bool:
        ai_ok = bfs_path_exists(
            self.ai_pos, self.ai_goal, self.board, self.human_pos
        )
        human_ok = bfs_path_exists(
            self.human_pos, self.human_goal, self.board, self.ai_pos
        )
        return ai_ok and human_ok


# ===========================================================================
# Evaluation function  (shared by Medium and Hard)
# ===========================================================================

def evaluate(state: _GameState) -> float:
    """
    Static evaluation of a board state from the AI's perspective.

    Higher values are better for the AI (Player 2).

    Formula
    -------
    score = (human_dist - ai_dist) * DIST_WEIGHT
           + (ai_walls - human_walls) * WALL_WEIGHT
           + terminal_bonus

    Explanation
    -----------
    • (human_dist - ai_dist): positive when the AI is closer to its goal.
      This is the single most important signal — shorter path = winning.

    • (ai_walls - human_walls): having more walls = more future options.
      Small bonus so the AI doesn't waste walls unless it gains path advantage.

    • terminal_bonus: large reward/penalty for win/loss states so the search
      always prefers winning over any heuristic advantage.
    """
    DIST_WEIGHT = 10
    WALL_WEIGHT = 1
    WIN_SCORE   = 10_000

    if state.ai_won():
        return WIN_SCORE
    if state.human_won():
        return -WIN_SCORE

    ai_dist    = bfs_distance(state.ai_pos,    state.ai_goal,    state.board)
    human_dist = bfs_distance(state.human_pos, state.human_goal, state.board)

    dist_score = (human_dist - ai_dist) * DIST_WEIGHT
    wall_score = (state.ai_walls - state.human_walls) * WALL_WEIGHT

    return dist_score + wall_score


# ===========================================================================
# Wall candidate filtering  (shared by Medium and Hard)
# ===========================================================================

def get_wall_candidates(
    state: _GameState,
    is_ai_turn: bool,
    max_candidates: int,
) -> List[Tuple[int, int, str]]:
    """
    Return a filtered list of wall placements worth considering.

    Strategy
    --------
    For each geometrically valid wall position, we compute how much it
    lengthens the OPPONENT's BFS path. We keep only the top N walls
    by that gain. Walls that don't lengthen the opponent's path at all
    are discarded entirely — they waste a wall and a search branch.

    If the current player has no walls left, return an empty list.

    Parameters
    ----------
    state          : current game state
    is_ai_turn     : True if we are generating candidates for the AI
    max_candidates : how many top walls to keep
    """
    if is_ai_turn and state.ai_walls == 0:
        return []
    if not is_ai_turn and state.human_walls == 0:
        return []

    # The "victim" whose path we are trying to lengthen
    if is_ai_turn:
        victim_pos  = state.human_pos
        victim_goal = state.human_goal
    else:
        victim_pos  = state.ai_pos
        victim_goal = state.ai_goal

    current_dist = bfs_distance(victim_pos, victim_goal, state.board)

    scored = []
    for (r, c, ori) in state.board.get_all_valid_wall_positions():
        # Simulate placing this wall
        test_board = state.board.copy()
        test_board.place_wall(r, c, ori)

        # Make sure both players can still reach their goal
        ai_ok = bfs_path_exists(
            state.ai_pos, state.ai_goal, test_board, state.human_pos
        )
        human_ok = bfs_path_exists(
            state.human_pos, state.human_goal, test_board, state.ai_pos
        )
        if not (ai_ok and human_ok):
            continue  # This wall would illegally block someone

        new_dist = bfs_distance(victim_pos, victim_goal, test_board)
        gain = new_dist - current_dist

        if gain > 0:
            scored.append((gain, r, c, ori))

    # Sort by most disruptive first, then take the top N
    scored.sort(key=lambda x: -x[0])
    return [(r, c, ori) for (_, r, c, ori) in scored[:max_candidates]]