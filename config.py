# SnakeGame/config.py
import json, os

CONFIG_PATH = "config.json"

DEFAULT_CONFIG = {
    "CELL": 24,
    "COLS": 40,
    "ROWS": 30,
    "difficulty": "Normal",
    "game_mode": "Survival",
    "map_type": "Standard",
    "FULLSCREEN": False,
    "theme": "Realistic", 

    "mode_settings": {
        "Classic": {
          "music": "assets/Music/classic.ogg",
          "base_fps": 12,
          "initial_length": 4,
          "DNA": { "base_death_chance": 0.0, "mutation_on_food": 0.0, "mutation_strength": 0.0, "death_min": 0.0, "death_max": 0.0 },
          "RULES": { "DNA_ACTIVE": False, "BOMBS_ACTIVE": False, "WALLS_ACTIVE": True, "SURVIVAL_ACTIVE": False, "CHASE_ACTIVE": False }
        },
        "Survival": {
          "music": "assets/Music/survival.ogg",
          "base_fps": 12,
          "initial_length": 4,
          "DNA": { "base_death_chance": 0.0, "mutation_on_food": 0.0, "mutation_strength": 0.0, "death_min": 0.0, "death_max": 0.0 },
          "RULES": { "DNA_ACTIVE": False, "BOMBS_ACTIVE": False, "WALLS_ACTIVE": True, "SURVIVAL_ACTIVE": True, "SURVIVAL_TIMER_DURATION": 5.0, "CHASE_ACTIVE": False }
        },
        "Mutation": {
          "music": "assets/Music/mutation.ogg",
          "base_fps": 14,
          "initial_length": 3,
          "DNA": { "base_death_chance": 0.05, "mutation_on_food": 0.0, "mutation_strength": 0.05, "death_min": 0.01, "death_max": 0.35 },
          "RULES": { "DNA_ACTIVE": True, "BOMBS_ACTIVE": False, "WALLS_ACTIVE": True, "RANDOM_MUTATION_INTERVAL": 2.5, "SURVIVAL_ACTIVE": True, "SURVIVAL_TIMER_DURATION": 7.0, "CHASE_ACTIVE": False }
        },
        "Bomb": {
          "music": "assets/Music/bomb.ogg",
          "base_fps": 12,
          "initial_length": 3,
          "DNA": { "base_death_chance": 0.0, "mutation_on_food": 0.0, "mutation_strength": 0.0, "death_min": 0.0, "death_max": 0.0 },
          "RULES": { "DNA_ACTIVE": False, "BOMBS_ACTIVE": True, "BOMB_SPAWN_INTERVAL": 3.0, "WALLS_ACTIVE": True, "MAX_BOMBS": 4, "BOMB_EXPLOSION_RADIUS": 4, "SURVIVAL_ACTIVE": False, "CHASE_ACTIVE": False }
        }
    },
    "SOUND": { "enabled": True },
    "BACKGROUND_MUSIC": "assets/Music/background.ogg"
}

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            config = DEFAULT_CONFIG.copy()
            for key, value in loaded.items():
                if key != "mode_settings":
                    config[key] = value
            merged_modes = DEFAULT_CONFIG["mode_settings"].copy()
            merged_modes.update(loaded.get("mode_settings", {}))
            config["mode_settings"] = merged_modes
            return config
        except Exception as e:
            print(f"Config load error: {e}. Loading default config.")
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")