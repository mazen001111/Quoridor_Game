"""event_handler.py — Mouse and keyboard input handling."""
import pygame

from ui.renderer import (
    BTN_MOVE_RECT, BTN_WALL_RECT, BTN_UNDO_RECT, BTN_REDO_RECT,
    BOARD_OFFSET_X, BOARD_OFFSET_Y, CELL_SIZE, GAP,
)


class EventHandler:
    def __init__(self, manager):
        self.manager = manager
        self.mode = "move"
        self.selected_pawn = False
        self.valid_moves = []
        self.hovered_wall = None

    def handle_menu_clicks(self, event, renderer, is_paused):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            # Scenario A: Game is OVER -> Check Winner Overlay Options
            if self.manager.game_over:
                if renderer.win_restart_btn.collidepoint(mouse_pos):
                    return "RESTART"
                elif renderer.win_exit_btn.collidepoint(mouse_pos):
                    return "MAIN_MENU"
                return None  # Ignore board clicks when game is over
            
            # Scenario B: Game is active -> Check if player clicks the floating corner icon
            if not is_paused:
                if renderer.menu_icon_rect.collidepoint(mouse_pos):
                    return "PAUSE"
            
            # Scenario C: Modal overlay is active -> Check options menu items
            else:
                if renderer.resume_btn.collidepoint(mouse_pos):
                    return "RESUME"
                elif renderer.restart_btn.collidepoint(mouse_pos):
                    return "RESTART"
                elif renderer.exit_btn.collidepoint(mouse_pos):
                    return "MAIN_MENU"
                    
        return None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            self.handle_key(event.key)

    def handle_key(self, key):
        if key == pygame.K_w:
            self._toggle_mode()
        elif key == pygame.K_u:          # ← UNDO
            self.manager.undo()
            self._clear_selection()
        elif key == pygame.K_p:          # ← REDO
            self.manager.redo()
            self._clear_selection()

    def handle_click(self, mouse_pos):
        # NEW: Check Undo / Redo buttons
        if BTN_UNDO_RECT.collidepoint(mouse_pos):
            self.manager.undo()
            self._clear_selection()
            return
        if BTN_REDO_RECT.collidepoint(mouse_pos):
            self.manager.redo()
            self._clear_selection()
            return
            
        if BTN_MOVE_RECT.collidepoint(mouse_pos):
            self._set_mode("move")
            return
        if BTN_WALL_RECT.collidepoint(mouse_pos):
            self._set_mode("wall")
            return

        if self.manager.game_over:
            return

        if self.mode == "move":
            self._handle_move_click(mouse_pos)
        else:
            self._handle_wall_click(mouse_pos)

    def handle_mouse_motion(self, mouse_pos):
        if self.mode == "wall" and not self.manager.game_over:
            self.hovered_wall = self._pixel_to_wall_slot(mouse_pos)
        else:
            self.hovered_wall = None

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _clear_selection(self):
        """Drop any pending pawn selection — used after undo/redo."""
        self.selected_pawn = False
        self.valid_moves   = []
        self.hovered_wall  = None

    def _toggle_mode(self):
        self._set_mode("wall" if self.mode == "move" else "move")

    def _set_mode(self, mode):
        self.mode = mode
        self._clear_selection()
        if mode == "move":
            self.manager.message = "Move mode: click your pawn."
        else:
            self.manager.message = "Wall mode: click a gap to place."

    def _handle_move_click(self, mouse_pos):
        cell = self._pixel_to_cell(mouse_pos)
        if cell is None:
            return

        current_pos = self.manager.get_current_pawn().position

        if cell == current_pos:
            self.selected_pawn = True
            self.valid_moves = self.manager.get_current_valid_moves()
            self.manager.message = "Choose a highlighted cell."
            return

        if self.selected_pawn and cell in self.valid_moves:
            self.manager.handle_pawn_move(cell)
            self._clear_selection()
            return

        self._clear_selection()
        self.manager.message = "Click your pawn first."

    def _handle_wall_click(self, mouse_pos):
        wall = self._pixel_to_wall_slot(mouse_pos)
        if wall is None:
            self.manager.message = "Click a gap between cells."
            return
        row, col, orientation = wall
        self.manager.handle_wall_placement(row, col, orientation)

    def _pixel_to_cell(self, mouse_pos):
        mx, my = mouse_pos
        x = mx - BOARD_OFFSET_X
        y = my - BOARD_OFFSET_Y
        if x < 0 or y < 0:
            return None
        col = x // (CELL_SIZE + GAP)
        row = y // (CELL_SIZE + GAP)
        xi  = x % (CELL_SIZE + GAP)
        yi  = y % (CELL_SIZE + GAP)
        if 0 <= row <= 8 and 0 <= col <= 8 and xi < CELL_SIZE and yi < CELL_SIZE:
            return int(row), int(col)
        return None

    def _pixel_to_wall_slot(self, mouse_pos):
        mx, my = mouse_pos
        x = mx - BOARD_OFFSET_X
        y = my - BOARD_OFFSET_Y
        if x < 0 or y < 0:
            return None
        col = x // (CELL_SIZE + GAP)
        row = y // (CELL_SIZE + GAP)
        xi  = x % (CELL_SIZE + GAP)
        yi  = y % (CELL_SIZE + GAP)
        if xi < CELL_SIZE and CELL_SIZE <= yi < CELL_SIZE + GAP:
            if 0 <= row <= 7 and 0 <= col <= 7:
                return int(row), int(col), "H"
        if yi < CELL_SIZE and CELL_SIZE <= xi < CELL_SIZE + GAP:
            if 0 <= row <= 7 and 0 <= col <= 7:
                return int(row), int(col), "V"
        return None