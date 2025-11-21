# SnakeGame/screens/menu.py
import pygame
import sys
from screens.base_screen import BaseScreen
from constants import WIDTH, HEIGHT

class Menu(BaseScreen):
    def __init__(self):
        super().__init__()
        self.title = "GLITCH VIPER"
        self.options = ["Start Game", "Options", "High Scores", "Statistics", "Quit"] 
        
        try:
            self.logo_original = pygame.image.load("assets/Images/logo.png").convert_alpha()
            original_width, original_height = self.logo_original.get_size()
            aspect_ratio = original_height / original_width
            new_width = WIDTH // 5 
            new_height = int(new_width * aspect_ratio)
            self.logo = pygame.transform.scale(self.logo_original, (new_width, new_height))
        except:
            self.logo = None 

    def draw(self, surf):
        super().draw(surf)
        if self.logo:
            rect = self.logo.get_rect(center=(WIDTH/2, HEIGHT/5))
            surf.blit(self.logo, rect)

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.selected == 0: return "GAME"
            if self.selected == 1: return "OPTIONS"
            if self.selected == 2: return "HS_MODE_MENU" 
            if self.selected == 3: return "STATS"
            if self.selected == 4: pygame.quit(); sys.exit()
        return "MENU"