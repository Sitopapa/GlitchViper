# SnakeGame/stats_manager.py
import json
import os

STATS_PATH = "stats.json"

def load_stats():
    if not os.path.exists(STATS_PATH):
        return {}
    try:
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_stats(stats):
    try:
        with open(STATS_PATH, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        print(f"Error saving stats: {e}")

def update_player_stats(player_name, score, time_played, powerups=0, max_combo=0):
    stats = load_stats()
    
    if player_name not in stats:
        stats[player_name] = {
            "total_games": 0,
            "total_score": 0,
            "total_time": 0,
            "highest_score": 0,
            "deaths": 0,
            "total_powerups": 0,
            "max_combo": 0
        }
    
    p_stats = stats[player_name]
    p_stats["total_games"] += 1
    p_stats["total_score"] += score
    p_stats["total_time"] += time_played
    p_stats["deaths"] += 1
    
    if "total_powerups" not in p_stats: p_stats["total_powerups"] = 0
    if "max_combo" not in p_stats: p_stats["max_combo"] = 0

    p_stats["total_powerups"] += powerups
    if max_combo > p_stats["max_combo"]:
        p_stats["max_combo"] = max_combo
    
    if score > p_stats["highest_score"]:
        p_stats["highest_score"] = score
        
    save_stats(stats)

def get_player_stats(player_name):
    stats = load_stats()
    return stats.get(player_name, None)