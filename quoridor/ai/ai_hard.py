"""
ai_hard.py
----------
Hard difficulty AI for the Quoridor game.

Strategy
--------
Minimax with Alpha-Beta pruning + iterative deepening up to depth 5.
Smarter wall candidate selection: only considers walls that actually
lengthen the opponent's BFS path. Much stronger opponent than Medium.

The search also uses move ordering (pawn moves sorted by BFS distance to
goal) to improve Alpha-Beta cut-offs.

Public interface
----------------
    from ai_hard import hard_action

    action = hard_action(state)   # state is a _GameState instance
    # Returns: ("move", (row, col)) or ("wall", row, col, orientation)
"""

from __future__ import annotations
import time
from typing import Optional, Tuple

from game.pathfinder import bfs_distance
from ai_player import _GameState, evaluate, get_wall_candidates, INF
from ai_easy   import easy_action

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------
Action = Tuple

# ---------------------------------------------------------------------------
# Hard-mode constants
# ---------------------------------------------------------------------------
HARD_DEPTH           = 5
HARD_WALL_CANDIDATES = 20
HARD_TIME_BUDGET     = 2.0   # seconds


# ===========================================================================
# Hard mode — Minimax + Alpha-Beta + Iterative Deepening
# ===========================================================================

def hard_action(state: _GameState) -> Action:
    """
    Iterative deepening Minimax with Alpha-Beta pruning.

    We run the search at depth 1, then 2, … up to HARD_DEPTH,
    stopping early if we exceed HARD_TIME_BUDGET seconds.
    The best action from the deepest completed search is returned.

    Falls back to easy_action if time ran out before depth 1 finished.
    """
    deadline    = time.time() + HARD_TIME_BUDGET
    best_action: Optional[Action] = None

    for depth in range(1, HARD_DEPTH + 1):
        if time.time() >= deadline:
            break

        action = _root_search(state, depth, deadline)

        if action is not None:
            best_action = action

        if time.time() >= deadline:
            break

    if best_action is None:
        # Time ran out before completing depth 1 — fall back to greedy
        return easy_action(state)

    return best_action


# ===========================================================================
# Root search for one depth level
# ===========================================================================

def _root_search(
    state: _GameState,
    depth: int,
    deadline: float,
) -> Optional[Action]:
    """
    Run one full Minimax search at the given depth.

    Returns the best action found, or None if time ran out mid-search.
    Uses move ordering on pawn moves (closest to goal first) to help
    Alpha-Beta prune more aggressively.
    """
    best_score  = -INF
    best_action: Optional[Action] = None
    alpha = -INF
    beta  =  INF

    # --- Pawn moves first; sort by proximity to goal for better pruning ---
    pawn_moves = state.get_ai_pawn_moves()
    pawn_moves.sort(
        key=lambda pos: bfs_distance(pos, state.ai_goal, state.board)
    )

    for dest in pawn_moves:
        if time.time() >= deadline:
            return best_action  # return whatever we have so far

        child = state.apply_ai_move(dest)
        score = _minimax(
            child, depth=depth - 1,
            is_maximizing=False,
            alpha=alpha, beta=beta,
            deadline=deadline,
        )
        if score > best_score:
            best_score  = score
            best_action = ("move", dest)
        alpha = max(alpha, best_score)
        if beta <= alpha:
            break

    # --- Wall placements ---
    for (r, c, ori) in get_wall_candidates(
        state, is_ai_turn=True, max_candidates=HARD_WALL_CANDIDATES
    ):
        if time.time() >= deadline:
            return best_action

        child = state.apply_ai_wall(r, c, ori)
        score = _minimax(
            child, depth=depth - 1,
            is_maximizing=False,
            alpha=alpha, beta=beta,
            deadline=deadline,
        )
        if score > best_score:
            best_score  = score
            best_action = ("wall", r, c, ori)
        alpha = max(alpha, best_score)
        if beta <= alpha:
            break

    return best_action


# ===========================================================================
# Core Minimax with Alpha-Beta pruning (Hard variant — time-aware)
# ===========================================================================

def _minimax(
    state: _GameState,
    depth: int,
    is_maximizing: bool,
    alpha: float,
    beta: float,
    deadline: float,
) -> float:
    """
    Minimax search with Alpha-Beta pruning and a time deadline.

    Parameters
    ----------
    state         : current game state snapshot
    depth         : remaining search depth (0 = evaluate immediately)
    is_maximizing : True on the AI's turn, False on the human's turn
    alpha         : best score the maximizer can guarantee so far
    beta          : best score the minimizer can guarantee so far
    deadline      : wall-clock time at which we must stop and evaluate

    Returns
    -------
    float — the heuristic value of the state from the AI's perspective
    """
    # Time check — return static eval if we're out of time
    if time.time() >= deadline:
        return evaluate(state)

    if state.is_terminal() or depth == 0:
        return evaluate(state)

    if is_maximizing:
        max_eval = -INF

        # Pawn moves
        for dest in state.get_ai_pawn_moves():
            child    = state.apply_ai_move(dest)
            score    = _minimax(child, depth - 1, False, alpha, beta, deadline)
            max_eval = max(max_eval, score)
            alpha    = max(alpha, score)
            if beta <= alpha:
                break  # Beta cut-off

        # Wall placements (only if we haven't already cut off)
        if max_eval < beta:
            for (r, c, ori) in get_wall_candidates(
                state, is_ai_turn=True, max_candidates=HARD_WALL_CANDIDATES
            ):
                child    = state.apply_ai_wall(r, c, ori)
                score    = _minimax(child, depth - 1, False, alpha, beta, deadline)
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
            score    = _minimax(child, depth - 1, True, alpha, beta, deadline)
            min_eval = min(min_eval, score)
            beta     = min(beta, score)
            if beta <= alpha:
                break  # Alpha cut-off

        # Wall placements
        if min_eval > alpha:
            for (r, c, ori) in get_wall_candidates(
                state, is_ai_turn=False, max_candidates=HARD_WALL_CANDIDATES
            ):
                child    = state.apply_human_wall(r, c, ori)
                score    = _minimax(child, depth - 1, True, alpha, beta, deadline)
                min_eval = min(min_eval, score)
                beta     = min(beta, score)
                if beta <= alpha:
                    break

        return min_eval