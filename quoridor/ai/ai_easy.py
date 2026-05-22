"""
ai_easy.py
----------
Easy difficulty AI for the Quoridor game.
"""

from __future__ import annotations
from typing import Tuple

from game.pathfinder import bfs_distance
# EXPLICIT IMPORT
from ai.ai_player import _GameState

Action = Tuple

def easy_action(state: _GameState) -> Action:
    """Greedy BFS follower."""
    moves = state.get_ai_pawn_moves()
    if not moves:
        return ("move", state.ai_pos)

    best_move = min(
        moves,
        key=lambda pos: bfs_distance(pos, state.ai_goal, state.board)
    )
    return ("move", best_move)