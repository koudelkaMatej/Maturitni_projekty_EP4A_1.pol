import pygame
import sys
import math
import random
import os
from main import game_loop

# === GLOBÁLNÍ NASTAVENÍ ===
RESOLUTIONS = [(1280, 720), (1600, 900), (1920, 1080)]
current_res_index = 2
WIDTH, HEIGHT = RESOLUTIONS[current_res_index]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blood Dash Menu")

font = pygame.font.SysFont(None, 60)
small_font = pygame.font.SysFont(None, 40)
WHITE, BLACK, RED, BLUE, GRAY = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 100, 255), (100, 100, 100)

user_name = ""
input_active = False
menu_items = ["Start", "Options", "Quit"]

# === KREV ===
class BloodSplat:
    def __init__(self, x, y, image, angle):
        final_angle = angle + random.randint(-12, 12)
        scale = random.uniform(0.18, 0.42)
        self.image = pygame.transform.rotozoom(image, final_angle, scale)
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = random.uniform(160, 230)
        self.fade_speed = random.uniform(0.25, 0.55)

    def draw(self, surface):
        self.image.set_alpha(int(self.alpha))
        surface.blit(self.image, self.rect)

    def update(self):
        self.alpha -= self.fade_speed
        return self.alpha > 0


# === NAČTENÍ BLOOD OBRÁZKU ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLOOD_PATH = os.path.join(BASE_DIR, "assets", "blood", "Bloodtrail.png")
BLOOD_IMAGE = pygame.image.load(BLOOD_PATH).convert_alpha()


# === RANDOM KREVNÍ STOPY ===
blood_list = []
next_blood_time = pygame.time.get_ticks()


def spawn_random_dash():
    """Spawne jednu náhodnou krevní stopu na random místě obrazovky."""
    sx = random.randint(50, WIDTH - 50)
    sy = random.randint(50, HEIGHT - 50)
    angle_deg = random.uniform(0, 360)
    angle_rad = math.radians(angle_deg)
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)
    dash_len = random.randint(120, 380)
    splat_angle = -math.degrees(math.atan2(dy, dx))
    num = random.randint(6, 10)
    step = dash_len / num
    for i in range(num):
        bx = sx + dx * i * step
        by = sy + dy * i * step
        blood_list.append(BloodSplat(bx, by, BLOOD_IMAGE, splat_angle))


def init_blood():
    """Předgeneruj stopy při startu aby nebyl prázdný background."""
    for _ in range(8):
        spawn_random_dash()


def update_blood(current_time):
    global next_blood_time, blood_list
    if current_time >= next_blood_time:
        spawn_random_dash()
        next_blood_time = current_time + random.randint(200, 500)
    blood_list = [b for b in blood_list if b.update()]
    if len(blood_list) > 500:
        blood_list = blood_list[-400:]


# === OPTIONS MENU ===
def options_menu():
    global WIDTH, HEIGHT, screen, current_res_index
    running = True
    clock = pygame.time.Clock()
    while running:
        current_time = pygame.time.get_ticks()
        screen.fill(BLACK)
        update_blood(current_time)
        for b in blood_list:
            b.draw(screen)

        mouse_pos = pygame.mouse.get_pos()
        title = font.render("Nastavení Rozlišení", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        res_text = f"Rozlišení: {RESOLUTIONS[current_res_index][0]}x{RESOLUTIONS[current_res_index][1]}"
        res_surface = font.render(res_text, True, BLUE)
        res_rect = res_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        if res_rect.collidepoint(mouse_pos):
            res_surface = font.render(res_text, True, RED)
        screen.blit(res_surface, res_rect)

        back_text = font.render("Zpět do menu", True, WHITE)
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        if back_rect.collidepoint(mouse_pos):
            back_text = font.render("Zpět do menu", True, RED)
        screen.blit(back_text, back_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if res_rect.collidepoint(mouse_pos):
                    current_res_index = (current_res_index + 1) % len(RESOLUTIONS)
                    WIDTH, HEIGHT = RESOLUTIONS[current_res_index]
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                if back_rect.collidepoint(mouse_pos):
                    running = False

        pygame.display.update()
        clock.tick(60)


# === DRAW MENU ===
def draw_menu(mouse_pos, input_rect, current_time):
    screen.fill(BLACK)

    update_blood(current_time)
    for b in blood_list:
        b.draw(screen)

    # 1. Tmavý panel za UI
    panel_w, panel_h = 300, 150 # Mírně zvětšeno pro lepší vzhled
    panel_x = WIDTH // 2 - panel_w // 2
    panel_y = input_rect.y - 60
    
    panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel_surf.fill((0, 0, 0, 180)) # Trochu tmavší průhlednost
    screen.blit(panel_surf, (panel_x, panel_y))
    
    # 2. Vstupní pole pro jméno
    label = small_font.render("Zadej jméno a potvrď Enterem:", True, WHITE)
    screen.blit(label, (WIDTH // 2 - label.get_width() // 2, input_rect.y - 40))

    # Barva ohraničení inputu (Modrá když píšeš, šedá když ne)
    input_border_color = BLUE if input_active else GRAY
    pygame.draw.rect(screen, input_border_color, input_rect, 2)
    
    # Vykreslení textu jména (vycentrováno v input_rect)
    name_surface = font.render(user_name, True, WHITE)
    screen.blit(name_surface, (input_rect.centerx - name_surface.get_width() // 2, input_rect.y + 5))

    # 3. Menu položky
    for i, item in enumerate(menu_items):
        text_color = RED if font.render(item, True, WHITE).get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 80)).collidepoint(mouse_pos) else WHITE
        text = font.render(item, True, text_color)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 80))
        screen.blit(text, text_rect)

    pygame.display.update()


# === MAIN MENU ===
def main_menu():
    global user_name, input_active, WIDTH, HEIGHT
    init_blood()
    running = True
    clock = pygame.time.Clock()

    while running:
        current_time = pygame.time.get_ticks()
        input_rect = pygame.Rect(WIDTH // 2 - 150, 100, 300, 50)
        mouse_pos = pygame.mouse.get_pos()
        draw_menu(mouse_pos, input_rect, current_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False

                if event.button == 1:
                    for i, item in enumerate(menu_items):
                        text_rect = font.render(item, True, WHITE).get_rect(
                            center=(WIDTH // 2, HEIGHT // 2 + i * 80))
                        if text_rect.collidepoint(mouse_pos):
                            if item == "Quit":
                                pygame.quit(); sys.exit()
                            elif item == "Options":
                                options_menu()
                            elif item == "Start":
                                if user_name == "":
                                    user_name = "Hrac"
                                while True:
                                    result = game_loop(user_name)
                                    if result == "restart":
                                        continue
                                    else:
                                        break

            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    user_name = user_name[:-1]
                else:
                    if len(user_name) < 15:
                        user_name += event.unicode

        clock.tick(60)


if __name__ == "__main__":
    main_menu()