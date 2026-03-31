import pygame
import random
import sys
import webbrowser
import os
import sqlite3
import json
import hashlib

# === CESTY K SOUBORŮM ===
ADRESAR_HRY = os.path.dirname(os.path.abspath(__file__))
CESTA_DATABAZE = os.path.join(ADRESAR_HRY, "data.db")

# === SYSTÉM DATABÁZE A LOGINU ===
def inicializuj_databazi():
    conn = sqlite3.connect(CESTA_DATABAZE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       jmeno TEXT UNIQUE NOT NULL, 
                       heslo TEXT NOT NULL,
                       max_body INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def hashuj_heslo(heslo):
    return hashlib.sha256(heslo.encode()).hexdigest()

def registrace(jmeno, heslo):
    if not jmeno or not heslo: return False, "Pole nesmí být prázdná!"
    conn = sqlite3.connect(CESTA_DATABAZE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (jmeno, heslo) VALUES (?, ?)", (jmeno, hashuj_heslo(heslo)))
        conn.commit()
        return True, "Registrace úspěšná!"
    except sqlite3.IntegrityError:
        return False, "Jméno již existuje!"
    finally:
        conn.close()

def prihlaseni(jmeno, heslo):
    conn = sqlite3.connect(CESTA_DATABAZE)
    cursor = conn.cursor()
    cursor.execute("SELECT jmeno FROM users WHERE jmeno = ? AND heslo = ?", (jmeno, hashuj_heslo(heslo)))
    uzivatel = cursor.fetchone()
    conn.close()
    return uzivatel[0] if uzivatel else None

def uloz_vysledek(jmeno, body):
    if not jmeno: return
    conn = sqlite3.connect(CESTA_DATABAZE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET max_body = MAX(max_body, ?) WHERE jmeno = ?", (body, jmeno))
    conn.commit()
    cursor.execute("SELECT jmeno, max_body FROM users ORDER BY max_body DESC LIMIT 5")
    zebricek = [{"jmeno": row[0], "body": row[1]} for row in cursor.fetchall()]
    conn.close()
    
    # === OPRAVA: Ukládání pro web bez serveru (JS místo JSON) ===
    try:
        js_cesta = os.path.join(ADRESAR_HRY, "data.js")
        with open(js_cesta, "w", encoding="utf-8") as f:
            # Vytvoříme JS proměnnou, kterou web snadno přečte
            f.write(f"const top5Data = {json.dumps(zebricek, ensure_ascii=False)};")
    except Exception as e:
        print(f"Chyba při zápisu data.js: {e}")

inicializuj_databazi()

# === GLOBÁLNÍ NASTAVENÍ ===
pygame.init()
AKTUALNI_UZIVATEL = None
ZAKLAD_SIRKA, ZAKLAD_VYSKA = 800, 600
ROZLISENI_LIST = [(800, 600), (900, 675), (1024, 768)]
rozliseni_index = 0
ŠÍŘKA, VÝŠKA = ROZLISENI_LIST[rozliseni_index]

FPS = 60
BÍLÁ, ZELENÁ, ČERVENÁ, ŽLUTÁ, ČERNÁ, ŠEDÁ = (255, 255, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (0, 0, 0), (50, 50, 50)

okno = pygame.display.set_mode((ŠÍŘKA, VÝŠKA))
pygame.display.set_caption("2D Ship Shooter - Pro Edition")

def scale(): return ŠÍŘKA / ZAKLAD_SIRKA

def fonty():
    s = scale()
    return (pygame.font.Font(None, max(25, int(70 * s))), 
            pygame.font.Font(None, max(20, int(45 * s))), 
            pygame.font.Font(None, max(18, int(30 * s))))

# --- ASSETY ---
def nacti_raw_obrazky():
    def nacti(nazev, barva, rozmer):
        cesta = os.path.join(ADRESAR_HRY, nazev)
        try: return pygame.image.load(cesta).convert_alpha()
        except:
            s = pygame.Surface(rozmer); s.fill(barva); return s
    return {
        "hrac": nacti("lod1.png", ZELENÁ, (70, 60)),
        "nepritel": nacti("lod2.png", ČERVENÁ, (60, 60)),
        "boss": nacti("lod4.png", ČERVENÁ, (150, 120)),
        "lucky": nacti("lucky.jpg", ŽLUTÁ, (40, 40)),
        "pozadi": nacti("pozadi.jpg", ČERNÁ, (800, 600)),
        "s_hrac": nacti("strela.png", ZELENÁ, (10, 20)),
        "s_nepritel": nacti("strela2.png", ŽLUTÁ, (10, 20)),
        "explo": nacti("explo.jpg", ŽLUTÁ, (60, 60))
    }

ASSETY_RAW = nacti_raw_obrazky()
font_nadpis, font_menu, font_skore = fonty()

def aktualizuj_assetty():
    global lod_hrac, lod_nepritel, lod_boss, lucky_img, pozadi_img, strela_hrac_img, strela_nepritel_img, explo_img, font_nadpis, font_menu, font_skore
    s = scale()
    lod_hrac = pygame.transform.scale(ASSETY_RAW["hrac"], (int(70*s), int(60*s)))
    lod_nepritel = pygame.transform.rotate(pygame.transform.scale(ASSETY_RAW["nepritel"], (int(60*s), int(60*s))), 180)
    lod_boss = pygame.transform.scale(ASSETY_RAW["boss"], (int(150*s), int(120*s)))
    lucky_img = pygame.transform.scale(ASSETY_RAW["lucky"], (int(40*s), int(40*s)))
    pozadi_img = pygame.transform.scale(ASSETY_RAW["pozadi"], (ŠÍŘKA, VÝŠKA))
    explo_img = pygame.transform.scale(ASSETY_RAW["explo"], (int(60*s), int(60*s)))
    
    sh_sirka, sh_vyska = int(15*s), int(30*s)
    strela_hrac_img = pygame.transform.scale(ASSETY_RAW["s_hrac"], (sh_sirka, sh_vyska))
    sn_sirka, sn_vyska = int(15*s), int(30*s)
    strela_nepritel_img = pygame.transform.rotate(pygame.transform.scale(ASSETY_RAW["s_nepritel"], (sn_sirka, sn_vyska)), 180)
    
    font_nadpis, font_menu, font_skore = fonty()

aktualizuj_assetty()

# === TŘÍDY ===
class Exploze(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = explo_img
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = pygame.time.get_ticks()
    def update(self):
        if pygame.time.get_ticks() - self.timer > 500:
            self.kill()

class Projektil(pygame.sprite.Sprite):
    def __init__(self, x, y, smer, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.rychlost = int(8 * scale()) * smer
    def update(self):
        self.rect.y += self.rychlost
        if self.rect.bottom < 0 or self.rect.top > VÝŠKA: self.kill()

class Hráč(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = lod_hrac
        self.rect = self.image.get_rect(center=(ŠÍŘKA//2, int(VÝŠKA*0.9)))
        self.zakladni_rychlost = int(6 * scale())
        self.rychlost = self.zakladni_rychlost
        self.dvojita_strela = False
        self.posledni_strela, self.lucky_timer = 0, 0 
    def update(self):
        ted = pygame.time.get_ticks()
        if self.lucky_timer > 0 and ted > self.lucky_timer:
            self.rychlost, self.dvojita_strela, self.lucky_timer = self.zakladni_rychlost, False, 0
        keys = pygame.key.get_pressed()
        min_y = int(VÝŠKA * 0.75)
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.rychlost
        if keys[pygame.K_RIGHT] and self.rect.right < ŠÍŘKA: self.rect.x += self.rychlost
        if keys[pygame.K_UP] and self.rect.top > min_y: self.rect.y -= self.rychlost
        if keys[pygame.K_DOWN] and self.rect.bottom < VÝŠKA: self.rect.y += self.rychlost
    def střela(self, vsechny, strely):
        ted = pygame.time.get_ticks()
        if ted - self.posledni_strela >= 400:
            self.posledni_strela = ted
            if not self.dvojita_strela:
                p = Projektil(self.rect.centerx, self.rect.top, -1, strela_hrac_img)
                vsechny.add(p); strely.add(p)
            else:
                p1 = Projektil(self.rect.left, self.rect.top, -1, strela_hrac_img)
                p2 = Projektil(self.rect.right, self.rect.top, -1, strela_hrac_img)
                vsechny.add(p1, p2); strely.add(p1, p2)

class Nepřítel(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = lod_nepritel
        self.rect = self.image.get_rect()
        self.směr = random.choice([-1, 1]); self.rychlost = int(2 * scale())
        self.cooldown = random.randint(60, 150)
    
    def update(self, nepratele_group=None, vsechny=None, strely_nep=None):
        if nepratele_group is None: return 
        stara_x = self.rect.x
        self.rect.x += self.směr * self.rychlost
        if self.rect.left <= 0 or self.rect.right >= ŠÍŘKA:
            self.směr *= -1; self.rect.x = stara_x
        for jiny in nepratele_group:
            if jiny != self and self.rect.colliderect(jiny.rect):
                self.směr *= -1; jiny.směr *= -1; self.rect.x += self.směr * self.rychlost
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.cooldown = random.randint(60, 150)
            s = Projektil(self.rect.centerx, self.rect.bottom, 1, strela_nepritel_img)
            vsechny.add(s); strely_nep.add(s)

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = lod_boss
        self.rect = self.image.get_rect(center=(ŠÍŘKA//2, int(VÝŠKA*0.15)))
        self.rychlost, self.směr, self.cooldown, self.životy = int(3 * scale()), 1, 60, 20 
    
    def update(self, vsechny=None, strely_nep=None):
        if vsechny is None: return
        self.rect.x += self.směr * self.rychlost
        if self.rect.left <= 0 or self.rect.right >= ŠÍŘKA: self.směr *= -1
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.cooldown = 45
            for x in [self.rect.left+30, self.rect.centerx, self.rect.right-30]:
                s = Projektil(x, self.rect.bottom, 1, strela_nepritel_img)
                vsechny.add(s); strely_nep.add(s)
    
    def vykresli_životy(self, surface):
        s = scale()
        sirka_baru = self.životy * int(10*s)
        pygame.draw.rect(surface, ČERVENÁ, (self.rect.centerx - sirka_baru//2, self.rect.top-20, sirka_baru, 10))

class LuckyBlock(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = lucky_img
        self.rect = self.image.get_rect(center=(random.randint(50, ŠÍŘKA-50), -50))
        self.rychlost = int(3 * scale())
    def update(self):
        self.rect.y += self.rychlost
        if self.rect.top > VÝŠKA: self.kill()

# === UI ===
def vykresli_text(text, font, barva, x, y):
    t = font.render(text, True, barva)
    okno.blit(t, t.get_rect(center=(x, y)))

def obrazovka_ucet(typ="login"):
    global AKTUALNI_UZIVATEL
    jmeno, heslo, aktivni_pole, zprava, barva_zpravy = "", "", 0, "", BÍLÁ
    while True:
        okno.fill(ČERNÁ); s = scale()
        nadpis = "PŘIHLÁŠENÍ" if typ == "login" else "REGISTRACE"
        vykresli_text(nadpis, font_nadpis, ŽLUTÁ, ŠÍŘKA//2, int(100*s))
        c1 = ZELENÁ if aktivni_pole == 0 else BÍLÁ
        c2 = ZELENÁ if aktivni_pole == 1 else BÍLÁ
        vykresli_text(f"Jméno: {jmeno}{'|' if aktivni_pole == 0 else ''}", font_menu, c1, ŠÍŘKA//2, int(220*s))
        vykresli_text(f"Heslo: {'*' * len(heslo)}{'|' if aktivni_pole == 1 else ''}", font_menu, c2, ŠÍŘKA//2, int(300*s))
        vykresli_text(zprava, font_skore, barva_zpravy, ŠÍŘKA//2, int(380*s))
        vykresli_text("[TAB] Přepnout   [ENTER] Potvrdit   [ESC] Zpět", font_skore, BÍLÁ, ŠÍŘKA//2, int(500*s))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return False
                if e.key == pygame.K_TAB: aktivni_pole = 1 - aktivni_pole
                if e.key == pygame.K_RETURN:
                    if typ == "login":
                        u = prihlaseni(jmeno, heslo)
                        if u: AKTUALNI_UZIVATEL = u; return True
                        else: zprava = "Chybné údaje!"; barva_zpravy = ČERVENÁ
                    else:
                        ok, msg = registrace(jmeno, heslo)
                        zprava = msg; barva_zpravy = ZELENÁ if ok else ČERVENÁ
                        if ok: jmeno, heslo = "", ""
                elif e.key == pygame.K_BACKSPACE:
                    if aktivni_pole == 0: jmeno = jmeno[:-1]
                    else: heslo = heslo[:-1]
                elif e.unicode.isprintable():
                    if aktivni_pole == 0 and len(jmeno) < 15: jmeno += e.unicode
                    elif aktivni_pole == 1 and len(heslo) < 20: heslo += e.unicode

# === HRA ===
def hra():
    global AKTUALNI_UZIVATEL
    if not AKTUALNI_UZIVATEL:
        if not obrazovka_ucet("login"): return

    všechny_sprity = pygame.sprite.Group()
    střely_hráč, střely_nep = pygame.sprite.Group(), pygame.sprite.Group()
    nepřátelé, lucky_blocky = pygame.sprite.Group(), pygame.sprite.Group()
    
    hráč = Hráč(); všechny_sprity.add(hráč)
    skore, spawn, boss_aktivní = 0, 0, False
    boss = None
    příští_boss = 10
    lucky_timer_spawn = pygame.time.get_ticks()
    hodiny = pygame.time.Clock()

    running = True
    while running:
        hodiny.tick(FPS); ted = pygame.time.get_ticks()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE: hráč.střela(všechny_sprity, střely_hráč)
                if e.key == pygame.K_ESCAPE: running = False

        if ted - lucky_timer_spawn >= 15000:
            lucky_timer_spawn = ted
            lb = LuckyBlock(); všechny_sprity.add(lb); lucky_blocky.add(lb)

        for sprite in všechny_sprity:
            if isinstance(sprite, Nepřítel):
                sprite.update(nepřátelé, všechny_sprity, střely_nep)
            elif isinstance(sprite, Boss):
                sprite.update(všechny_sprity, střely_nep)
            else:
                sprite.update()

        for lb in pygame.sprite.spritecollide(hráč, lucky_blocky, True):
            hráč.dvojita_strela = True; hráč.lucky_timer = ted + 7000 

        spawn += 1
        if not boss_aktivní and spawn > 60 and len(nepřátelé) < 5:
            n = Nepřítel()
            n.rect.center = (random.randint(50, ŠÍŘKA-50), random.randint(50, int(VÝŠKA*0.3)))
            if not pygame.sprite.spritecollideany(n, nepřátelé):
                spawn = 0; všechny_sprity.add(n); nepřátelé.add(n)

        if skore >= příští_boss and not boss_aktivní:
            for n in nepřátelé: n.kill()
            boss = Boss(); všechny_sprity.add(boss); boss_aktivní = True

        if boss_aktivní and boss:
            zasahy = pygame.sprite.spritecollide(boss, střely_hráč, True)
            if zasahy:
                boss.životy -= len(zasahy)
                if boss.životy <= 0:
                    ex = Exploze(boss.rect.centerx, boss.rect.centery)
                    všechny_sprity.add(ex)
                    boss.kill(); boss_aktivní = False; boss = None
                    skore += 10; příští_boss += 30

        kolize_nep = pygame.sprite.groupcollide(nepřátelé, střely_hráč, True, True)
        for en in kolize_nep:
            skore += 1
            ex = Exploze(en.rect.centerx, en.rect.centery)
            všechny_sprity.add(ex)

        if pygame.sprite.spritecollideany(hráč, střely_nep) or pygame.sprite.spritecollideany(hráč, nepřátelé):
            uloz_vysledek(AKTUALNI_UZIVATEL, skore)
            running = False

        okno.blit(pozadi_img, (0, 0))
        všechny_sprity.draw(okno)
        if boss_aktivní and boss: boss.vykresli_životy(okno)
        vykresli_text(f"{AKTUALNI_UZIVATEL} | Skóre: {skore}", font_skore, ŽLUTÁ, ŠÍŘKA//2, 30)
        if hráč.lucky_timer > ted: vykresli_text("BUFF!", font_skore, ZELENÁ, 50, VÝŠKA-30)
        pygame.display.flip()

# === MENU ===
def menu():
    global rozliseni_index, ŠÍŘKA, VÝŠKA, okno, AKTUALNI_UZIVATEL
    while True:
        okno.fill(ČERNÁ); s = scale()
        vykresli_text("2D SHIP SHOOTER PRO", font_nadpis, BÍLÁ, ŠÍŘKA//2, int(100*s))
        status = AKTUALNI_UZIVATEL if AKTUALNI_UZIVATEL else "Nepřihlášen"
        barva_statusu = ZELENÁ if AKTUALNI_UZIVATEL else ŠEDÁ
        vykresli_text(f"Uživatel: {status}", font_skore, barva_statusu, ŠÍŘKA//2, int(160*s))
        
        polozky = [("HRÁT / LOGIN", 240), ("REGISTRACE", 300), 
                   (f"ROZLIŠENÍ: {ROZLISENI_LIST[rozliseni_index][0]}x{ROZLISENI_LIST[rozliseni_index][1]}", 360),
                   ("OTEVŘÍT WEB", 420), ("ODHLÁSIT", 480), ("KONEC", 540)]
        
        mx, my = pygame.mouse.get_pos()
        for i, (txt, y) in enumerate(polozky):
            y_pos = int(y * s); hover = abs(my - y_pos) < 20 and abs(mx - ŠÍŘKA//2) < 150
            barva = ZELENÁ if hover else BÍLÁ
            if i == 4 and not AKTUALNI_UZIVATEL: barva = ŠEDÁ
            vykresli_text(txt, font_menu, barva, ŠÍŘKA//2, y_pos)
            
            if pygame.mouse.get_pressed()[0] and hover:
                pygame.time.delay(200)
                if i == 0: hra()
                elif i == 1: obrazovka_ucet("register")
                elif i == 2:
                    rozliseni_index = (rozliseni_index + 1) % len(ROZLISENI_LIST)
                    ŠÍŘKA, VÝŠKA = ROZLISENI_LIST[rozliseni_index]
                    okno = pygame.display.set_mode((ŠÍŘKA, VÝŠKA)); aktualizuj_assetty()
                
                # --- OPRAVENÉ OTEVÍRÁNÍ WEBU ---
                elif i == 3: 
                    cesta_k_webu = os.path.abspath(os.path.join(ADRESAR_HRY, "web.html"))
                    if os.path.exists(cesta_k_webu):
                        # Převedení cesty na URL formát s ošetřením zpětných lomítek
                        url = f"file:///{cesta_k_webu.replace(os.sep, '/')}"
                        try:
                            # Pokus o vynucení Chrome (pro Windows)
                            chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe \"%s\""
                            if os.path.exists("C:/Program Files/Google/Chrome/Application/chrome.exe"):
                                webbrowser.get(chrome_path).open(url)
                            else:
                                webbrowser.open(url)
                        except:
                            webbrowser.open(url)
                    else:
                        print(f"Soubor {cesta_k_webu} nebyl nalezen!")
                
                elif i == 4: AKTUALNI_UZIVATEL = None
                elif i == 5: pygame.quit(); sys.exit()
        
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()

if __name__ == "__main__":
    menu()