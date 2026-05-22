"""
ai_medium.py
------------
Medium difficulty AI for the Quoridor game.
"""

from __future__ import annotations
from typing import Optional, Tuple

# EXPLICIT IMPORTS
from ai.ai_player import _GameState, evaluate, get_wall_candidates, INF
from ai.ai_easy   import easy_action

Action = Tuple

MEDIUM_DEPTH           = 3
MEDIUM_WALL_CANDIDATES = 15

def medium_action(state: _GameState) -> Action:
    best_score  = -INF
    best_action: Optional[Action] = None
    alpha = -INF
    beta  =  INF

    for dest in state.get_ai_pawn_moves():
        child = state.apply_ai_move(dest)
        score = _minimax(child, depth=MEDIUM_DEPTH - 1, is_maximizing=False, alpha=alpha, beta=beta)
        if score > best_score:
            best_score  = score
            best_action = ("move", dest)
        alpha = max(alpha, best_score)

    for (r, c, ori) in get_wall_candidates(state, is_ai_turn=True, max_candidates=MEDIUM_WALL_CANDIDATES):
        child = state.apply_ai_wall(r, c, ori)
        score = _minimax(child, depth=MEDIUM_DEPTH - 1, is_maximizing=False, alpha=alpha, beta=beta)
        if score > best_score:
            best_score  = score
            best_action = ("wall", r, c, ori)
        alpha = max(alpha, best_score)

    if best_action is None:
        return easy_action(state)

    return best_action

def _minimax(state: _GameState, depth: int, is_maximizing: bool, alpha: float, beta: float) -> float:
    if state.is_terminal() or depth == 0:
        return evaluate(state)

    if is_maximizing:
        max_eval = -INF
        for dest in state.get_ai_pawn_moves():
            child    = state.apply_ai_move(dest)
            score    = _minimax(child, depth - 1, False, alpha, beta)
            max_eval = max(max_eval, score)
            alpha    = max(alpha, score)
            if beta <= alpha: break

        if max_eval < beta:
            for (r, c, ori) in get_wall_candidates(state, is_ai_turn=True, max_candidates=MEDIUM_WALL_CANDIDATES):
                child    = state.apply_ai_wall(r, c, ori)
                score    = _minimax(child, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, score)
                alpha    = max(alpha, score)
                if beta <= alpha: break
        return max_eval
    else:
        min_eval = INF
        for dest in state.get_human_pawn_moves():
            child    = state.apply_human_move(dest)
            score    = _minimax(child, depth - 1, True, alpha, beta)
            min_eval = min(min_eval, score)
            beta     = min(beta, score)
            if beta <= alpha: break

        if min_eval > alpha:
            for (r, c, ori) in get_wall_candidates(state, is_ai_turn=False, max_candidates=MEDIUM_WALL_CANDIDATES):
                child    = state.apply_human_wall(r, c, ori)
                score    = _minimax(child, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, score)
                beta     = min(beta, score)
                if beta <= alpha: break
        return min_eval