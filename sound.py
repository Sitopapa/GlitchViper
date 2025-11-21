# SnakeGame/sound.py
import pygame, os
from config import load_config

CONFIG = load_config()
ASSETS_DIR = "assets/Music"
SOUND_FILES = {
    "eat": os.path.join(ASSETS_DIR, "eat.wav"),
    "game_over": os.path.join(ASSETS_DIR, "game_over.wav")
}

SOUNDS = {}
sound_enabled = CONFIG.get("SOUND", {}).get("enabled", True)
current_track_path = None

def init_sound(is_menu=False):
    global SOUNDS, sound_enabled, CONFIG, current_track_path
    
    CONFIG = load_config()
    sound_enabled = CONFIG.get("SOUND", {}).get("enabled", True)
    
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except:
            sound_enabled = False
            return

    if sound_enabled:
        try:
            for k, path in SOUND_FILES.items():
                if k not in SOUNDS:
                    SOUNDS[k] = pygame.mixer.Sound(path) if os.path.exists(path) else None
            
            if is_menu:
                bg_music = CONFIG.get("BACKGROUND_MUSIC")
            else:
                current_mode = CONFIG.get("game_mode", "Survival")
                mode_music = CONFIG["mode_settings"].get(current_mode, {}).get("music")
                bg_music = mode_music if mode_music and os.path.exists(mode_music) else CONFIG.get("BACKGROUND_MUSIC")
            
            if bg_music == current_track_path and pygame.mixer.music.get_busy():
                return

            if bg_music and os.path.exists(bg_music):
                pygame.mixer.music.stop()
                pygame.mixer.music.load(bg_music)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                current_track_path = bg_music
            else:
                pygame.mixer.music.stop()
                current_track_path = None
                    
        except Exception as e:
            print("Sound init error:", e)
            sound_enabled = False
    else:
        if pygame.mixer.get_init():
             pygame.mixer.music.stop()

def play_sound(key):
    if sound_enabled and SOUNDS.get(key):
        try: SOUNDS[key].play()
        except: pass