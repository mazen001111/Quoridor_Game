"""
ai_easy.py
----------
Easy difficulty AI for the Quoridor game.

Strategy
--------
Greedy BFS follower. Always moves its pawn one step closer to its goal row
along the shortest path. Never places walls. Simple to beat with any wall
strategy.

Public interface
----------------
    from ai_easy import easy_action

    action = easy_action(state)   # state is a _GameState instance
    # Returns: ("move", (row, col))
"""

from __future__ import annotations
from typing import Tuple

from game.pathfinder import bfs_distance
from ai_player import _GameState

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------
Action = Tuple


# ===========================================================================
# Easy mode
# ===========================================================================

def easy_action(state: _GameState) -> Action:
    """
    Greedy BFS follower.

    The AI always moves one step along its shortest BFS path to its goal row.
    It never places walls. This is the weakest mode — any human who places
    even one well-placed wall will slow it significantly.

    If somehow no moves are available (shouldn't happen in a legal game),
    fall back to the current position as a no-op.
    """
    moves = state.get_ai_pawn_moves()
    if not moves:
        # Should never happen in a legal game, but be safe
        return ("move", state.ai_pos)

    # Pick the move that gets us closest to the goal (lowest BFS distance)
    best_move = min(
        moves,
        key=lambda pos: bfs_distance(pos, state.ai_goal, state.board)
    )
    return ("move", best_move)