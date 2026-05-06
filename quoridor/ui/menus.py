"""
menus.py — Start screen, difficulty selection, and reset button reference.
"""
import pygame
import sys

# ── Palette ───────────────────────────────────────────────────────────────────
BG_DARK    = (18,  14,  24)
TEXT_MAIN  = (230, 225, 240)
TEXT_DIM   = (140, 130, 160)
GOLD       = (255, 210,  60)
GREEN_ON   = (50,  160,  80)
GREEN_OFF  = (28,   80,  45)
BLUE_ON    = (50,  100, 200)
BLUE_OFF   = (25,   50, 110)
RED_BTN    = (140,  35,  35)
AMBER      = (180, 110,  30)
AMBER_OFF  = (75,   55,  20)
GRAY_BTN   = (60,   56,  76)


def _load_fonts():
    fonts = {}
    for size, bold in [(18, False), (24, False), (34, True), (60, True)]:
        for name in ("Segoe UI", "DejaVu Sans", "Ubuntu", "Arial"):
            try:
                fonts[(size, bold)] = pygame.font.SysFont(name, size, bold=bold)
                break
            except Exception:
                fonts[(size, bold)] = pygame.font.Font(None, size)
    return fonts


def _draw_btn(screen, rect, label, sublabel, color, fonts, active=False):
    # Shadow
    sh = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    sh.fill((0, 0, 0, 80))
    screen.blit(sh, (rect.x + 3, rect.y + 5))

    pygame.draw.rect(screen, color, rect, border_radius=12)

    # Sheen
    sheen = pygame.Surface((rect.w - 4, rect.h // 3), pygame.SRCALPHA)
    sheen.fill((255, 255, 255, 18))
    screen.blit(sheen, (rect.x + 2, rect.y + 2))

    rim = [min(c + 60, 255) for c in color] if active else (80, 74, 96)
    pygame.draw.rect(screen, rim, rect, 2, border_radius=12)

    font_main = fonts[(34, True)] if not sublabel else fonts[(24, False)]
    lbl_surf  = font_main.render(label, True, TEXT_MAIN)

    if sublabel:
        sub_surf = fonts[(18, False)].render(sublabel, True, TEXT_DIM)
        total_h  = lbl_surf.get_height() + 4 + sub_surf.get_height()
        y0 = rect.centery - total_h // 2
        screen.blit(lbl_surf, (rect.centerx - lbl_surf.get_width() // 2, y0))
        screen.blit(sub_surf, (rect.centerx - sub_surf.get_width() // 2,
                               y0 + lbl_surf.get_height() + 4))
    else:
        screen.blit(lbl_surf, (rect.centerx - lbl_surf.get_width() // 2,
                               rect.centery - lbl_surf.get_height() // 2))


def _draw_ghost_board(screen, alpha=40):
    cell, gap, ox, oy = 28, 4, 560, 160
    for r in range(9):
        for c in range(9):
            s = pygame.Surface((cell, cell), pygame.SRCALPHA)
            s.fill((80, 72, 100, alpha))
            screen.blit(s, (ox + c * (cell + gap), oy + r * (cell + gap)))


def show_start_menu(screen):
    """Returns (mode, difficulty): ('hvh', None) or ('hvc', 'easy'/'medium'/'hard')."""
    fonts = _load_fonts()
    W, H  = screen.get_size()
    hvh_rect = pygame.Rect(W // 2 - 220, 320, 440, 90)
    hvc_rect = pygame.Rect(W // 2 - 220, 440, 440, 90)
    clock = pygame.time.Clock()

    while True:
        screen.fill(BG_DARK)
        _draw_ghost_board(screen)
        pygame.draw.rect(screen, GOLD, pygame.Rect(0, 0, W, 3))

        title = fonts[(60, True)].render("QUORIDOR", True, TEXT_MAIN)
        screen.blit(title, (W // 2 - title.get_width() // 2, 130))

        sub = fonts[(18, False)].render("A strategy board game", True, TEXT_DIM)
        screen.blit(sub, (W // 2 - sub.get_width() // 2, 205))

        pygame.draw.rect(screen, (60, 54, 80), pygame.Rect(W // 2 - 160, 235, 320, 1))

        mx, my = pygame.mouse.get_pos()
        _draw_btn(screen, hvh_rect, "Human vs Human", "Play locally with a friend",
                  GREEN_ON if hvh_rect.collidepoint(mx, my) else GREEN_OFF, fonts,
                  active=hvh_rect.collidepoint(mx, my))
        _draw_btn(screen, hvc_rect, "Human vs Computer", "Challenge the AI",
                  BLUE_ON if hvc_rect.collidepoint(mx, my) else BLUE_OFF, fonts,
                  active=hvc_rect.collidepoint(mx, my))

        ver = fonts[(18, False)].render("v1.0  ·  Pygame Powered", True, TEXT_DIM)
        screen.blit(ver, (W // 2 - ver.get_width() // 2, H - 36))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hvh_rect.collidepoint(event.pos):
                    return "hvh", None
                if hvc_rect.collidepoint(event.pos):
                    result = show_difficulty_menu(screen)
                    if result[0] != "back":
                        return result


def show_difficulty_menu(screen):
    """Returns ('hvc', difficulty) or ('back', None)."""
    fonts = _load_fonts()
    W, H  = screen.get_size()

    easy_rect = pygame.Rect(W // 2 - 200, 280, 400, 80)
    med_rect  = pygame.Rect(W // 2 - 200, 390, 400, 80)
    hard_rect = pygame.Rect(W // 2 - 200, 500, 400, 80)
    back_rect = pygame.Rect(30, 30, 110, 44)

    btns = {
        "easy":   (easy_rect, GREEN_ON,  GREEN_OFF,  "Easy",   "Random legal moves"),
        "medium": (med_rect,  AMBER,     AMBER_OFF,  "Medium", "Minimax search"),
        "hard":   (hard_rect, RED_BTN,   (80,20,20), "Hard",   "Alpha-Beta pruning"),
    }

    clock = pygame.time.Clock()

    while True:
        screen.fill(BG_DARK)
        _draw_ghost_board(screen)
        pygame.draw.rect(screen, GOLD, pygame.Rect(0, 0, W, 3))

        title = fonts[(34, True)].render("Choose Difficulty", True, TEXT_MAIN)
        screen.blit(title, (W // 2 - title.get_width() // 2, 180))

        mx, my = pygame.mouse.get_pos()
        for key, (rect, on_c, off_c, lbl, sub) in btns.items():
            hover = rect.collidepoint(mx, my)
            _draw_btn(screen, rect, lbl, sub, on_c if hover else off_c, fonts, active=hover)

        hover_back = back_rect.collidepoint(mx, my)
        _draw_btn(screen, back_rect, "← Back", None,
                  (90, 84, 110) if hover_back else GRAY_BTN, fonts, active=hover_back)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if easy_rect.collidepoint(event.pos):  return "hvc", "easy"
                if med_rect.collidepoint(event.pos):   return "hvc", "medium"
                if hard_rect.collidepoint(event.pos):  return "hvc", "hard"
                if back_rect.collidepoint(event.pos):  return "back", None


# ── Reset button rect (for any module that needs it) ──────────────────────────
def _get_reset_rect():
    try:
        from ui.renderer import BTN_RESET_RECT
        return BTN_RESET_RECT
    except ImportError:
        return pygame.Rect(860, 740, 120, 44)

RESET_BUTTON_RECT = _get_reset_rect()
