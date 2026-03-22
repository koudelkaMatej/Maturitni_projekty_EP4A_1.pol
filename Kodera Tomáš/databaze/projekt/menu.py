import pygame
import sys
from main import game_loop 

# === GLOBÁLNÍ NASTAVENÍ ===
RESOLUTIONS = [(1280, 720), (1600, 900), (1920, 1080)]
current_res_index = 2  # Index pro 1920x1080
WIDTH, HEIGHT = RESOLUTIONS[current_res_index]

pygame.init()
# Přidán flag FULLSCREEN nebo RESIZABLE podle potřeby, zde klasické okno
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blood Dash Menu")

# Fonty a barvy
font = pygame.font.SysFont(None, 60)
small_font = pygame.font.SysFont(None, 40)
WHITE, BLACK, RED, BLUE, GRAY = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 100, 255), (100, 100, 100)

# === PROMĚNNÉ PRO JMÉNO ===
user_name = ""
input_active = False
# Rect se musí přepočítávat při změně rozlišení, proto ho definujeme v draw
menu_items = ["Start", "Options", "Quit"]

def options_menu():
    global WIDTH, HEIGHT, screen, current_res_index
    running = True
    while running:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()

        # Titulek
        title = font.render("Nastavení Rozlišení", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        # Zobrazení aktuálního rozlišení
        res_text = f"Rozlišení: {RESOLUTIONS[current_res_index][0]}x{RESOLUTIONS[current_res_index][1]}"
        res_surface = font.render(res_text, True, BLUE)
        res_rect = res_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        if res_rect.collidepoint(mouse_pos):
            res_surface = font.render(res_text, True, RED)
        screen.blit(res_surface, res_rect)

        # Tlačítko zpět
        back_text = font.render("Zpět do menu", True, WHITE)
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        if back_rect.collidepoint(mouse_pos):
            back_text = font.render("Zpět do menu", True, RED)
        screen.blit(back_text, back_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if res_rect.collidepoint(mouse_pos):
                        # Přepnutí rozlišení
                        current_res_index = (current_res_index + 1) % len(RESOLUTIONS)
                        WIDTH, HEIGHT = RESOLUTIONS[current_res_index]
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    
                    if back_rect.collidepoint(mouse_pos):
                        running = False

        pygame.display.update()

def draw_menu(mouse_pos, input_rect):
    screen.fill(BLACK)
    
    # 1. Text nad políčkem
    label = small_font.render("Zadej jméno a potvrď Enterem:", True, WHITE)
    screen.blit(label, (input_rect.x, input_rect.y - 40))

    # 2. Obdélník pro vstup
    color = BLUE if input_active else GRAY
    pygame.draw.rect(screen, color, input_rect, 2)
    
    # 3. Psané jméno
    name_surface = font.render(user_name, True, WHITE)
    screen.blit(name_surface, (input_rect.x + 5, input_rect.y + 5))

    # 4. Položky menu
    for i, item in enumerate(menu_items):
        text = font.render(item, True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 80))
        if text_rect.collidepoint(mouse_pos):
            text = font.render(item, True, RED)
        screen.blit(text, text_rect)
    
    pygame.display.update()

def main_menu():
    global user_name, input_active, WIDTH, HEIGHT
    running = True
    while running:
        # Dynamicky vypočítaný input_rect podle aktuálního rozlišení
        input_rect = pygame.Rect(WIDTH // 2 - 150, 100, 300, 50)
        mouse_pos = pygame.mouse.get_pos()
        draw_menu(mouse_pos, input_rect)
        
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
                        text_rect = font.render(item, True, WHITE).get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 80))
                        if text_rect.collidepoint(mouse_pos):
                            if item == "Quit":
                                pygame.quit(); sys.exit()
                            elif item == "Options":
                                options_menu()
                            elif item == "Start":
                                if user_name == "": user_name = "Hrac"
                                while True:
                                    result = game_loop(user_name)
                                    if result == "restart": continue
                                    else: break

            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    user_name = user_name[:-1]
                else:
                    if len(user_name) < 15:
                        user_name += event.unicode

if __name__ == "__main__":
    main_menu()