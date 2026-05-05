"""Mouse and keyboard input handling."""
import pygame


CELL_SIZE = 60
GAP = 10
BOARD_OFFSET_X = 85
BOARD_OFFSET_Y = 90


class EventHandler:
    def __init__(self, manager):
        self.manager = manager

        self.mode = "move"
        self.selected_pawn = False
        self.valid_moves = []

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_click(event.pos)

        elif event.type == pygame.KEYDOWN:
            self.handle_key(event.key)

    def handle_key(self, key):
        if key == pygame.K_w:
            if self.mode == "move":
                self.mode = "wall"
                self.selected_pawn = False
                self.valid_moves = []
                self.manager.message = "Wall mode: click a wall slot."
            else:
                self.mode = "move"
                self.manager.message = "Move mode: click your pawn."

        elif key == pygame.K_r:
            self.manager.reset_game()
            self.selected_pawn = False
            self.valid_moves = []

    def handle_click(self, mouse_pos):
        if self.manager.game_over:
            return

        if self.mode == "move":
            self.handle_move_click(mouse_pos)

        elif self.mode == "wall":
            self.handle_wall_click(mouse_pos)

    def handle_move_click(self, mouse_pos):
        cell = self.pixel_to_cell(mouse_pos)

        if cell is None:
            return

        current_pawn_pos = self.manager.get_current_pawn().position

        if cell == current_pawn_pos:
            self.selected_pawn = True
            self.valid_moves = self.manager.get_current_valid_moves()
            self.manager.message = "Choose a highlighted cell."
            return

        if self.selected_pawn and cell in self.valid_moves:
            self.manager.handle_pawn_move(cell)
            self.selected_pawn = False
            self.valid_moves = []
            return

        self.selected_pawn = False
        self.valid_moves = []
        self.manager.message = "Click your pawn first."

    def handle_wall_click(self, mouse_pos):
        wall = self.pixel_to_wall_slot(mouse_pos)

        if wall is None:
            self.manager.message = "Click between cells to place a wall."
            return

        row, col, orientation = wall
        self.manager.handle_wall_placement(row, col, orientation)

    def pixel_to_cell(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos

        x = mouse_x - BOARD_OFFSET_X
        y = mouse_y - BOARD_OFFSET_Y

        if x < 0 or y < 0:
            return None

        col = x // (CELL_SIZE + GAP)
        row = y // (CELL_SIZE + GAP)

        x_inside = x % (CELL_SIZE + GAP)
        y_inside = y % (CELL_SIZE + GAP)

        if 0 <= row <= 8 and 0 <= col <= 8:
            if x_inside < CELL_SIZE and y_inside < CELL_SIZE:
                return int(row), int(col)

        return None

    def pixel_to_wall_slot(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos

        x = mouse_x - BOARD_OFFSET_X
        y = mouse_y - BOARD_OFFSET_Y

        if x < 0 or y < 0:
            return None

        col = x // (CELL_SIZE + GAP)
        row = y // (CELL_SIZE + GAP)

        x_inside = x % (CELL_SIZE + GAP)
        y_inside = y % (CELL_SIZE + GAP)

        # Horizontal wall gap below a cell
        if x_inside < CELL_SIZE and CELL_SIZE <= y_inside < CELL_SIZE + GAP:
            if 0 <= row <= 7 and 0 <= col <= 7:
                return int(row), int(col), "H"

        # Vertical wall gap to the right of a cell
        if y_inside < CELL_SIZE and CELL_SIZE <= x_inside < CELL_SIZE + GAP:
            if 0 <= row <= 7 and 0 <= col <= 7:
                return int(row), int(col), "V"

        return None
