import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Segoe UI", 30)

# Barvy
BG_COLOR = (7, 16, 39)
TEXT_COLOR = (234, 246, 255)
BUTTON_COLOR = (30, 167, 255)
BUTTON_HOVER = (13, 141, 229)
ACTIVE_BORDER = (255, 200, 50)
EYE_HOVER = (255, 200, 50)
BORDER_COLOR = (200, 40, 40)  # červený rámeček
BLOCK_SIZE = 20

# Stav aplikace
screen_state = "menu"
username = ""
password = ""
show_password = False
active_input = None

# Snake proměnné
snake = []
dx = dy = 0
food = []
score = 0
paused = False
snake_timer = 0
snake_speed = 150  # rychlost hada v ms

# Načtení obrázků
snake_head_img = pygame.image.load("head.png").convert_alpha()
snake_body_img = pygame.image.load("body.png").convert_alpha()
snake_tail_img = pygame.image.load("ass.png").convert_alpha()
apple_img = pygame.image.load("Jablko.png").convert_alpha()


def draw_text(surface, text, pos, font, color=TEXT_COLOR):
    label = font.render(text, True, color)
    rect = label.get_rect(center=pos)
    surface.blit(label, rect)


def button(surface, text, rect, action=None):
    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=8)
    draw_text(surface, text, rect.center, FONT)
    if rect.collidepoint(mouse_pos) and click[0] == 1 and action:
        pygame.time.delay(150)
        action()


def start_game():
    global snake, dx, dy, food, score, paused, screen_state
    snake = [[WIDTH // 2, HEIGHT // 2]]
    dx = dy = 0
    score = 0
    paused = False
    spawn_food()
    change_screen("game")


def spawn_food():
    global food
    # Hrací plocha pod skóre – rámeček 50px nahoře
    food = [
        random.randrange(1, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE,
        random.randrange(3, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
    ]


def change_screen(state):
    global screen_state, active_input, username, password
    screen_state = state
    if state == "menu":
        active_input = None
        username = ""
        password = ""


def toggle_password():
    global show_password
    show_password = not show_password


def draw_login():
    WIN.fill(BG_COLOR)
    draw_text(WIN, "Uživatelské jméno:", (WIDTH // 2, HEIGHT // 2 - 130), FONT)
    draw_text(WIN, "Heslo:", (WIDTH // 2, HEIGHT // 2 - 20), FONT)

    global username_rect, password_rect, show_rect, back_rect, confirm_rect
    username_rect = pygame.Rect(WIDTH // 2 - 125, HEIGHT // 2 - 100, 250, 50)
    password_rect = pygame.Rect(WIDTH // 2 - 125, HEIGHT // 2, 250, 50)
    show_rect = pygame.Rect(WIDTH // 2 + 135, HEIGHT // 2, 50, 50)
    confirm_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 70, 150, 50)
    back_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 140, 150, 50)

    username_color = ACTIVE_BORDER if active_input == "username" else TEXT_COLOR
    password_color = ACTIVE_BORDER if active_input == "password" else TEXT_COLOR
    pygame.draw.rect(WIN, username_color, username_rect, 3, border_radius=5)
    pygame.draw.rect(WIN, password_color, password_rect, 3, border_radius=5)

    username_surface = FONT.render(username, True, TEXT_COLOR)
    WIN.blit(username_surface, username_surface.get_rect(center=username_rect.center))

    display_pass = password if show_password else '*' * len(password)
    password_surface = FONT.render(display_pass, True, TEXT_COLOR)
    WIN.blit(password_surface, password_surface.get_rect(center=password_rect.center))

    mouse_pos = pygame.mouse.get_pos()
    eye_color = EYE_HOVER if show_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.ellipse(WIN, eye_color, show_rect, 2)
    if show_password:
        pygame.draw.circle(WIN, eye_color, show_rect.center, 5)
    else:
        pygame.draw.line(WIN, eye_color,
                         (show_rect.left + 5, show_rect.top + show_rect.height // 2),
                         (show_rect.right - 5, show_rect.top + show_rect.height // 2), 3)

    button(WIN, "Potvrdit", confirm_rect, lambda: change_screen("menu"))
    button(WIN, "Zpět", back_rect, lambda: change_screen("menu"))


def draw_menu():
    WIN.fill(BG_COLOR)
    draw_text(WIN, "Snake Game", (WIDTH // 2, HEIGHT // 4), FONT)

    play_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 - 90, 150, 50)
    controls_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 - 20, 150, 50)
    login_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 50, 150, 50)
    end_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 120, 150, 50)

    button(WIN, "Play", play_rect, start_game)
    button(WIN, "Ovládání", controls_rect, lambda: change_screen("controls"))
    button(WIN, "Login", login_rect, lambda: change_screen("login"))
    button(WIN, "Konec", end_rect, lambda: sys.exit())


def draw_controls():
    WIN.fill(BG_COLOR)
    draw_text(WIN, "Ovládání hry", (WIDTH // 2, HEIGHT // 4), FONT)
    draw_text(WIN, "Šipky / W,A,S,D: pohyb hada", (WIDTH // 2, HEIGHT // 2 - 40), FONT, TEXT_COLOR)
    draw_text(WIN, "SPACE / P: pauza", (WIDTH // 2, HEIGHT // 2), FONT, TEXT_COLOR)
    draw_text(WIN, "ENTER: návrat do menu ze hry", (WIDTH // 2, HEIGHT // 2 + 40), FONT, TEXT_COLOR)

    back_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 100, 150, 50)
    button(WIN, "Zpět", back_rect, lambda: change_screen("menu"))


def draw_game(delta_time):
    global snake, dx, dy, food, score, snake_timer
    WIN.fill(BG_COLOR)

    # Rámeček skóre
    score_rect = pygame.Rect(10, 10, 140, 40)
    pygame.draw.rect(WIN, (255, 255, 255), score_rect, 2)
    draw_text(WIN, f"Skóre: {score}", score_rect.center, FONT)

    # Červený rám pro herní plochu
    play_area = pygame.Rect(0, 60, WIDTH, HEIGHT - 60)
    pygame.draw.rect(WIN, BORDER_COLOR, play_area, 3)

    if not paused:
        snake_timer += delta_time
        if snake_timer >= snake_speed:
            snake_timer = 0
            new_head = [snake[0][0] + dx, snake[0][1] + dy]
            snake.insert(0, new_head)

            if snake[0] == food:
                score += 1
                spawn_food()
            else:
                snake.pop()

            # Kolize s hranou hrací plochy nebo se sebou
            if (new_head[0] < play_area.left or
                new_head[0] >= play_area.right - BLOCK_SIZE or
                new_head[1] < play_area.top or
                new_head[1] >= play_area.bottom - BLOCK_SIZE or
                new_head in snake[1:]):
                draw_text(WIN, f"Hra skončila! Skóre: {score}", (WIDTH // 2, HEIGHT // 2), FONT)
                pygame.display.update()
                pygame.time.delay(2000)
                change_screen("menu")

    # Vykreslení hada
    for i, segment in enumerate(snake):
        if i == 0:  # hlava
            if dx == BLOCK_SIZE:
                head_rotated = pygame.transform.rotate(snake_head_img, -90)
            elif dx == -BLOCK_SIZE:
                head_rotated = pygame.transform.rotate(snake_head_img, 90)
            elif dy == -BLOCK_SIZE:
                head_rotated = snake_head_img
            elif dy == BLOCK_SIZE:
                head_rotated = pygame.transform.rotate(snake_head_img, 180)
            else:
                head_rotated = snake_head_img
            WIN.blit(head_rotated, segment)
        elif i == len(snake) - 1:  # ocas
            prev = snake[i - 1]
            if segment[0] < prev[0]:
                tail_rotated = pygame.transform.rotate(snake_tail_img, 270)
            elif segment[0] > prev[0]:
                tail_rotated = pygame.transform.rotate(snake_tail_img, 90)
            elif segment[1] < prev[1]:
                tail_rotated = pygame.transform.rotate(snake_tail_img, 180)
            elif segment[1] > prev[1]:
                tail_rotated = snake_tail_img
            WIN.blit(tail_rotated, segment)
        else:
            WIN.blit(snake_body_img, segment)

    WIN.blit(apple_img, food)


# ===============================
# HLAVNÍ SMYČKA
# ===============================
while True:
    delta_time = CLOCK.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if screen_state == "login":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if username_rect.collidepoint(event.pos):
                    active_input = "username"
                elif password_rect.collidepoint(event.pos):
                    active_input = "password"
                elif show_rect.collidepoint(event.pos):
                    toggle_password()
                else:
                    active_input = None
            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_BACKSPACE:
                    if active_input == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]
                elif event.key == pygame.K_RETURN:
                    pass
                else:
                    if active_input == "username" and len(username) < 20:
                        username += event.unicode
                    elif active_input == "password" and len(password) < 20:
                        password += event.unicode

        if screen_state == "game" and event.type == pygame.KEYDOWN:
            if not paused:  # <<<<< přidáno – zabrání pohybu při pauze
                if event.key in [pygame.K_UP, pygame.K_w] and dy == 0:
                    dx, dy = 0, -BLOCK_SIZE
                if event.key in [pygame.K_DOWN, pygame.K_s] and dy == 0:
                    dx, dy = 0, BLOCK_SIZE
                if event.key in [pygame.K_LEFT, pygame.K_a] and dx == 0:
                    dx, dy = -BLOCK_SIZE, 0
                if event.key in [pygame.K_RIGHT, pygame.K_d] and dx == 0:
                    dx, dy = BLOCK_SIZE, 0

            if event.key in [pygame.K_SPACE, pygame.K_p]:
                paused = not paused
            if event.key == pygame.K_RETURN:
                change_screen("menu")

    if screen_state == "menu":
        draw_menu()
    elif screen_state == "login":
        draw_login()
    elif screen_state == "controls":
        draw_controls()
    elif screen_state == "game":
        draw_game(delta_time)

    pygame.display.update()
