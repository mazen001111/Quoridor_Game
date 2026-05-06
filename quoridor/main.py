import pygame

from game.game_manager import GameManager
from ui.renderer import Renderer
from ui.event_handler import EventHandler
from ui.menus import show_start_menu


def main():
    pygame.init()

    screen = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption("Quoridor")

    clock = pygame.time.Clock()

    mode, difficulty = show_start_menu(screen)

    manager = GameManager(mode=mode, ai_difficulty=difficulty)
    renderer = Renderer(screen)
    event_handler = EventHandler(manager)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            event_handler.handle_event(event)

        renderer.draw(manager, event_handler)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
