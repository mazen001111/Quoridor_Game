"""
game_manager.py
---------------
Controls the overall Quoridor game state.

This module is responsible for:
- Creating the board and pawns
- Managing turns
- Handling pawn movement
- Handling wall placement
- Checking win conditions
- Resetting the game
- Connecting later with the AI player
"""

from game.board import Board
from game.pawn import Pawn
from game.pathfinder import get_valid_moves, bfs_path_exists


class GameManager:
    """
    Central controller for the Quoridor game.

    The GameManager does not draw the board and does not handle mouse clicks.
    It only manages the rules and the game state.

    Other modules should talk to this class.
    For example:
        event_handler.py asks GameManager to move a pawn or place a wall.
        renderer.py reads GameManager state to draw the game.
        ai_player.py can read the state and return an action.
    """

    def __init__(self, mode="hvh", ai_difficulty=None):
        """
        Create a new game.

        Parameters
        ----------
        mode : str
            "hvh" = Human vs Human
            "hvc" = Human vs Computer

        ai_difficulty : str or None
            None, "easy", "medium", or "hard"
        """
        self.mode = mode
        self.ai_difficulty = ai_difficulty

        self.board = Board()

        self.pawns = {
            1: Pawn(start_pos=(8, 4), goal_row=0, player_id=1),
            2: Pawn(start_pos=(0, 4), goal_row=8, player_id=2)
        }

        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.message = "Player 1's turn"

    # ------------------------------------------------------------------
    # Basic helper methods
    # ------------------------------------------------------------------

    def other_player(self):
        """Return the opponent of the current player."""
        return 2 if self.current_player == 1 else 1

    def switch_turn(self):
        """Switch turn from Player 1 to Player 2, or Player 2 to Player 1."""
        if self.game_over:
            return

        self.current_player = self.other_player()
        self.message = f"Player {self.current_player}'s turn"

    def get_current_pawn(self):
        """Return the Pawn object for the current player."""
        return self.pawns[self.current_player]

    def get_opponent_pawn(self):
        """Return the Pawn object for the opponent."""
        return self.pawns[self.other_player()]

    # ------------------------------------------------------------------
    # Pawn movement
    # ------------------------------------------------------------------

    def get_current_valid_moves(self):
        """
        Return all legal pawn moves for the current player.
        Used by the UI for move highlighting.
        """
        current_pawn = self.get_current_pawn()
        opponent_pawn = self.get_opponent_pawn()

        return get_valid_moves(
            current_pawn.position,
            opponent_pawn.position,
            self.board
        )

    def handle_pawn_move(self, destination):
        """
        Try to move the current player's pawn.

        Parameters
        ----------
        destination : tuple
            Target cell as (row, col)

        Returns
        -------
        bool
            True if the move was successful.
            False if the move was illegal.
        """
        if self.game_over:
            self.message = "Game is already over."
            return False

        valid_moves = self.get_current_valid_moves()

        if destination not in valid_moves:
            self.message = "Invalid pawn move."
            return False

        current_pawn = self.get_current_pawn()
        current_pawn.move_to(destination)

        if self.check_win_condition():
            return True

        self.switch_turn()
        return True

    # ------------------------------------------------------------------
    # Wall placement
    # ------------------------------------------------------------------

    def handle_wall_placement(self, row, col, orientation):
        """
        Try to place a wall for the current player.

        Parameters
        ----------
        row : int
            Wall anchor row.

        col : int
            Wall anchor column.

        orientation : str
            'H' for horizontal or 'V' for vertical.

        Returns
        -------
        bool
            True if the wall was placed.
            False if the wall was illegal.
        """
        if self.game_over:
            self.message = "Game is already over."
            return False

        current_pawn = self.get_current_pawn()

        if not current_pawn.has_walls():
            self.message = f"Player {self.current_player} has no walls left."
            return False

        # First, ask Board if this wall is geometrically valid.
        placed = self.board.place_wall(row, col, orientation)

        if not placed:
            self.message = "Invalid wall placement."
            return False

        # Then check the important Quoridor rule:
        # both players must still have at least one path to their goal.
        if not self.paths_exist_for_both_players():
            self.board.remove_wall(row, col, orientation)
            self.message = "Invalid wall: it blocks all paths."
            return False

        # Wall is legal, so reduce current player's wall count.
        current_pawn.place_wall()

        self.message = f"Player {self.current_player} placed a wall."

        self.switch_turn()
        return True

    def paths_exist_for_both_players(self):
        """
        Check that both players still have a valid path to their goal row.

        This is required after every wall placement.
        """
        p1 = self.pawns[1]
        p2 = self.pawns[2]

        p1_has_path = bfs_path_exists(
            start=p1.position,
            goal_row=p1.goal_row,
            board=self.board,
            opponent_pos=p2.position
        )

        p2_has_path = bfs_path_exists(
            start=p2.position,
            goal_row=p2.goal_row,
            board=self.board,
            opponent_pos=p1.position
        )

        return p1_has_path and p2_has_path

    # ------------------------------------------------------------------
    # Win condition and reset
    # ------------------------------------------------------------------

    def check_win_condition(self):
        """
        Check if the current player has reached their goal row.
        """
        current_pawn = self.get_current_pawn()

        if current_pawn.has_won():
            self.game_over = True
            self.winner = self.current_player
            self.message = f"Player {self.current_player} wins!"
            return True

        return False

    def reset_game(self):
        """
        Reset the whole game while keeping the selected mode and AI difficulty.
        """
        old_mode = self.mode
        old_difficulty = self.ai_difficulty
        self.__init__(mode=old_mode, ai_difficulty=old_difficulty)

    # ------------------------------------------------------------------
    # AI support
    # ------------------------------------------------------------------

    def is_ai_turn(self):
        """
        Return True if the current turn belongs to the AI.

        In this project, the AI is Player 2 in Human vs Computer mode.
        """
        return self.mode == "hvc" and self.current_player == 2 and not self.game_over

    def handle_ai_turn(self):
        """
        Ask the AI for a move and apply it.

        This is a placeholder until Member 6 implements ai_player.py.
        Later, ai_player.py should return actions like:
            ("move", (row, col))
            ("wall", row, col, orientation)
        """
        if not self.is_ai_turn():
            return False

        # TODO: Connect this when ai_player.py is implemented.
        self.message = "AI turn logic is not implemented yet."
        return False

    # ------------------------------------------------------------------
    # State access for UI
    # ------------------------------------------------------------------

    def get_state(self):
        """
        Return self so the renderer/UI can read the current game state.

        This allows code like:
            state = manager.get_state()
            state.board
            state.pawns
            state.current_player
        """
        return self  # Turn management and win condition handling.

