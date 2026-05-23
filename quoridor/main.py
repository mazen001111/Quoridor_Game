import sys
import os
import pygame

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    sys.path.insert(0, sys._MEIPASS)
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    for path in [current_dir, parent_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)

from game.game_manager import GameManager
from ui.renderer import Renderer
from ui.event_handler import EventHandler
from ui.menus import show_start_menu


# --- Quick pop-up to ask for a timer before the game launches ---
def show_timer_menu(screen):
    font = pygame.font.SysFont("Arial", 30, bold=True)
    small_font = pygame.font.SysFont("Arial", 22)
    
    options = [(300, "No Timer", 0), (450, "5 Minutes", 5), (600, "10 Minutes", 10)]
    
    while True:
        screen.fill((18, 14, 24)) 
        title = font.render("Select Match Time Limit", True, (255, 255, 255))
        screen.blit(title, (500 - title.get_width()//2, 250))
        
        mouse_pos = pygame.mouse.get_pos()
        clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True

        for x_pos, text, mins in options:
            btn_rect = pygame.Rect(x_pos - 60, 350, 120, 50)
            color = (50, 150, 230) if btn_rect.collidepoint(mouse_pos) else (80, 80, 90)
            pygame.draw.rect(screen, color, btn_rect, border_radius=8)
            
            lbl = small_font.render(text, True, (255, 255, 255))
            screen.blit(lbl, (btn_rect.centerx - lbl.get_width()//2, btn_rect.centery - lbl.get_height()//2))
            
            if clicked and btn_rect.collidepoint(mouse_pos):
                return mins 

        pygame.display.flip()
# --------------------------------------------------------------------


def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption("Quoridor")
    clock = pygame.time.Clock()

    master_running = True
    show_menu = True  
    
    mode = None
    difficulty = None
    timer_minutes = 0

    while master_running:
        
        if show_menu:
            mode, difficulty = show_start_menu(screen)
            timer_minutes = show_timer_menu(screen) 
            
        manager = GameManager(mode=mode, ai_difficulty=difficulty)
        renderer = Renderer(screen)
        event_handler = EventHandler(manager)

        running = True
        game_paused = False  
        
        # Setup timers in seconds
        p1_time = timer_minutes * 60 if timer_minutes > 0 else None
        p2_time = timer_minutes * 60 if timer_minutes > 0 else None
        
        # NEW: Timer to track how long the AI has been "thinking"
        ai_delay_timer = 0.0

        try:
            while running:
                # Capture the exact time passed this frame (in seconds)
                dt = clock.tick(60) / 1000.0

                if not manager.is_ai_turn() or game_paused or manager.game_over:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            master_running = False

                        menu_action = event_handler.handle_menu_clicks(event, renderer, game_paused)
                        
                        if menu_action == "PAUSE":
                            game_paused = True
                        elif menu_action == "RESUME":
                            game_paused = False
                        elif menu_action == "RESTART":
                            show_menu = False  
                            running = False    
                        elif menu_action == "MAIN_MENU":
                            show_menu = True   
                            running = False    

                        if not game_paused and menu_action is None:
                            event_handler.handle_event(event)
                else:
                    for event in pygame.event.get(pygame.QUIT):
                        running = False
                        master_running = False

                # --- NEW: Non-Blocking AI Delay Logic ---
                if not game_paused and manager.is_ai_turn() and not manager.game_over and running:
                    ai_delay_timer += dt  # Add the frame time to the AI's thinking timer
                    
                    if ai_delay_timer >= 1.0:  # Wait exactly 1.0 seconds
                        turn_successful = manager.handle_ai_turn()
                        if not turn_successful:
                            manager.switch_turn()
                            
                        ai_delay_timer = 0.0  # Reset for the next time it's the AI's turn
                else:
                    ai_delay_timer = 0.0  # Keep it reset when it is the human's turn
                # ----------------------------------------
                
                # --- Timer Countdown Logic ---
                if not game_paused and not manager.game_over and p1_time is not None:
                    if manager.current_player == 1:
                        p1_time -= dt
                        if p1_time <= 0:
                            manager.game_over = True
                            manager.winner = 2
                            manager.message = "Time's up! Player 2 Wins!"
                    else:
                        p2_time -= dt
                        if p2_time <= 0:
                            manager.game_over = True
                            manager.winner = 1
                            manager.message = "Time's up! Player 1 Wins!"
                # ----------------------------------

                if running:
                    renderer.draw(manager, event_handler, is_paused=game_paused, p1_time=p1_time, p2_time=p2_time)
                    pygame.display.flip()

        except Exception as e:
            print("\n" + "="*50)
            print("THE GAME CRASHED! DETAILED ERROR BELOW:")
            import traceback
            traceback.print_exc()
            input("Press Enter to close this window...") 
            break 

    pygame.quit()


if __name__ == "__main__":
    main()