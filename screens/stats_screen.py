# SnakeGame/screens/stats_screen.py
import pygame
from screens.base_screen import BaseScreen
from stats_manager import load_stats
from utils import draw_text
from constants import WIDTH, HEIGHT, FONT, BIG, TEXT, TEXT_HIGHLIGHT, BG2, TEXT_DIM

class StatsScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.stats = load_stats()

    def draw(self, surf):
        surf.fill(BG2)
        
        draw_text("PLAYER STATS", BIG, TEXT_HIGHLIGHT, surf, WIDTH/2, 50)
        draw_text("Press ENTER or ESC to return", FONT, TEXT_DIM, surf, WIDTH/2, HEIGHT - 30)

        y_offset = 100
        headers = ["Name", "Games", "Score", "High", "Powerups", "Combo"]
        x_positions = [
            WIDTH * 0.10,
            WIDTH * 0.30,
            WIDTH * 0.45,
            WIDTH * 0.60,
            WIDTH * 0.75,
            WIDTH * 0.90 
        ]
        
        for i, header in enumerate(headers):
            draw_text(header, FONT, (255, 200, 0), surf, x_positions[i], y_offset)
        
        y_offset += 40
        sorted_players = sorted(self.stats.items(), key=lambda x: x[1]['total_score'], reverse=True)

        for name, data in sorted_players[:12]: 
            p_ups = data.get('total_powerups', 0)
            combo = data.get('max_combo', 0)

            draw_text(name[:10], FONT, TEXT, surf, x_positions[0], y_offset)
            draw_text(str(data['total_games']), FONT, TEXT, surf, x_positions[1], y_offset)
            draw_text(str(data['total_score']), FONT, TEXT, surf, x_positions[2], y_offset)
            draw_text(str(data['highest_score']), FONT, (100, 255, 100), surf, x_positions[3], y_offset)
            
            draw_text(str(p_ups), FONT, (100, 200, 255), surf, x_positions[4], y_offset)
            draw_text(str(combo), FONT, (255, 100, 255), surf, x_positions[5], y_offset)

            y_offset += 30

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                return "MENU"
        return "STATS"