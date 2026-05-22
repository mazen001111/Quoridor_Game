"""
ai_hard.py
----------
Hard difficulty AI for the Quoridor game.
"""

from __future__ import annotations
import time
from typing import Optional, Tuple

from game.pathfinder import bfs_distance
# EXPLICIT IMPORTS
from ai.ai_player import _GameState, evaluate, get_wall_candidates, INF
from ai.ai_easy   import easy_action

Action = Tuple

HARD_DEPTH           = 5
HARD_WALL_CANDIDATES = 20
HARD_TIME_BUDGET     = 2.0

def hard_action(state: _GameState) -> Action:
    deadline    = time.time() + HARD_TIME_BUDGET
    best_action: Optional[Action] = None

    for depth in range(1, HARD_DEPTH + 1):
        if time.time() >= deadline: break
        action = _root_search(state, depth, deadline)
        if action is not None:
            best_action = action
        if time.time() >= deadline: break

    if best_action is None:
        return easy_action(state)
    return best_action

def _root_search(state: _GameState, depth: int, deadline: float) -> Optional[Action]:
    best_score  = -INF
    best_action: Optional[Action] = None
    alpha, beta = -INF, INF

    pawn_moves = state.get_ai_pawn_moves()
    pawn_moves.sort(key=lambda pos: bfs_distance(pos, state.ai_goal, state.board))

    for dest in pawn_moves:
        if time.time() >= deadline: return best_action
        child = state.apply_ai_move(dest)
        score = _minimax(child, depth=depth - 1, is_maximizing=False, alpha=alpha, beta=beta, deadline=deadline)
        if score > best_score:
            best_score  = score
            best_action = ("move", dest)
        alpha = max(alpha, best_score)
        if beta <= alpha: break

    for (r, c, ori) in get_wall_candidates(state, is_ai_turn=True, max_candidates=HARD_WALL_CANDIDATES):
        if time.time() >= deadline: return best_action
        child = state.apply_ai_wall(r, c, ori)
        score = _minimax(child, depth=depth - 1, is_maximizing=False, alpha=alpha, beta=beta, deadline=deadline)
        if score > best_score:
            best_score  = score
            best_action = ("wall", r, c, ori)
        alpha = max(alpha, best_score)
        if beta <= alpha: break

    return best_action

def _minimax(state: _GameState, depth: int, is_maximizing: bool, alpha: float, beta: float, deadline: float) -> float:
    if time.time() >= deadline or state.is_terminal() or depth == 0:
        return evaluate(state)

    if is_maximizing:
        max_eval = -INF
        for dest in state.get_ai_pawn_moves():
            child    = state.apply_ai_move(dest)
            score    = _minimax(child, depth - 1, False, alpha, beta, deadline)
            max_eval = max(max_eval, score)
            alpha    = max(alpha, score)
            if beta <= alpha: break

        if max_eval < beta:
            for (r, c, ori) in get_wall_candidates(state, is_ai_turn=True, max_candidates=HARD_WALL_CANDIDATES):
                child    = state.apply_ai_wall(r, c, ori)
                score    = _minimax(child, depth - 1, False, alpha, beta, deadline)
                max_eval = max(max_eval, score)
                alpha    = max(alpha, score)
                if beta <= alpha: break
        return max_eval
    else:
        min_eval = INF
        for dest in state.get_human_pawn_moves():
            child    = state.apply_human_move(dest)
            score    = _minimax(child, depth - 1, True, alpha, beta, deadline)
            min_eval = min(min_eval, score)
            beta     = min(beta, score)
            if beta <= alpha: break

        if min_eval > alpha:
            for (r, c, ori) in get_wall_candidates(state, is_ai_turn=False, max_candidates=HARD_WALL_CANDIDATES):
                child    = state.apply_human_wall(r, c, ori)
                score    = _minimax(child, depth - 1, True, alpha, beta, deadline)
                min_eval = min(min_eval, score)
                beta     = min(beta, score)
                if beta <= alpha: break
        return min_eval