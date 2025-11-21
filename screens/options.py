# SnakeGame/screens/options.py
import pygame
from screens.base_screen import BaseScreen
from config import load_config, save_config
from sound import init_sound
from utils import draw_text
from constants import (
    CONFIG, FONT, TEXT_HIGHLIGHT, TEXT_DIM, AVAILABLE_THEMES, 
    reload_theme, THEME_ASSETS, BIG, WIDTH, HEIGHT, TEXT, MAP_TYPES
)

class OptionsScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.title = "Game Settings"
        self.modes = sorted(list(CONFIG.get("mode_settings", {}).keys()))
        self.difficulties = ["Easy", "Normal", "Hard"]
        self.themes = AVAILABLE_THEMES
        self.map_types = MAP_TYPES
        
        self.update_options_text()
        self.update_self_assets()

    def update_self_assets(self):
        self.background_img = THEME_ASSETS.get("background")

    def update_options_text(self):
        current_mode = CONFIG.get("game_mode", "Survival")
        current_diff = CONFIG.get("difficulty", "Normal") 
        current_theme = CONFIG.get("theme", "System")
        current_map = CONFIG.get("map_type", "Standard")
        fullscreen = "On" if CONFIG.get("FULLSCREEN", False) else "Off"
        sound = "On" if CONFIG.get("SOUND", {}).get("enabled", True) else "Off"
        
        self.options = [
            f"Mode: < {current_mode} >",
            f"Difficulty: < {current_diff} >",
            f"Theme: < {current_theme} >",
            f"Map: < {current_map} >",
            f"Fullscreen: < {fullscreen} >",
            f"Sound: < {sound} >"
        ]

    def change_setting(self, setting_key, available_list, direction):
        current_val = CONFIG.get(setting_key, available_list[0])
        try:
            current_idx = available_list.index(current_val)
        except ValueError:
            current_idx = 0
            
        new_idx = (current_idx + direction + len(available_list)) % len(available_list)
        new_val = available_list[new_idx]
        
        CONFIG[setting_key] = new_val
        
        if setting_key == "theme":
            print(f"Theme changed to: {new_val}. Reloading assets...")
            reload_theme()
            self.update_self_assets()
        
        self.update_options_text()

    def toggle_sound(self):
        if "SOUND" not in CONFIG: CONFIG["SOUND"] = {}
        CONFIG["SOUND"]["enabled"] = not CONFIG["SOUND"].get("enabled", True)
        self.update_options_text()

    def toggle_fullscreen(self): 
        CONFIG["FULLSCREEN"] = not CONFIG.get("FULLSCREEN", False)
        self.update_options_text()

    def save_config(self):
        save_config(CONFIG)
        init_sound(is_menu=True) 

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_ESCAPE:
                self.save_config()
                return "MENU"

            direction = 0
            if event.key in (pygame.K_LEFT, pygame.K_a): direction = -1
            if event.key in (pygame.K_RIGHT, pygame.K_d): direction = 1

            if direction == 0 and event.key not in (pygame.K_RETURN, pygame.K_SPACE):
                return "OPTIONS"

            if self.selected == 0:
                self.change_setting("game_mode", self.modes, direction)
            elif self.selected == 1:
                self.change_setting("difficulty", self.difficulties, direction)
            elif self.selected == 2:
                self.change_setting("theme", self.themes, direction)
            elif self.selected == 3:
                self.change_setting("map_type", self.map_types, direction)
            elif self.selected == 4:
                self.toggle_fullscreen()
            elif self.selected == 5:
                self.toggle_sound()
            
        return "OPTIONS"

    def draw(self, surf):
        if self.background_img:
            surf.blit(self.background_img, (0, 0))
        else:
            surf.fill((13, 5, 32))
        
        title_surf = BIG.render(self.title, True, TEXT)
        rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 5))
        surf.blit(title_surf, rect)
        
        y_start = HEIGHT // 2 - 60
        for i, option in enumerate(self.options):
            color = TEXT_HIGHLIGHT if i == self.selected else TEXT_DIM
            text = FONT.render(option, True, color)
            rect = text.get_rect(center=(WIDTH // 2, y_start + i * 40))
            surf.blit(text, rect)
        
        draw_text("Press ESC to Save & Back", FONT, TEXT_DIM, surf, WIDTH/2, HEIGHT - 40)