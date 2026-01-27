import pygame, sys, os, random, sqlite3, datetime
from pygame.locals import *

# --- KONFIGURACE ---
SW, SH = 1920, 1080
GROUND_Y = 850
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "WEB")
ASSETS = os.path.join(BASE_DIR, "assets")
DB_PATH = os.path.join(BASE_DIR, "game.db")

pygame.init()
screen = pygame.display.set_mode((SW, SH), FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 35, bold=True)
big_font = pygame.font.SysFont("arial", 80, bold=True)

# Barvy
WHITE, BLACK, BLUE = (255, 255, 255), (20, 20, 20), (0, 120, 215)
SKY_ORANGE, SAND_BEIGE, MESA_RED = (255, 190, 120), (210, 180, 140), (160, 82, 45)

# --- FUNKCE PRO WEB ---
def generate_web():
    try:
        if not os.path.exists(WEB_DIR): os.makedirs(WEB_DIR)
        target = os.path.join(WEB_DIR, "leaderboard.html")
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Vybíráme data přímo z DB včetně uloženého času hráče
        c.execute("SELECT username, high_score, last_date, last_time FROM users WHERE high_score > 0 ORDER BY high_score DESC LIMIT 10")
        rows = c.fetchall()
        
        html_fragment = ""
        for i, row in enumerate(rows, 1):
            html_fragment += f"<tr><td>{i}</td><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>\n"
        
        with open(target, "w", encoding="utf-8") as f:
            f.write(html_fragment)
        conn.close()
    except Exception as e:
        print(f"Chyba webu: {e}")

# --- DB OPERACE ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tabulka nyní obsahuje sloupce pro datum a čas konkrétního rekordu
    c.execute("""CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, 
                  password TEXT, 
                  high_score INTEGER DEFAULT 0,
                  last_date TEXT DEFAULT '-',
                  last_time TEXT DEFAULT '-')""")
    conn.commit(); conn.close()

def db_action(user, pwd, action):
    if not user or not pwd: return "Chybí údaje!"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        if action == "reg":
            c.execute("INSERT INTO users (username, password) VALUES (?,?)", (user, pwd))
            conn.commit(); conn.close()
            return "Registrace úspěšná!"
        else:
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
            res = c.fetchone()
            conn.close()
            return "Přihlášení úspěšné!" if res else "Chybné údaje!"
    except: 
        conn.close()
        return "Uživatel již existuje!"

def update_score(user, score):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.now()
    datum = now.strftime("%d.%m.%Y")
    cas = now.strftime("%H:%M")
    
    # Aktualizuje skóre a čas POUZE pokud je nové skóre vyšší
    c.execute("""UPDATE users SET 
                 last_date = CASE WHEN ? > high_score THEN ? ELSE last_date END,
                 last_time = CASE WHEN ? > high_score THEN ? ELSE last_time END,
                 high_score = MAX(high_score, ?)
                 WHERE username = ?""", (score, datum, score, cas, score, user))
    conn.commit(); conn.close()

# --- TŘÍDY (Hráč, Překážky, Input) ---
def load_img(name, size):
    try:
        img = pygame.image.load(os.path.join(ASSETS, name)).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        s = pygame.Surface(size); s.fill((200, 0, 0)); return s

class Player:
    def __init__(self):
        self.w, self.h = 160, 200
        self.x, self.y = 150, GROUND_Y - 200
        self.vel_y, self.on_g, self.duck = 0, True, False
        self.img = load_img("kovboj.png", (self.w, self.h))
    def update(self, dt):
        h = 100 if self.duck else 200
        if not self.on_g:
            self.vel_y += 2600 * dt
            self.y += self.vel_y * dt
        if self.y + h >= GROUND_Y:
            self.y, self.vel_y, self.on_g = GROUND_Y - h, 0, True
    def draw(self, s):
        h = 100 if self.duck else 200
        curr_y = (GROUND_Y - h) if (self.duck and self.on_g) else self.y
        s.blit(pygame.transform.scale(self.img, (self.w, h)), (self.x, curr_y))
    def mask(self):
        h = 100 if self.duck else 200
        return pygame.mask.from_surface(pygame.transform.scale(self.img, (self.w, h)))

class Obstacle:
    def __init__(self, type, speed):
        self.type = type
        if type == 0:
            self.w, self.h = random.randint(100, 160), random.randint(130, 220)
            self.y = GROUND_Y - self.h
        else:
            self.w, self.h = 130, 90
            self.y = GROUND_Y - 240
        self.x, self.speed = SW + 100, speed
        self.img = load_img("kaktus.png" if type == 0 else "ptak.png", (self.w, self.h))
    def update(self, dt): self.x -= self.speed * dt
    def draw(self, s): s.blit(self.img, (self.x, self.y))
    def mask(self): return pygame.mask.from_surface(self.img)

class InputBox:
    def __init__(self, x, y, w, h, is_pwd=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text, self.active, self.is_pwd = "", False, is_pwd
    def handle(self, e):
        if e.type == MOUSEBUTTONDOWN and e.button == 1: self.active = self.rect.collidepoint(e.pos)
        if e.type == KEYDOWN and self.active:
            if e.key == K_BACKSPACE: self.text = self.text[:-1]
            elif len(self.text) < 14: self.text += e.unicode
    def draw(self, s):
        pygame.draw.rect(s, BLUE if self.active else BLACK, self.rect, 4)
        txt = ("*" * len(self.text)) if self.is_pwd else self.text
        s.blit(font.render(txt, True, BLACK), (self.rect.x+10, self.rect.y+10))

# --- HLAVNÍ SMYČKA ---
def main():
    init_db()
    state, user, msg_db = "menu", None, ""
    u_box = InputBox(SW//2-200, 450, 400, 60)
    p_box = InputBox(SW//2-200, 550, 400, 60, True)
    mesas = [[random.randint(200, 600), random.randint(150, 400)] for _ in range(10)]
    ctrls_info = ["MEZERNÍK / ŠIPKA NAHORU - Skok", "ŠIPKA DOLŮ - Přikrčení", "ESC - Konec hry"]

    def reset(): return Player(), [], 0, 1.0, pygame.time.get_ticks() + 2000
    player, obs, score, speed, next_spw = reset()

    while True:
        dt = clock.tick(60)/1000
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE): pygame.quit(); sys.exit()
            
            if state == "auth":
                u_box.handle(e); p_box.handle(e)
                if e.type == MOUSEBUTTONDOWN and e.button == 1:
                    if pygame.Rect(SW//2-210, 650, 200, 80).collidepoint(e.pos):
                        res = db_action(u_box.text, p_box.text, "login")
                        msg_db = res
                        if res == "Přihlášení úspěšné!": user = u_box.text; state = "menu"
                    elif pygame.Rect(SW//2+10, 650, 200, 80).collidepoint(e.pos):
                        msg_db = db_action(u_box.text, p_box.text, "reg")
                    elif pygame.Rect(50, 50, 150, 70).collidepoint(e.pos): state = "menu"; msg_db = ""

            elif state == "menu":
                if e.type == MOUSEBUTTONDOWN and e.button == 1:
                    if pygame.Rect(SW//2-250, 300, 500, 80).collidepoint(e.pos): 
                        player, obs, score, speed, next_spw = reset(); state = "playing"
                    elif pygame.Rect(SW//2-250, 400, 500, 80).collidepoint(e.pos): state = "controls"
                    elif pygame.Rect(SW//2-250, 500, 500, 80).collidepoint(e.pos): state = "auth"
                    elif pygame.Rect(SW//2-250, 600, 500, 80).collidepoint(e.pos): pygame.quit(); sys.exit()

            elif state == "playing":
                if e.type == KEYDOWN:
                    if e.key in (K_SPACE, K_UP) and player.on_g: player.on_g, player.vel_y = False, -1150
                    if e.key == K_DOWN and player.on_g: player.duck = True
                if e.type == KEYUP and e.key == K_DOWN: player.duck = False

        screen.fill(SKY_ORANGE)
        for i, m in enumerate(mesas): pygame.draw.rect(screen, MESA_RED, (i*250, GROUND_Y - m[1], m[0], m[1]))
        pygame.draw.rect(screen, SAND_BEIGE, (0, GROUND_Y, SW, SH - GROUND_Y))
        
        if state == "menu":
            t = big_font.render("WILD JUMP", True, BLACK)
            screen.blit(t, (SW//2 - t.get_width()//2, 100))
            labels = ["HRÁT", "OVLÁDÁNÍ", user if user else "PŘIHLÁŠENÍ", "EXIT"]
            for i, txt in enumerate(labels):
                rect = pygame.Rect(SW//2-250, 300 + i*100, 500, 80)
                color = (0, 150, 255) if rect.collidepoint(mx, my) else BLUE
                pygame.draw.rect(screen, color, rect, border_radius=15)
                lbl = font.render(txt, True, WHITE)
                screen.blit(lbl, lbl.get_rect(center=rect.center))

        elif state == "controls":
            pygame.draw.rect(screen, WHITE, (SW//2-400, 250, 800, 500), border_radius=20)
            for i, line in enumerate(ctrls_info):
                txt = font.render(line, True, BLACK)
                screen.blit(txt, (SW//2 - txt.get_width()//2, 350 + i*70))
            back_b = pygame.Rect(SW//2-100, 650, 200, 70)
            pygame.draw.rect(screen, BLUE, back_b, border_radius=10)
            screen.blit(font.render("ZPĚT", True, WHITE), font.render("ZPĚT", True, WHITE).get_rect(center=back_b.center))
            if pygame.mouse.get_pressed()[0] and back_b.collidepoint(mx, my): state = "menu"

        elif state == "playing":
            player.update(dt)
            move_speed = (700 + score * 15) * speed 
            if pygame.time.get_ticks() >= next_spw:
                obs.append(Obstacle(0 if random.random() > 0.3 else 1, move_speed))
                next_spw = pygame.time.get_ticks() + max(700, int(2000 / speed))
            for o in obs[:]:
                o.update(dt); o.draw(screen)
                if o.x < -300: obs.remove(o); score += 1
                curr_h = 100 if player.duck else 200
                if player.mask().overlap(o.mask(), (int(o.x - player.x), int(o.y - (GROUND_Y-curr_h if (player.duck and player.on_g) else player.y)))):
                    if user: 
                        update_score(user, score)
                        generate_web()
                    state = "menu"
            player.draw(screen)
            screen.blit(big_font.render(f"Skóre: {score}", True, BLACK), (50, 150))
        
        elif state == "auth":
            u_box.draw(screen); p_box.draw(screen)
            screen.blit(font.render("Jméno:", True, BLACK), (SW//2-350, 460))
            screen.blit(font.render("Heslo:", True, BLACK), (SW//2-350, 560))
            back_rect = pygame.Rect(50, 50, 150, 70)
            pygame.draw.rect(screen, BLACK, back_rect, 3, border_radius=5)
            screen.blit(font.render("ZPĚT", True, BLACK), (85, 65))
            for i, btn in enumerate(["Login", "Reg"]):
                r = pygame.Rect(SW//2-210+i*220, 650, 200, 80)
                color = (0, 150, 255) if r.collidepoint(mx, my) else BLUE
                pygame.draw.rect(screen, color, r, border_radius=10)
                screen.blit(font.render(btn, True, WHITE), font.render(btn, True, WHITE).get_rect(center=r.center))
            if msg_db:
                msg_color = (34, 139, 34) if "úspěšná" in msg_db or "úspěšné" in msg_db else (200, 0, 0)
                m_surf = font.render(msg_db, True, msg_color)
                screen.blit(m_surf, m_surf.get_rect(center=(SW//2, 760)))

        pygame.display.flip()

if __name__ == "__main__": main()