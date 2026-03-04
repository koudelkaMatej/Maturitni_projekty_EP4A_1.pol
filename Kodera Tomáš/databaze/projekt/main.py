import pygame
import sys
import random
import math
import os
import requests
import json

# === TŘÍDA PRO KREV ===
class BloodSplat:
    def __init__(self, x, y, images, angle):
        # Vybere náhodný obrázek ze seznamu (u tebe je v seznamu jen jeden)
        self.original_image = random.choice(images)
        
        # Náhodná rotace a velikost pro každý cákanec
        final_angle = angle + random.randint(-10, 10)
        scale = random.uniform(0.2, 0.4)
        
        self.image = pygame.transform.rotozoom(self.original_image, final_angle, scale)
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


    BG_PATH = os.path.join(ASSETS_DIR, "background.png")

    try:
        # Načtení a transformace na velikost okna
        bg_image = pygame.image.load(BG_PATH).convert() # .convert() pro rychlejší vykreslování
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    except Exception as e:
        # Záložní barva, kdyby obrázek chyběl
        bg_image = pygame.Surface((WIDTH, HEIGHT))
        bg_image.fill((50, 50, 50))
    
    frenzy_overlay = pygame.Surface((WIDTH, HEIGHT))
    frenzy_overlay.fill((255, 0, 0))  # Světle modrá barva
    frenzy_overlay.set_alpha(60)
    
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
    enemy_size = 60
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
    combo_count = 0          
    frenzy_mode = False        
    frenzy_start_time = 0      
    frenzy_duration = 5000
    base_player_speed = 5
    combo = 0
    limit = 5

    font = pygame.font.SysFont(None, 40)
    clock = pygame.time.Clock()

    #enemy animace
    enemy_frames_right = [pygame.transform.scale(img, (enemy_size, enemy_size)) 
                      for img in load_animation(os.path.join(ASSETS_DIR, "enemy"))]

    enemy_frames_left = [pygame.transform.flip(frame, True, False) for frame in enemy_frames_right]

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
        
        if frenzy_mode:
            if current_time - frenzy_start_time < frenzy_duration:
                player_speed = base_player_speed * 1.5  # Hráč je o 50 % rychlejší
                enemy_speed = 1
                dash_cooldown = 600                       # Nepřátelé zpomalí na minimum
            else:
                frenzy_mode = False
                # Tady se vrátíme k logice rychlosti podle skóre, kterou už v kódu máš
        else:
            if SCORE >= 100: enemy_speed = 4
            elif SCORE >= 50: enemy_speed = 3
            else: enemy_speed = 2
        if not frenzy_mode:
            player_speed = base_player_speed
            dash_cooldown = 1000

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
                combo = 0
                dash_dx, dash_dy = dash_dx / dist, dash_dy / dist
                start_x, start_y = player_x, player_y
                dash_angle = -math.degrees(math.atan2(dash_dy, dash_dx))

                enemies.sort(key=lambda e: math.hypot(e['rect'].centerx - start_x, e['rect'].centery - start_y))
                
                # VYTVOŘENÍ KRVE (Před samotným skokem)
                for i in range(8):
                    spawn_x = start_x + (dash_dx * (i * 35))
                    spawn_y = start_y + (dash_dy * (i * 35))
                    blood_list.append(BloodSplat(spawn_x, spawn_y, [BLOOD_IMAGE], dash_angle))

                player_x += dash_dx * dash_distance
                player_y += dash_dy * dash_distance
                last_dash_time = current_time

                # Zabíjení při dashi
                dash_rect = pygame.Rect(min(start_x, player_x), min(start_y, player_y), 
                                        abs(player_x - start_x) + 64, abs(player_y - start_y) + 64)

                for enemy in enemies[:]:
                        if dash_rect.colliderect(enemy['rect']):
                            enemies.remove(enemy)
                            combo += 1
                        if combo >= limit:
                            break
                if combo > 0:
                    points_gained = sum(range(1, combo + 1))
                    SCORE += min(points_gained, 5) # Přičte body, ale maximálně 5
                if combo >=5:
                    combo_count += 1
                    if combo_count >=3:
                        frenzy_mode = True
                        frenzy_start_time = current_time
                        combo_count = 0

        # 3. KONTROLA HRANIC A NEPŘÁTEL
        if current_time - last_spawn_time > enemy_spawn_delay:
            side = random.randint(0, 3)
            if side == 0: ex, ey = random.randint(0, WIDTH), -enemy_size # Nahoře
            elif side == 1: ex, ey = random.randint(0, WIDTH), HEIGHT + enemy_size # Dole
            elif side == 2: ex, ey = -enemy_size, random.randint(0, HEIGHT) # Vlevo
            else: ex, ey = WIDTH + enemy_size, random.randint(0, HEIGHT) # Vpravo
            
            enemies.append({
            'rect': pygame.Rect(ex, ey, enemy_size, enemy_size),
            'frame': 0,
            'last_update': pygame.time.get_ticks(),
            'direction': 'right'
            })
            last_spawn_time = current_time

        # --- DRAWING (POŘADÍ VRSTEV) ---
        screen.blit(bg_image, (0, 0))
        if frenzy_mode:
            pulse = 60 + math.sin(pygame.time.get_ticks() * 0.005) * 30
            frenzy_overlay.set_alpha(int(pulse))
            screen.blit(frenzy_overlay, (0, 0))

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

            # 1. Nejprve vypočítáme pohyb (vektory ex, ey a move_x, move_y)
            ex, ey = player_x - enemy_rect.x, player_y - enemy_rect.y
            d = math.hypot(ex, ey)
            
            move_x, move_y = 0, 0  # Inicializace na nulu
            
            if d != 0:
                move_x = (ex / d) * enemy_speed
                move_y = (ey / d) * enemy_speed
                
                # Aplikace pohybu
                enemy_rect.x += move_x
                enemy_rect.y += move_y

            # 2. TEĎ už můžeme bezpečně použít move_x pro směr animace
            if move_x > 0:
                enemy['direction'] = 'right'
            elif move_x < 0:
                enemy['direction'] = 'left'

            # 3. Aktualizace snímku animace
            enemy_animation_delay = 100 
            if current_time - enemy['last_update'] > enemy_animation_delay:
                # Kontrola, zda seznam snímků není prázdný
                if enemy_frames_right:
                    enemy['frame'] = (enemy['frame'] + 1) % len(enemy_frames_right)
                enemy['last_update'] = current_time
            
            # 4. Odtlačování mezi nepřáteli (zůstává stejné)
            for j, other_enemy in enumerate(enemies):
                if i != j:
                    if enemy_rect.colliderect(other_enemy['rect']):
                        diff_x = enemy_rect.x - other_enemy['rect'].x
                        diff_y = enemy_rect.y - other_enemy['rect'].y
                        dist_diff = math.hypot(diff_x, diff_y)
                        
                        if dist_diff < enemy_size:
                            if dist_diff == 0:
                                enemy_rect.x += random.choice([-1, 1])
                            else:
                                enemy_rect.x += (diff_x / dist_diff) * 1.5
                                enemy_rect.y += (diff_y / dist_diff) * 1.5

            # 5. Vykreslení animovaného nepřítele
            current_list = enemy_frames_right if enemy['direction'] == 'right' else enemy_frames_left
            if current_list:
                # Ochrana proti indexu mimo rozsah
                idx = enemy['frame'] % len(current_list)
                screen.blit(current_list[idx], (enemy_rect.x, enemy_rect.y))
            else:
                # Záložní zobrazení, pokud obrázky chybí
                pygame.draw.rect(screen, (0, 0, 255), enemy_rect)

            # 6. Kontrola kolize s hráčem
            if player_rect.colliderect(enemy_rect):
                send_score_to_server(current_user, SCORE)
                return death_screen(screen, font, SCORE)
        

        # UI
        cooldown_text = font.render(f"Dash cooldown: {max(0, (dash_cooldown-(current_time-last_dash_time))/1000):.1f}s", True, (0,0,0))
        screen.blit(cooldown_text, (10, 10))
        screen.blit(font.render(f"Score: {SCORE}", True, (0,0,0)), (10, 40))
        if frenzy_mode:
            frenzy_ui_text = font.render("!!! FRENZY ACTIVE !!!", True, (0, 0, 0))
        else:
            frenzy_ui_text = font.render(f"Frenzy Charge: {combo_count}/3", True, (0, 0, 0))
        
        screen.blit(frenzy_ui_text, (10, 70))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "guest"
    game_loop(username)