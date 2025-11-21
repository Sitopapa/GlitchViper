# SnakeGame/screens/high_scores.py
import pygame
from screens.base_screen import BaseScreen
from high_scores import load_high_scores
from constants import WIDTH, HEIGHT, FONT, TEXT, BG2, BIG, TEXT_HIGHLIGHT, TEXT_DIM
from utils import draw_text

class HighScoresDisplay(BaseScreen):
    def __init__(self, map_name, mode_name):
        super().__init__()
        self.map_to_display = map_name
        self.mode_to_display = mode_name
        
        self.title = f"{map_name} - {mode_name}"
        self.scores = self.load_scores()
        self.options = ["Press ENTER or ESC to Back"]
        self.line_height = 20
        
        self.difficulty_order = ["Easy", "Normal", "Hard"]
        self.COL_W = WIDTH // 3
        self.COL_POS = [self.COL_W * i + self.COL_W // 2 for i in range(3)] 
        self.COL_OFFSET_X = 50 
        
        self.scroll_y = 0
        self.max_scroll = 0
        self.list_start_y = HEIGHT // 6 + 40
        self.list_end_y = HEIGHT - 50
        self.view_height = self.list_end_y - self.list_start_y

    def load_scores(self):
         return load_high_scores()

    def draw(self, surf):
        surf.fill(BG2)
        
        draw_text(self.title, BIG, TEXT_HIGHLIGHT, surf, WIDTH/2, HEIGHT/16)
        
        for i, diff in enumerate(self.difficulty_order):
            draw_text(diff.upper(), BIG, TEXT_HIGHLIGHT, surf, self.COL_POS[i], HEIGHT // 6)
            
        clip_rect = pygame.Rect(0, self.list_start_y, WIDTH, self.view_height)
        surf.set_clip(clip_rect)
        
        all_scores = self.load_scores()
        
        filtered_scores = []
        for s in all_scores:
            s_map = s.get("map", "Standard")
            s_mode = s.get("mode", "Survival")
            
            if s_map == self.map_to_display and s_mode == self.mode_to_display:
                filtered_scores.append(s)
        
        grouped_scores = {diff: [] for diff in self.difficulty_order}
        for score in filtered_scores:
            diff = score.get("difficulty", "Normal")
            if diff in grouped_scores:
                grouped_scores[diff].append(score)
        
        max_rows = max(len(l) for l in grouped_scores.values()) if grouped_scores else 0
        total_content_h = max_rows * (self.line_height * 2.5)
        self.max_scroll = max(0, total_content_h - self.view_height)
        
        for c, diff in enumerate(self.difficulty_order):
            scores_list = grouped_scores.get(diff, [])
            
            for r, score in enumerate(scores_list):
                row_y = self.list_start_y + (r * self.line_height * 2.5) - self.scroll_y
                
                if row_y + self.line_height * 2 < self.list_start_y: continue
                if row_y > self.list_end_y: break
                
                rank_name = f"{r+1}. {score.get('name', 'Unknown')}" 
                draw_text(rank_name, FONT, TEXT, surf, self.COL_POS[c] - self.COL_OFFSET_X, row_y, center=False)
                
                score_time = f"{score.get('score', 0)} pts ({score.get('time', 0)}s)"
                draw_text(score_time, FONT, TEXT_DIM, surf, self.COL_POS[c] - self.COL_OFFSET_X, row_y + self.line_height, center=False)
        
        surf.set_clip(None)
        
        if self.max_scroll > 0:
            bar_x = WIDTH - 10
            bar_h = self.view_height * (self.view_height / (total_content_h + self.view_height))
            bar_y = self.list_start_y + (self.scroll_y / self.max_scroll) * (self.view_height - bar_h)
            pygame.draw.rect(surf, (100, 100, 100), (bar_x, self.list_start_y, 5, self.view_height))
            pygame.draw.rect(surf, (200, 200, 200), (bar_x, bar_y, 5, bar_h))

        hint = "Use ARROWS/SCROLL to view more" if self.max_scroll > 0 else ""
        draw_text(hint, FONT, TEXT_DIM, surf, WIDTH/2, HEIGHT - 60)
        
        opt_text = self.options[0]
        draw_text(opt_text, FONT, TEXT_HIGHLIGHT, surf, WIDTH/2, HEIGHT - 30)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_m):
                return "HS_MODE_MENU" 
            
            if event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - 40)
            if event.key == pygame.K_DOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + 40)

        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * 30 
            self.scroll_y = max(0, min(self.max_scroll, self.scroll_y))
        
        return f"HS_DISPLAY_{self.map_to_display}_{self.mode_to_display}"