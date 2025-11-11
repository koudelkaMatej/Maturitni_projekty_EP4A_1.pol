import random
import pygame as pg

pg.init()


OKNO_SIRKA = 800
OKNO_VYSKA = 600

BILA = (255, 255, 255)
CERNA = (0, 0, 0)

okno = pg.display.set_mode((OKNO_SIRKA, OKNO_VYSKA))
pg.display.set_caption("Shooter")

hodiny = pg.time.Clock()
FPS = 60

score_font = pg.font.Font("freesansbold.ttf", 32)
button_font = pg.font.Font("freesansbold.ttf", 40)

# Herní stavy
MENU = "menu"
GAME = "game"
SCOREBOARD = "scoreboard"
SETTINGS = "settings"

current_state = MENU

# Event pro spawn nepřátel
SPAWN_ENEMY_EVENT = pg.USEREVENT + 1
pg.time.set_timer(SPAWN_ENEMY_EVENT, 2000)


class GameObject(pg.sprite.Sprite):
    def __init__(self, x, y, rychlost, obrazek=None, scale=1, color=None, size=(50,50)):
        super().__init__()
        # Pokud není obrázek, použij barevný obdélník
        if obrazek:
            image_surface = pg.image.load(obrazek).convert_alpha()
            w = int(image_surface.get_width() * scale)
            h = int(image_surface.get_height() * scale)
            self.image = pg.transform.scale(image_surface, (w, h))
        else:
            self.image = pg.Surface(size)
            self.image.fill(color if color else (255,0,0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rychlost = rychlost

class Hrac(GameObject):
    def __init__(self, x, y, rychlost, obrazek=None, scale=1):
        super().__init__(x, y, rychlost, obrazek, scale, color=(0,0,255))
        self.skore = 0

    def update(self):
        self.pohyb()
        self.zkontroluj_hranice()

    def pohyb(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            self.rect.y -= self.rychlost
        if keys[pg.K_DOWN]:
            self.rect.y += self.rychlost

    def zkontroluj_hranice(self):
        self.rect.y = max(0, min(self.rect.y, OKNO_VYSKA - self.rect.height))

class Enemy(GameObject):
    def __init__(self, x, y, obrazek=None, scale=1):
        super().__init__(x, y, 0, obrazek, scale, color=(255,0,0))

    def update(self, speed=5):
        self.rect.x -= speed
        if self.rect.right < 0:
            self.rect.left = OKNO_SIRKA

class Strela(GameObject):
    def __init__(self, x, y, obrazek=None, scale=1):
        super().__init__(x, y, 0, obrazek, scale, color=(0,255,0), size=(20,10))

    def update(self, speed=40):
        self.rect.x += speed
        if self.rect.left > OKNO_SIRKA:
            self.kill()


def restart_game():
    player = Hrac(50, OKNO_VYSKA // 2, 5, "sprites/zbran.png", 0.25)
    hrac_group = pg.sprite.Group(player)
    enemy_group = pg.sprite.Group()
    strela_group = pg.sprite.Group()
    return player, hrac_group, enemy_group, strela_group

# Menu tlačítka
buttons = [
    {"text": "Start", "state": GAME},
    {"text": "Tabulka skóre", "state": SCOREBOARD},
    {"text": "Nastavení", "state": SETTINGS},
    {"text": "Konec", "state": "quit"}
]

BACK_BUTTON = {"text": "Zpět", "state": MENU, "rect": None}

def draw_menu():
    okno.fill(BILA)
    title = pg.font.Font("freesansbold.ttf", 70).render("SHOOTER", True, CERNA)
    okno.blit(title, (OKNO_SIRKA // 2 - title.get_width() // 2, 80))

    mouse_pos = pg.mouse.get_pos()
    y = 200
    for btn in buttons:
        rect = pg.Rect(OKNO_SIRKA//2 - 175, y, 350, 60)
        color = (180, 180, 180) if rect.collidepoint(mouse_pos) else (220, 220, 220)
        pg.draw.rect(okno, color, rect, border_radius=15)

        text = button_font.render(btn["text"], True, CERNA)
        okno.blit(text, (rect.centerx - text.get_width()//2,
                         rect.centery - text.get_height()//2))

        btn["rect"] = rect
        y += 100

def draw_scoreboard():
    okno.fill(BILA)
    text = button_font.render("Zatím žádná skóre", True, CERNA)
    okno.blit(text, (100, 250))

    # Draw back button
    mouse_pos = pg.mouse.get_pos()
    rect = pg.Rect(OKNO_SIRKA//2 - 100, 500, 200, 50)
    color = (180, 180, 180) if rect.collidepoint(mouse_pos) else (220, 220, 220)
    pg.draw.rect(okno, color, rect, border_radius=10)
    text_surface = button_font.render(BACK_BUTTON["text"], True, CERNA)
    okno.blit(text_surface, (rect.centerx - text_surface.get_width()//2,
                             rect.centery - text_surface.get_height()//2))
    BACK_BUTTON["rect"] = rect

def draw_settings():
    okno.fill(BILA)
    text = button_font.render("Nastavení - ve vývoji", True, CERNA)
    okno.blit(text, (130, 250))

    # Draw back button
    mouse_pos = pg.mouse.get_pos()
    rect = pg.Rect(OKNO_SIRKA//2 - 100, 500, 200, 50)
    color = (180, 180, 180) if rect.collidepoint(mouse_pos) else (220, 220, 220)
    pg.draw.rect(okno, color, rect, border_radius=10)
    text_surface = button_font.render(BACK_BUTTON["text"], True, CERNA)
    okno.blit(text_surface, (rect.centerx - text_surface.get_width()//2,
                             rect.centery - text_surface.get_height()//2))
    BACK_BUTTON["rect"] = rect

def game_over_screen(skore):
    okno.fill(BILA)
    game_over_font = pg.font.Font("freesansbold.ttf", 50)
    game_over_text = game_over_font.render("Game Over", True, CERNA)
    score_text = score_font.render(f"Skóre: {skore}", True, CERNA)

    okno.blit(game_over_text, (OKNO_SIRKA // 2 - game_over_text.get_width() // 2, OKNO_VYSKA // 3))
    okno.blit(score_text, (OKNO_SIRKA // 2 - score_text.get_width() // 2, OKNO_VYSKA // 2))
    pg.display.flip()
    pg.time.wait(2000)

# =HRA=
player, hrac_group, enemy_group, strela_group = restart_game()
current_state = MENU
running = True

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        # Click menu buttons
        if current_state == MENU:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for btn in buttons:
                    if btn["rect"] and btn["rect"].collidepoint(pg.mouse.get_pos()):
                        if btn["state"] == "quit":
                            running = False
                        elif btn["state"] == GAME:
                            player, hrac_group, enemy_group, strela_group = restart_game()
                            current_state = GAME
                        else:
                            current_state = btn["state"]

        # Back button for Settings and Scoreboard
        if current_state in [SCOREBOARD, SETTINGS]:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if BACK_BUTTON["rect"] and BACK_BUTTON["rect"].collidepoint(pg.mouse.get_pos()):
                    current_state = MENU

        # Game logic
        if current_state == GAME:
            if event.type == SPAWN_ENEMY_EVENT:
                enemy = Enemy(OKNO_SIRKA, random.randint(0, OKNO_VYSKA-50),
                              "sprites/enemy.png", 0.25)
                enemy_group.add(enemy)

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    strela = Strela(player.rect.x, player.rect.y, "sprites/strela.png", 0.05)
                    strela_group.add(strela)


    if current_state == MENU:
        draw_menu()
    elif current_state == SCOREBOARD:
        draw_scoreboard()
    elif current_state == SETTINGS:
        draw_settings()
    elif current_state == GAME:
        hrac_group.update()
        enemy_group.update()
        strela_group.update()

        if pg.sprite.spritecollide(player, enemy_group, True):
            game_over_screen(player.skore)
            current_state = MENU

        collisions = pg.sprite.groupcollide(strela_group, enemy_group, True, True)
        if collisions:
            player.skore += 1

        okno.fill(BILA)
        hrac_group.draw(okno)
        enemy_group.draw(okno)
        strela_group.draw(okno)
        skore_text = score_font.render(f"Skóre: {player.skore}", True, CERNA)
        okno.blit(skore_text, (10, 10))

    pg.display.flip()
    hodiny.tick(FPS)

pg.quit()
