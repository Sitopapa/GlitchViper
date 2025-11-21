# SnakeGame/screens/base_screen.py
import pygame
from utils import draw_text
from constants import WIDTH, HEIGHT
from constants import BG2, BIG, TEXT_HIGHLIGHT, TEXT_DIM, FONT

class BaseScreen:
    def __init__(self):
        self.selected = 0
        self.options = []

    def draw(self, surf):
        surf.fill(BG2)
        
        if not hasattr(self, 'logo') or self.logo is None:
            title_text = getattr(self, 'title', 'Screen')
            draw_text(title_text, BIG, TEXT_HIGHLIGHT, surf, WIDTH/2, HEIGHT/4)
        
        for i, opt in enumerate(self.options):
            y_pos = HEIGHT/2 + i * 40
            
            if i == self.selected:
                color = TEXT_HIGHLIGHT
                draw_text(">", FONT, color, surf, WIDTH/2 - 150, y_pos)
                draw_text(opt, FONT, color, surf, WIDTH/2, y_pos)
            else:
                color = TEXT_DIM
                draw_text(opt, FONT, color, surf, WIDTH/2, y_pos)

    def up(self):
        self.selected = (self.selected - 1 + len(self.options)) % len(self.options)

    def down(self):
        self.selected = (self.selected + 1) % len(self.options)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.up()
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.down()