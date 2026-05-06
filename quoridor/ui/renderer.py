"""
renderer.py
-----------
Premium dark board-game visual redesign for Quoridor.

Layout (1000x800 window):
  - Top header bar: turn indicator + message
  - Left sidebar: Player 1 wall rack
  - Right sidebar: Player 2 wall rack
  - Centre: 9x9 dark board
  - Bottom bar: player pill | MOVE btn | WALL btn | RESET btn
"""
import pygame

# ── Window ────────────────────────────────────────────────────────────────────
SCREEN_W = 1000
SCREEN_H = 800

# ── Board geometry ─────────────────────────────────────────────────────────────
CELL_SIZE  = 62
GAP        = 8
BOARD_COLS = 9
BOARD_ROWS = 9

BOARD_PX_W = BOARD_COLS * CELL_SIZE + (BOARD_COLS - 1) * GAP   # 622
BOARD_PX_H = BOARD_ROWS * CELL_SIZE + (BOARD_ROWS - 1) * GAP   # 622

BOARD_OFFSET_X = (SCREEN_W - BOARD_PX_W) // 2   # ≈ 189
BOARD_OFFSET_Y = 90

# ── Palette ───────────────────────────────────────────────────────────────────
BG_DARK        = (18,  14,  24)
BG_PANEL       = (28,  22,  36)
CELL_DARK      = (42,  38,  52)
CELL_BORDER    = (58,  52,  72)
GRID_LINE      = (35,  30,  45)

WALL_COLOR     = (210, 120,  40)
WALL_GHOST     = (210, 120,  40, 110)

PAWN_P1        = (220,  60,  60)
PAWN_P2        = (60,  110, 220)
PAWN_SHINE     = (255, 255, 255, 90)

HIGHLIGHT_FILL = (100, 220, 120, 90)
HIGHLIGHT_RIM  = (100, 220, 120, 200)

RACK_WALL      = (190, 110,  35)
RACK_USED      = (50,  44,  60)

HEADER_BG      = (24,  18,  32)
HEADER_ACCENT1 = (220,  60,  60)
HEADER_ACCENT2 = (60,  110, 220)

BTN_MOVE_ON    = (50,  160,  80)
BTN_MOVE_OFF   = (30,   80,  45)
BTN_WALL_ON    = (180, 110,  30)
BTN_WALL_OFF   = (75,   55,  20)
BTN_RESET      = (140,  35,  35)
BTN_TEXT       = (240, 240, 240)

TEXT_MAIN      = (230, 225, 240)
TEXT_DIM       = (140, 130, 160)
TEXT_P1        = (220,  70,  70)
TEXT_P2        = (70,  120, 230)

WINNER_BG      = (0,   0,   0, 180)
WINNER_GOLD    = (255, 210,  60)

# ── Bottom bar geometry (shared with event_handler) ───────────────────────────
BOTTOM_BAR_Y = BOARD_OFFSET_Y + BOARD_PX_H + 16
BOTTOM_BAR_H = SCREEN_H - BOTTOM_BAR_Y

BTN_W, BTN_H = 140, 48
_btn_y = BOTTOM_BAR_Y + (BOTTOM_BAR_H - BTN_H) // 2

BTN_MOVE_RECT  = pygame.Rect(SCREEN_W // 2 - BTN_W - 8, _btn_y, BTN_W, BTN_H)
BTN_WALL_RECT  = pygame.Rect(SCREEN_W // 2 + 8,          _btn_y, BTN_W, BTN_H)
BTN_RESET_RECT = pygame.Rect(SCREEN_W - 170,             _btn_y, 140,   BTN_H)

# ── Sidebar geometry ──────────────────────────────────────────────────────────
SIDEBAR_W     = BOARD_OFFSET_X - 10
SIDEBAR_L_X   = 5
SIDEBAR_R_X   = BOARD_OFFSET_X + BOARD_PX_W + 5

RACK_WALL_W   = min(SIDEBAR_W - 16, 24)
RACK_WALL_H   = 10
RACK_WALL_GAP = 5
RACK_START_Y  = BOARD_OFFSET_Y + 20


def _rack_wall_rect(sidebar_x, index):
    x = sidebar_x + (SIDEBAR_W - RACK_WALL_W) // 2
    y = RACK_START_Y + index * (RACK_WALL_H + RACK_WALL_GAP)
    return pygame.Rect(x, y, RACK_WALL_W, RACK_WALL_H)


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()

        def load_font(size, bold=False):
            for name in ("Segoe UI", "DejaVu Sans", "Ubuntu", "Arial"):
                try:
                    return pygame.font.SysFont(name, size, bold=bold)
                except Exception:
                    pass
            return pygame.font.Font(None, size)

        self.font_sm  = load_font(18)
        self.font_md  = load_font(22)
        self.font_lg  = load_font(30, bold=True)
        self.font_xl  = load_font(52, bold=True)
        self.font_hud = load_font(20, bold=True)

    # ── Master draw ────────────────────────────────────────────────────────────
    def draw(self, manager, event_handler=None):
        self.screen.fill(BG_DARK)
        self._draw_header(manager)
        self._draw_board_bg()
        self._draw_highlights(event_handler)
        self._draw_ghost_wall(event_handler)
        self._draw_walls(manager.board)
        self._draw_pawns(manager)
        self._draw_sidebars(manager)
        self._draw_bottom_bar(manager, event_handler)
        if manager.game_over:
            self._draw_winner_overlay(manager)

    # ── Header ────────────────────────────────────────────────────────────────
    def _draw_header(self, manager):
        pygame.draw.rect(self.screen, HEADER_BG,
                         pygame.Rect(0, 0, SCREEN_W, BOARD_OFFSET_Y - 4))
        accent = HEADER_ACCENT1 if manager.current_player == 1 else HEADER_ACCENT2
        pygame.draw.rect(self.screen, accent, pygame.Rect(0, 0, SCREEN_W, 3))

        label = f"PLAYER {manager.current_player}'s TURN"
        surf = self.font_lg.render(label, True, TEXT_MAIN)
        self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, 18))

        if manager.message:
            msg = self.font_sm.render(manager.message, True, TEXT_DIM)
            self.screen.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, 52))

    # ── Board background & cells ───────────────────────────────────────────────
    def _draw_board_bg(self):
        shadow = pygame.Rect(BOARD_OFFSET_X - 6, BOARD_OFFSET_Y - 6,
                             BOARD_PX_W + 12, BOARD_PX_H + 12)
        pygame.draw.rect(self.screen, (10, 8, 16), shadow, border_radius=10)

        board_bg = pygame.Rect(BOARD_OFFSET_X - 3, BOARD_OFFSET_Y - 3,
                               BOARD_PX_W + 6, BOARD_PX_H + 6)
        pygame.draw.rect(self.screen, GRID_LINE, board_bg, border_radius=8)

        for row in range(9):
            for col in range(9):
                x, y = self._cell_to_pixel(row, col)
                r = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, CELL_DARK, r, border_radius=3)
                pygame.draw.rect(self.screen, CELL_BORDER, r, 1, border_radius=3)

    # ── Pawns ─────────────────────────────────────────────────────────────────
    def _draw_pawns(self, manager):
        for pid, pawn in manager.pawns.items():
            row, col = pawn.position
            x, y = self._cell_to_pixel(row, col)
            cx = x + CELL_SIZE // 2
            cy = y + CELL_SIZE // 2
            r  = CELL_SIZE // 2 - 6
            color = PAWN_P1 if pid == 1 else PAWN_P2

            # Drop shadow
            sh = pygame.Surface((r*2+8, r*2+8), pygame.SRCALPHA)
            pygame.draw.circle(sh, (0, 0, 0, 120), (r+4, r+6), r)
            self.screen.blit(sh, (cx - r - 4, cy - r - 4))

            pygame.draw.circle(self.screen, color, (cx, cy), r)

            # Specular glint
            shine = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(shine, PAWN_SHINE, (r//2, r//2), r//3)
            self.screen.blit(shine, (cx - r, cy - r))

            pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), r, 2)

    # ── Placed walls ──────────────────────────────────────────────────────────
    def _draw_walls(self, board):
        for row, col in board.get_horizontal_walls():
            self._draw_wall_rect(row, col, 'H', WALL_COLOR)
        for row, col in board.get_vertical_walls():
            self._draw_wall_rect(row, col, 'V', WALL_COLOR)

    def _draw_wall_rect(self, row, col, orientation, color, alpha=None):
        x, y = self._cell_to_pixel(row, col)
        if orientation == 'H':
            rx, ry, rw, rh = x, y + CELL_SIZE, 2 * CELL_SIZE + GAP, GAP
        else:
            rx, ry, rw, rh = x + CELL_SIZE, y, GAP, 2 * CELL_SIZE + GAP

        if alpha is not None:
            surf = pygame.Surface((rw, rh), pygame.SRCALPHA)
            surf.fill((*color[:3], alpha))
            self.screen.blit(surf, (rx, ry))
        else:
            rect = pygame.Rect(rx, ry, rw, rh)
            pygame.draw.rect(self.screen, color, rect, border_radius=2)
            hi = tuple(min(c + 60, 255) for c in color[:3])
            pygame.draw.rect(self.screen, hi, pygame.Rect(rx, ry, rw, 2))

    # ── Move highlights ───────────────────────────────────────────────────────
    def _draw_highlights(self, eh):
        if eh is None or not eh.selected_pawn:
            return
        for row, col in eh.valid_moves:
            x, y = self._cell_to_pixel(row, col)
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            surf.fill(HIGHLIGHT_FILL)
            self.screen.blit(surf, (x, y))
            rim = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(rim, HIGHLIGHT_RIM, rim.get_rect(), 2, border_radius=3)
            self.screen.blit(rim, (x, y))

    # ── Ghost wall preview ────────────────────────────────────────────────────
    def _draw_ghost_wall(self, eh):
        if eh is None or eh.hovered_wall is None:
            return
        row, col, orientation = eh.hovered_wall
        self._draw_wall_rect(row, col, orientation, WALL_GHOST[:3], alpha=WALL_GHOST[3])

    # ── Sidebars — wall racks ─────────────────────────────────────────────────
    def _draw_sidebars(self, manager):
        self._draw_rack(SIDEBAR_L_X, manager.pawns[1].walls_remaining, TEXT_P1, "P1  Walls")
        self._draw_rack(SIDEBAR_R_X, manager.pawns[2].walls_remaining, TEXT_P2, "P2  Walls")

    def _draw_rack(self, sidebar_x, walls_remaining, label_color, label):
        lbl = self.font_sm.render(label, True, label_color)
        self.screen.blit(lbl, (sidebar_x + (SIDEBAR_W - lbl.get_width()) // 2,
                               BOARD_OFFSET_Y - 22))
        for i in range(10):
            slot_idx = 10 - 1 - i
            rect = _rack_wall_rect(sidebar_x, i)
            if slot_idx < walls_remaining:
                pygame.draw.rect(self.screen, RACK_WALL, rect, border_radius=2)
                hi = pygame.Rect(rect.x, rect.y, rect.w, 3)
                pygame.draw.rect(self.screen, (255, 200, 120), hi, border_radius=2)
            else:
                pygame.draw.rect(self.screen, RACK_USED, rect, border_radius=2)

    # ── Bottom bar ────────────────────────────────────────────────────────────
    def _draw_bottom_bar(self, manager, eh):
        pygame.draw.rect(self.screen, BG_PANEL,
                         pygame.Rect(0, BOTTOM_BAR_Y - 4, SCREEN_W, BOTTOM_BAR_H + 8))
        pygame.draw.rect(self.screen, (50, 44, 64),
                         pygame.Rect(0, BOTTOM_BAR_Y - 4, SCREEN_W, 2))

        # Player indicator pill
        pid    = manager.current_player
        pcolor = TEXT_P1 if pid == 1 else TEXT_P2
        pill   = pygame.Rect(16, BOTTOM_BAR_Y + (BOTTOM_BAR_H - 44) // 2, 140, 44)
        pill_surf = pygame.Surface((pill.w, pill.h), pygame.SRCALPHA)
        pill_surf.fill((*pcolor, 40))
        self.screen.blit(pill_surf, (pill.x, pill.y))
        pygame.draw.rect(self.screen, pcolor, pill, 2, border_radius=8)
        p_lbl = self.font_hud.render(f"P{pid} TURN", True, pcolor)
        self.screen.blit(p_lbl, (pill.centerx - p_lbl.get_width() // 2,
                                 pill.centery - p_lbl.get_height() // 2))

        # Mode buttons
        mode = eh.mode if eh else "move"
        self._draw_mode_btn(BTN_MOVE_RECT, "MOVE",
                            BTN_MOVE_ON if mode == "move" else BTN_MOVE_OFF,
                            active=(mode == "move"))
        self._draw_mode_btn(BTN_WALL_RECT, "WALL",
                            BTN_WALL_ON if mode == "wall" else BTN_WALL_OFF,
                            active=(mode == "wall"))
        self._draw_mode_btn(BTN_RESET_RECT, "RESET", BTN_RESET, active=False)

        hint = self.font_sm.render("W: toggle mode  |  R: reset", True, TEXT_DIM)
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2,
                                BOTTOM_BAR_Y + BOTTOM_BAR_H - 22))

    def _draw_mode_btn(self, rect, label, color, active=False):
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        rim_color = tuple(min(c + 80, 255) for c in color) if active else (80, 74, 96)
        pygame.draw.rect(self.screen, rim_color, rect, 2, border_radius=8)
        txt = self.font_hud.render(label, True, BTN_TEXT)
        self.screen.blit(txt, (rect.centerx - txt.get_width() // 2,
                               rect.centery - txt.get_height() // 2))

    # ── Winner overlay ────────────────────────────────────────────────────────
    def _draw_winner_overlay(self, manager):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill(WINNER_BG)
        self.screen.blit(overlay, (0, 0))

        card = pygame.Rect(SCREEN_W // 2 - 240, SCREEN_H // 2 - 110, 480, 220)
        pygame.draw.rect(self.screen, BG_PANEL, card, border_radius=16)
        pcolor = HEADER_ACCENT1 if manager.winner == 1 else HEADER_ACCENT2
        pygame.draw.rect(self.screen, pcolor, card, 3, border_radius=16)

        w_txt = self.font_xl.render(f"PLAYER {manager.winner} WINS!", True, WINNER_GOLD)
        self.screen.blit(w_txt, (SCREEN_W // 2 - w_txt.get_width() // 2,
                                 SCREEN_H // 2 - 80))
        r_txt = self.font_md.render("Press  R  to play again", True, TEXT_DIM)
        self.screen.blit(r_txt, (SCREEN_W // 2 - r_txt.get_width() // 2,
                                 SCREEN_H // 2 + 50))

    # ── Utility ───────────────────────────────────────────────────────────────
    def _cell_to_pixel(self, row, col):
        x = BOARD_OFFSET_X + col * (CELL_SIZE + GAP)
        y = BOARD_OFFSET_Y + row * (CELL_SIZE + GAP)
        return x, y
