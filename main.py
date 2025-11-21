# SnakeGame/main.py
import pygame, sys
from config import load_config
from sound import init_sound
from high_scores import add_high_score
from stats_manager import update_player_stats

CONFIG = load_config()
CELL = CONFIG.get("CELL", 24)
COLS = CONFIG.get("COLS", 40)
ROWS = CONFIG.get("ROWS", 30)
WIDTH = CELL * COLS
HEIGHT = CELL * ROWS

pygame.init()
flags = pygame.FULLSCREEN if CONFIG.get("FULLSCREEN", False) else 0
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
pygame.display.set_caption("GLITCH VIPER")
clock = pygame.time.Clock()

from game import Game
from screens.menu import Menu
from screens.options import OptionsScreen
from screens.high_scores import HighScoresDisplay
from screens.name_input import NameInputScene 
from screens.hs_mode_menu import HighScoresMenu
from screens.stats_screen import StatsScreen 
from constants import BG2 

PLAYER_NAME = "GUEST"

def reset_display(config):
    CELL = config.get("CELL", 24)
    COLS = config.get("COLS", 40)
    ROWS = config.get("ROWS", 30)
    WIDTH = CELL * COLS
    HEIGHT = CELL * ROWS
    flags = pygame.FULLSCREEN if config.get("FULLSCREEN", False) else 0
    return pygame.display.set_mode((WIDTH, HEIGHT), flags)

def save_game_results(game):
    time_elapsed = game.elapsed()
    difficulty = CONFIG.get("difficulty", "Normal") 
    mode = CONFIG.get("game_mode", "Survival")
    map_type = CONFIG.get("map_type", "Standard")
    
    add_high_score(PLAYER_NAME, game.score_food, time_elapsed, mode, difficulty, map_type)
    
    update_player_stats(PLAYER_NAME, game.score_food, time_elapsed, game.powerups_collected, game.max_combo_reached)
    
    print(f"Stats updated for {PLAYER_NAME}")

def main():
    global screen, PLAYER_NAME, CONFIG
    
    init_sound(is_menu=True)
    
    screens = {
        "NAME_INPUT": NameInputScene(), 
        "MENU": Menu(),
        "OPTIONS": OptionsScreen(),
        "HS_MODE_MENU": HighScoresMenu(),
        "STATS": StatsScreen()
    }
    
    game_state = "NAME_INPUT" 
    input_queued = False 
    game = None 

    while True:
        raw_dt = clock.tick(60)/1000.0
        dt = min(raw_dt, 0.1)
        
        new_state = game_state
        old_state = game_state

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if game_state in screens:
                result = screens[game_state].handle_event(event)
                if result:
                    if isinstance(result, tuple) and result[0] == "PROFILE_SET":
                        PLAYER_NAME = result[1]
                        new_state = "MENU"
                    else:
                        new_state = result

            elif game_state == "GAME":
                if event.type == pygame.KEYDOWN:
                    
                    if event.key in (pygame.K_ESCAPE, pygame.K_m):
                        if game.game_over:
                             save_game_results(game)
                        new_state="MENU"

                    elif game.game_over:
                        if event.key == pygame.K_r:
                            save_game_results(game)
                            game.reset()
                            game.player_name = PLAYER_NAME
                    
                    elif not input_queued:
                        new_dir = None
                        if event.key in (pygame.K_UP, pygame.K_w): new_dir = (0,-1)
                        elif event.key in (pygame.K_DOWN, pygame.K_s): new_dir = (0,1)
                        elif event.key in (pygame.K_LEFT, pygame.K_a): new_dir = (-1,0)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d): new_dir = (1,0)
                        
                        if new_dir:
                            game.change_dir(new_dir)
                            input_queued = True 

        if new_state != game_state:
            game_state = new_state
            
            if old_state == "OPTIONS":
                 CONFIG = load_config() 
                 screen = reset_display(CONFIG)
                 init_sound(is_menu=True) 

            if game_state == "GAME":
                init_sound(is_menu=False)
                game = Game(player_name=PLAYER_NAME)
                input_queued = False 
            
            elif game_state == "MENU":
                 init_sound(is_menu=True)

            elif game_state.startswith("HS_DISPLAY_"):
                parts = game_state.split("_")
                if len(parts) >= 4:
                    map_name = parts[2]
                    mode_name = parts[3]
                    screens[game_state] = HighScoresDisplay(map_name, mode_name)
            
            elif game_state == "STATS":
                 screens["STATS"] = StatsScreen()
            
            elif game_state == "HS_MODE_MENU":
                screens["HS_MODE_MENU"] = HighScoresMenu()
                for key in list(screens.keys()):
                    if key.startswith("HS_DISPLAY_"):
                        del screens[key]

        if game_state == "GAME":
            if not game.game_over:
                game.accumulator += dt
                step_time = 1.0 / game.FPS 
                while game.accumulator >= step_time:
                    game.step()
                    input_queued = False 
                    game.accumulator -= step_time
            
            game.update_particles(dt)

        if game_state == "GAME":
            game.draw(screen, dt)
        elif game_state in screens:
            screens[game_state].draw(screen)

        pygame.display.flip()

if __name__=="__main__":
    main()