import sys
import os

# 1. Path Fix: Ensure Python looks in both directories for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for path in [current_dir, parent_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

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

    # Launch menu and get configuration
    mode, difficulty = show_start_menu(screen)

    manager = GameManager(mode=mode, ai_difficulty=difficulty)
    renderer = Renderer(screen)
    event_handler = EventHandler(manager)

    running = True

    # Crash-catcher: Force Python to show us the error if it fails mid-game
    try:
        while running:
            # A. Handle Human Inputs (Only if it's NOT the AI's turn)
            if not manager.is_ai_turn():
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    event_handler.handle_event(event)
            else:
                # Keep window responsive/closable during AI thinking
                for event in pygame.event.get(pygame.QUIT):
                    running = False

            # B. Trigger AI Turn Processing
            if manager.is_ai_turn() and not manager.game_over and running:
                pygame.time.wait(200) # Quick pause for visual smoothness
                
                # Run the turn logic and capture success status
                turn_successful = manager.handle_ai_turn()
                
                # Safety Valve: If the AI failed to make a valid move, 
                # force turn switch to prevent freezing/terminating
                if not turn_successful:
                    print("Warning: AI generated an invalid move. Forcing turn switch.")
                    manager.switch_turn()

            # C. Render updated board frame
            renderer.draw(manager, event_handler)
            pygame.display.flip()
            clock.tick(60)

    except Exception as e:
        print("\n" + "="*50)
        print("THE GAME CRASHED! DETAILED ERROR BELOW:")
        print("="*50)
        import traceback
        traceback.print_exc()
        print("="*50 + "\n")
        # Keep terminal open so you can read it
        input("Press Enter to close this window...") 

    pygame.quit()


if __name__ == "__main__":
    main()