# SnakeGame/high_scores.py
import json, os

HIGH_SCORES_PATH = "high_scores.json"

def load_high_scores():
    if not os.path.exists(HIGH_SCORES_PATH):
        return []
    try:
        with open(HIGH_SCORES_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip(): 
                return []
            return json.loads(content)
    except json.JSONDecodeError: 
        return []
    except:
        return []

def save_high_scores(scores):
    try:
        with open(HIGH_SCORES_PATH, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error saving high scores:", e)

def add_high_score(name, score, time, mode, difficulty, map_type="Standard"):
    scores = load_high_scores()
    scores.append({
        "name": name, 
        "score": score, 
        "time": time, 
        "mode": mode, 
        "difficulty": difficulty,
        "map": map_type
    }) 
    
    scores = sorted(scores, key=lambda x: (x["score"], x["time"]), reverse=True)[:200]
    save_high_scores(scores)