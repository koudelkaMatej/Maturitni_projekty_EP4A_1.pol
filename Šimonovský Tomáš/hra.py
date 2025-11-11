import pygame
import random
import math
import struct
import sys
from pygame.locals import *

# --------- Nastavení ---------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 400
GROUND_Y = 300
FPS = 60

# Hráč
PLAYER_W = 70
PLAYER_H = 80
DUCK_H = 30

# Překážky
OBSTACLE_MIN_W = 60
OBSTACLE_MAX_W = 60
OBSTACLE_MIN_H = 70
OBSTACLE_MAX_H = 70
SPAWN_INTERVAL = 2000  # ms

# Barvy
WHITE = (255, 255, 255)
BLACK = (25, 25, 25)
BLUE1 = (0, 120, 215)
BG = (240, 249, 255)

# --------- Inicializace pygame ---------
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("JumpRex - Skákačka")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20)
big_font = pygame.font.SysFont("arial", 36)

# --------- Zvuky ---------
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()

def make_beep(freq=440, duration_ms=120, volume=0.5):
    sample_rate = 44100
    amplitude = int(32767 * volume)
    n_samples = int(sample_rate * duration_ms / 1000.0)
    buf = bytearray()
    for i in range(n_samples):
        t = float(i) / sample_rate
        value = int(amplitude * math.sin(2.0 * math.pi * freq * t) * (1 - (i / n_samples) * 0.8))
        buf += struct.pack('<h', value)
    return pygame.mixer.Sound(buffer=bytes(buf))

jump_sound = make_beep(650, 90, 0.4)
hit_sound = make_beep(120, 220, 0.6)
master_volume = 0.05
jump_sound.set_volume(master_volume)
hit_sound.set_volume(master_volume)

# --------- Třídy ---------
class Player:
    def __init__(self):
        self.w = PLAYER_W
        self.h = PLAYER_H
        self.x = 80
        self.y = GROUND_Y - self.h
        self.vel_y = 0
        self.on_ground = True
        self.ducking = False
        self.gravity = 1400
        self.jump_speed = -520

        # 🖼️ Vlastní obrázek hráče (player.png)
        try:
            self.image = pygame.image.load("kovboj.png").convert_alpha()
        except:
            self.image = None
            self.color = (60, 60, 60)

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h if not self.ducking else DUCK_H)

    def get_mask(self):
        if self.image:
            current_h = self.h if not self.ducking else DUCK_H
            scaled_img = pygame.transform.scale(self.image, (self.w, current_h))
            return pygame.mask.from_surface(scaled_img)
        return None

    def update(self, dt):
        if not self.on_ground:
            self.vel_y += self.gravity * dt
            self.y += self.vel_y * dt
            if self.y >= GROUND_Y - (self.h if not self.ducking else DUCK_H):
                self.y = GROUND_Y - (self.h if not self.ducking else DUCK_H)
                self.vel_y = 0
                self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_speed
            self.on_ground = False
            jump_sound.play()

    def duck(self, enable):
        if enable and self.on_ground:
            if not self.ducking:
                # posun dolů o rozdíl výšek
                self.y += (self.h - DUCK_H)
            self.ducking = True
        else:
            if self.ducking:
                # vrátit y zpět nahoru, když přestaneme skrčovat
                self.y -= (self.h - DUCK_H)
            self.ducking = False
            if self.on_ground:
                self.y = GROUND_Y - self.h

    def draw(self, surf):
        r = self.rect()
        if self.image:
            current_h = self.h if not self.ducking else DUCK_H
            img = pygame.transform.scale(self.image, (self.w, current_h))
            surf.blit(img, (self.x, self.y))
        else:
            pygame.draw.rect(surf, self.color, r)

class Obstacle:
    def __init__(self, x, w, h, speed):
        self.x = x
        self.w = w
        self.h = h
        self.y = GROUND_Y - h
        self.speed = speed

        # 🖼️ Načti překážku (obstacle1.png, obstacle2.png)
        possible_images = ["bedna.png", "benda.png"]
        self.image = None
        for path in possible_images:
            try:
                self.image = pygame.image.load(path).convert_alpha()
                break
            except:
                continue

        if not self.image:
            self.color = (80, 30, 30)

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def get_mask(self):
        if self.image:
            scaled_img = pygame.transform.scale(self.image, (self.w, self.h))
            return pygame.mask.from_surface(scaled_img)
        return None

    def update(self, dt):
        self.x -= self.speed * dt

    def draw(self, surf):
        if self.image:
            img = pygame.transform.scale(self.image, (self.w, self.h))
            surf.blit(img, (self.x, self.y))
        else:
            pygame.draw.rect(surf, self.color, self.rect())

# --------- Pomocné funkce ---------
def spawn_obstacle(speed):
    w = random.randint(OBSTACLE_MIN_W, OBSTACLE_MAX_W)
    h = random.randint(OBSTACLE_MIN_H, OBSTACLE_MAX_H)
    return Obstacle(SCREEN_WIDTH + 10, w, h, speed)

def reset_game():
    player = Player()
    obstacles = []
    score = 0
    speed = 300
    next_spawn = pygame.time.get_ticks() + SPAWN_INTERVAL
    return player, obstacles, score, speed, next_spawn

# --------- UI prvky ---------
class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text

    def draw(self, surf):
        pygame.draw.rect(surf, BLUE1, self.rect, border_radius=8)
        label = big_font.render(self.text, True, WHITE)
        surf.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

class Slider:
    def __init__(self, x, y, w, value=0.7):
        self.x = x
        self.y = y
        self.w = w
        self.h = 8
        self.handle_r = 10
        self.value = max(0.0, min(1.0, value))
        self.dragging = False

    def rect(self):
        return pygame.Rect(self.x, self.y - self.h // 2, self.w, self.h)

    def handle_pos(self):
        return (int(self.x + self.value * self.w), self.y)

    def draw(self, surf):
        pygame.draw.rect(surf, (200,200,200), self.rect(), border_radius=4)
        filled = pygame.Rect(self.x, self.y - self.h // 2, int(self.w * self.value), self.h)
        pygame.draw.rect(surf, (0,160,255), filled, border_radius=4)
        hx, hy = self.handle_pos()
        pygame.draw.circle(surf, (60,60,60), (hx, hy), self.handle_r)
        t = font.render(f"Hlasitost: {int(self.value * 100)}%", True, BLACK)
        surf.blit(t, (self.x + self.w + 14, self.y - 12))

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            hx, hy = self.handle_pos()
            if pygame.Vector2(event.pos).distance_to((hx, hy)) <= self.handle_r + 4:
                self.dragging = True
                return True
        if event.type == MOUSEBUTTONUP:
            self.dragging = False
        if event.type == MOUSEMOTION and self.dragging:
            mx = event.pos[0]
            rel = (mx - self.x) / self.w
            self.value = max(0.0, min(1.0, rel))
            return True
        return False

# --------- Hlavní smyčka ---------
def main():
    global master_volume
    running = True
    game_state = "menu"  # menu / playing / paused
    high_score = 0
    pygame.mixer.music.load("music.mp3")  # nebo cesta k souboru
    pygame.mixer.music.set_volume(master_volume)  # nastavit hlasitost podle slideru
    pygame.mixer.music.play(-1)  # -1 znamená nekonečný loop


    start_btn = Button((SCREEN_WIDTH//2 - 100, 120, 200, 56), "Spustit hru")
    volume_slider = Slider(SCREEN_WIDTH//2 - 120, 220, 240, master_volume)
    resume_btn = Button((SCREEN_WIDTH//2 - 100, 170, 200, 56), "Pokračovat")
    menu_btn = Button((SCREEN_WIDTH//2 - 100, 240, 200, 56), "Návrat do menu")

    player, obstacles, score, speed, next_spawn = reset_game()

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ---- MENU ----
            if game_state == "menu":
                if event.type == MOUSEBUTTONDOWN:
                    if start_btn.clicked(event.pos):
                        game_state = "playing"
                        player, obstacles, score, speed, next_spawn = reset_game()
                    volume_slider.handle_event(event)
                elif event.type == MOUSEMOTION:
                    # změna hlasitosti pouze pokud právě táhneš slider (dragging)
                    if volume_slider.dragging:
                        volume_slider.handle_event(event)
                elif event.type == MOUSEBUTTONUP:
                    volume_slider.handle_event(event)

                master_volume = volume_slider.value
                jump_sound.set_volume(master_volume)
                hit_sound.set_volume(master_volume)
                pygame.mixer.music.set_volume(master_volume)


            # ---- HRANÍ ----
            elif game_state == "playing":
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        game_state = "paused"
                    elif event.key in (K_SPACE, K_UP):
                        player.jump()
                    elif event.key == K_DOWN:
                        player.duck(True)
                elif event.type == KEYUP:
                    if event.key == K_DOWN:
                        player.duck(False)

            # ---- PAUZA ----
            elif game_state == "paused":
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    game_state = "playing"
                elif event.type == MOUSEBUTTONDOWN:
                    if resume_btn.clicked(event.pos):
                        game_state = "playing"
                    elif menu_btn.clicked(event.pos):
                        game_state = "menu"

        # --- UPDATE ---
        if game_state == "playing":
            player.update(dt)
            now = pygame.time.get_ticks()
            if now >= next_spawn:
                obstacles.append(spawn_obstacle(speed))
                adj = max(650, SPAWN_INTERVAL - (speed - 300) * 2)
                next_spawn = now + int(adj)
            for obs in list(obstacles):
                obs.update(dt)
                if obs.x + obs.w < -20:
                    obstacles.remove(obs)
                    score += 10

            # kolize pomocí masek
            p_rect = player.rect()
            p_mask = player.get_mask()
            for obs in obstacles:
                o_rect = obs.rect()
                o_mask = obs.get_mask()
                if p_mask and o_mask:
                    offset = (int(o_rect.x - p_rect.x), int(o_rect.y - p_rect.y))
                    if p_mask.overlap(o_mask, offset):
                        hit_sound.play()
                        if score > high_score:
                            high_score = score
                        game_state = "menu"
                        break

            # zvýšení rychlosti
            speed = 300 + (score // 50) * 20
            for obs in obstacles:
                obs.speed = speed
            score += int(40 * dt)

        # --- KRESLENÍ ---
        screen.fill(BG)
        pygame.draw.rect(screen, (230, 245, 255), (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))

        if game_state == "menu":
            title = big_font.render("JumpRex", True, BLACK)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 40))
            start_btn.draw(screen)
            volume_slider.draw(screen)
            info = font.render("↑/Mezerník = skok, ↓ = skrčit, ESC = pauza", True, BLACK)
            screen.blit(info, (SCREEN_WIDTH//2 - info.get_width()//2, 280))
            hs = font.render(f"High score: {high_score}", True, BLACK)
            screen.blit(hs, (20, 20))

        elif game_state == "playing":
            player.draw(screen)
            for obs in obstacles:
                obs.draw(screen)
            score_surf = font.render(f"Skóre: {score}", True, BLACK)
            screen.blit(score_surf, (SCREEN_WIDTH - 180, 16))
            speed_surf = font.render(f"Rychlost: {int(speed)}", True, BLACK)
            screen.blit(speed_surf, (SCREEN_WIDTH - 220, 40))

        elif game_state == "paused":
            player.draw(screen)
            for obs in obstacles:
                obs.draw(screen)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            text = big_font.render("⏸ PAUZA", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 80))
            resume_btn.draw(screen)
            menu_btn.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
