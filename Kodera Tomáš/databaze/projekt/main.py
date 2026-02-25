import pygame
import sys
import random
import math
import os
import requests
import json

# === TŘÍDA PRO KREV ===
class BloodSplat:
    def __init__(self, x, y, images):
        # Vybere náhodný obrázek ze seznamu (u tebe je v seznamu jen jeden)
        self.original_image = random.choice(images)
        
        # Náhodná rotace a velikost pro každý cákanec
        angle = random.randint(0, 360)
        scale = random.uniform(0.1, 0.2)
        
        self.image = pygame.transform.rotozoom(self.original_image, angle, scale)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.alpha = 255  # Plná viditelnost na začátku
        self.fade_speed = 1

    def draw(self, surface):
        # Nastavení průhlednosti a vykreslení
        self.image.set_alpha(self.alpha)
        surface.blit(self.image, self.rect)

    def update(self):
        self.alpha -= self.fade_speed
        return self.alpha > 0

# === FUNKCE PRO SERVER ===
def send_score_to_server(username, score):
    url = "http://127.0.0.1:8000/api/update_score/"
    data = {"username": username, "score": score}
    try:
        response = requests.post(url, json=data)
        print(f"Server response: {response.status_code}")
    except Exception as e:
        print(f"Server error: {e}")

# === OSTATNÍ POMOCNÉ FUNKCE ===
def load_animation(path):
    frames = []
    if not os.path.exists(path):
        return frames
    for filename in sorted(os.listdir(path)):
        if filename.endswith(".png"):
            frame = pygame.image.load(os.path.join(path, filename)).convert_alpha()
            frames.append(frame)
    return frames

def death_screen(screen, font, score):
    while True:
        screen.fill((0, 0, 0))
        texts = [
            font.render("GAME OVER", True, (255, 0, 0)),
            font.render(f"Score: {score}", True, (255, 255, 255)),
            font.render("ENTER - New Game", True, (255, 255, 255)),
            font.render("ESC - Back to Menu", True, (255, 255, 255))
        ]
        for i, text in enumerate(texts):
            screen.blit(text, (800, 400 + i * 50))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: return "restart"
                if event.key == pygame.K_ESCAPE: return "menu"

# === HLAVNÍ HRA ===
def game_loop(current_user):
    pygame.init()

    # Nastavení okna (Musí být jako první!)
    WIDTH, HEIGHT = 1920, 1080
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Blood Dash Game")

    # Adresáře
    BASE_DIR = os.path.dirname(__file__)
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    
    BLOOD_PATH = os.path.join(ASSETS_DIR, "blood", "Bloodtrail.png")
    
    try:
        BLOOD_IMAGE = pygame.image.load(BLOOD_PATH).convert_alpha()
    except Exception as e:
        # Náhradní čtverec, kdyby to selhalo
        BLOOD_IMAGE = pygame.Surface((100, 100))
        BLOOD_IMAGE.fill((255, 0, 0))
    
    blood_list = []

    # Načtení animací
    animations = {
        "up": load_animation(os.path.join(ASSETS_DIR, "Hráč_nahoru")),
        "down": load_animation(os.path.join(ASSETS_DIR, "Hráč_dolu")),
        "left": load_animation(os.path.join(ASSETS_DIR, "Hráč_nalevo")),
        "right": load_animation(os.path.join(ASSETS_DIR, "Hráč_napravo")),
        "idle": load_animation(os.path.join(ASSETS_DIR, "Hráč_Idle"))
    }

    # Hráč a nepřátelé
    player_x, player_y = WIDTH // 2, HEIGHT // 2
    player_speed = 5
    dash_distance = 250
    dash_cooldown = 1000
    last_dash_time = -dash_cooldown
    enemy_size = 40
    direction = "down"
    state = "idle"
    current_frame = 0
    frame_delay = 100
    last_frame_update = pygame.time.get_ticks()

    enemies = []
    enemy_spawn_delay = 1000
    last_spawn_time = pygame.time.get_ticks()
    enemy_speed = 2
    SCORE = 0

    font = pygame.font.SysFont(None, 40)
    clock = pygame.time.Clock()

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # 1. LOGIKA POHYBU
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        moving = False
        dx, dy = 0, 0
        if keys[pygame.K_a]: dx -= 1; moving = True
        if keys[pygame.K_d]: dx += 1; moving = True
        if keys[pygame.K_w]: dy -= 1; moving = True
        if keys[pygame.K_s]: dy += 1; moving = True

        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx, dy = dx / length, dy / length
            player_x += dx * player_speed
            player_y += dy * player_speed

        if moving:
            if abs(dx) >= abs(dy): direction = "right" if dx > 0 else "left"
            else: direction = "down" if dy > 0 else "up"
            state = "walk"
        else: state = "idle"

        # 2. LOGIKA DASH + KREV
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0] and current_time - last_dash_time >= dash_cooldown:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dash_dx = mouse_x - player_x
            dash_dy = mouse_y - player_y
            dist = math.hypot(dash_dx, dash_dy)
            
            if dist != 0:
                dash_dx, dash_dy = dash_dx / dist, dash_dy / dist
                start_x, start_y = player_x, player_y
                
                # VYTVOŘENÍ KRVE (Před samotným skokem)
                for i in range(8):
                    spawn_x = start_x + (dash_dx * (i * 35))
                    spawn_y = start_y + (dash_dy * (i * 35))
                    blood_list.append(BloodSplat(spawn_x, spawn_y, [BLOOD_IMAGE]))

                player_x += dash_dx * dash_distance
                player_y += dash_dy * dash_distance
                last_dash_time = current_time

                # Zabíjení při dashi
                dash_rect = pygame.Rect(min(start_x, player_x), min(start_y, player_y), 
                                        abs(player_x - start_x) + 64, abs(player_y - start_y) + 64)
                for enemy in enemies[:]:
                    if dash_rect.colliderect(enemy['rect']):
                        enemies.remove(enemy)
                        SCORE += 1

        # 3. KONTROLA HRANIC A NEPŘÁTEL
        if current_time - last_spawn_time > enemy_spawn_delay:
            side = random.randint(0, 3)
            if side == 0: ex, ey = random.randint(0, WIDTH), -enemy_size # Nahoře
            elif side == 1: ex, ey = random.randint(0, WIDTH), HEIGHT + enemy_size # Dole
            elif side == 2: ex, ey = -enemy_size, random.randint(0, HEIGHT) # Vlevo
            else: ex, ey = WIDTH + enemy_size, random.randint(0, HEIGHT) # Vpravo
            
            enemies.append({'rect': pygame.Rect(ex, ey, enemy_size, enemy_size)})
            last_spawn_time = current_time

        # --- DRAWING (POŘADÍ VRSTEV) ---
        screen.fill((255, 255, 255)) # 1. BÍLÉ POZADÍ (úplně vespod)

        # 2. KREV (nad pozadím, pod hráčem)
        blood_list = [b for b in blood_list if b.update()]
        for b in blood_list:
            b.draw(screen)

        # 3. HRÁČ
        now = pygame.time.get_ticks()
        if now - last_frame_update > frame_delay:
            frames = animations.get(direction if state == "walk" else "idle", [])
            if frames: current_frame = (current_frame + 1) % len(frames)
            last_frame_update = now
            
        frames = animations.get(direction if state == "walk" else "idle", [])
        if frames:
            image = frames[current_frame % len(frames)]
            screen.blit(image, (player_x, player_y))
            player_rect = pygame.Rect(player_x, player_y, image.get_width(), image.get_height())
        else:
            player_rect = pygame.Rect(player_x, player_y, 64, 64)

        # 4. NEPŘÁTELÉ
        for i, enemy in enumerate(enemies[:]):
            enemy_rect = enemy['rect']
            
            # 1. Pohyb směrem k hráči (původní logika)
            ex, ey = player_x - enemy_rect.x, player_y - enemy_rect.y
            d = math.hypot(ex, ey)
            if d != 0:
                move_x = (ex / d) * enemy_speed
                move_y = (ey / d) * enemy_speed
                
                # Předběžný posun
                enemy_rect.x += move_x
                enemy_rect.y += move_y

            # 2. KOLIZE MEZI NEPŘÁTELI (Odtlačování)
            # Procházíme ostatní nepřátele a kontrolujeme, jestli se nepřekrývají
            for j, other_enemy in enumerate(enemies):
                if i != j:  # Nekontroluj kolizi sám se sebou
                    if enemy_rect.colliderect(other_enemy['rect']):
                        # Pokud dojde ke kolizi, odtlač nepřítele zpět
                        # Vypočítáme směr odtlačení
                        diff_x = enemy_rect.x - other_enemy['rect'].x
                        diff_y = enemy_rect.y - other_enemy['rect'].y
                        dist_diff = math.hypot(diff_x, diff_y)
                        
                        if dist_diff < enemy_size: # enemy_size je 40
                            if dist_diff == 0: # Pokud jsou přesně na sobě
                                enemy_rect.x += random.choice([-1, 1])
                            else:
                                # Odtlačení o malý kousek
                                enemy_rect.x += (diff_x / dist_diff) * 2
                                enemy_rect.y += (diff_y / dist_diff) * 2

            # Vykreslení nepřítele
            pygame.draw.rect(screen, (0, 0, 255), enemy_rect)

            # Kontrola kolize s hráčem
            if player_rect.colliderect(enemy_rect):
                send_score_to_server(current_user, SCORE)
                return death_screen(screen, font, SCORE)
        

        # UI
        cooldown_text = font.render(f"Dash cooldown: {max(0, (dash_cooldown-(current_time-last_dash_time))/1000):.1f}s", True, (0,0,0))
        screen.blit(cooldown_text, (10, 10))
        screen.blit(font.render(f"Score: {SCORE}", True, (0,0,0)), (10, 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "guest"
    game_loop(username)