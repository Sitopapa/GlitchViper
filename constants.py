# SnakeGame/constants.py
import pygame
import os
from config import load_config

CONFIG = load_config()

CELL = CONFIG.get("CELL", 24)
COLS = CONFIG.get("COLS", 40)
ROWS = CONFIG.get("ROWS", 30)
WIDTH = CELL * COLS
HEIGHT = CELL * ROWS

MAP_TYPES = ["Standard", "Room", "Tunnel"]

pygame.init()
pygame.font.init()

def load_sprite(path, size=(CELL, CELL)):
    if not os.path.exists(path):
        print(f"Warning: Sprite not found at {path}")
        return None
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size)
    except Exception as e:
        print(f"Error loading sprite {path}: {e}")
        return None

try:
    FONT = pygame.font.Font("assets/Font/PixelFont.ttf", 20)
    BIG = pygame.font.Font("assets/Font/PixelFont.ttf", 40)
    MEDIUM = pygame.font.Font("assets/Font/PixelFont.ttf", 30) 
except:
    FONT = pygame.font.SysFont("Consolas", 20)
    BIG = pygame.font.SysFont("Consolas", 40)
    MEDIUM = pygame.font.SysFont("Consolas", 30)

BG2 = (13, 5, 32) 
TEXT = (220, 220, 220)
TEXT_DIM = (150, 150, 150)
TEXT_HIGHLIGHT = (255, 255, 255)
WALL = (80, 90, 110)
GRID_COLOR = (40, 55, 70) 

POWERUP_TYPES = {
    "MAGNET": {"COLOR": (50, 100, 255), "DURATION": 10.0, "LABEL": "MAG"},
    "SHIELD": {"COLOR": (0, 255, 255), "DURATION": 15.0, "LABEL": "SHD"},
    "SLOW":   {"COLOR": (180, 0, 255),  "DURATION": 8.0,  "LABEL": "SLW"},
    "DOUBLE": {"COLOR": (255, 215, 0),  "DURATION": 10.0, "LABEL": "2X"}
}
COMBO_WINDOW = 3.0 

POWERUP_FILES = {
    "MAGNET": "magnet.png",
    "SHIELD": "shield.png",
    "SLOW":   "slow.png",
    "DOUBLE": "x2.png" 
}

POWERUP_ASSETS = {}

def load_powerup_assets():
    global POWERUP_ASSETS
    img_dir = "assets/Images"
    print("--- Loading Power-Up Assets ---")
    for p_type, filename in POWERUP_FILES.items():
        path = os.path.join(img_dir, filename)
        img = load_sprite(path, size=(CELL, CELL))
        if img:
            POWERUP_ASSETS[p_type] = img
        else:
            POWERUP_ASSETS[p_type] = None

BG_SURFACE = pygame.Surface((WIDTH, HEIGHT))
BG_SURFACE.fill((20, 30, 40)) 
BORDER_SURFACE = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.draw.rect(BORDER_SURFACE, (200, 50, 50), (0, 0, CELL, HEIGHT))
pygame.draw.rect(BORDER_SURFACE, (200, 50, 50), (WIDTH - CELL, 0, CELL, HEIGHT))
pygame.draw.rect(BORDER_SURFACE, (200, 50, 50), (0, 0, WIDTH, CELL * 3)) 
pygame.draw.rect(BORDER_SURFACE, (200, 50, 50), (0, HEIGHT - CELL, WIDTH, CELL))
pygame.draw.rect(BORDER_SURFACE, (255, 255, 255), (CELL, CELL*3, WIDTH - 2*CELL, HEIGHT - 4*CELL), 2)

FALLBACK_THEME_ASSETS = {
    "background": BG_SURFACE,
    "border": BORDER_SURFACE,
    "snake_skin": {
        "SNAKE_HEAD": (110, 220, 110),
        "SNAKE_BODY": (60, 180, 80),
        "SNAKE_BODY_INNER": (80, 200, 100)
    },
    "foods": {
        "apple": {"COLOR": (255, 100, 100), "BASE_POINTS": 100}
    }
}

THEMES_DIR = "assets/Themes"

def get_available_themes():
    if not os.path.exists(THEMES_DIR): return []
    try: return sorted([d for d in os.listdir(THEMES_DIR) if os.path.isdir(os.path.join(THEMES_DIR, d))])
    except: return []

def load_theme_assets(theme_name):
    if theme_name == "System": return FALLBACK_THEME_ASSETS
    path = os.path.join(THEMES_DIR, theme_name)
    if not os.path.isdir(path): return FALLBACK_THEME_ASSETS
    try:
        assets = {
            "background": load_sprite(os.path.join(path, "background.png"), size=(WIDTH, HEIGHT)),
            "border": load_sprite(os.path.join(path, "border.png"), size=(WIDTH, HEIGHT)),
            "snake_skin": {k: load_sprite(os.path.join(path, f"{k}.png")) for k in [
                "head-up", "head-down", "head-left", "head-right",
                "tail-up", "tail-down", "tail-left", "tail-right",
                "body-vertical", "body-horizontal",
                "body-up-right", "body-up-left", "body-down-right", "body-down-left"
            ]},
            "foods": {}
        }
        known_food_types = {"apple": {"BASE_POINTS": 100, "COLOR": (255, 100, 100)}, "grape": {"BASE_POINTS": 150, "COLOR": (200, 100, 255)}}
        for food_name, data in known_food_types.items():
            food_path = os.path.join(path, f"{food_name}.png")
            if os.path.exists(food_path):
                assets["foods"][food_name] = {"IMAGE": load_sprite(food_path), "COLOR": data["COLOR"], "BASE_POINTS": data["BASE_POINTS"]}
        if not assets["foods"]: assets["foods"] = FALLBACK_THEME_ASSETS["foods"]
        return assets
    except: return FALLBACK_THEME_ASSETS

AVAILABLE_THEMES = ["System"] + get_available_themes()
THEME_ASSETS = {}
def reload_theme():
    theme_name = CONFIG.get("theme", "System")
    if theme_name not in AVAILABLE_THEMES: theme_name = "System"
    THEME_ASSETS.clear()
    THEME_ASSETS.update(load_theme_assets(theme_name))
    load_powerup_assets()

reload_theme()