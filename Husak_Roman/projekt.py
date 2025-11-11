import pygame
import random
import sys

# Inicializace pygame
pygame.init()

# Konstanty
ŠÍŘKA, VÝŠKA = 800, 600
FPS = 60
BÍLÁ = (255, 255, 255)
ZELENÁ = (0, 255, 0)
ČERVENÁ = (255, 0, 0)
ŽLUTÁ = (255, 255, 0)
ČERNÁ = (0, 0, 0)

# Jas aplikace (0 = tmavé, 255 = plný jas)
jas = 255

# Herní okno
okno = pygame.display.set_mode((ŠÍŘKA, VÝŠKA))
pygame.display.set_caption("2D Ship Shooter")

# Fonty
font_nadpis = pygame.font.Font(None, 70)
font_menu = pygame.font.Font(None, 50)
font_skore = pygame.font.Font(None, 30)

# Načtení obrázků lodí
lod_hrac = pygame.image.load("lod1.png").convert_alpha()
lod_nepritel = pygame.image.load("lod2.png").convert_alpha()

lod_hrac = pygame.transform.scale(lod_hrac, (70, 60))
lod_nepritel = pygame.transform.scale(lod_nepritel, (60, 60))
lod_nepritel = pygame.transform.rotate(lod_nepritel, 180)


# --- TŘÍDY ---
class Hráč(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = lod_hrac
        self.rect = self.image.get_rect(center=(ŠÍŘKA // 2, VÝŠKA - 60))
        self.rychlost = 5

    def update(self, keys=None):
        if keys is None:
            keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.rychlost
        if keys[pygame.K_RIGHT] and self.rect.right < ŠÍŘKA:
            self.rect.x += self.rychlost
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.rychlost
        if keys[pygame.K_DOWN] and self.rect.bottom < VÝŠKA:
            self.rect.y += self.rychlost

    def střela(self):
        projektil = Projektil(self.rect.centerx, self.rect.top, -8, ZELENÁ)
        všechny_sprity.add(projektil)
        hráčovy_střely.add(projektil)


class Nepřítel(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = lod_nepritel
        self.rect = self.image.get_rect(center=(
            random.randint(40, ŠÍŘKA - 40),
            random.randint(40, VÝŠKA // 3)
        ))
        self.cooldown = random.randint(60, 120)
        self.směr = random.choice([-1, 1])

    def update(self):
        self.rect.x += self.směr * 2
        if self.rect.left <= 0 or self.rect.right >= ŠÍŘKA:
            self.směr *= -1

        self.cooldown -= 1
        if self.cooldown <= 0:
            self.cooldown = random.randint(60, 120)
            střela = Projektil(self.rect.centerx, self.rect.bottom, 6, ŽLUTÁ)
            všechny_sprity.add(střela)
            nepřátelské_střely.add(střela)


class Projektil(pygame.sprite.Sprite):
    def __init__(self, x, y, rychlost, barva):
        super().__init__()
        self.image = pygame.Surface((6, 12))
        self.image.fill(barva)
        self.rect = self.image.get_rect(center=(x, y))
        self.rychlost = rychlost

    def update(self):
        self.rect.y += self.rychlost
        if self.rect.bottom < 0 or self.rect.top > VÝŠKA:
            self.kill()


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("lod4.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (150, 120))
        self.rect = self.image.get_rect(center=(ŠÍŘKA // 2, 100))
        self.rychlost = 3
        self.směr = 1
        self.cooldown = 90
        self.životy = 10

    def update(self):
        self.rect.x += self.směr * self.rychlost
        if self.rect.left <= 0 or self.rect.right >= ŠÍŘKA:
            self.směr *= -1

        self.cooldown -= 1
        if self.cooldown <= 0:
            self.cooldown = 90
            střela1 = Projektil(self.rect.centerx, self.rect.bottom, 6, ŽLUTÁ)
            střela2 = Projektil(self.rect.left + 20, self.rect.bottom, 6, ŽLUTÁ)
            střela3 = Projektil(self.rect.right - 20, self.rect.bottom, 6, ŽLUTÁ)
            všechny_sprity.add(střela1, střela2, střela3)
            nepřátelské_střely.add(střela1, střela2, střela3)

    def vykresli_životy(self, surface):
        for i in range(self.životy):
            pygame.draw.rect(surface, ČERVENÁ, (self.rect.left + i*15, self.rect.top - 20, 10, 10))


# --- FUNKCE ---
def vykresli_text(text, font, barva, střed):
    render = font.render(text, True, barva)
    rect = render.get_rect(center=střed)
    okno.blit(render, rect)


def nastaveni():
    global jas
    běží = True
    while běží:
        okno.fill(ČERNÁ)
        vykresli_text("NASTAVENÍ", font_nadpis, BÍLÁ, (ŠÍŘKA // 2, 150))
        vykresli_text(f"Jas: {jas}", font_menu, BÍLÁ, (ŠÍŘKA // 2, 300))
        vykresli_text("ZVÝŠIT JAS", font_menu, ZELENÁ, (ŠÍŘKA // 2, 380))
        vykresli_text("SNÍŽIT JAS", font_menu, ČERVENÁ, (ŠÍŘKA // 2, 460))
        vykresli_text("ZPĚT", font_menu, BÍLÁ, (ŠÍŘKA // 2, 530))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 355 < y < 405:
                    jas = min(255, jas + 25)
                elif 435 < y < 485:
                    jas = max(0, jas - 25)
                elif 505 < y < 555:
                    běží = False


def menu():
    while True:
        okno.fill(ČERNÁ)
        vykresli_text("2D SHIP SHOOTER", font_nadpis, BÍLÁ, (ŠÍŘKA // 2, 150))
        vykresli_text("HRÁT", font_menu, ZELENÁ, (ŠÍŘKA // 2, 300))
        vykresli_text("NASTAVENÍ", font_menu, BÍLÁ, (ŠÍŘKA // 2, 380))
        vykresli_text("KONEC", font_menu, ČERVENÁ, (ŠÍŘKA // 2, 460))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 275 < y < 325:
                    hra()
                elif 355 < y < 405:
                    nastaveni()
                elif 435 < y < 485:
                    pygame.quit()
                    sys.exit()


def hra():
    global všechny_sprity, hráčovy_střely, nepřátelské_střely

    všechny_sprity = pygame.sprite.Group()
    hráčovy_střely = pygame.sprite.Group()
    nepřátelské_střely = pygame.sprite.Group()
    nepřátelé = pygame.sprite.Group()

    hráč = Hráč()
    všechny_sprity.add(hráč)

    hodiny = pygame.time.Clock()
    spawn_timer = 0
    běží = True
    skore = 0

    boss = None
    boss_aktivní = False

    while běží:
        hodiny.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    hráč.střela()
                elif event.key == pygame.K_r:
                    běží = False  # návrat do menu

        keys = pygame.key.get_pressed()
        hráč.update(keys)

        # Spawn nepřátel jen pokud není boss
        if not boss_aktivní:
            spawn_timer += 1
            if spawn_timer > 80 and len(nepřátelé) < 6:
                spawn_timer = 0
                nepřítel = Nepřítel()
                všechny_sprity.add(nepřítel)
                nepřátelé.add(nepřítel)

        # Spawni bosse po 10 bodech
        if skore >= 10 and not boss_aktivní:
            boss = Boss()
            všechny_sprity.add(boss)
            boss_aktivní = True
            nepřátelé.empty()  # vyčisti normální nepřátele

        všechny_sprity.update()

        # Zásahy bosse
        if boss_aktivní:
            zásahy_boss = pygame.sprite.spritecollide(boss, hráčovy_střely, True)
            boss.životy -= len(zásahy_boss)
            if boss.životy <= 0:
                boss.kill()
                boss_aktivní = False
                skore = 0  # reset skóre nebo pokračuj

        # Zásahy normálních nepřátel
        zásahy = pygame.sprite.groupcollide(nepřátelé, hráčovy_střely, True, True)
        skore += len(zásahy)

        # Kolize hráče
        if pygame.sprite.spritecollideany(hráč, nepřátelské_střely):
            běží = False

        # Kreslení
        okno.fill(ČERNÁ)
        všechny_sprity.draw(okno)

        # Kreslení skóre
        text_skore = font_skore.render(f"Skóre: {skore}", True, BÍLÁ)
        okno.blit(text_skore, (10, VÝŠKA - 30))

        # Kreslení životů bosse
        if boss_aktivní:
            boss.vykresli_životy(okno)

        # Překrytí pro jas
        if jas < 255:
            překryv = pygame.Surface((ŠÍŘKA, VÝŠKA))
            překryv.set_alpha(255 - jas)
            překryv.fill(ČERNÁ)
            okno.blit(překryv, (0, 0))

        pygame.display.flip()

    menu()


# --- SPUŠTĚNÍ ---
menu()
