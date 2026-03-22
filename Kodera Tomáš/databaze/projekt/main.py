import pygame
import sys
import random
import math
import os
import requests
import json
import threading

# === TŘÍDA PRO KREV ===
class BloodSplat:
    def __init__(self, x, y, images, angle):
        # Vybere náhodný obrázek ze seznamu (u tebe je v seznamu jen jeden)
        self.original_image = random.choice(images)
        
        # Přidá k úhlu dashe malou náhodu, aby to vypadalo přirozeně
        final_angle = angle + random.randint(-10, 10)
        # Náhodná velikost cákance (zmenšení na 20% až 40%)
        scale = random.uniform(0.2, 0.4)
        
        # Vytvoří otočený a zmenšený obrázek
        self.image = pygame.transform.rotozoom(self.original_image, final_angle, scale)
        # Vytvoří neviditelný obdélník pro umístění obrázku na střed (x, y)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.alpha = 255  # Průhlednost (255 = viditelný, 0 = průhledný)
        self.fade_speed = 1 # Rychlost mizení

    def draw(self, surface):
        # Nastavení průhlednosti a vykreslení
        self.image.set_alpha(self.alpha)
        # Vykreslí obrázek na daný povrch (screen)
        surface.blit(self.image, self.rect)

    def update(self):
        # S každým snímkem sníží průhlednost
        self.alpha -= self.fade_speed
        # Vrátí True, pokud je ještě vidět (aby ho hra nesmazala)
        return self.alpha > 0

# === FUNKCE PRO SERVER ===
def send_score_to_server(username, score):
    # Spuštěno v threadu, aby hra nezamrzla při čekání na API
    def post_request():
        url = "http://127.0.0.1:8000/api/update_score/"
        data = {"username": username, "score": score}
        try:
            # Pošle POST požadavek s daty, čeká max 3 sekundy
            requests.post(url, json=data, timeout=3)
        except Exception as e:
            # Pokud server neběží, vypíše chybu do konzole, ale neshodí hru
            print(f"Server error: {e}")
    
    # Spustí post_request na pozadí (v novém vlákně)
    threading.Thread(target=post_request, daemon=True).start()

# === OSTATNÍ POMOCNÉ FUNKCE ===
def load_animation(path):
    frames = []
    # Pokud složka neexistuje, vrátí prázdný seznam
    if not os.path.exists(path):
        return frames
    # Seřadí soubory podle názvu a načte všechny .png
    for filename in sorted(os.listdir(path)):
        if filename.endswith(".png"):
            # Načte obrázek a převede ho na formát vhodný pro Pygame
            frame = pygame.image.load(os.path.join(path, filename)).convert_alpha()
            frames.append(frame)
    return frames

def death_screen(screen, font, score):
    while True:
        screen.fill((0, 0, 0)) # Černá obrazovka
        # Příprava textů pro zobrazení
        texts = [
            font.render("GAME OVER", True, (255, 0, 0)),
            font.render(f"Score: {score}", True, (255, 255, 255)),
            font.render("ENTER - New Game", True, (255, 255, 255)),
            font.render("ESC - Back to Menu", True, (255, 255, 255))
        ]
        # Vykreslení textů pod sebe
        for i, text in enumerate(texts):
            screen.blit(text, (800, 400 + i * 50))

        pygame.display.flip() # Aktualizace obrazovky
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: return "restart" # Znovu do hry
                if event.key == pygame.K_ESCAPE: return "menu"    # Do menu


# === HLAVNÍ HRA ===
def game_loop(current_user):
    pygame.init() # Zapne motory Pygame

    WIDTH, HEIGHT = 1920, 1080 # Rozlišení
    # Vytvoření okna na celou obrazovku
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Blood Dash Game")

    # Cesty k souborům
    BASE_DIR = os.path.dirname(__file__)
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    BG_PATH = os.path.join(ASSETS_DIR, "background.png")

    try:
        # Načtení pozadí a roztažení na celé okno
        bg_image = pygame.image.load(BG_PATH).convert()
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    except Exception as e:
        # Pokud chybí obrázek, udělá šedé pozadí
        bg_image = pygame.Surface((WIDTH, HEIGHT))
        bg_image.fill((50, 50, 50))
    
    # Červený filtr pro Frenzy mód
    frenzy_overlay = pygame.Surface((WIDTH, HEIGHT))
    frenzy_overlay.fill((255, 0, 0))
    frenzy_overlay.set_alpha(60) # Průhlednost filtru
    
    BLOOD_PATH = os.path.join(ASSETS_DIR, "blood", "Bloodtrail.png")
    try:
        BLOOD_IMAGE = pygame.image.load(BLOOD_PATH).convert_alpha()
    except Exception as e:
        BLOOD_IMAGE = pygame.Surface((100, 100))
        BLOOD_IMAGE.fill((255, 0, 0))
    
    blood_list = [] # Seznam všech cákanců na zemi

    # Slovník se všemi animacemi hráče
    animations = {
        "up": load_animation(os.path.join(ASSETS_DIR, "Hráč_nahoru")),
        "down": load_animation(os.path.join(ASSETS_DIR, "Hráč_dolu")),
        "left": load_animation(os.path.join(ASSETS_DIR, "Hráč_nalevo")),
        "right": load_animation(os.path.join(ASSETS_DIR, "Hráč_napravo")),
        "idle": load_animation(os.path.join(ASSETS_DIR, "Hráč_Idle"))
    }
    

    player_x, player_y = WIDTH // 2, HEIGHT // 2 # Start uprostřed
    player_speed = 5
    dash_distance = 250 # Jak daleko skočíš
    dash_cooldown = 1000 # Čekání na další skok (1 sekunda)
    last_dash_time = -dash_cooldown # Aby mohl skočit hned na začátku
    enemy_size = 60
    direction = "down" # Výchozí směr pohledu
    state = "idle"     # Výchozí stav (stojí)
    current_frame = 0  # Který obrázek animace hraje
    frame_delay = 100  # Rychlost animace v ms
    last_frame_update = pygame.time.get_ticks() # Čas poslední změny obrázku

    enemies = [] # Seznam živých nepřátel
    enemy_spawn_delay = 1000 # Nový nepřítel každou sekundu
    last_spawn_time = pygame.time.get_ticks()
    enemy_speed = 2
    SCORE = 0
    combo_count = 0 # Nabíjení Frenzy (kolikrát jsi udělal combo 5+)
    frenzy_mode = False
    frenzy_start_time = 0
    frenzy_duration = 5000 # Frenzy trvá 5 sekund
    base_player_speed = 5
    combo = 0 # Kolik nepřátel jsi zabil jedním dashem
    limit = 5 # Limit pro jedno combo

    font = pygame.font.SysFont(None, 40) # Písmo pro UI
    clock = pygame.time.Clock() # Pro hlídání FPS

    # Načtení animací nepřítele (pravá a otočená levá)
    enemy_frames_right = [pygame.transform.scale(img, (enemy_size, enemy_size)) 
                      for img in load_animation(os.path.join(ASSETS_DIR, "enemy"))]
    enemy_frames_left = [pygame.transform.flip(frame, True, False) for frame in enemy_frames_right]

    running = True
    while running:
        current_time = pygame.time.get_ticks() # Aktuální čas od startu programu
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Zavření křížkem
                pygame.quit(); sys.exit()

        # --- POHYB ---
        keys = pygame.key.get_pressed()
        moving = False
        dx, dy = 0, 0
        if keys[pygame.K_a]: dx -= 1; moving = True
        if keys[pygame.K_d]: dx += 1; moving = True
        if keys[pygame.K_w]: dy -= 1; moving = True
        if keys[pygame.K_s]: dy += 1; moving = True

        if dx != 0 or dy != 0:
            # Normalizace vektoru (aby nebyl rychlejší šikmo)
            length = math.hypot(dx, dy)
            dx, dy = dx / length, dy / length
            player_x += dx * player_speed
            player_y += dy * player_speed

        # Aktualizace kolizního obdélníku hráče podle jeho aktuální pozice
        player_rect = pygame.Rect(player_x, player_y, 64, 64)
        
        #abilitka - ability_cooldown = 5000
                    #last_ability_time = -ability_cooldown
                    #ability_range = 200
        
        #if keys[pygame.K_e] and current_time - last_ability_time >= ability_cooldown:
            #for enemy in enemies[:]:
                #dist = math.hypot(enemy['rect'].centerx - (player_x + 32), 
                                #enemy['rect'].centery - (player_y + 32))
                #if dist < ability_range:
                    #enemies.remove(enemy)
                    #SCORE += 1
                    #blood_list.append(BloodSplat(enemy['rect'].centerx, enemy['rect'].centery, [BLOOD_IMAGE], 0))
            #last_ability_time = current_time

        #ability_elapsed = current_time - last_ability_time
        #if ability_elapsed < 300: # Kruh bude vidět 300ms
            #s = pygame.Surface((ability_range * 2, ability_range * 2), pygame.SRCALPHA)
            #alpha = 255 - (ability_elapsed * 0.8) # Postupně mizí
            #pygame.draw.circle(s, (255, 255, 255, int(alpha)), (ability_range, ability_range), ability_range, 5)
            #screen.blit(s, (player_x + 32 - ability_range, player_y + 32 - ability_range))
            
        # --- FRENZY LOGIKA ---
        if frenzy_mode:
            if current_time - frenzy_start_time < frenzy_duration:
                player_speed = base_player_speed * 1.5 # Super rychlost
                enemy_speed = 1 # Nepřátelé zpomalí
                dash_cooldown = 600 # Rychlejší dash
            else:
                frenzy_mode = False # Konec frenzy
        else:
            # Postupné zrychlování nepřátel podle skóre
            if SCORE >= 100: enemy_speed = 4
            elif SCORE >= 50: enemy_speed = 3
            else: enemy_speed = 2
            player_speed = base_player_speed
            dash_cooldown = 1000

        # Určení směru pro animaci
        if moving:
            if abs(dx) >= abs(dy): direction = "right" if dx > 0 else "left"
            else: direction = "down" if dy > 0 else "up"
            state = "walk"
        else: state = "idle"

        # --- DASH (SKOK) ---
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0] and current_time - last_dash_time >= dash_cooldown:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Výpočet směru k myši
            dash_dx = mouse_x - player_x
            dash_dy = mouse_y - player_y
            dist = math.hypot(dash_dx, dash_dy)
            
            if dist != 0:
                combo = 0
                dash_dx, dash_dy = dash_dx / dist, dash_dy / dist # Směr na 1 jednotku
                start_x, start_y = player_x, player_y
                # Úhel pro otočení krve
                dash_angle = -math.degrees(math.atan2(dash_dy, dash_dx))

                # Seřazení nepřátel od nejbližšího (pro efektivitu zabíjení v řadě)
                enemies.sort(key=lambda e: math.hypot(e['rect'].centerx - start_x, e['rect'].centery - start_y))
                
                # Vytvoření 8 cákanců krve podél dráhy skoku
                for i in range(8):
                    spawn_x = start_x + (dash_dx * (i * 35))
                    spawn_y = start_y + (dash_dy * (i * 35))
                    blood_list.append(BloodSplat(spawn_x, spawn_y, [BLOOD_IMAGE], dash_angle))

                # Samotný teleport hráče
                player_x += dash_dx * dash_distance
                player_y += dash_dy * dash_distance
                last_dash_time = current_time

                # Vytvoří obdélník útoku (pokrývá celou cestu skoku)
                dash_rect = pygame.Rect(min(start_x, player_x), min(start_y, player_y), 
                                        abs(player_x - start_x) + 64, abs(player_y - start_y) + 64)

                # Kontrola, koho jsi dáshem trefil
                for enemy in enemies[:]:
                        if dash_rect.colliderect(enemy['rect']):
                            enemies.remove(enemy)
                            combo += 1
                        if combo >= limit: break # Max 5 najednou
                
                if combo > 0:
                    # Výpočet bodů (bonus za combo)
                    points_gained = sum(range(1, combo + 1))
                    SCORE += min(points_gained, 5) 
                
                if combo >= 5: # Pokud jsi zabil 5 nepřátel, nabije se frenzy
                    combo_count += 1
                    if combo_count >= 3:
                        frenzy_mode = True
                        frenzy_start_time = current_time
                        combo_count = 0

        # --- SPAWNOVÁNÍ NEPŘÁTEL ---
        if current_time - last_spawn_time > enemy_spawn_delay:
            side = random.randint(0, 3) # Vybere jednu ze 4 stran obrazovky
            if side == 0: ex, ey = random.randint(0, WIDTH), -enemy_size 
            elif side == 1: ex, ey = random.randint(0, WIDTH), HEIGHT + enemy_size 
            elif side == 2: ex, ey = -enemy_size, random.randint(0, HEIGHT) 
            else: ex, ey = WIDTH + enemy_size, random.randint(0, HEIGHT) 
            
            # Přidá nepřítele s jeho daty
            enemies.append({
            'rect': pygame.Rect(ex, ey, enemy_size, enemy_size),
            'frame': 0,
            'last_update': pygame.time.get_ticks(),
            'direction': 'right'
            })
            last_spawn_time = current_time

        # --- VYKRESLOVÁNÍ (BLIT) ---
        screen.blit(bg_image, (0, 0)) # Nejdřív pozadí
        
        if frenzy_mode:
            # Pulzování červeného filtru pomocí funkce sinus
            pulse = 60 + math.sin(pygame.time.get_ticks() * 0.005) * 30
            frenzy_overlay.set_alpha(int(pulse))
            screen.blit(frenzy_overlay, (0, 0))

        # Vykreslení a smazání staré krve
        blood_list = [b for b in blood_list if b.update()]
        for b in blood_list: b.draw(screen)

        # --- ANIMACE HRÁČE ---
        now = pygame.time.get_ticks()
        if now - last_frame_update > frame_delay:
            frames = animations.get(direction if state == "walk" else "idle", [])
            if frames: current_frame = (current_frame + 1) % len(frames)
            last_frame_update = now
            
        frames = animations.get(direction if state == "walk" else "idle", [])
        if frames:
            image = frames[current_frame % len(frames)]
            screen.blit(image, (player_x, player_y)) # Vykreslí hráče
            # Aktualizace velikosti rectu podle reálného obrázku
            player_rect = pygame.Rect(player_x, player_y, image.get_width(), image.get_height())
        else:
            player_rect = pygame.Rect(player_x, player_y, 64, 64)

        # --- LOGIKA A VYKRESLOVÁNÍ NEPŘÁTEL ---
        for i, enemy in enumerate(enemies[:]):
            enemy_rect = enemy['rect']

            # Pohyb nepřítele k hráči
            ex, ey = player_x - enemy_rect.x, player_y - enemy_rect.y
            d = math.hypot(ex, ey)
            move_x, move_y = 0, 0 
            
            if d != 0:
                move_x = (ex / d) * enemy_speed
                move_y = (ey / d) * enemy_speed
                enemy_rect.x += move_x
                enemy_rect.y += move_y

            # Směr pohledu nepřítele
            enemy['direction'] = 'right' if move_x > 0 else 'left'

            # Animace nepřítele
            if current_time - enemy['last_update'] > 100:
                if enemy_frames_right:
                    enemy['frame'] = (enemy['frame'] + 1) % len(enemy_frames_right)
                enemy['last_update'] = current_time
            
            # Kolize mezi nepřáteli (odtlačování, aby se neslepili do jednoho)
            for j, other_enemy in enumerate(enemies):
                if i != j:
                    if enemy_rect.colliderect(other_enemy['rect']):
                        diff_x = enemy_rect.x - other_enemy['rect'].x
                        diff_y = enemy_rect.y - other_enemy['rect'].y
                        dist_diff = math.hypot(diff_x, diff_y)
                        if dist_diff < enemy_size:
                            if dist_diff == 0: enemy_rect.x += random.choice([-1, 1])
                            else:
                                enemy_rect.x += (diff_x / dist_diff) * 1.5
                                enemy_rect.y += (diff_y / dist_diff) * 1.5

            # Vykreslení nepřítele
            current_list = enemy_frames_right if enemy['direction'] == 'right' else enemy_frames_left
            if current_list:
                idx = enemy['frame'] % len(current_list)
                screen.blit(current_list[idx], (enemy_rect.x, enemy_rect.y))

            # --- SMRT HRÁČE ---
            if player_rect.colliderect(enemy_rect):
                send_score_to_server(current_user, SCORE) # Pošle skóre
                return death_screen(screen, font, SCORE)  # Konec hry
        
        # --- UI (TEXTY NA OBRAZOVCE) ---
        cooldown_val = max(0, (dash_cooldown-(current_time-last_dash_time))/1000)
        cooldown_text = font.render(f"Dash cooldown: {cooldown_val:.1f}s", True, (0,0,0))
        screen.blit(cooldown_text, (10, 10))
        screen.blit(font.render(f"Score: {SCORE}", True, (0,0,0)), (10, 40))
        
        # Frenzy UI
        if frenzy_mode: frenzy_ui_text = font.render("!!! FRENZY ACTIVE !!!", True, (0, 0, 0))
        else: frenzy_ui_text = font.render(f"Frenzy Charge: {combo_count}/3", True, (0, 0, 0))
        screen.blit(frenzy_ui_text, (10, 70))

        pygame.display.flip() # Prohození bufferů (zobrazení nakresleného)
        clock.tick(60) # Omezení na 60 FPS

    pygame.quit()

# --- SPOUŠTĚČ ---
if __name__ == "__main__":
    # Načte jméno z argumentů (např. z jiného skriptu)
    username = sys.argv[1] if len(sys.argv) > 1 else "guest"
    while True:
        res = game_loop(username)
        if res != "restart": # Pokud hráč nedal restart, ukončí se smyčka
            break