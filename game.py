# SnakeGame/game.py
import pygame, random, time, math
from collections import deque
from config import load_config
from sound import play_sound
from utils import grid_to_pixel
from constants import (
    CELL, COLS, ROWS, WIDTH, HEIGHT, BG2, WALL, GRID_COLOR, TEXT, TEXT_DIM, 
    FONT, BIG, MEDIUM, CONFIG, THEME_ASSETS, POWERUP_TYPES, COMBO_WINDOW,
    POWERUP_ASSETS
)

class FloatingText:
    def __init__(self, text, pos, color=(255, 255, 255), duration=1.0, size="small"):
        self.text = text
        self.x, self.y = pos
        self.color = color
        self.life = duration
        self.max_life = duration
        self.vy = -30 
        self.font = MEDIUM if size == "medium" else FONT

    def update(self, dt):
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surf):
        if self.life <= 0: return
        alpha = int(255 * (self.life / self.max_life))
        txt_surf = self.font.render(self.text, True, self.color)
        txt_surf.set_alpha(alpha)
        rect = txt_surf.get_rect(center=(self.x, self.y))
        surf.blit(txt_surf, rect)

class PowerUp:
    def __init__(self, pos, p_type):
        self.pos = pos
        self.type = p_type
        self.x, self.y = grid_to_pixel(pos)
        self.data = POWERUP_TYPES[p_type]
        self.timer = 15.0 
        self.pulse_time = 0

    def update(self, dt):
        self.timer -= dt
        self.pulse_time += dt

    def draw(self, surf):
        img = POWERUP_ASSETS.get(self.type)
        cx, cy = self.x + CELL//2, self.y + CELL//2
        scale = 1.0 + 0.1 * (0.5 + 0.5 * pygame.math.Vector2(0, 1).rotate(self.pulse_time * 360).y)
        
        if img:
            w = int(CELL * scale)
            h = int(CELL * scale)
            scaled_img = pygame.transform.scale(img, (w, h))
            rect = scaled_img.get_rect(center=(cx, cy))
            surf.blit(scaled_img, rect)
        else:
            color = self.data["COLOR"]
            r = int((CELL//2 - 2) * scale)
            pygame.draw.circle(surf, color, (cx, cy), r, 2)
            txt = FONT.render(self.data["LABEL"][0], True, color)
            rect = txt.get_rect(center=(cx, cy))
            surf.blit(txt, rect)

class Particle:
    def __init__(self, pos, color):
        self.x, self.y = pos
        self.color = color
        self.vx = (random.random()-0.5)*2.5
        self.vy = (random.random()-1.5)*2.5
        self.life = random.uniform(0.5, 1.2)
    def update(self, dt):
        self.x += self.vx*dt*60
        self.y += self.vy*dt*60
        self.life -= dt
    def draw(self, surf):
        if self.life <= 0: return
        r = max(1, int(4*self.life))
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        alpha = max(0, int(255*self.life))
        pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2]), (r,r), r)
        s.set_alpha(alpha)
        surf.blit(s, (self.x-r, self.y-r))

class Bomb:
    def __init__(self, pos, image=None):
        self.pos = pos
        self.x, self.y = grid_to_pixel(pos)
        self.timer = 5.0 
        self.exploding = False
        self.explosion_time = 0.5
        self.image = image

    def update(self, dt):
        if not self.exploding:
            self.timer = max(0, self.timer - dt)
            if self.timer == 0: self.exploding = True
        else: self.explosion_time = max(0, self.explosion_time - dt)
    
    def draw(self, surf):
        center_x = self.x + CELL // 2
        center_y = self.y + CELL // 2
        
        if self.exploding:
            ratio = (0.5 - self.explosion_time) / 0.5
            radius = int(CELL * 0.5 + (CELL * CONFIG["mode_settings"]["Bomb"]["RULES"]["BOMB_EXPLOSION_RADIUS"] * ratio))
            
            explosion_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surf, (255, 140, 0, 150), (radius, radius), radius) 
            pygame.draw.circle(explosion_surf, (255, 69, 0, 200), (radius, radius), radius, 4) 
            surf.blit(explosion_surf, (center_x - radius, center_y - radius))
            return

        try:
            radius_grid = CONFIG["mode_settings"]["Bomb"]["RULES"].get("BOMB_EXPLOSION_RADIUS", 4)
            radius_pixel = int(radius_grid * CELL) 
            range_surf = pygame.Surface((radius_pixel*2, radius_pixel*2), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, (255, 50, 50, 30), (radius_pixel, radius_pixel), radius_pixel, 2)
            surf.blit(range_surf, (center_x - radius_pixel, center_y - radius_pixel))
        except: pass
        
        if self.image:
            pulse = (math.sin(time.time() * 8) + 1) / 2
            scale = 0.9 + 0.2 * pulse
            
            w = int(CELL * scale)
            h = int(CELL * scale)
            scaled_img = pygame.transform.scale(self.image, (w, h))
            rect = scaled_img.get_rect(center=(center_x, center_y))
            surf.blit(scaled_img, rect)
        else:
            ratio = self.timer / 5.0
            r = int(CELL * 0.4 * ratio + CELL * 0.1)
            pulse = (math.sin(time.time() * 8) + 1) / 2
            red_val = int(150 + (105 * pulse))
            color = (red_val, 30, 30)
            pygame.draw.circle(surf, color, (center_x, center_y), r)

        font_size = FONT.render(str(int(self.timer)+1), True, (255,255,255))
        rect = font_size.get_rect(center=(center_x, center_y))
        surf.blit(font_size, rect)

class Game:
    def __init__(self, player_name="Player"): 
        self.player_name = player_name
        self.ICON_SIZE = (20, 20)
        try:
            self.icon_time = pygame.transform.scale(pygame.image.load("assets/Images/time.png").convert_alpha(), self.ICON_SIZE)
            self.icon_score = pygame.transform.scale(pygame.image.load("assets/Images/score.png").convert_alpha(), self.ICON_SIZE)
        except:
            self.icon_time = None
            self.icon_score = None
        self.reset()

    @property
    def FPS(self):
        base = getattr(self, "_base_fps", 10)
        active = getattr(self, "active_effects", {})
        if active.get("SLOW", 0) > 0:
            return base * 0.85
        return base

    def reset(self):
        global CONFIG, THEME_ASSETS
        from config import load_config
        CONFIG = load_config()
        try:
            from constants import THEME_ASSETS as LATEST_THEME_ASSETS
            THEME_ASSETS = LATEST_THEME_ASSETS
        except ImportError: pass

        self.background_img = THEME_ASSETS["background"]
        self.border_img = THEME_ASSETS["border"]
        self.current_mode = CONFIG.get("game_mode", "Survival") 
        self.current_difficulty = CONFIG.get("difficulty", "Normal") 
        self.snake_skin = THEME_ASSETS["snake_skin"]
        self.food_definitions = THEME_ASSETS.get("foods", {})
        
        self.powerups = []
        self.active_effects = {} 
        
        self.set_mode_settings(self.current_mode, self.current_difficulty) 

        midx, midy = COLS//2, ROWS//2
        
        self.current_map = CONFIG.get("map_type", "Standard")
        
        if self.current_map == "Room":
            midx = COLS // 4 
            
        if midy < 4: midy = 4
        
        self.snake = deque()
        self.snake.appendleft((midx, midy))
        for i in range(1, self.initial_length): self.snake.append((midx-i, midy))
        
        self.snake_dir = (1,0)
        self.pending_dir = (1,0)
        self.walls = set() 
        
        if self.current_map == "Room":
            cx, cy = COLS//2, ROWS//2
            for i in range(-3, 4):
                self.walls.add((cx + i, cy)) 
                self.walls.add((cx, cy + i)) 
            self.walls.add((5, 7))
            self.walls.add((COLS-6, 7))
            self.walls.add((5, ROWS-4))
            self.walls.add((COLS-6, ROWS-4))
        
        self.bombs = [] 
        self.next_bomb_spawn_time = time.time() + self.rules.get("BOMB_SPAWN_INTERVAL", 100)
        
        try:
            self.bomb_img = pygame.image.load("assets/Images/bomb.png").convert_alpha()
        except Exception as e:
            print("Bomb image not found:", e)
            self.bomb_img = None

        self.next_powerup_time = time.time() + random.uniform(10, 20)
        self.floating_texts = []
        
        self.shake_timer = 0.0
        self.shake_magnitude = 0.0
        self.flash_alpha = 0
        
        self.combo_count = 0
        self.combo_multiplier = 1.0
        self.max_combo_reached = 0 
        self.powerups_collected = 0 
        
        self.last_eat_time = 0.0
        self.ghost_timer = 0.0 
        
        self.last_mutation_time = time.time() 
        self.survival_timer_duration = self.rules.get("SURVIVAL_TIMER_DURATION", 100)
        self.hunger_timer = self.survival_timer_duration
        self.next_chase_time = time.time() + self.rules.get("CHASE_INTERVAL", 100)
        self.foods = []
        self.spawn_food()
        
        self.game_over = False
        self.end_time = None
        self.food_count = 0
        self.score_food = 0
        self.death_log = []
        self.particles = []
        self.accumulator = 0.0
        self.start_time = time.time()

    def trigger_shake(self, duration, magnitude):
        self.shake_timer = duration
        self.shake_magnitude = magnitude

    def trigger_flash(self):
        self.flash_alpha = 200

    def set_mode_settings(self, mode, difficulty):
        cfg = CONFIG["mode_settings"].get(mode, {})
        default_cfg = CONFIG["mode_settings"]["Classic"]
        diff_multipliers = {
            "Easy": {"fps_mult": 0.8, "decay_mult": 0.5, "length_mult": 1.2, "hunger_mult": 1.5, "bomb_mult": 0.7, "chase_mult": 1.5},
            "Normal": {"fps_mult": 1.0, "decay_mult": 1.0, "length_mult": 1.0, "hunger_mult": 1.0, "bomb_mult": 1.0, "chase_mult": 1.0},
            "Hard": {"fps_mult": 1.2, "decay_mult": 1.5, "length_mult": 0.8, "hunger_mult": 0.75, "bomb_mult": 1.3, "chase_mult": 0.75}
        }
        mult = diff_multipliers.get(difficulty, diff_multipliers["Normal"])
        
        raw_fps = cfg.get("base_fps", default_cfg.get("base_fps", 12))
        self._base_fps = max(1.0, raw_fps * mult["fps_mult"])
        
        self.initial_length = max(2, int(cfg.get("initial_length", 4) * mult["length_mult"])) 
        self.rules = cfg.get("RULES", default_cfg["RULES"])
        if "SURVIVAL_TIMER_DURATION" in self.rules: self.rules["SURVIVAL_TIMER_DURATION"] *= mult["hunger_mult"]
        if "MAX_BOMBS" in self.rules: self.rules["MAX_BOMBS"] = int(self.rules["MAX_BOMBS"] * mult["bomb_mult"])
        if "CHASE_INTERVAL" in self.rules: self.rules["CHASE_INTERVAL"] *= mult["chase_mult"]
        dna_cfg = cfg.get("DNA", default_cfg["DNA"])
        self.dna = {
            "base_death_chance": dna_cfg.get("base_death_chance") * mult["decay_mult"],
            "mutation_on_food": dna_cfg.get("mutation_on_food"),
            "mutation_strength": dna_cfg.get("mutation_strength"),
            "death_min": dna_cfg.get("death_min") * mult["decay_mult"],
            "death_max": dna_cfg.get("death_max") * mult["decay_mult"]
        }
        if not self.rules.get("DNA_ACTIVE", True): self.dna["base_death_chance"] = 0.0

    def spawn_food(self):
        if not self.food_definitions: return
        food_type_name = random.choice(list(self.food_definitions.keys()))
        food_data = self.food_definitions[food_type_name]
        all_cells = {(x,y) for x in range(1, COLS-1) for y in range(4, ROWS-1)}
        food_positions = {f["pos"] for f in self.foods}
        blocked = set(self.snake) | self.walls | {b.pos for b in self.bombs} | food_positions | {p.pos for p in self.powerups}
        free = list(all_cells - blocked)
        if free: self.foods.append({"pos": random.choice(free), "type": food_type_name, "data": food_data})

    def spawn_powerup(self):
        all_cells = {(x,y) for x in range(1, COLS-1) for y in range(4, ROWS-1)}
        blocked = set(self.snake) | self.walls | {b.pos for b in self.bombs} | {f["pos"] for f in self.foods} | {p.pos for p in self.powerups}
        free = list(all_cells - blocked)
        if free:
            possible_types = list(POWERUP_TYPES.keys())
            if self.current_mode in ["Classic", "Bomb"] and "SLOW" in possible_types:
                possible_types.remove("SLOW")
            
            if possible_types:
                p_type = random.choice(possible_types)
                self.powerups.append(PowerUp(random.choice(free), p_type))

    def change_dir(self, newdir):
        dx, dy = newdir
        cdx, cdy = self.pending_dir 
        if (dx, dy) == (-cdx, -cdy): return
        self.pending_dir = (dx, dy)

    def spawn_bomb(self):
         all_cells = {(x,y) for x in range(1, COLS-1) for y in range(4, ROWS-1)}
         blocked = set(self.snake) | self.walls | {b.pos for b in self.bombs} | {f["pos"] for f in self.foods}
         head = self.snake[0]
         dx, dy = self.snake_dir
         for i in range(1, 4): blocked.add((head[0] + dx*i, head[1] + dy*i))
         free = list(all_cells - blocked)
         if free:
             self.bombs.append(Bomb(random.choice(free), self.bomb_img))

    def set_game_over(self):
        if self.active_effects.get("SHIELD", 0) > 0:
            self.active_effects["SHIELD"] = 0 
            play_sound("game_over") 
            self.trigger_shake(0.4, 5) 
            
            head_px = grid_to_pixel(self.snake[0])
            cx, cy = head_px[0] + CELL//2, head_px[1] + CELL//2
            self.floating_texts.append(FloatingText("SHIELD BROKEN!", (cx, cy - 20), (0, 255, 255), 1.5))
            
            self.ghost_timer = 3.0
            self.floating_texts.append(FloatingText("GHOST MODE!", (cx, cy + 20), (200, 200, 255), 1.5))
            
            for _ in range(20): self.particles.append(Particle((cx, cy), (0, 255, 255)))
            return 

        if not self.game_over:
            self.game_over = True
            self.end_time = time.time() 
            play_sound("game_over")
            self.trigger_shake(2.0, 5)

    def trigger_explosion(self, bomb):
        head = self.snake[0]
        radius = self.rules.get("BOMB_EXPLOSION_RADIUS", 4)
        dist = abs(head[0] - bomb.pos[0]) + abs(head[1] - bomb.pos[1]) 
        
        self.trigger_shake(0.3, 5) 
        self.trigger_flash()       
        
        if dist <= radius:
             if self.ghost_timer <= 0:
                 self.set_game_over()
        
        bx, by = grid_to_pixel(bomb.pos)
        for _ in range(30): self.particles.append(Particle((bx+CELL/2, by+CELL/2), (255,100,0)))
        if bomb in self.bombs: self.bombs.remove(bomb)

    def get_closest_bomb_distance(self):
        if not self.bombs or not self.foods: return float('inf')
        fx, fy = self.foods[0]["pos"]
        min_dist = float('inf')
        for b in self.bombs:
            if b.exploding: continue
            dist = abs(fx - b.pos[0]) + abs(fy - b.pos[1])
            if dist < min_dist: min_dist = dist
        return min_dist
    
    def chase_tail_shrink(self):
        if len(self.snake) <= 2:
             self.set_game_over()
             return
        tail_pos = self.snake.pop() 
        self.walls.add(tail_pos) 
        self.death_log.append((tail_pos, time.time()))

    def step(self):
        if self.game_over: return
        self.snake_dir = self.pending_dir
        head = self.snake[0]
        dx, dy = self.snake_dir
        new_head = (head[0]+dx, head[1]+dy)
        
        if self.rules.get("BOMBS_ACTIVE", False):
            for bomb in self.bombs:
                if new_head == bomb.pos and not bomb.exploding:
                    bomb.timer = 0 
                    bomb.exploding = True
                    break 
        
        hit_wall = not (1 <= new_head[0] < COLS - 1 and 3 <= new_head[1] < ROWS - 1)
        
        if hit_wall:
            is_tunnel = (CONFIG.get("map_type") == "Tunnel")
            has_shield = (self.active_effects.get("SHIELD", 0) > 0)
            
            if has_shield or is_tunnel:
                if new_head[0] < 1: new_head = (COLS - 2, new_head[1])
                elif new_head[0] >= COLS - 1: new_head = (1, new_head[1])
                elif new_head[1] < 3: new_head = (new_head[0], ROWS - 2)
                elif new_head[1] >= ROWS - 1: new_head = (new_head[0], 3)
            elif self.ghost_timer <= 0:
                self.set_game_over()
                return

        if (new_head in self.snake or new_head in self.walls):
            if self.ghost_timer <= 0:
                self.set_game_over()
                if not self.game_over and self.ghost_timer > 0:
                    pass
                else:
                    return

        self.snake.appendleft(new_head)
        
        hit_powerup = None
        for p in self.powerups:
            if new_head == p.pos:
                hit_powerup = p
                break
        
        if hit_powerup:
            self.powerups.remove(hit_powerup)
            self.powerups_collected += 1 
            p_data = POWERUP_TYPES[hit_powerup.type]
            self.active_effects[hit_powerup.type] = p_data["DURATION"]
            play_sound("eat")
            
            px, py = grid_to_pixel(hit_powerup.pos)
            self.floating_texts.append(FloatingText(f"{p_data['LABEL']}!", (px+CELL//2, py), p_data["COLOR"]))

        ate_food = None
        magnet_range = 4 if self.active_effects.get("MAGNET", 0) > 0 else 0
        
        for food in self.foods:
            dist = abs(new_head[0] - food["pos"][0]) + abs(new_head[1] - food["pos"][1])
            if new_head == food["pos"] or (magnet_range > 0 and dist <= magnet_range):
                ate_food = food
                break
        
        if ate_food:
            self.foods.remove(ate_food) 
            self.food_count += 1
            points = 0
            base_points = ate_food["data"].get("BASE_POINTS", 100) 
            
            if self.current_mode == "Classic": points = base_points 
            elif self.current_mode == "Survival":
                max_time = self.rules.get("SURVIVAL_TIMER_DURATION", 5.0)
                time_left = self.hunger_timer
                speed_bonus = (base_points * 1.5) * (time_left / max_time) 
                points = base_points + int(speed_bonus)
            elif self.current_mode == "Mutation":
                max_time = self.rules.get("SURVIVAL_TIMER_DURATION", 7.0)
                time_left = self.hunger_timer
                speed_bonus = (base_points * 1.5) * (time_left / max_time)
                decay_risk_bonus = self.dna["base_death_chance"] * 500
                points = base_points + int(speed_bonus) + int(decay_risk_bonus)
            elif self.current_mode == "Bomb":
                risk_bonus = 0
                closest_bomb_dist = self.get_closest_bomb_distance()
                if closest_bomb_dist <= 3: risk_bonus = base_points * 3 
                elif closest_bomb_dist <= 6: risk_bonus = base_points * 1.5 
                points = base_points + int(risk_bonus)

            now = time.time()
            if now - self.last_eat_time < COMBO_WINDOW:
                self.combo_count += 1
                self.combo_multiplier = min(3.0, 1.0 + (self.combo_count * 0.1))
                
                if self.combo_count > self.max_combo_reached:
                    self.max_combo_reached = self.combo_count

                if self.combo_count > 1:
                    head_px = grid_to_pixel(new_head)
                    txt_pos = (head_px[0] + CELL, head_px[1] - 10)
                    color = (255, 215, 0) if self.combo_count >= 5 else (200, 200, 200)
                    self.floating_texts.append(FloatingText(f"x{self.combo_multiplier:.1f}!", txt_pos, color, 0.8, "small"))
            else:
                self.combo_count = 1
                self.combo_multiplier = 1.0
            
            self.last_eat_time = now
            points = int(points * self.combo_multiplier)

            if self.active_effects.get("DOUBLE", 0) > 0:
                points *= 2
                head_px = grid_to_pixel(new_head)
                self.floating_texts.append(FloatingText("2X!", (head_px[0], head_px[1]-30), (255, 215, 0), 0.6))

            self.score_food += points 
            play_sound("eat")
            fx, fy = grid_to_pixel(ate_food["pos"])
            
            if new_head != ate_food["pos"]:
                head_px = grid_to_pixel(new_head)
                for i in range(5):
                    lx = fx + (head_px[0] - fx) * (i/5)
                    ly = fy + (head_px[1] - fy) * (i/5)
                    self.particles.append(Particle((lx+CELL/2, ly+CELL/2), (50, 100, 255)))

            particle_color = ate_food["data"].get("COLOR", (255, 100, 100))
            for _ in range(15): self.particles.append(Particle((fx+CELL/2, fy+CELL/2), particle_color))
            
            self.spawn_food() 
            if self.rules.get("SURVIVAL_ACTIVE", False): self.hunger_timer = self.survival_timer_duration
            if self.rules.get("DNA_ACTIVE", True) and not self.rules.get("RANDOM_MUTATION_INTERVAL") and random.random() < self.dna["mutation_on_food"]:
                self.mutate_dna()
        else:
            self.snake.pop()
            
        if self.rules.get("DNA_ACTIVE", True): self.random_segment_death()
        if self.rules.get("CHASE_ACTIVE", False) and time.time() > self.next_chase_time:
            self.chase_tail_shrink(); self.next_chase_time = time.time() + self.rules.get("CHASE_INTERVAL", 1.5)
        
        max_bombs = self.rules.get("MAX_BOMBS", 4)
        if self.rules.get("BOMBS_ACTIVE", False) and time.time() > self.next_bomb_spawn_time and len(self.bombs) < max_bombs:
            self.spawn_bomb(); self.next_bomb_spawn_time = time.time() + self.rules.get("BOMB_SPAWN_INTERVAL", 5.0)
        if self.rules.get("RANDOM_MUTATION_INTERVAL") and time.time() > self.last_mutation_time + self.rules.get("RANDOM_MUTATION_INTERVAL", 1.5):
            self.mutate_dna(); self.last_mutation_time = time.time()

    def random_segment_death(self):
        if len(self.snake) <= 2: return
        if random.random() < self.dna["base_death_chance"]:
            i = random.randint(1, len(self.snake)-1)
            pos = self.snake[i]
            self.snake = deque(s for idx, s in enumerate(self.snake) if idx != i)
            self.walls.add(pos); self.death_log.append((pos, time.time()))

    def mutate_dna(self):
        delta = (random.random()*2-1)*self.dna.get("mutation_strength", 0.02)
        self.dna["base_death_chance"] = max(self.dna.get("death_min", 0.01), min(self.dna.get("death_max", 0.25), self.dna.get("base_death_chance", 0.07) + delta))
        delta2 = (random.random()*2-1)*(self.dna.get("mutation_strength", 0.02)/2)
        self.dna["mutation_on_food"] = max(0.0, min(0.6, self.dna.get("mutation_on_food",0.25)+delta2))

    def elapsed(self):
        current = self.end_time if self.end_time is not None else time.time()
        return int(current - self.start_time)

    def update_particles(self, dt):
        if self.shake_timer > 0: self.shake_timer -= dt
        if self.flash_alpha > 0: self.flash_alpha = max(0, self.flash_alpha - 1000 * dt)
        
        if self.ghost_timer > 0:
            self.ghost_timer -= dt

        if time.time() > self.next_powerup_time:
            self.spawn_powerup()
            self.next_powerup_time = time.time() + random.uniform(15, 30) 
        
        for p in self.powerups[:]:
            p.update(dt)
            if p.timer <= 0: self.powerups.remove(p)

        expired_effects = []
        for effect, timer in self.active_effects.items():
            self.active_effects[effect] -= dt
            if self.active_effects[effect] <= 0:
                expired_effects.append(effect)
        
        for ef in expired_effects:
            del self.active_effects[ef]
            head_px = grid_to_pixel(self.snake[0])
            msg = "SHIELD EXPIRED" if ef == "SHIELD" else f"{POWERUP_TYPES[ef]['LABEL']} END"
            self.floating_texts.append(FloatingText(msg, (head_px[0], head_px[1]-20), (200, 200, 200), 0.5))

        if time.time() - self.last_eat_time > COMBO_WINDOW and self.combo_count > 1:
            self.combo_count = 0
            self.combo_multiplier = 1.0

        for ft in self.floating_texts[:]:
            ft.update(dt)
            if ft.life <= 0: self.floating_texts.remove(ft)

        if self.rules.get("SURVIVAL_ACTIVE", False) and not self.game_over:
            decay_factor = 1.0
            if self.active_effects.get("SLOW", 0) > 0:
                decay_factor = 0.4
            
            self.hunger_timer = max(0, self.hunger_timer - (dt * decay_factor))
            
            if self.hunger_timer == 0: 
                if self.active_effects.get("SHIELD", 0) > 0:
                    self.active_effects["SHIELD"] = 0
                    self.hunger_timer = self.survival_timer_duration 
                    play_sound("eat") 
                    head_px = grid_to_pixel(self.snake[0])
                    self.floating_texts.append(FloatingText("SHIELD SAVED!", (head_px[0], head_px[1]-40), (0, 255, 255), 2.0))
                    self.ghost_timer = 2.0 
                else:
                    self.set_game_over()
        
        if self.rules.get("BOMBS_ACTIVE", False):
            for b in self.bombs[:]:
                b.update(dt)
                if b.exploding:
                    if not self.game_over: self.trigger_explosion(b)
                    if b.explosion_time <= 0 and b in self.bombs: self.bombs.remove(b)
        for p in self.particles[:]:
            p.update(dt)
            if p.life <= 0: self.particles.remove(p)

    def draw(self, screen, dt):
        surf = pygame.Surface((WIDTH, HEIGHT))
        
        surf.blit(self.background_img, (0, 0)) 
        
        surf.blit(self.border_img, (0, 0))
        
        for w in self.walls:
            x, y = grid_to_pixel(w)
            pygame.draw.rect(surf, WALL, (x, y, CELL, CELL), border_radius=4)
            
        for food in self.foods:
            x, y = grid_to_pixel(food["pos"])
            food_data = food["data"]
            if "IMAGE" in food_data: surf.blit(food_data["IMAGE"], (x, y))
            else:
                FOOD_COLOR = food_data.get("COLOR", (255, 0, 0))
                pygame.draw.rect(surf, FOOD_COLOR, (x, y, CELL, CELL), border_radius=8)
                pygame.draw.rect(surf, (255,255,255), (x+4, y+4, 6,6), border_radius=3)
        
        for p in self.powerups:
            p.draw(surf)

        if self.ghost_timer <= 0 or (int(time.time() * 15) % 2 == 0):
            is_sprite_skin = "head-up" in self.snake_skin
            if is_sprite_skin: self.draw_snake_sprites(surf)
            else: self.draw_snake_colors(surf)
        
        if self.active_effects.get("SHIELD", 0) > 0:
            head_px = grid_to_pixel(self.snake[0])
            cx, cy = head_px[0] + CELL//2, head_px[1] + CELL//2
            angle = time.time() * 5
            off_x = int(10 * pygame.math.Vector2(1,0).rotate(angle).x)
            off_y = int(10 * pygame.math.Vector2(1,0).rotate(angle).y)
            pygame.draw.circle(surf, (0, 255, 255), (cx, cy), CELL, 1)
            pygame.draw.circle(surf, (0, 255, 255), (cx+off_x, cy+off_y), 2)

        for b in self.bombs: b.draw(surf)
        for p in self.particles: p.draw(surf)
        
        for ft in self.floating_texts: ft.draw(surf)

        hud_surf = pygame.Surface((WIDTH, 36)) 
        hud_surf.fill((10, 10, 14)) 
        x_offset = 10
        y_padding = (36 - self.ICON_SIZE[1]) // 2 
        if self.icon_score: hud_surf.blit(self.icon_score, (x_offset, y_padding)); x_offset += self.ICON_SIZE[0] + 4
        hud_surf.blit(FONT.render(f"{self.score_food}", True, TEXT), (x_offset, 8)); x_offset += 80
        if self.icon_time: hud_surf.blit(self.icon_time, (x_offset, y_padding)); x_offset += self.ICON_SIZE[0] + 4
        hud_surf.blit(FONT.render(f"{self.elapsed()}s", True, TEXT), (x_offset, 8)); x_offset += 80
        
        hud_text = f"{self.player_name} | {self.current_mode} ({self.current_difficulty[0]}) | {self.current_map}"
        text_surf = FONT.render(hud_text, True, TEXT_DIM)
        text_rect = text_surf.get_rect(center=(WIDTH//2, 18))
        hud_surf.blit(text_surf, text_rect)

        p_offset_x = WIDTH - 30
        for ef_name, timer in self.active_effects.items():
            img = POWERUP_ASSETS.get(ef_name)
            if img:
                icon_scale = pygame.transform.scale(img, (24, 24))
                rect = icon_scale.get_rect(center=(p_offset_x, 14))
                hud_surf.blit(icon_scale, rect)
            else:
                data = POWERUP_TYPES[ef_name]
                pygame.draw.circle(hud_surf, data["COLOR"], (p_offset_x, 14), 10)

            max_duration = POWERUP_TYPES[ef_name]["DURATION"]
            ratio = max(0, timer / max_duration)
            bar_w = 24
            bar_h = 4
            pygame.draw.rect(hud_surf, (50, 50, 50), (p_offset_x - 12, 28, bar_w, bar_h))
            col = (0, 255, 0)
            if ratio < 0.5: col = (255, 255, 0)
            if ratio < 0.2: col = (255, 0, 0)
            pygame.draw.rect(hud_surf, col, (p_offset_x - 12, 28, int(bar_w * ratio), bar_h))
            p_offset_x -= 35

        surf.blit(hud_surf, (0,0))
        
        if self.rules.get("SURVIVAL_ACTIVE", False) and not self.game_over:
            ratio = self.hunger_timer / self.survival_timer_duration
            bar_width = int(WIDTH * 0.3) 
            current_width = int(bar_width * ratio)
            bar_x = WIDTH - bar_width - 10 
            bar_y = 45 
            pygame.draw.rect(surf, (50,30,30), (bar_x, bar_y, bar_width, 10), border_radius=4)
            bar_color = (0, 200, 0)
            if ratio < 0.5: bar_color = (255, 200, 0) 
            if ratio < 0.2: bar_color = (200, 0, 0) 
            pygame.draw.rect(surf, bar_color, (bar_x, bar_y, current_width, 10), border_radius=4)
        
        if self.combo_count > 1:
            combo_ratio = (COMBO_WINDOW - (time.time() - self.last_eat_time)) / COMBO_WINDOW
            if combo_ratio > 0:
                bar_x = WIDTH//2 - 50
                bar_y = 40
                combo_icon = POWERUP_ASSETS.get("DOUBLE")
                if combo_icon:
                    icon_surf = pygame.transform.scale(combo_icon, (20, 20))
                    surf.blit(icon_surf, (bar_x - 25, bar_y - 8))
                pygame.draw.rect(surf, (255, 215, 0), (bar_x, bar_y, int(100 * combo_ratio), 4))

        now = time.time()
        for pos, ts in self.death_log[-50:]:
            age = now - ts
            if age > 2: continue
            alpha = max(0, 255-int(age*120)) 
            s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
            s.fill((200,200,200, alpha))
            surf.blit(s, grid_to_pixel(pos))
            
        if self.game_over:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((BG2[0], BG2[1], BG2[2], 200))
            surf.blit(s, (0,0))
            go = BIG.render("GAME OVER", True, TEXT)
            rect = go.get_rect(center=(WIDTH//2, HEIGHT//2-40))
            surf.blit(go, rect)
            score_text = FONT.render(f"Score: {self.score_food}", True, TEXT)
            score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2+10))
            surf.blit(score_text, score_rect)
            info = FONT.render("Press R to Restart / ESC for Menu", True, TEXT_DIM)
            info_rect = info.get_rect(center=(WIDTH//2, HEIGHT//2+50))
            surf.blit(info, info_rect)
        
        shake_x, shake_y = 0, 0
        if self.shake_timer > 0:
            shake_x = random.randint(-int(self.shake_magnitude), int(self.shake_magnitude))
            shake_y = random.randint(-int(self.shake_magnitude), int(self.shake_magnitude))
        
        screen.blit(surf, (shake_x, shake_y))
        
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(min(255, int(self.flash_alpha)))
            screen.blit(flash_surf, (0, 0))

    def draw_snake_colors(self, surf):
        SNAKE_HEAD_COLOR = self.snake_skin["SNAKE_HEAD"]
        SNAKE_BODY_COLOR = self.snake_skin["SNAKE_BODY"]
        SNAKE_BODY_INNER_COLOR = self.snake_skin["SNAKE_BODY_INNER"]
        for idx, seg in enumerate(self.snake):
            x, y = grid_to_pixel(seg)
            if idx == 0: pygame.draw.rect(surf, SNAKE_HEAD_COLOR, (x, y, CELL, CELL), border_radius=8)
            else:
                pygame.draw.rect(surf, SNAKE_BODY_COLOR, (x, y, CELL, CELL), border_radius=6)
                pygame.draw.rect(surf, SNAKE_BODY_INNER_COLOR, (x+2, y+2, CELL-4, CELL-4), border_radius=6)

    def draw_snake_sprites(self, surf):
        for idx, seg in enumerate(self.snake):
            x, y = grid_to_pixel(seg)
            if idx == 0:
                dx, dy = self.snake_dir
                if   (dx, dy) == (1, 0):  sprite = self.snake_skin["head-right"]
                elif (dx, dy) == (-1, 0): sprite = self.snake_skin["head-left"]
                elif (dx, dy) == (0, 1):  sprite = self.snake_skin["head-down"]
                else:                     sprite = self.snake_skin["head-up"]
            elif idx == len(self.snake) - 1:
                prev_seg = self.snake[idx - 1]
                dx = prev_seg[0] - seg[0]; dy = prev_seg[1] - seg[1]
                if   (dx, dy) == (1, 0):  sprite = self.snake_skin["tail-right"]
                elif (dx, dy) == (-1, 0): sprite = self.snake_skin["tail-left"]
                elif (dx, dy) == (0, 1):  sprite = self.snake_skin["tail-down"]
                else:                     sprite = self.snake_skin["tail-up"]
            else:
                prev_seg = self.snake[idx + 1]; next_seg = self.snake[idx - 1]
                v_in  = (seg[0] - prev_seg[0], seg[1] - prev_seg[1])
                v_out = (next_seg[0] - seg[0],  next_seg[1] - seg[1])
                if v_in != v_out:
                    if (v_in == (0, -1) and v_out == (-1, 0)) or (v_in == (1, 0) and v_out == (0, 1)): sprite = self.snake_skin["body-up-left"]
                    elif (v_in == (0, -1) and v_out == (1, 0)) or (v_in == (-1, 0) and v_out == (0, 1)): sprite = self.snake_skin["body-up-right"]
                    elif (v_in == (0, 1) and v_out == (-1, 0)) or (v_in == (1, 0) and v_out == (0, -1)): sprite = self.snake_skin["body-down-left"]
                    elif (v_in == (0, 1) and v_out == (1, 0)) or (v_in == (-1, 0) and v_out == (0, -1)): sprite = self.snake_skin["body-down-right"]
                    else: sprite = self.snake_skin["body-horizontal"] 
                else:
                    if v_in[1] == 0: sprite = self.snake_skin["body-horizontal"]
                    else: sprite = self.snake_skin["body-vertical"]
            surf.blit(sprite, (x, y))