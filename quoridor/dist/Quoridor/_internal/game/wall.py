# wall.py
# Defines the Wall data class and wall-related constants.
# This is a simple data container — the actual placement logic is in board.py

# No external libraries needed.
# We use Python's built-in dataclasses module to create a clean Wall object.
from dataclasses import dataclass


# Constants — shared across the entire project

# Board dimensions
BOARD_SIZE = 9          # 9x9 cells
WALL_GRID_SIZE = 8      # 8x8 possible wall anchor positions (0 to 7)

# Each player starts with this many walls
INITIAL_WALL_COUNT = 10

# Wall orientations — use these constants everywhere instead of raw strings
HORIZONTAL = 'H'
VERTICAL = 'V'


# Wall Data Class

@dataclass
class Wall:
    """
    Represents a single placed wall on the board.

    This is a pure data object — it just stores information about
    where a wall is and what orientation it has.
    It does NOT contain any logic. Logic lives in board.py.

    Attributes:
        row (int):         Row of the wall's anchor point (0–7)
        col (int):         Column of the wall's anchor point (0–7)
        orientation (str): 'H' for horizontal, 'V' for vertical

    Why do we need this class?
        - The Board stores walls as a set of (row, col) tuples
          per orientation. That's efficient for lookups.
        - But sometimes we need to pass a wall around as a single
          object (e.g., the AI says "place this wall", the undo
          system records "this wall was placed"). The Wall class
          makes that clean.

    Example:
        w = Wall(row=3, col=4, orientation='H')
        board.place_wall(w.row, w.col, w.orientation)
    """
    row: int
    col: int
    orientation: str

    def is_horizontal(self):
        """Returns True if this is a horizontal wall."""
        return self.orientation == HORIZONTAL

    def is_vertical(self):
        """Returns True if this is a vertical wall."""
        return self.orientation == VERTICAL

    def is_valid_position(self):
        """
        Checks if this wall's anchor is within the valid placement grid.
        Valid anchors: row 0–7, col 0–7.

        Note: This only checks bounds. It does NOT check overlaps or
        path blocking — that's board.py's job.

        Returns:
            True if the anchor is within bounds, False otherwise.
        """
        return (0 <= self.row <= WALL_GRID_SIZE - 1 and
                0 <= self.col <= WALL_GRID_SIZE - 1 and
                self.orientation in (HORIZONTAL, VERTICAL))

    def to_tuple(self):
        """
        Converts this Wall to a (row, col, orientation) tuple.
        Useful for storing in lists or passing to functions that
        expect tuples instead of Wall objects.

        Returns:
            tuple: (row, col, orientation)

        Example:
            w = Wall(3, 4, 'H')
            w.to_tuple()  →  (3, 4, 'H')
        """
        return (self.row, self.col, self.orientation)

    def to_dict(self):
        """
        Converts this Wall to a dictionary.
        Used by the save/load system (Member 6) to serialize to JSON.

        Returns:
            dict: {'row': int, 'col': int, 'orientation': str}

        Example:
            w = Wall(3, 4, 'H')
            w.to_dict()  →  {'row': 3, 'col': 4, 'orientation': 'H'}
        """
        return {
            'row': self.row,
            'col': self.col,
            'orientation': self.orientation
        }

    @staticmethod
    def from_dict(data):
        """
        Creates a Wall object from a dictionary.
        Used by the save/load system (Member 6) when loading from JSON.

        Parameters:
            data (dict): {'row': int, 'col': int, 'orientation': str}

        Returns:
            Wall object

        Example:
            data = {'row': 3, 'col': 4, 'orientation': 'H'}
            w = Wall.from_dict(data)
        """
        return Wall(
            row=data['row'],
            col=data['col'],
            orientation=data['orientation']
        )

    def __repr__(self):
        """
        String representation for debugging.
        When you print a Wall object, this is what you see.

        Example:
            w = Wall(3, 4, 'H')
            print(w)  →  Wall(H @ row=3, col=4)
        """
        name = "Horizontal" if self.is_horizontal() else "Vertical"
        return f"Wall({name} @ row={self.row}, col={self.col})"


# Utility Functions

def get_cells_blocked_by_wall(wall):
    """
    Returns the two cell-edge pairs that a wall blocks.

    This is useful for:
        - The renderer (Member 4) to know exactly where to draw the wall
        - Debugging to understand what a wall does

    Parameters:
        wall (Wall): A Wall object

    Returns:
        list of two tuples, each being (cell_a, cell_b) where
        cell_a and cell_b are adjacent cells with the wall between them.

    Example:
        wall = Wall(row=3, col=4, orientation='H')
        get_cells_blocked_by_wall(wall)
        → [((3,4), (4,4)),   ← wall blocks movement between row 3 and row 4 at col 4
           ((3,5), (4,5))]   ← and at col 5
    """
    if wall.is_horizontal():
        # Horizontal wall at (row, col) blocks:
        # - gap between (row, col)   and (row+1, col)
        # - gap between (row, col+1) and (row+1, col+1)
        return [
            ((wall.row, wall.col),     (wall.row + 1, wall.col)),
            ((wall.row, wall.col + 1), (wall.row + 1, wall.col + 1))
        ]
    else:
        # Vertical wall at (row, col) blocks:
        # - gap between (row,   col) and (row,   col+1)
        # - gap between (row+1, col) and (row+1, col+1)
        return [
            ((wall.row,     wall.col), (wall.row,     wall.col + 1)),
            ((wall.row + 1, wall.col), (wall.row + 1, wall.col + 1))
        ]


def walls_would_cross(wall_a, wall_b):
    """
    Checks if two walls would cross each other.

    Two walls cross if and only if:
        - They have DIFFERENT orientations
        - They share the SAME anchor point (row, col)

    Parameters:
        wall_a (Wall): First wall
        wall_b (Wall): Second wall

    Returns:
        True if the walls would cross, False otherwise

    Example:
        a = Wall(3, 4, 'H')
        b = Wall(3, 4, 'V')
        walls_would_cross(a, b)  →  True   (same anchor, different orientation)

        a = Wall(3, 4, 'H')
        b = Wall(3, 5, 'V')
        walls_would_cross(a, b)  →  False  (different anchor)
    """
    if wall_a.orientation == wall_b.orientation:
        return False  # Same orientation walls can overlap but not cross
    return wall_a.row == wall_b.row and wall_a.col == wall_b.col


def walls_would_overlap(wall_a, wall_b):
    """
    Checks if two walls of the SAME orientation would overlap.

    Two horizontal walls overlap if they share the same row and
    their columns differ by exactly 1 (they share one edge slot).
    Same logic applies to vertical walls.

    Parameters:
        wall_a (Wall): First wall
        wall_b (Wall): Second wall

    Returns:
        True if the walls overlap, False otherwise

    Example:
        a = Wall(3, 4, 'H')
        b = Wall(3, 5, 'H')
        walls_would_overlap(a, b)  →  True  (adjacent horizontal walls share a slot)

        a = Wall(3, 4, 'H')
        b = Wall(3, 6, 'H')
        walls_would_overlap(a, b)  →  False (too far apart)
    """
    if wall_a.orientation != wall_b.orientation:
        return False  # Different orientations handled by walls_would_cross

    if wall_a.orientation == HORIZONTAL:
        # Same row, columns differ by 1
        return wall_a.row == wall_b.row and abs(wall_a.col - wall_b.col) <= 1

    else:  # VERTICAL
        # Same col, rows differ by 1
        return wall_a.col == wall_b.col and abs(wall_a.row - wall_b.row) <= 1