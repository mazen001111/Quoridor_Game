"""Rendering logic for board, pawns, and walls."""
import pygame
from ui.menus import draw_reset_button


CELL_SIZE = 60
GAP = 10
BOARD_OFFSET_X = 85
BOARD_OFFSET_Y = 90

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

BEIGE = (235, 205, 160)
BROWN = (120, 75, 35)
DARK_BROWN = (70, 40, 20)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (210, 60, 60)
BLUE = (60, 100, 220)
GREEN = (80, 200, 100)
GRAY = (220, 220, 220)


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 40)

    def cell_to_pixel(self, row, col):
        x = BOARD_OFFSET_X + col * (CELL_SIZE + GAP)
        y = BOARD_OFFSET_Y + row * (CELL_SIZE + GAP)
        return x, y

    def draw(self, manager, event_handler=None):
        self.screen.fill(GRAY)

        self.draw_board()
        self.draw_highlights(event_handler)
        self.draw_ghost_wall(event_handler)
        self.draw_walls(manager.board)
        self.draw_pawns(manager)
        self.draw_hud(manager, event_handler)
        draw_reset_button(self.screen)

        if manager.game_over:
            self.draw_winner_overlay(manager)

    def draw_board(self):
        for row in range(9):
            for col in range(9):
                x, y = self.cell_to_pixel(row, col)
                pygame.draw.rect(
                    self.screen,
                    BEIGE,
                    (x, y, CELL_SIZE, CELL_SIZE)
                )
                pygame.draw.rect(
                    self.screen,
                    BROWN,
                    (x, y, CELL_SIZE, CELL_SIZE),
                    2
                )

    def draw_pawns(self, manager):
        colors = {
            1: RED,
            2: BLUE
        }

        for player_id, pawn in manager.pawns.items():
            row, col = pawn.position
            x, y = self.cell_to_pixel(row, col)

            center_x = x + CELL_SIZE // 2
            center_y = y + CELL_SIZE // 2

            pygame.draw.circle(
                self.screen,
                colors[player_id],
                (center_x, center_y),
                CELL_SIZE // 3
            )

            pygame.draw.circle(
                self.screen,
                BLACK,
                (center_x, center_y),
                CELL_SIZE // 3,
                2
            )

    def draw_walls(self, board):
        for row, col in board.get_horizontal_walls():
            x, y = self.cell_to_pixel(row, col)

            wall_x = x
            wall_y = y + CELL_SIZE
            wall_width = 2 * CELL_SIZE + GAP
            wall_height = GAP

            pygame.draw.rect(
                self.screen,
                DARK_BROWN,
                (wall_x, wall_y, wall_width, wall_height)
            )

        for row, col in board.get_vertical_walls():
            x, y = self.cell_to_pixel(row, col)

            wall_x = x + CELL_SIZE
            wall_y = y
            wall_width = GAP
            wall_height = 2 * CELL_SIZE + GAP

            pygame.draw.rect(
                self.screen,
                DARK_BROWN,
                (wall_x, wall_y, wall_width, wall_height)
            )

    def draw_highlights(self, event_handler):
        if event_handler is None:
            return

        if not event_handler.selected_pawn:
            return

        for row, col in event_handler.valid_moves:
            x, y = self.cell_to_pixel(row, col)

            highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            highlight.fill((80, 200, 100, 120))
            self.screen.blit(highlight, (x, y))

    def draw_ghost_wall(self, event_handler):
<<<<<<< HEAD
        """Draw a semi-transparent ghost wall at the hovered wall position."""
=======
        
>>>>>>> d142e58b43f38c3805894d62ce6079f2f6c43d50
        if event_handler is None or event_handler.hovered_wall is None:
            return

        row, col, orientation = event_handler.hovered_wall
        x, y = self.cell_to_pixel(row, col)

<<<<<<< HEAD
        if orientation == 'H':
=======
        # Create a semi-transparent brown color (R, G, B, Alpha/Transparency)
        # 150 means it is mostly see-through (0 is invisible, 255 is solid)
        ghost_color = (70, 40, 20, 120)

        if orientation == "H":
>>>>>>> d142e58b43f38c3805894d62ce6079f2f6c43d50
            wall_x = x
            wall_y = y + CELL_SIZE
            wall_width = 2 * CELL_SIZE + GAP
            wall_height = GAP
<<<<<<< HEAD
        else:
=======
        else:  # "V"
>>>>>>> d142e58b43f38c3805894d62ce6079f2f6c43d50
            wall_x = x + CELL_SIZE
            wall_y = y
            wall_width = GAP
            wall_height = 2 * CELL_SIZE + GAP

<<<<<<< HEAD
        ghost = pygame.Surface((wall_width, wall_height), pygame.SRCALPHA)
        ghost.fill((80, 40, 10, 130))
        self.screen.blit(ghost, (wall_x, wall_y))
=======
        ghost_surface = pygame.Surface((wall_width, wall_height), pygame.SRCALPHA)
        ghost_surface.fill(ghost_color)
        
        self.screen.blit(ghost_surface, (wall_x, wall_y))

>>>>>>> d142e58b43f38c3805894d62ce6079f2f6c43d50

    def draw_hud(self, manager, event_handler=None):
        turn_text = f"Player {manager.current_player}'s Turn"
        message_text = manager.message

        p1_walls = manager.pawns[1].walls_remaining
        p2_walls = manager.pawns[2].walls_remaining

        self.screen.blit(
            self.font.render(turn_text, True, BLACK),
            (20, 15)
        )

        self.screen.blit(
            self.font.render(f"Player 1 Walls: {p1_walls}", True, RED),
            (20, 735)
        )

        self.screen.blit(
            self.font.render(f"Player 2 Walls: {p2_walls}", True, BLUE),
            (20, 45)
        )

        self.screen.blit(
            self.font.render(message_text, True, BLACK),
            (250, 735)
        )

        if event_handler is not None:
            mode_text = f"Mode: {event_handler.mode.upper()} | Press W to toggle wall mode | Press R to reset"
            self.screen.blit(
                self.font.render(mode_text, True, BLACK),
                (160, 765)
            )

    def draw_winner_overlay(self, manager):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        text = self.big_font.render(
            f"Player {manager.winner} Wins!",
            True,
            WHITE
        )

        restart = self.font.render(
            "Press R to restart",
            True,
            WHITE
        )

        self.screen.blit(text, (280, 350))
        self.screen.blit(restart, (310, 410))
