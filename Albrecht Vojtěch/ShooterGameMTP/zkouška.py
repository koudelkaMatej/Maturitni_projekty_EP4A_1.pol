# --------------------------
# IMPORTY KNIHOVEN
# --------------------------

import unittest              # knihovna pro testování kódu (unit testy)
import random                # náhodná čísla (spawn nepřátel apod.)
import pygame as pg          # hlavní herní knihovna
import requests              # komunikace s Flask API (login, score)
import threading             # vlákna (aby login neblokoval hru)
import time                  # čas (cooldowny, leaderboard refresh)
import static_ffmpeg         # knihovna pro práci s videem (ffmpeg)
static_ffmpeg.add_paths()    # přidání ffmpeg do PATH (aby fungovalo video)
from pyvidplayer2 import Video  # přehrávání videa v pygame

# inicializace pygame (nutné pro všechno)
pg.init()

# --------------------------
# ZÁKLADNÍ ROZMĚRY
# --------------------------

BASE_WIDTH = 800   # interní šířka hry (logika běží vždy v tomto rozlišení)
BASE_HEIGHT = 600  # interní výška hry

OKNO_SIRKA = 800   # aktuální šířka okna
OKNO_VYSKA = 600   # aktuální výška okna

# vytvoření okna (RESIZABLE = lze měnit velikost)
okno = pg.display.set_mode((OKNO_SIRKA, OKNO_VYSKA), pg.RESIZABLE)

# surface pro samotnou hru (renderuje se sem a pak se škáluje)
game_surface = pg.Surface((BASE_WIDTH, BASE_HEIGHT))

# název okna
pg.display.set_caption("ShooterGameMTP")

# --------------------------
# ROZLIŠENÍ (SETTINGS)
# --------------------------

# dostupná rozlišení v menu
RESOLUTIONS = [
    (800, 600),
    (1024, 768),
    (1280, 960)
]

# --------------------------
# NAČTENÍ ZDROJŮ
# --------------------------

# pokus o načtení videa na pozadí
try:
    video = Video("static/background_video.mp4")  # video soubor
    video.resize((800, 600))                      # změna velikosti
except:
    video = None  # pokud selže → žádné video

# pokus o načtení obrázkového pozadí
try:
    original_background = pg.image.load("static/background.png").convert()
except:
    # fallback pokud obrázek neexistuje
    original_background = pg.Surface((800, 600))
    original_background.fill((30, 30, 30))  # šedé pozadí

# přizpůsobení pozadí na velikost hry
background = pg.transform.scale(original_background, (BASE_WIDTH, BASE_HEIGHT))

# načtení obrázku srdce (životy)
heart_img = pg.image.load("sprites/heart.png").convert_alpha()
heart_img = pg.transform.scale(heart_img, (40, 40))

# --------------------------
# BARVY
# --------------------------

BILA = (250, 250, 250)       # bílá
CERNA = (0, 0, 0)            # černá
MODRA = (0, 0, 255)          # modrá
CERVENA = (255, 0, 0)        # červená
ZELENA = (0, 255, 0)         # zelená
SEDA = (220, 220, 220)       # světle šedá
TMAVA_SEDA = (180, 180, 180) # tmavší šedá
CYAN = (0, 255, 255)         # cyan
PLASMA_PURPLE = (200, 0, 255)# fialová

# --------------------------
# RESIZE OKNA
# --------------------------

def resize_window(width, height):
    global OKNO_SIRKA, OKNO_VYSKA, okno
    OKNO_SIRKA, OKNO_VYSKA = width, height  # uložit nové rozměry
    okno = pg.display.set_mode((OKNO_SIRKA, OKNO_VYSKA), pg.RESIZABLE)

# FPS kontrola
hodiny = pg.time.Clock()  # objekt pro měření FPS
FPS = 60                  # cílové FPS

# --------------------------
# FONTY
# --------------------------

def update_fonts():
    global text1_font, text2_font, score_font, button_font
    # načtení fontu (musí existovat soubor!)
    text1_font = pg.font.Font("Audiowide-Regular.ttf", 45)
    text2_font = pg.font.Font("Audiowide-Regular.ttf", 30)
    score_font = pg.font.Font("Audiowide-Regular.ttf", 30)
    button_font = pg.font.Font("Audiowide-Regular.ttf", 30)

update_fonts()

# --------------------------
# STAVY HRY
# --------------------------

LOGIN = "login"         # login obrazovka
MENU = "menu"           # hlavní menu
GAME = "game"           # samotná hra
SCOREBOARD = "scoreboard"
SETTINGS = "settings"
GAME_OVER = "game_over"

current_state = LOGIN   # start ve loginu

# --------------------------
# API DATA
# --------------------------

BASE_URL = "http://127.0.0.1:5000/api"  # Flask backend
logged_in_user_id = None                # ID přihlášeného uživatele

username_input = ""  # text z inputu username
password_input = ""  # text z inputu password
active_input = "username"  # který input je aktivní

leaderboard_data = []      # data z API
last_leaderboard_fetch = 0 # poslední fetch

# --------------------------
# GAME OVER DATA
# --------------------------

game_over_user = ""   # jméno hráče
game_over_score = 0   # skóre

def show_game_over(player):
    global current_state, game_over_user, game_over_score
    # pokud přihlášen → username, jinak HOST
    game_over_user = username_input if logged_in_user_id else "HOST"
    game_over_score = player.skore
    current_state = GAME_OVER

# --------------------------
# API FUNKCE
# --------------------------

def login_thread(username, password):
    global logged_in_user_id, current_state
    try:
        # POST request na backend
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
        return  # host neodesílá score
    try:
        requests.post(f"{BASE_URL}/submit_score",
                      json={"user_id": logged_in_user_id, "score": score},
                      timeout=2)
    except:
        pass

# --------------------------
# SLOW MOTION
# --------------------------

SLOW_DURATION = 5
SLOW_COOLDOWN = 15

slow_active = False
slow_timer = 0.0
slow_cooldown = SLOW_COOLDOWN

# --------------------------
# HIT FLASH
# --------------------------

HIT_FLASH_DURATION = 0.4
hit_flash_timer = 0.0

# --------------------------
# ZÁKLADNÍ TŘÍDA OBJEKTU
# --------------------------

class GameObject(pg.sprite.Sprite):
    def __init__(self, x, y, image_path=None, color=CERVENA, size=(50, 50)):
        super().__init__()

        # default surface
        self.image = pg.Surface(size)
        self.image.fill(color)

        # pokud existuje obrázek → použij ho
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

        # pohyb nahoru
        if keys[pg.K_UP] and self.rect.top > 0:
            self.rect.y -= self.rychlost

        # pohyb dolů
        if keys[pg.K_DOWN] and self.rect.bottom < BASE_HEIGHT:
            self.rect.y += self.rychlost

    def lose_life(self):
        global hit_flash_timer
        self.lives -= 1
        hit_flash_timer = HIT_FLASH_DURATION  # spustit efekt

        if self.lives <= 0:
            submit_score(self.skore)
            show_game_over(self)

# --------------------------
# TESTY
# --------------------------

class TestShooterGame(unittest.TestCase):

    def test_restart_game(self):
        p, hg, eg, sg, esg = restart_game()
        self.assertIsInstance(p, Hrac)  # hráč existuje
        self.assertEqual(len(hg), 1)    # skupina obsahuje hráče
        self.assertEqual(len(eg), 0)    # žádní nepřátelé

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

# --------------------------
# SPUŠTĚNÍ TESTŮ
# --------------------------

if __name__ == "__main__":
    print("\n=== SPUŠTĚNÍ UNITTESTŮ ===")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("=== TESTY DOKONČENY ===\n")