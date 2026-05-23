"""
ai_medium.py
------------
Medium difficulty AI for the Quoridor game.

Strategy
--------
Minimax with Alpha-Beta pruning at depth 3. Places walls and moves using a
BFS-based evaluation function. Wall candidates are filtered to only "useful"
ones (those that lengthen the opponent's path) to stay fast.

Public interface
----------------
    from ai_medium import medium_action

    action = medium_action(state)   # state is a _GameState instance
    # Returns: ("move", (row, col)) or ("wall", row, col, orientation)
"""

from __future__ import annotations
from typing import Optional, Tuple

from ai_player import _GameState, evaluate, get_wall_candidates, INF
from ai_easy   import easy_action

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------
Action = Tuple

# ---------------------------------------------------------------------------
# Medium-mode constants
# ---------------------------------------------------------------------------
MEDIUM_DEPTH           = 3
MEDIUM_WALL_CANDIDATES = 15


# ===========================================================================
# Medium mode — Minimax + Alpha-Beta, depth 3
# ===========================================================================

def medium_action(state: _GameState) -> Action:
    """
    Minimax with Alpha-Beta pruning at depth 3.

    The AI considers both pawn moves and wall placements.
    Wall candidates are filtered (only walls that lengthen the human's path).
    Falls back to easy_action if no action is found (shouldn't occur normally).
    """
    best_score  = -INF
    best_action: Optional[Action] = None
    alpha = -INF
    beta  =  INF

    # --- Pawn moves ---
    for dest in state.get_ai_pawn_moves():
        child = state.apply_ai_move(dest)
        score = _minimax(
            child, depth=MEDIUM_DEPTH - 1,
            is_maximizing=False,
            alpha=alpha, beta=beta,
        )
        if score > best_score:
            best_score  = score
            best_action = ("move", dest)
        alpha = max(alpha, best_score)

    # --- Wall placements ---
    for (r, c, ori) in get_wall_candidates(
        state, is_ai_turn=True, max_candidates=MEDIUM_WALL_CANDIDATES
    ):
        child = state.apply_ai_wall(r, c, ori)
        score = _minimax(
            child, depth=MEDIUM_DEPTH - 1,
            is_maximizing=False,
            alpha=alpha, beta=beta,
        )
        if score > best_score:
            best_score  = score
            best_action = ("wall", r, c, ori)
        alpha = max(alpha, best_score)

    # Fallback: if somehow nothing scored, just advance greedily
    if best_action is None:
        return easy_action(state)

    return best_action


# ===========================================================================
# Core Minimax with Alpha-Beta pruning (Medium variant)
# ===========================================================================

def _minimax(
    state: _GameState,
    depth: int,
    is_maximizing: bool,
    alpha: float,
    beta: float,
) -> float:
    """
    Minimax search with Alpha-Beta pruning (no time limit).

    Parameters
    ----------
    state         : current game state snapshot
    depth         : remaining search depth (0 = evaluate immediately)
    is_maximizing : True on the AI's turn, False on the human's turn
    alpha         : best score the maximizer can guarantee so far
    beta          : best score the minimizer can guarantee so far

    Returns
    -------
    float — the heuristic value of the state from the AI's perspective
    """
    if state.is_terminal() or depth == 0:
        return evaluate(state)

    if is_maximizing:
        max_eval = -INF

        # Pawn moves
        for dest in state.get_ai_pawn_moves():
            child    = state.apply_ai_move(dest)
            score    = _minimax(child, depth - 1, False, alpha, beta)
            max_eval = max(max_eval, score)
            alpha    = max(alpha, score)
            if beta <= alpha:
                break  # Beta cut-off

        # Wall placements (only if we haven't already cut off)
        if max_eval < beta:
            for (r, c, ori) in get_wall_candidates(
                state, is_ai_turn=True, max_candidates=MEDIUM_WALL_CANDIDATES
            ):
                child    = state.apply_ai_wall(r, c, ori)
                score    = _minimax(child, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, score)
                alpha    = max(alpha, score)
                if beta <= alpha:
                    break

        return max_eval

    else:
        min_eval = INF

        # Pawn moves
        for dest in state.get_human_pawn_moves():
            child    = state.apply_human_move(dest)
            score    = _minimax(child, depth - 1, True, alpha, beta)
            min_eval = min(min_eval, score)
            beta     = min(beta, score)
            if beta <= alpha:
                break  # Alpha cut-off

        # Wall placements
        if min_eval > alpha:
            for (r, c, ori) in get_wall_candidates(
                state, is_ai_turn=False, max_candidates=MEDIUM_WALL_CANDIDATES
            ):
                child    = state.apply_human_wall(r, c, ori)
                score    = _minimax(child, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, score)
                beta     = min(beta, score)
                if beta <= alpha:
                    break

        return min_eval