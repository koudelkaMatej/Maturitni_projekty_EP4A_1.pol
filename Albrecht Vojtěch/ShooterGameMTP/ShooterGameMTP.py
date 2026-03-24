# --------------------------
# IMPORTY KNIHOVEN
# --------------------------
import unittest
import random
import pygame as pg
import requests 
import threading
import time
import static_ffmpeg
static_ffmpeg.add_paths()
from pyvidplayer2 import Video
 
# inicializace pygame
pg.init()
 
# --------------------------
# ZÁKLADNÍ ROZMĚRY
# --------------------------
BASE_WIDTH = 800
BASE_HEIGHT = 600
 
OKNO_SIRKA = 800
OKNO_VYSKA = 600
 
okno = pg.display.set_mode((OKNO_SIRKA, OKNO_VYSKA), pg.RESIZABLE)
game_surface = pg.Surface((BASE_WIDTH, BASE_HEIGHT))
pg.display.set_caption("ShooterGameMTP")
 
# --------------------------
# ROZLIŠENÍ (SETTINGS)
# --------------------------
RESOLUTIONS = [
    (800, 600),
    (1024, 768),
    (1280, 960)
]
 
# --------------------------
# NAČTENÍ ZDROJŮ
# --------------------------
try:
    video = Video("static/background_video.mp4")
    video.resize((800, 600))
except:
    video = None
 
try:
    original_background = pg.image.load("static/background.png").convert()
except:
    original_background = pg.Surface((800, 600))
    original_background.fill((30, 30, 30))
 
background = pg.transform.scale(original_background, (BASE_WIDTH, BASE_HEIGHT))
 
# Načtení srdce
heart_img = pg.image.load("sprites/heart.png").convert_alpha()
heart_img = pg.transform.scale(heart_img, (40, 40))
 
# --------------------------
# BARVY
# --------------------------
BILA = (250, 250, 250)
CERNA = (0, 0, 0)
MODRA = (0, 0, 255)
CERVENA = (255, 0, 0)
ZELENA = (0, 255, 0)
SEDA = (220, 220, 220)
TMAVA_SEDA = (180, 180, 180)
CYAN = (0, 255, 255)
PLASMA_PURPLE = (200, 0, 255)
 
# --------------------------
# RESIZE OKNA
# --------------------------
def resize_window(width, height):
    global OKNO_SIRKA, OKNO_VYSKA, okno
    OKNO_SIRKA, OKNO_VYSKA = width, height
    okno = pg.display.set_mode((OKNO_SIRKA, OKNO_VYSKA), pg.RESIZABLE)
 
# FPS kontrola
hodiny = pg.time.Clock()
FPS = 60
 
# --------------------------
# FONTY
# --------------------------
def update_fonts():
    global text1_font, text2_font, score_font, button_font
    text1_font = pg.font.Font("Audiowide-Regular.ttf", 45)
    text2_font = pg.font.Font("Audiowide-Regular.ttf", 30)
    score_font = pg.font.Font("Audiowide-Regular.ttf", 30)
    button_font = pg.font.Font("Audiowide-Regular.ttf", 30)
 
update_fonts()
 
# --------------------------
# STAVY HRY
# --------------------------
LOGIN, MENU, GAME, SCOREBOARD, SETTINGS, GAME_OVER = "login", "menu", "game", "scoreboard", "settings", "game_over"
current_state = LOGIN
 
# --------------------------
# API DATA
# --------------------------
BASE_URL = "http://127.0.0.1:5000/api"
logged_in_user_id = None
username_input = ""
password_input = ""
active_input = "username"
 
leaderboard_data = []
last_leaderboard_fetch = 0
 
# --------------------------
# GAME OVER DATA
# --------------------------
game_over_user = ""
game_over_score = 0
 
def show_game_over(player):
    global current_state, game_over_user, game_over_score
    game_over_user = username_input if logged_in_user_id else "HOST"
    game_over_score = player.skore
    current_state = GAME_OVER
 
# --------------------------
# API FUNKCE
# --------------------------
def login_thread(username, password):
    global logged_in_user_id, current_state
    try:
        resp = requests.post(f"{BASE_URL}/login",
                             json={"username": username, "password": password},
                             timeout=2).json()
        if resp.get("success"):
            logged_in_user_id = resp["user_id"]
            current_state = MENU
        else:
            print("Neplatné údaje")
    except:
        print("Server offline - vstup jako host")
        current_state = MENU
 
def fetch_leaderboard():
    global leaderboard_data
    try:
        resp = requests.get(f"{BASE_URL}/scoreboard", timeout=2)
        leaderboard_data = resp.json()
    except:
        pass
 
def submit_score(score):
    if logged_in_user_id is None:
        return
    try:
        requests.post(f"{BASE_URL}/submit_score",
                      json={"user_id": logged_in_user_id, "score": score},
                      timeout=2)
    except:
        pass
 
# --------------------------
# GLOBÁLNÍ NÁSOBITEL RYCHLOSTI NEPŘÁTEL
# --------------------------
enemy_speed_multiplier = 1
 
# --------------------------
# SLOW MOTION
# --------------------------
SLOW_DURATION = 5       # sekund
SLOW_COOLDOWN = 15      # sekund
slow_active = False
slow_timer = 0.0
slow_cooldown = SLOW_COOLDOWN   # cooldown začíná od začátku hry
 
# --------------------------
# HIT FLASH (červené zčervenání obrazovky)
# --------------------------
HIT_FLASH_DURATION = 0.4   # sekund jak dlouho efekt trvá
hit_flash_timer = 0.0      # odpočet
 
# --------------------------
# ZÁKLADNÍ TŘÍDA OBJEKTU
# --------------------------
class GameObject(pg.sprite.Sprite):
    def __init__(self, x, y, image_path=None, color=CERVENA, size=(50, 50)):
        super().__init__()
        self.image = pg.Surface(size)
        self.image.fill(color)
        if image_path:
            try:
                img = pg.image.load(image_path).convert_alpha()
                self.image = pg.transform.scale(img, size)
            except:
                pass
        self.rect = self.image.get_rect(topleft=(x, y))
 
# --------------------------
# HRÁČ
# --------------------------
class Hrac(GameObject):
    def __init__(self):
        super().__init__(50, BASE_HEIGHT//2, "sprites/hrac.png", MODRA, (70, 50))
        self.skore = 0
        self.rychlost = 7
        self.max_lives = 3
        self.lives = self.max_lives
 
    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_UP] and self.rect.top > 0:
            self.rect.y -= self.rychlost
        if keys[pg.K_DOWN] and self.rect.bottom < BASE_HEIGHT:
            self.rect.y += self.rychlost
        #if keys[pg.K_RIGHT] and self.rect.right < BASE_WIDTH:
           # self.rect.x += self.rychlost
       # if keys[pg.K_LEFT] and self.rect.left > 0:
            #self.rect.x -= self.rychlost
 
    def lose_life(self):
        global hit_flash_timer
        self.lives -= 1
        hit_flash_timer = HIT_FLASH_DURATION   # spustit flash efekt
        if self.lives <= 0:
            submit_score(self.skore)
            show_game_over(self)
 
# --------------------------
# NEPŘÁTELÉ
# --------------------------
class Enemy1(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, "sprites/enemy1.png", CERVENA, (50, 50))
        self.speed = random.randint(3, 4)
 
    def update(self):
        spd = self.speed * enemy_speed_multiplier * (0.5 if slow_active else 1)
        self.rect.x -= spd
        if self.rect.right < 0:
            self.kill()
 
class Enemy2(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, "sprites/enemy2.png", PLASMA_PURPLE, (50, 50))
        self.speed = 2
        self.shoot_cooldown = random.randint(60, 120)
        self.shoot_timer = 0
 
    def update(self):
        spd = self.speed * enemy_speed_multiplier * (0.5 if slow_active else 1)
        self.rect.x -= spd
        if self.rect.right < 0:
            self.kill()
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            self.shoot_cooldown = random.randint(60, 120)
            enemy_strela_group.add(EnemyStrela(self.rect.left, self.rect.centery))
 
# --------------------------
# STŘELY
# --------------------------
class Strela(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, "sprites/strela.png", ZELENA, (35, 10))
        self.speed = 12
 
    def update(self):
        self.rect.x += self.speed
        if self.rect.left > BASE_WIDTH:
            self.kill()
 
class EnemyStrela(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, "sprites/enemystrela.png", CERVENA, (40, 20))
        self.speed = 8
 
    def update(self):
        spd = self.speed * (0.5 if slow_active else 1)
        self.rect.x -= spd
        if self.rect.right < 0:
            self.kill()
 
# --------------------------
# HERNÍ FUNKCE
# --------------------------
def restart_game():
    global slow_active, slow_timer, slow_cooldown, hit_flash_timer
    slow_active = False
    slow_timer = 0.0
    slow_cooldown = SLOW_COOLDOWN
    hit_flash_timer = 0.0
    p = Hrac()
    return p, pg.sprite.Group(p), pg.sprite.Group(), pg.sprite.Group(), pg.sprite.Group()
 
def update_buttons():
    global buttons
    buttons = [
        {"text": "Start", "state": GAME, "rect": pg.Rect(250, 200, 300, 50)},
        {"text": "Tabulka", "state": SCOREBOARD, "rect": pg.Rect(250, 280, 300, 50)},
        {"text": "Nastaveni", "state": SETTINGS, "rect": pg.Rect(250, 360, 300, 50)},
        {"text": "Konec", "state": "quit", "rect": pg.Rect(250, 440, 300, 50)}
    ]
 
def update_settings_buttons():
    global settings_buttons
    settings_buttons = []
    for i, (w, h) in enumerate(RESOLUTIONS):
        settings_buttons.append({
            "text": f"{w} x {h}",
            "size": (w, h),
            "rect": pg.Rect(250, 200 + i*80, 300, 50)
        })
 
def draw_button(rect, text, m_pos):
    col = TMAVA_SEDA if rect.collidepoint(m_pos) else SEDA
    pg.draw.rect(game_surface, col, rect, border_radius=10)
    txt = button_font.render(text, True, CERNA)
    game_surface.blit(txt, (rect.centerx - txt.get_width()//2,
                            rect.centery - txt.get_height()//2))
 
# --------------------------
# START
# --------------------------
player, hrac_group, enemy_group, strela_group, enemy_strela_group = restart_game()
update_buttons()
update_settings_buttons()
 
SPAWN_EVENT = pg.USEREVENT + 1
pg.time.set_timer(SPAWN_EVENT, random.randint(2000, 3000))
 
running = True
 
# --------------------------
# HLAVNÍ LOOP
# --------------------------
while running:
    dt = hodiny.get_time() / 1000.0
 
    scale = min(OKNO_SIRKA / BASE_WIDTH, OKNO_VYSKA / BASE_HEIGHT)
    mouse = pg.mouse.get_pos()
    m_pos = (mouse[0] / scale, mouse[1] / scale)
 
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.VIDEORESIZE:
            resize_window(event.w, event.h)
            update_buttons()
            update_settings_buttons()
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if current_state == LOGIN:
                if pg.Rect(300, 450, 200, 50).collidepoint(m_pos):
                    threading.Thread(target=login_thread,
                                     args=(username_input, password_input),
                                     daemon=True).start()
            elif current_state == MENU:
                for b in buttons:
                    if b["rect"].collidepoint(m_pos):
                        if b["state"] == "quit":
                            running = False
                        elif b["state"] == GAME:
                            player, hrac_group, enemy_group, strela_group, enemy_strela_group = restart_game()
                            current_state = GAME
                        else:
                            current_state = b["state"]
            elif current_state == SETTINGS:
                for b in settings_buttons:
                    if b["rect"].collidepoint(m_pos):
                        resize_window(*b["size"])
                if pg.Rect(300, 520, 200, 50).collidepoint(m_pos):
                    current_state = MENU
            elif current_state == SCOREBOARD:
                if pg.Rect(300, 520, 200, 50).collidepoint(m_pos):
                    current_state = MENU
            elif current_state == GAME_OVER:
                new_game_rect = pg.Rect(250, 350, 300, 50)
                menu_rect = pg.Rect(250, 430, 300, 50)
                if new_game_rect.collidepoint(m_pos):
                    player, hrac_group, enemy_group, strela_group, enemy_strela_group = restart_game()
                    current_state = GAME
                elif menu_rect.collidepoint(m_pos):
                    current_state = MENU
        if event.type == pg.KEYDOWN:
            if current_state == LOGIN:
                if event.key == pg.K_RETURN:
                    threading.Thread(target=login_thread,
                                     args=(username_input, password_input),
                                     daemon=True).start()
                elif event.key == pg.K_TAB:
                    active_input = "password" if active_input == "username" else "username"
                elif event.key == pg.K_BACKSPACE:
                    if active_input == "username":
                        username_input = username_input[:-1]
                    else:
                        password_input = password_input[:-1]
                else:
                    if event.unicode.isprintable():
                        if active_input == "username":
                            username_input += event.unicode
                        else:
                            password_input += event.unicode
            if current_state == GAME and event.key == pg.K_SPACE:
                strela_group.add(Strela(player.rect.right, player.rect.centery))
            # --- SLOW MOTION aktivace klávesou S ---
            if current_state == GAME and event.key == pg.K_s:
                if not slow_active and slow_cooldown <= 0:
                    slow_active = True
                    slow_timer = SLOW_DURATION
                    slow_cooldown = SLOW_COOLDOWN
        if event.type == SPAWN_EVENT and current_state == GAME:
            if random.random() < 0.7:
                enemy_group.add(Enemy1(BASE_WIDTH, random.randint(50, BASE_HEIGHT-50)))
            if random.random() < 0.5:
                enemy_group.add(Enemy2(BASE_WIDTH, random.randint(50, BASE_HEIGHT-50)))
            pg.time.set_timer(SPAWN_EVENT, random.randint(2000, 3000))
 
    # --------------------------
    # UPDATE SLOW MOTION TIMERY
    # --------------------------
    if current_state == GAME:
        if slow_active:
            slow_timer -= dt
            if slow_timer <= 0:
                slow_active = False
                slow_timer = 0.0
        if slow_cooldown > 0:
            slow_cooldown -= dt
            if slow_cooldown < 0:
                slow_cooldown = 0.0
        if hit_flash_timer > 0:
            hit_flash_timer -= dt
            if hit_flash_timer < 0:
                hit_flash_timer = 0.0
 
    # --------------------------
    # DRAW
    # --------------------------
    game_surface.fill(CERNA)
 
    if current_state == LOGIN:
        if video:
            if not video.active:
                video.restart()
            video.draw(game_surface, (0, 0))
        game_surface.blit(button_font.render("LOGIN", True, BILA), (350, 100))
        u_col = MODRA if active_input == "username" else BILA
        p_col = MODRA if active_input == "password" else BILA
        game_surface.blit(button_font.render(f"User: {username_input}", True, u_col), (150, 250))
        game_surface.blit(button_font.render(f"Pass: {'*'*len(password_input)}", True, p_col), (150, 320))
        draw_button(pg.Rect(300, 450, 200, 50), "Login", m_pos)
    elif current_state == MENU:
        if video:
            if not video.active:
                video.restart()
            video.draw(game_surface, (0, 0))
        title = text1_font.render("SPACE SHOOTER", True, CYAN)
        game_surface.blit(title, (200, 70))
        for b in buttons:
            draw_button(b["rect"], b["text"], m_pos)
    elif current_state == GAME:
        game_surface.blit(background, (0, 0))
        hrac_group.update()
        enemy_group.update()
        strela_group.update()
        enemy_strela_group.update()
 
        # Kontrola kolizí - ztráta života
        if pg.sprite.spritecollide(player, enemy_group, True):
            player.lose_life()
        if pg.sprite.spritecollide(player, enemy_strela_group, True):
            player.lose_life()
 
        # --- Skóre ---
        hits = pg.sprite.groupcollide(strela_group, enemy_group, True, True)
        for strela, enemies_hit in hits.items():
            for enemy in enemies_hit:
                if isinstance(enemy, Enemy2):
                    player.skore += 2
                else:
                    player.skore += 1
 
        # --- Zvýšení rychlosti nepřátel každých 10 bodů ---
        enemy_speed_multiplier = 1 + player.skore // 10
 
        hrac_group.draw(game_surface)
        enemy_group.draw(game_surface)
        strela_group.draw(game_surface)
        enemy_strela_group.draw(game_surface)
        game_surface.blit(score_font.render(f"Score: {player.skore}", True, BILA), (20, 20))
 
        # --- Draw lives ---
        for i in range(player.lives):
            game_surface.blit(heart_img, (BASE_WIDTH - 50 - i*50, 10))
 
        # --- Draw slow motion UI ---
        if slow_active:
            txt = score_font.render(f"SLOW: {slow_timer:.1f}s", True, CYAN)
            game_surface.blit(txt, (20, 60))
        elif slow_cooldown > 0:
            txt = score_font.render(f"[S] CD: {slow_cooldown:.1f}s", True, TMAVA_SEDA)
            game_surface.blit(txt, (20, 60))
        else:
            txt = score_font.render("[S] READY", True, ZELENA)
            game_surface.blit(txt, (20, 60))
 
        # --- Hit flash efekt (červené zčervenání) ---
        if hit_flash_timer > 0:
            alpha = int(180 * (hit_flash_timer / HIT_FLASH_DURATION))
            flash_surface = pg.Surface((BASE_WIDTH, BASE_HEIGHT), pg.SRCALPHA)
            flash_surface.fill((200, 0, 0, alpha))
            game_surface.blit(flash_surface, (0, 0))
 
    elif current_state == GAME_OVER:
        if video:
            if not video.active:
                video.restart()
            video.draw(game_surface, (0, 0))
        title = text1_font.render("GAME OVER", True, CERVENA)
        game_surface.blit(title, (250, 100))
        info1 = text2_font.render(f"Player: {game_over_user} ", True, BILA)
        info2 = text2_font.render(f"Score: {game_over_score}", True, BILA)
        game_surface.blit(info1, (150, 230))
        game_surface.blit(info2, (150, 280))
        # Tlačítka
        new_game_rect = pg.Rect(250, 350, 300, 50)
        menu_rect = pg.Rect(250, 430, 300, 50)
        draw_button(new_game_rect, "Nová hra", m_pos)
        draw_button(menu_rect, "Menu", m_pos)
    elif current_state == SCOREBOARD:
        if video:
            if not video.active:
                video.restart()
            video.draw(game_surface, (0, 0))
        if time.time() - last_leaderboard_fetch > 5:
            threading.Thread(target=fetch_leaderboard, daemon=True).start()
            last_leaderboard_fetch = time.time()
        title = button_font.render("TOP HRÁČI", True, BILA)
        game_surface.blit(title, (300, 50))
        y = 130
        for i, item in enumerate(leaderboard_data[:5]):
            txt = score_font.render(f"{i+1}. {item.get('username')} - {item.get('score')}", True, BILA)
            game_surface.blit(txt, (200, y))
            y += 45
        draw_button(pg.Rect(300, 520, 200, 50), "Zpet", m_pos)
    elif current_state == SETTINGS:
        if video:
            if not video.active:
                video.restart()
            video.draw(game_surface, (0, 0))
        title = button_font.render("NASTAVENI - ROZLISENI", True, BILA)
        game_surface.blit(title, (200, 100))
        for b in settings_buttons:
            draw_button(b["rect"], b["text"], m_pos)
        draw_button(pg.Rect(300, 520, 200, 50), "Zpet", m_pos)
 
    # --------------------------
    # SCALE DO OKNA
    # --------------------------
    new_w = int(BASE_WIDTH * scale)
    new_h = int(BASE_HEIGHT * scale)
    scaled_surface = pg.transform.scale(game_surface, (new_w, new_h))
    okno.fill((0, 0, 0))
    okno.blit(scaled_surface, ((OKNO_SIRKA-new_w)//2, (OKNO_VYSKA-new_h)//2))
    pg.display.flip()
    hodiny.tick(FPS)
 
pg.quit()
 
# --------------------------
# UNNITEST TŘÍDA
# --------------------------
class TestShooterGame(unittest.TestCase):
    def test_restart_game(self):
        p, hg, eg, sg, esg = restart_game()
        self.assertIsInstance(p, Hrac)
        self.assertEqual(len(hg), 1)
        self.assertEqual(len(eg), 0)
 
    def test_player_life(self):
        p = Hrac()
        start = p.lives
        p.lose_life()
        self.assertEqual(p.lives, start - 1)
 
    def test_enemy_movement(self):
        e = Enemy1(500, 100)
        start_x = e.rect.x
        e.update()
        self.assertLess(e.rect.x, start_x)
 
    def test_strela_movement(self):
        s = Strela(100, 100)
        start_x = s.rect.x
        s.update()
        self.assertGreater(s.rect.x, start_x)
 
    def test_collision(self):
        strela = Strela(200, 200)
        enemy = Enemy1(200, 200)
        strely = pg.sprite.Group(strela)
        enemies = pg.sprite.Group(enemy)
        hits = pg.sprite.groupcollide(strely, enemies, True, True)
        self.assertTrue(hits)
 
# --------------
# SPUŠTĚNÍ TESTŮ
# --------------
if __name__ == "__main__":
    print("\n=== SPUŠTĚNÍ UNITTESTŮ ===")
    # exit=False zajistí, že program neukončí hned po testech, pokud by následoval další kód
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("=== TESTY DOKONČENY ===\n")