"""
game_manager.py
---------------
Controls the overall Quoridor game state.

Undo / Redo
-----------
Every successful pawn move or wall placement pushes a full snapshot onto
_history before changing anything.  Undo pops the top snapshot and pushes
the current state onto _redo_stack.  Redo does the reverse.
Any new action clears _redo_stack so the tree stays linear.

Keys (wired in event_handler.py):
    U — undo last action
    P — redo last undone action
"""

from game.board import Board
from game.pawn import Pawn
from game.pathfinder import get_valid_moves, bfs_path_exists
from ai.ai_player import get_ai_action

# Maximum number of states to keep in the undo history (memory guard)
_MAX_HISTORY = 100


class GameManager:

    def __init__(self, mode="hvh", ai_difficulty=None):
        self.mode           = mode
        self.ai_difficulty  = ai_difficulty
        self.board          = Board()
        self.pawns = {
            1: Pawn(start_pos=(8, 4), goal_row=0, player_id=1),
            2: Pawn(start_pos=(0, 4), goal_row=8, player_id=2),
        }
        self.current_player = 1
        self.game_over      = False
        self.winner         = None
        self.message        = "Player 1's turn"

        # Undo / Redo stacks — each entry is a dict from _snapshot()
        self._history    = []   # past states  (undo source)
        self._redo_stack = []   # future states (redo source)

    # ------------------------------------------------------------------
    # Snapshot helpers  (private)
    # ------------------------------------------------------------------

    def _snapshot(self) -> dict:
        """Return a deep copy of every piece of mutable game state."""
        return {
            "current_player": self.current_player,
            "game_over":      self.game_over,
            "winner":         self.winner,
            "message":        self.message,
            "pawns": {
                1: {
                    "position":        self.pawns[1].position,
                    "walls_remaining": self.pawns[1].walls_remaining,
                },
                2: {
                    "position":        self.pawns[2].position,
                    "walls_remaining": self.pawns[2].walls_remaining,
                },
            },
            "horizontal_walls": set(self.board.horizontal_walls),
            "vertical_walls":   set(self.board.vertical_walls),
        }

    def _restore(self, snap: dict) -> None:
        """Overwrite the live state with a previously captured snapshot."""
        self.current_player = snap["current_player"]
        self.game_over      = snap["game_over"]
        self.winner         = snap["winner"]
        self.message        = snap["message"]

        for pid in (1, 2):
            self.pawns[pid].position        = snap["pawns"][pid]["position"]
            self.pawns[pid].walls_remaining = snap["pawns"][pid]["walls_remaining"]

        self.board.horizontal_walls = set(snap["horizontal_walls"])
        self.board.vertical_walls   = set(snap["vertical_walls"])

    def _push_history(self) -> None:
        """Save current state before a destructive action."""
        self._history.append(self._snapshot())
        if len(self._history) > _MAX_HISTORY:
            self._history.pop(0)

    # ------------------------------------------------------------------
    # Public undo / redo
    # ------------------------------------------------------------------

    def undo(self) -> bool:
        """
        Revert the last action.
        In HvC mode, pops twice so the human undoes their own move (not just
        the AI's response that immediately followed it).
        Returns True if an undo was available, False if already at start.
        """
        if not self._history:
            self.message = "Nothing to undo."
            return False

        # In AI mode the history contains pairs: [human_action, ai_action].
        # Popping once would land on the AI's turn and trigger another AI move
        # immediately.  Pop twice so we land back on the human's turn.
        if self.mode == "hvc" and len(self._history) >= 2:
            # Save current state for redo, then skip the AI half-turn too.
            self._redo_stack.append(self._snapshot())   # current  (post-AI)
            ai_snap = self._history.pop()               # pre-AI   (post-human)
            self._redo_stack.append(ai_snap)            # also keep for redo
            self._restore(self._history.pop())          # pre-human
        else:
            self._redo_stack.append(self._snapshot())
            self._restore(self._history.pop())

        self.message = "Undo!"
        return True

    def redo(self) -> bool:
        """
        Re-apply the last undone action.
        In HvC mode, pushes twice to restore both the human and AI half-turns.
        Returns True if a redo was available, False if redo stack is empty.
        """
        if not self._redo_stack:
            self.message = "Nothing to redo."
            return False

        # Mirror of undo: in AI mode the redo stack holds two entries per
        # logical turn (the post-human state and the post-AI state).
        if self.mode == "hvc" and len(self._redo_stack) >= 2:
            self._history.append(self._snapshot())          # current (pre-human)
            human_snap = self._redo_stack.pop()             # post-human / pre-AI
            self._history.append(human_snap)               # keep for undo
            self._restore(self._redo_stack.pop())           # post-AI
        else:
            self._history.append(self._snapshot())
            self._restore(self._redo_stack.pop())

        self.message = "Redo!"
        return True

    # ------------------------------------------------------------------
    # Basic helpers
    # ------------------------------------------------------------------

    def other_player(self):
        return 2 if self.current_player == 1 else 1

    def switch_turn(self):
        if self.game_over:
            return
        self.current_player = self.other_player()
        self.message = f"Player {self.current_player}'s turn"

    def get_current_pawn(self):
        return self.pawns[self.current_player]

    def get_opponent_pawn(self):
        return self.pawns[self.other_player()]

    # ------------------------------------------------------------------
    # Pawn movement
    # ------------------------------------------------------------------

    def get_current_valid_moves(self):
        return get_valid_moves(
            self.get_current_pawn().position,
            self.get_opponent_pawn().position,
            self.board,
        )

    def handle_pawn_move(self, destination):
        if self.game_over:
            self.message = "Game is already over."
            return False

        if destination not in self.get_current_valid_moves():
            self.message = "Invalid pawn move."
            return False

        # Snapshot BEFORE mutating — redo history wiped on new action
        self._push_history()
        self._redo_stack.clear()

        self.get_current_pawn().move_to(destination)

        if self.check_win_condition():
            return True

        self.switch_turn()
        return True

    # ------------------------------------------------------------------
    # Wall placement
    # ------------------------------------------------------------------

    def handle_wall_placement(self, row, col, orientation):
        if self.game_over:
            self.message = "Game is already over."
            return False

        current_pawn = self.get_current_pawn()

        if not current_pawn.has_walls():
            self.message = f"Player {self.current_player} has no walls left."
            return False

        # Geometry check
        placed = self.board.place_wall(row, col, orientation)
        if not placed:
            self.message = "Invalid wall placement."
            return False

        # Path check
        if not self.paths_exist_for_both_players():
            self.board.remove_wall(row, col, orientation)
            self.message = "Invalid wall: it blocks all paths."
            return False

        # Wall is valid. Remove it temporarily, snapshot the pre-wall state,
        # then re-place — this keeps the snapshot clean (no wall yet).
        self.board.remove_wall(row, col, orientation)
        self._push_history()
        self._redo_stack.clear()
        self.board.place_wall(row, col, orientation)

        current_pawn.place_wall()
        self.message = f"Player {self.current_player} placed a wall."
        self.switch_turn()
        return True

    def paths_exist_for_both_players(self):
        p1, p2 = self.pawns[1], self.pawns[2]
        return (
            bfs_path_exists(p1.position, p1.goal_row, self.board, p2.position) and
            bfs_path_exists(p2.position, p2.goal_row, self.board, p1.position)
        )

    # ------------------------------------------------------------------
    # Win condition and reset
    # ------------------------------------------------------------------

    def check_win_condition(self):
        current_pawn = self.get_current_pawn()
        if current_pawn.has_won():
            self.game_over = True
            self.winner    = self.current_player
            self.message   = f"Player {self.current_player} wins!"
            return True
        return False

    def reset_game(self):
        old_mode       = self.mode
        old_difficulty = self.ai_difficulty
        self.__init__(mode=old_mode, ai_difficulty=old_difficulty)

    # ------------------------------------------------------------------
    # AI support
    # ------------------------------------------------------------------

    def is_ai_turn(self):
        return self.mode == "hvc" and self.current_player == 2 and not self.game_over

    def handle_ai_turn(self):
        if not self.is_ai_turn():
            return False
        action = get_ai_action(self)
        if action[0] == "move":
            return self.handle_pawn_move(action[1])
        elif action[0] == "wall":
            _, r, c, ori = action
            return self.handle_wall_placement(r, c, ori)
        return True

    # ------------------------------------------------------------------
    # State access for UI
    # ------------------------------------------------------------------

    def get_state(self):
        return self