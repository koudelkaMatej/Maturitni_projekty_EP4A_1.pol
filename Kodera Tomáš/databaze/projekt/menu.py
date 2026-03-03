import pygame
import sys
from main import game_loop 

pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blood Dash Menu")

# Fonty a barvy
font = pygame.font.SysFont(None, 60)
small_font = pygame.font.SysFont(None, 40)
WHITE, BLACK, RED, BLUE, GRAY = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 100, 255), (100, 100, 100)

# === PROMĚNNÉ PRO JMÉNO ===
user_name = ""  # Začínáme s prázdným jménem
input_active = False # Je políčko aktivní (píše se do něj)?
input_rect = pygame.Rect(WIDTH // 2 - 150, 100, 300, 50) # Pozice boxu pro jméno

menu_items = ["Start", "Options", "Quit"]

def draw_menu(mouse_pos):
    screen.fill(BLACK)
    
    # 1. Vykreslení textu nad políčkem
    label = small_font.render("Zadej jméno a potvrď Enterem:", True, WHITE)
    screen.blit(label, (input_rect.x, input_rect.y - 40))

    # 2. Vykreslení obdélníku pro vstup
    color = BLUE if input_active else GRAY
    pygame.draw.rect(screen, color, input_rect, 2)
    
    # 3. Vykreslení psaného jména
    name_surface = font.render(user_name, True, WHITE)
    screen.blit(name_surface, (input_rect.x + 5, input_rect.y + 5))

    # 4. Vykreslení položek menu (Start, Options, Quit)
    for i, item in enumerate(menu_items):
        text = font.render(item, True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 80))
        if text_rect.collidepoint(mouse_pos):
            text = font.render(item, True, RED)
        screen.blit(text, text_rect)
    
    pygame.display.update()

def main_menu():
    global user_name, input_active
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        draw_menu(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Kliknutí na políčko pro jméno
                if input_rect.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
                
                # Kliknutí na tlačítka menu
                if event.button == 1:
                    for i, item in enumerate(menu_items):
                        text_rect = font.render(item, True, WHITE).get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 80))
                        if text_rect.collidepoint(mouse_pos):
                            if item == "Quit":
                                pygame.quit(); sys.exit()
                            elif item == "Start":
                                if user_name == "": user_name = "Hrac" # Pojistka
                                
                                # SPUŠTĚNÍ HRY SE ZADANÝM JMÉNEM
                                while True:
                                    result = game_loop(user_name)
                                    if result == "restart": continue
                                    else: break

            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    input_active = False # Enterem potvrdíš jméno
                elif event.key == pygame.K_BACKSPACE:
                    user_name = user_name[:-1] # Smazání znaku
                else:
                    # Přidání znaku (pokud není jméno moc dlouhé)
                    if len(user_name) < 15:
                        user_name += event.unicode

if __name__ == "__main__":
    main_menu()