# SnakeGame/screens/name_input.py
import pygame
from utils import draw_text
from constants import WIDTH, HEIGHT, BIG, FONT, TEXT_HIGHLIGHT, TEXT, TEXT_DIM, BG2

class NameInputScene:
    def __init__(self): 
        self.name = ""
        self.max_len = 12
        self.title = "CREATE PROFILE"
        self.cursor_visible = True
        self.last_blink = 0

    def draw(self, surf):
        surf.fill(BG2)
        draw_text("WELCOME TO GLITCH VIPER", BIG, (255, 215, 0), surf, WIDTH/2, HEIGHT/4)
        draw_text(self.title, FONT, TEXT_HIGHLIGHT, surf, WIDTH/2, HEIGHT/3)
        
        draw_text("Enter your name to start:", FONT, TEXT, surf, WIDTH/2, HEIGHT/2 - 20)

        now = pygame.time.get_ticks()
        if now - self.last_blink > 500:
            self.cursor_visible = not self.cursor_visible
            self.last_blink = now

        name_display = self.name.upper()
        if self.cursor_visible:
             name_display += "_"
        else:
             name_display += " "

        pygame.draw.rect(surf, (30, 30, 40), (WIDTH/2 - 150, HEIGHT/2 + 10, 300, 50), border_radius=5)
        pygame.draw.rect(surf, (100, 100, 120), (WIDTH/2 - 150, HEIGHT/2 + 10, 300, 50), 2, border_radius=5)
        
        draw_text(name_display, BIG, (0, 255, 255), surf, WIDTH/2, HEIGHT/2 + 35)
        
        draw_text("Press ENTER to Continue", FONT, TEXT_DIM, surf, WIDTH/2, HEIGHT - 80)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.name.strip():
                    return ("PROFILE_SET", self.name.strip().upper())
                
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]

            elif event.unicode and len(self.name) < self.max_len and (event.unicode.isalnum() or event.unicode == ' '):
                self.name += event.unicode

        return "NAME_INPUT"