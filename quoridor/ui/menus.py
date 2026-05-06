"""Start screen, mode selection, and reset menus."""
import pygame
import sys


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK = (40, 40, 40)
GREEN = (80, 160, 100)
BLUE = (80, 100, 180)



def draw_button(screen, rect, text, font, color):           # Helper to draw a button with text
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)

    label = font.render(text, True, WHITE)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)


def show_start_menu(screen):                # Display the start menu and return the selected mode and difficulty
    font_big = pygame.font.SysFont("arial", 52)
    font = pygame.font.SysFont("arial", 28)

    hvh_button = pygame.Rect(250, 300, 300, 70)
    hvc_button = pygame.Rect(250, 400, 300, 70)

    while True:
        screen.fill(DARK)

        title = font_big.render("QUORIDOR GAME", True, WHITE)
        screen.blit(title, (225, 170))

        draw_button(screen, hvh_button, "Human vs Human", font, GREEN)
        draw_button(screen, hvc_button, "Human vs Computer", font, BLUE)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if hvh_button.collidepoint(event.pos):
                    return "hvh", None

                if hvc_button.collidepoint(event.pos):    
                    mode, difficulty = show_difficulty_menu(screen)

                    if mode != "back":
                        return mode, difficulty
                


def show_difficulty_menu(screen):           # Display the difficulty selection menu and return the selected difficulty
    font_big = pygame.font.SysFont("arial", 44)
    font = pygame.font.SysFont("arial", 28)

    easy_button = pygame.Rect(250, 280, 300, 60)
    medium_button = pygame.Rect(250, 370, 300, 60)
    hard_button = pygame.Rect(250, 460, 300, 60)
    back_button = pygame.Rect(20, 20, 100, 40)

    while True:
        screen.fill(DARK)

        title = font_big.render("Choose Difficulty", True, WHITE)
        screen.blit(title, (215, 170))

        draw_button(screen, easy_button, "Easy", font, GREEN)
        draw_button(screen, medium_button, "Medium", font, BLUE)
        draw_button(screen, hard_button, "Hard", font, (160, 80, 80))
        draw_button(screen, back_button, "Back", font, (100, 100, 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.collidepoint(event.pos):
                    return "hvc", "easy"

                if medium_button.collidepoint(event.pos):
                    return "hvc", "medium"

                if hard_button.collidepoint(event.pos):
                    return "hvc", "hard"
                if back_button.collidepoint(event.pos):
                    return "back", None

RESET_BUTTON_RECT = pygame.Rect(650, 20, 100, 40)
def draw_reset_button(screen):
    """Draws the reset button on the screen during gameplay."""
    font = pygame.font.SysFont("arial", 20)
    # Using the dark red color
    draw_button(screen, RESET_BUTTON_RECT, "Reset", font, (160, 80, 80))