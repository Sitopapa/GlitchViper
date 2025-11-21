# SnakeGame/utils.py
from constants import CELL
import pygame

def draw_text(text, font, color, surface, x, y, center=True):
    """Metni yüzeye çizer."""
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def grid_to_pixel(pos):
    """Grid koordinatlarını piksel koordinatlarına çevirir."""
    x, y = pos
    return x*CELL, y*CELL