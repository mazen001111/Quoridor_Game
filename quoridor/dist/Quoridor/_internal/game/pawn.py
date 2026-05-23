"""
pawn.py
-------
Stores a player's pawn state: current position and the goal row
they must reach to win.

Coordinate system
-----------------
Rows and columns are 0-indexed integers in the range [0, 8].
Row 0 is the top edge; row 8 is the bottom edge.

  Player 1 starts at (row=8, col=4)  →  goal_row = 0
  Player 2 starts at (row=0, col=4)  →  goal_row = 8
"""


class Pawn:
    """Represents a Quoridor pawn for one player.

    Attributes
    ----------
    position : tuple[int, int]
        Current (row, col) of the pawn on the 9×9 board.
    goal_row : int
        The row the pawn must reach (0 or 8) to win.
    walls_remaining : int
        How many walls this player still has to place (starts at 10).
    player_id : int
        1 or 2 – used for display / logging purposes.
    """

    def __init__(self, start_pos: tuple, goal_row: int,
                 player_id: int, walls: int = 10):
        """
        Parameters
        ----------
        start_pos    : (row, col) starting position
        goal_row     : row index the pawn must reach to win
        player_id    : 1 or 2
        walls        : number of walls the player starts with (default 10)
        """
        if not (isinstance(start_pos, tuple) and len(start_pos) == 2):
            raise ValueError("start_pos must be a (row, col) tuple")
        r, c = start_pos
        if not (0 <= r <= 8 and 0 <= c <= 8):
            raise ValueError(f"start_pos {start_pos} is off the 9×9 board")
        if goal_row not in (0, 8):
            raise ValueError("goal_row must be 0 or 8")

        self.position: tuple = start_pos
        self.goal_row: int = goal_row
        self.walls_remaining: int = walls
        self.player_id: int = player_id

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def row(self) -> int:
        """Current row of the pawn."""
        return self.position[0]

    @property
    def col(self) -> int:
        """Current column of the pawn."""
        return self.position[1]

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    def has_won(self) -> bool:
        """Return True if the pawn has reached its goal row."""
        return self.row == self.goal_row

    def has_walls(self) -> bool:
        """Return True if the player still has walls to place."""
        return self.walls_remaining > 0

    # ------------------------------------------------------------------
    # Mutation helpers  (called by the game engine, not directly by AI)
    # ------------------------------------------------------------------

    def move_to(self, new_pos: tuple) -> None:
        """Move the pawn to *new_pos* (no legality check here)."""
        self.position = new_pos

    def place_wall(self) -> None:
        """Decrement wall count when a wall is placed."""
        if self.walls_remaining <= 0:
            raise ValueError(f"Player {self.player_id} has no walls left")
        self.walls_remaining -= 1

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (f"Pawn(player={self.player_id}, pos={self.position}, "
                f"goal_row={self.goal_row}, walls={self.walls_remaining})")