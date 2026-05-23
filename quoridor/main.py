import sys
import os

# 1. Path Fix: Ensure Python looks in the right place whether running as script or EXE
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # We are running as a PyInstaller --onefile EXE
    sys.path.insert(0, sys._MEIPASS)
else:
    # We are running normally from VS Code
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

# ... rest of your main.py stays exactly the same! ...
def main():
    pygame.init()

    screen = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption("Quoridor")
    clock = pygame.time.Clock()

    master_running = True
    show_menu = True  # NEW: Tracks if we should show the menu or skip it
    
    # Declare these variables outside the loop so a "Restart" remembers them
    mode = None
    difficulty = None

    while master_running:
        
        # Only show the dashboard if the user explicitly clicked "Main Menu" or if it's the first boot
        if show_menu:
            mode, difficulty = show_start_menu(screen)
            
        # Initialize core instances clean on game startup / restart
        manager = GameManager(mode=mode, ai_difficulty=difficulty)
        renderer = Renderer(screen)
        event_handler = EventHandler(manager)

        running = True
        game_paused = False  

        try:
            while running:
                # A. Handle Human Inputs 
                if not manager.is_ai_turn() or game_paused or manager.game_over:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            master_running = False

                        # Detect if user clicked an interactive UI overlay block
                        menu_action = event_handler.handle_menu_clicks(event, renderer, game_paused)
                        
                        if menu_action == "PAUSE":
                            game_paused = True
                        elif menu_action == "RESUME":
                            game_paused = False
                        
                        # --- THE FIX IS HERE ---
                        elif menu_action == "RESTART":
                            show_menu = False  # Skip the start menu on the next pass
                            running = False    # Break current match to re-instantiate GameManager immediately
                        elif menu_action == "MAIN_MENU":
                            show_menu = True   # Force the start menu to show on the next pass
                            running = False    
                        # -----------------------

                        # Pass clicks to player board game engine ONLY when match isn't frozen
                        if not game_paused and menu_action is None:
                            event_handler.handle_event(event)
                else:
                    # Keep window responsive/closable during AI thinking operations
                    for event in pygame.event.get(pygame.QUIT):
                        running = False
                        master_running = False

                # B. Trigger AI Turn Processing (Halted if UI state is active)
                if not game_paused and manager.is_ai_turn() and not manager.game_over and running:
                    pygame.time.wait(200) 
                    
                    turn_successful = manager.handle_ai_turn()
                    
                    if not turn_successful:
                        print("Warning: AI generated an invalid move. Forcing turn switch.")
                        manager.switch_turn()

                # C. Render updated board frame layout
                if running:
                    renderer.draw(manager, event_handler, is_paused=game_paused)
                    pygame.display.flip()
                    clock.tick(60)

        except Exception as e:
            print("\n" + "="*50)
            print("THE GAME CRASHED! DETAILED ERROR BELOW:")
            print("="*50)
            import traceback
            traceback.print_exc()
            print("="*50 + "\n")
            input("Press Enter to close this window...") 
            break 

    pygame.quit()


if __name__ == "__main__":
    main()