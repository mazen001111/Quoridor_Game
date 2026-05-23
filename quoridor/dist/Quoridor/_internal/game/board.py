
import copy


class Board:
    """
    Represents the Quoridor game board.

    The board is a 9x9 grid of cells.
    Cells are identified by (row, col) where both range from 0 to 8.

    Walls are stored as sets of (row, col) tuples.
    Each wall tuple represents the TOP-LEFT anchor of a 2-cell-long wall.

    HORIZONTAL wall at (row, col):
        - Sits in the gap BELOW cells (row, col) and (row, col+1)
        - Blocks movement between row `row` and row `row+1`
          for columns `col` and `col+1`
        - Valid anchor positions: row 0–7, col 0–7

    VERTICAL wall at (row, col):
        - Sits in the gap to the RIGHT of cells (row, col) and (row+1, col)
        - Blocks movement between col `col` and col `col+1`
          for rows `row` and `row+1`
        - Valid anchor positions: row 0–7, col 0–7
    """

    # Constructor

    def __init__(self):
        """
        Creates a fresh, empty board with no walls placed.
        Called once at the start of every new game.
        """
        # A set of (row, col) tuples for every horizontal wall placed.
        # Example: {(3, 2), (5, 6)} means two horizontal walls are placed.
        self.horizontal_walls = set()

        # A set of (row, col) tuples for every vertical wall placed.
        self.vertical_walls = set()

    
    # Wall Placement — Public Methods (called by Game Manager)
    

    def place_wall(self, row, col, orientation):
        """
        Attempts to place a wall on the board.

        Parameters:
            row (int): Row of the wall anchor (0–7)
            col (int): Column of the wall anchor (0–7)
            orientation (str): 'H' for horizontal, 'V' for vertical

        Returns:
            True  — if the wall was placed successfully
            False — if the wall is out of bounds or overlaps an existing wall
                    (path-blocking check is done by the Game Manager, not here)

        Example usage:
            success = board.place_wall(3, 4, 'H')
            if not success:
                print("Cannot place wall there!")
        """
        if orientation == 'H':
            return self._place_horizontal_wall(row, col)
        elif orientation == 'V':
            return self._place_vertical_wall(row, col)
        else:
            # Invalid orientation string passed
            return False

    def remove_wall(self, row, col, orientation):
        """
        Removes a previously placed wall.
        Used by:
          - The Game Manager to undo a wall if pathfinding fails
          - The Bonus undo/redo feature

        Parameters:
            row (int): Row of the wall anchor
            col (int): Column of the wall anchor
            orientation (str): 'H' or 'V'

        Returns:
            True  — if the wall was found and removed
            False — if no wall existed at that position
        """
        if orientation == 'H':
            if (row, col) in self.horizontal_walls:
                self.horizontal_walls.remove((row, col))
                return True
            return False
        elif orientation == 'V':
            if (row, col) in self.vertical_walls:
                self.vertical_walls.remove((row, col))
                return True
            return False
        return False

    
    # Wall Placement — Private Helper
    

    def _place_horizontal_wall(self, row, col):
        """
        Internal method to validate and place a horizontal wall.

        A horizontal wall at (row, col) occupies the gap below:
            - cell (row, col)     → blocked edge 1
            - cell (row, col+1)  → blocked edge 2

        Overlap conditions:
            1. (row, col) is already in horizontal_walls
               → exact same wall already placed
            2. (row, col-1) is in horizontal_walls
               → a wall one slot to the left also covers (row, col)
            3. (row, col) is in vertical_walls
               → a vertical wall at the same anchor CROSSES this wall
        """
        # Check bounds: anchor must be in rows 0–7 and cols 0–7
        if not (0 <= row <= 7 and 0 <= col <= 7):
            return False

        # Check overlap with existing horizontal walls
        if (row, col) in self.horizontal_walls:
            return False  # exact duplicate
        if (row, col - 1) in self.horizontal_walls:
            return False  # wall to the left: its right edge overlaps our left edge
        if (row, col + 1) in self.horizontal_walls:
            return False  # wall to the right: its left edge overlaps our right edge

        # Check crossing with a vertical wall at the same anchor point
        if (row, col) in self.vertical_walls:
            return False  # walls would cross each other

        # All checks passed — place the wall
        self.horizontal_walls.add((row, col))
        return True

    def _place_vertical_wall(self, row, col):
        """
        Internal method to validate and place a vertical wall.

        A vertical wall at (row, col) occupies the gap to the right of:
            - cell (row,   col)  → blocked edge 1
            - cell (row+1, col)  → blocked edge 2

        Overlap conditions:
            1. (row, col) is already in vertical_walls
               → exact same wall already placed
            2. (row-1, col) is in vertical_walls
               → a wall one slot above also covers (row, col)
            3. (row, col) is in horizontal_walls
               → a horizontal wall at the same anchor CROSSES this wall
        """
        # Check bounds
        if not (0 <= row <= 7 and 0 <= col <= 7):
            return False

        # Check overlap with existing vertical walls
        if (row, col) in self.vertical_walls:
            return False  # exact duplicate
        if (row - 1, col) in self.vertical_walls:
            return False  # wall above: its lower edge overlaps our upper edge
        if (row + 1, col) in self.vertical_walls:
            return False  # wall below: its upper edge overlaps our lower edge

        # Check crossing with a horizontal wall at the same anchor point
        if (row, col) in self.horizontal_walls:
            return False  # walls would cross each other

        # All checks passed — place the wall
        self.vertical_walls.add((row, col))
        return True

    
    # Wall Query — Most Important Method in the Entire Project
    

    def is_wall_between(self, cell_a, cell_b):
        """
        Checks whether there is a wall blocking movement between two
        adjacent cells.

        This is called by:
          - Member 2 (pathfinder) to find valid pawn moves
          - Member 2 (BFS) to verify paths exist after wall placement
          - Member 4 (renderer) to draw walls correctly
          - Member 6 (AI) to evaluate board states

        Parameters:
            cell_a (tuple): (row, col) of the first cell
            cell_b (tuple): (row, col) of the second cell
                            Must be orthogonally adjacent to cell_a

        Returns:
            True  — movement is BLOCKED by a wall
            False — movement is FREE (no wall in the way)

        Example:
            board.is_wall_between((3, 4), (4, 4))
            → True if there's a horizontal wall blocking downward movement

        HOW IT WORKS:
        A horizontal wall at anchor (r, c) blocks the gap between
        row r and row r+1 for columns c and c+1.
        So to check if moving DOWN from (r, c) to (r+1, c) is blocked,
        we check if (r, c) OR (r, c-1) is in horizontal_walls.
        """
        r1, c1 = cell_a
        r2, c2 = cell_b

        # --- Moving DOWN: r2 = r1 + 1, c2 = c1 ---
        # Blocked by a horizontal wall whose anchor is at (r1, c1) or (r1, c1-1)
        if r2 == r1 + 1 and c2 == c1:
            return (r1, c1) in self.horizontal_walls or \
                   (r1, c1 - 1) in self.horizontal_walls

        # --- Moving UP: r2 = r1 - 1, c2 = c1 ---
        # The gap is between r2 and r1, so horizontal wall anchor is at (r2, ...)
        if r2 == r1 - 1 and c2 == c1:
            return (r2, c1) in self.horizontal_walls or \
                   (r2, c1 - 1) in self.horizontal_walls

        # --- Moving RIGHT: c2 = c1 + 1, r2 = r1 ---
        # Blocked by a vertical wall whose anchor is at (r1, c1) or (r1-1, c1)
        if c2 == c1 + 1 and r2 == r1:
            return (r1, c1) in self.vertical_walls or \
                   (r1 - 1, c1) in self.vertical_walls

        # --- Moving LEFT: c2 = c1 - 1, r2 = r1 ---
        # The gap is between c2 and c1, so vertical wall anchor is at (..., c2)
        if c2 == c1 - 1 and r2 == r1:
            return (r1, c2) in self.vertical_walls or \
                   (r1 - 1, c2) in self.vertical_walls

        # Cells are not adjacent — no wall concept applies
        return False

    
    # Board State Access — Used by Renderer, AI, Save/Load
    

    def get_horizontal_walls(self):
        """
        Returns a copy of the set of all placed horizontal wall anchors.
        Member 4 (renderer) uses this to know where to draw horizontal walls.
        Member 6 (AI) uses this to evaluate the board state.

        Returns:
            set of (row, col) tuples
        """
        return set(self.horizontal_walls)  # copy so no one can modify our internal set

    def get_vertical_walls(self):
        """
        Returns a copy of the set of all placed vertical wall anchors.

        Returns:
            set of (row, col) tuples
        """
        return set(self.vertical_walls)

    def get_all_walls(self):
        """
        Returns both wall sets as a dictionary.
        Useful for saving the game state to a file (Member 6 bonus feature).

        Returns:
            dict with keys 'horizontal' and 'vertical',
            each containing a list of [row, col] pairs
            (lists instead of sets because JSON doesn't support sets)

        Example return value:
            {
                'horizontal': [[3, 2], [5, 6]],
                'vertical':   [[1, 4]]
            }
        """
        return {
            'horizontal': [list(w) for w in self.horizontal_walls],
            'vertical':   [list(w) for w in self.vertical_walls]
        }

    def get_wall_count(self):
        """
        Returns the total number of walls currently on the board.
        Useful for debugging and for the AI.

        Returns:
            int — total number of placed walls (horizontal + vertical)
        """
        return len(self.horizontal_walls) + len(self.vertical_walls)

    
    # Board State Restoration — Used by Save/Load and Undo/Redo
    

    def load_walls(self, horizontal_list, vertical_list):
        """
        Restores walls from saved data.
        Called by the save/load system (Member 6 bonus feature).

        Parameters:
            horizontal_list: list of [row, col] pairs, e.g. [[3,2],[5,6]]
            vertical_list:   list of [row, col] pairs, e.g. [[1,4]]
        """
        self.horizontal_walls = set(tuple(w) for w in horizontal_list)
        self.vertical_walls = set(tuple(w) for w in vertical_list)

    def copy(self):
        """
        Returns a deep copy of this board.
        Used by the AI (Member 6) to simulate moves without
        affecting the real game board.

        Returns:
            A new Board object with the same walls as this one.

        Example:
            simulated_board = board.copy()
            simulated_board.place_wall(3, 4, 'H')
            # The real board is unchanged
        """
        new_board = Board()
        new_board.horizontal_walls = set(self.horizontal_walls)
        new_board.vertical_walls = set(self.vertical_walls)
        return new_board

    def reset(self):
        """
        Clears all walls from the board.
        Called when the game is reset (Member 3).
        """
        self.horizontal_walls = set()
        self.vertical_walls = set()

    
    # Validation Helpers — Used Internally and by Game Manager
    

    def is_valid_wall_position(self, row, col, orientation):
        """
        Checks if a wall CAN be placed at a position (bounds + overlap only).
        Does NOT check if it blocks paths — that's Member 2's job.

        This is useful for the UI (Member 5) to show which wall slots
        the player is even allowed to click on.

        Parameters:
            row (int): Row anchor
            col (int): Column anchor
            orientation (str): 'H' or 'V'

        Returns:
            True if placement is geometrically valid, False otherwise
        """
        # Save current state, attempt placement, then undo if needed
        if orientation == 'H':
            if not (0 <= row <= 7 and 0 <= col <= 7):
                return False
            if (row, col) in self.horizontal_walls:
                return False
            if (row, col - 1) in self.horizontal_walls:
                return False
            if (row, col) in self.vertical_walls:
                return False
            return True

        elif orientation == 'V':
            if not (0 <= row <= 7 and 0 <= col <= 7):
                return False
            if (row, col) in self.vertical_walls:
                return False
            if (row - 1, col) in self.vertical_walls:
                return False
            if (row, col) in self.horizontal_walls:
                return False
            return True

        return False

    def get_all_valid_wall_positions(self):
        """
        Returns all wall positions that are geometrically valid
        (not yet blocked by overlap — path check not included).

        Used by the AI (Member 6) to generate all possible wall moves.

        Returns:
            list of (row, col, orientation) tuples
        """
        valid = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_wall_position(row, col, 'H'):
                    valid.append((row, col, 'H'))
                if self.is_valid_wall_position(row, col, 'V'):
                    valid.append((row, col, 'V'))
        return valid

    
    # Debug Helper
    

    def print_board(self):
        """
        Prints a simple text representation of the board to the console.
        Useful for debugging without needing the full GUI.

        Legend:
            [ ] = empty cell
            --- = horizontal wall below this row
             |  = vertical wall to the right of this cell
        """
        print("\n=== BOARD STATE ===")
        for row in range(9):
            # Print the row of cells
            row_str = ""
            for col in range(9):
                row_str += "[ ]"
                # Check for vertical wall to the right
                if col < 8:
                    if self.is_wall_between((row, col), (row, col + 1)):
                        row_str += "|"
                    else:
                        row_str += " "
            print(row_str)

            # Print horizontal walls below this row
            if row < 8:
                wall_str = ""
                for col in range(9):
                    if self.is_wall_between((row, col), (row + 1, col)):
                        wall_str += "---"
                    else:
                        wall_str += "   "
                    if col < 8:
                        wall_str += " "
                print(wall_str)
        print("===================\n")