"""
ai_player.py
------------
Public entry point + shared utilities for the Quoridor AI opponent.
"""

from __future__ import annotations
import math
from typing import Optional, Tuple, List

from game.pathfinder import bfs_distance, bfs_path_exists, get_valid_moves
from game.board import Board
from game.pawn import Pawn

# ---------------------------------------------------------------------------
# Type aliases & Constants
# ---------------------------------------------------------------------------
Action   = Tuple   # ("move", pos) or ("wall", r, c, ori)
Position = Tuple[int, int]
INF = math.inf

# ===========================================================================
# Public entry point
# ===========================================================================

def get_ai_action(game_manager) -> Action:
    """Return the best action for the AI (Player 2) given the current game state."""
    # EXPLICIT IMPORTS: Using the 'ai.' prefix so Python finds them from the root
    from ai.ai_easy   import easy_action
    from ai.ai_medium import medium_action
    from ai.ai_hard   import hard_action

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
    """A minimal, copyable game state for the Minimax search tree."""

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

    def ai_won(self) -> bool:
        return self.ai_pos[0] == self.ai_goal

    def human_won(self) -> bool:
        return self.human_pos[0] == self.human_goal

    def is_terminal(self) -> bool:
        return self.ai_won() or self.human_won()

    def get_ai_pawn_moves(self) -> List[Position]:
        return get_valid_moves(self.ai_pos, self.human_pos, self.board)

    def get_human_pawn_moves(self) -> List[Position]:
        return get_valid_moves(self.human_pos, self.ai_pos, self.board)

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
    DIST_WEIGHT = 10
    WALL_WEIGHT = 1
    WIN_SCORE   = 10_000

    if state.ai_won(): return WIN_SCORE
    if state.human_won(): return -WIN_SCORE

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
    if is_ai_turn and state.ai_walls == 0: return []
    if not is_ai_turn and state.human_walls == 0: return []

    if is_ai_turn:
        victim_pos  = state.human_pos
        victim_goal = state.human_goal
    else:
        victim_pos  = state.ai_pos
        victim_goal = state.ai_goal

    current_dist = bfs_distance(victim_pos, victim_goal, state.board)
    scored = []
    
    for (r, c, ori) in state.board.get_all_valid_wall_positions():
        test_board = state.board.copy()
        test_board.place_wall(r, c, ori)

        if not (bfs_path_exists(state.ai_pos, state.ai_goal, test_board, state.human_pos) and 
                bfs_path_exists(state.human_pos, state.human_goal, test_board, state.ai_pos)):
            continue

        new_dist = bfs_distance(victim_pos, victim_goal, test_board)
        gain = new_dist - current_dist
        if gain > 0:
            scored.append((gain, r, c, ori))

    scored.sort(key=lambda x: -x[0])
    return [(r, c, ori) for (_, r, c, ori) in scored[:max_candidates]]