# SnakeGame/screens/hs_mode_menu.py
import pygame
from screens.base_screen import BaseScreen
from constants import CONFIG, WIDTH, HEIGHT, FONT, TEXT_DIM, MAP_TYPES
from utils import draw_text

class HighScoresMenu(BaseScreen):
    def __init__(self):
        super().__init__()
        self.stage = "MAP" 
        self.selected_map = "Standard"
        
        self.title = "Select Map"
        self.options = MAP_TYPES 
        
        self.modes = sorted(list(CONFIG.get("mode_settings", {}).keys()))

    def draw(self, surf):
        super().draw(surf)
        
        if self.stage == "MAP":
            info = "Select Map Type"
        else:
            info = f"Map: {self.selected_map} > Select Mode"
            
        draw_text(info, FONT, (200, 200, 100), surf, WIDTH/2, HEIGHT/6 + 90)
        
        draw_text("Press ENTER to Select / ESC to Back", FONT, TEXT_DIM, surf, WIDTH/2, HEIGHT - 40)

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_ESCAPE:
                if self.stage == "MODE":
                    self.stage = "MAP"
                    self.title = "Select Map"
                    self.options = MAP_TYPES
                    self.selected = 0
                    return "HS_MODE_MENU"
                else:
                    return "MENU"

            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selected < len(self.options):
                    choice = self.options[self.selected]
                    
                    if self.stage == "MAP":
                        self.selected_map = choice
                        self.stage = "MODE"
                        self.title = "Select Game Mode"
                        self.options = self.modes
                        self.selected = 0
                        return "HS_MODE_MENU"
                    
                    elif self.stage == "MODE":
                        return f"HS_DISPLAY_{self.selected_map}_{choice}"
            
        return "HS_MODE_MENU"