import random
import sys
import traceback
import pygame

from api_client import api_get, api_post
from assets import load_assets
from config import (
    ACTIVE_BORDER,
    BG_COLOR,
    BLOCK_SIZE,
    BORDER_COLOR,
    BUTTON_BAR_BG,
    BUTTON_COLOR,
    BUTTON_HOVER,
    EYE_HOVER,
    ERROR_COLOR,
    LABEL_COLOR,
    SUCCESS_COLOR,
    TEXT_COLOR,
    TOP_MARGIN,
    init_display_fullscreen,
    mode_config,
)

pygame.init()

# ===============================
# Displej a fonty
# ===============================
WIN, WIDTH, HEIGHT = init_display_fullscreen()
CLOCK = pygame.time.Clock()

FONT = pygame.font.SysFont("Segoe UI", 36)
SMALL_FONT = pygame.font.SysFont("Segoe UI", 26)
selected_mode = "classic"
current_mode = selected_mode

# ===============================
# Stav aplikace
# ===============================
screen_state = "menu"
active_input = None
paused = False

username = ""
password = ""
reg_email = ""
reg_username = ""
reg_password = ""
reg_password2 = ""
show_password_login = False
show_password_reg = False
show_password_reg2 = False
login_msg = ""
login_msg_color = TEXT_COLOR
register_msg = ""
register_msg_color = TEXT_COLOR
auth_token = ""
account_data = None
account_msg = ""
account_msg_color = TEXT_COLOR
leaderboard_data = {}
leaderboard_msg = ""
leaderboard_loading = False
leaderboard_mode = "classic"
leaderboard_left_rect = pygame.Rect(0, 0, 0, 0)
leaderboard_right_rect = pygame.Rect(0, 0, 0, 0)
leaderboard_fetched = False

# placeholdery pro rects, aby byly vždy definované
username_rect = pygame.Rect(0, 0, 0, 0)
password_rect = pygame.Rect(0, 0, 0, 0)
login_show_rect = pygame.Rect(0, 0, 0, 0)
reg_email_rect = pygame.Rect(0, 0, 0, 0)
reg_username_rect = pygame.Rect(0, 0, 0, 0)
reg_password_rect = pygame.Rect(0, 0, 0, 0)
reg_password2_rect = pygame.Rect(0, 0, 0, 0)
reg_show_rect = pygame.Rect(0, 0, 0, 0)
reg_show_rect2 = pygame.Rect(0, 0, 0, 0)
mode_buttons = []
start_rect = pygame.Rect(0, 0, 0, 0)
mode_back_rect = pygame.Rect(0, 0, 0, 0)

# ===============================
# Herní stav
# ===============================
snake = []
dx, dy = 0, 0
food = []  # {pos: [x, y], type: "normal"|"poison"}
pillars = []
score = 0
snake_timer = 0
snake_speed = mode_config[current_mode]["speed"]
LEFT_PADDING = 220
RIGHT_PADDING = 220
TOP_OFFSET = 120
BOTTOM_PADDING = 200
PLAY_AREA_SCALE = 0.63
BASE_PLAY_AREA = pygame.Rect(
    LEFT_PADDING,
    TOP_MARGIN + TOP_OFFSET,
    WIDTH - LEFT_PADDING - RIGHT_PADDING,
    HEIGHT - TOP_MARGIN - TOP_OFFSET - BOTTOM_PADDING,
)
BORDER_THICKNESS = 5
COLLISION_MARGIN = BORDER_THICKNESS // 2
def _align_block_size(value: int) -> int:
    return max(BLOCK_SIZE, (value // BLOCK_SIZE) * BLOCK_SIZE)

scaled_width = _align_block_size(int(BASE_PLAY_AREA.width * PLAY_AREA_SCALE))
scaled_height = _align_block_size(int(BASE_PLAY_AREA.height * PLAY_AREA_SCALE))
scaled_left = BASE_PLAY_AREA.left + (BASE_PLAY_AREA.width - scaled_width) // 2
scaled_top = BASE_PLAY_AREA.top + (BASE_PLAY_AREA.height - scaled_height) // 2
PLAY_AREA = pygame.Rect(scaled_left, scaled_top, scaled_width, scaled_height)
PLAY_AREA_COLLISION = PLAY_AREA.inflate(COLLISION_MARGIN * 2, COLLISION_MARGIN * 2)

# ===============================
# Načtení obrázků
# ===============================
assets = load_assets()
snake_head_img = assets["head"]
snake_body_img = assets["body"]
snake_tail_img = assets["tail"]
apple_img = assets["apple"]
poisoned_apple_img = assets["poisoned"]
pillar_img = assets["pillar"]
background_img = pygame.transform.smoothscale(assets["background"], (WIDTH, HEIGHT))

# ===============================
# Pomocné funkce
# ===============================
def draw_text(surface, text, pos, font, color=TEXT_COLOR):
    label = font.render(text, True, color)
    rect = label.get_rect(center=pos)
    surface.blit(label, rect)


def format_created_at(raw: str) -> str:
    # Show date and time without microseconds
    if not raw:
        return ""
    trimmed = raw.replace("T", " ")
    if "." in trimmed:
        trimmed = trimmed.split(".")[0]
    return trimmed


def button(surface, text, rect, action=None):
    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    hovered = rect.collidepoint(mouse_pos)
    color = BUTTON_HOVER if hovered else BUTTON_COLOR
    if hovered:
        glow_rect = rect.inflate(16, 16)
        pygame.draw.rect(surface, BUTTON_HOVER, glow_rect, border_radius=14)
    pygame.draw.rect(surface, color, rect, border_radius=10)
    draw_text(surface, text, rect.center, FONT)
    if rect.collidepoint(mouse_pos) and click[0] and action:
        pygame.time.delay(150)
        action()


def change_screen(state: str):
    global screen_state, active_input, paused, login_msg, register_msg, account_msg
    screen_state = state
    active_input = None
    paused = False
    if state in {"menu", "login", "register"}:
        login_msg = ""
        register_msg = ""
    if state != "account":
        account_msg = ""


def open_account_page():
    fetch_account()
    change_screen("account")

def reset_inputs():
    global username, password, reg_email, reg_username, reg_password, reg_password2, show_password_login, show_password_reg, show_password_reg2
    username = ""
    password = ""
    reg_email = ""
    reg_username = ""
    reg_password = ""
    reg_password2 = ""
    show_password_login = False
    show_password_reg = False
    show_password_reg2 = False


# Inicializuje nový průběh a had se začne pohybovat doprava ze středu
def start_game():
    global snake, dx, dy, food, pillars, score, snake_timer, current_mode, snake_speed
    current_mode = selected_mode
    cfg = mode_config[current_mode]
    snake_speed = cfg["speed"]
    fetch_leaderboard()

    # Had začíná uprostřed zorného pole a míří doprava
    center_x = PLAY_AREA_COLLISION.left + ((PLAY_AREA_COLLISION.width // 2) // BLOCK_SIZE) * BLOCK_SIZE
    center_y = PLAY_AREA_COLLISION.top + ((PLAY_AREA_COLLISION.height // 2) // BLOCK_SIZE) * BLOCK_SIZE
    snake = [[center_x, center_y]]
    dx, dy = BLOCK_SIZE, 0

    score = 0
    snake_timer = 0
    food = []
    pillars = []

    spawn_pillars(cfg["pillars"])
    spawn_food()
    change_screen("game")

# Vrací všechny volné bloky v bezpečné oblasti pro spawn jídla a sloupů
def available_positions():
    occupied = {tuple(pos) for pos in snake} | {tuple(p) for p in pillars}
    positions = []
    for x in range(PLAY_AREA_COLLISION.left, PLAY_AREA_COLLISION.right - BLOCK_SIZE + 1, BLOCK_SIZE):
        for y in range(PLAY_AREA_COLLISION.top, PLAY_AREA_COLLISION.bottom - BLOCK_SIZE + 1, BLOCK_SIZE):
            if (x, y) not in occupied:
                positions.append((x, y))
    return positions

# Naplní herní pole pilíři, které jsou umístěné na volných blocích
def spawn_pillars(count: int):
    global pillars
    pillars = []
    positions = available_positions()
    random.shuffle(positions)
    for pos in positions[:count]:
        pillars.append([pos[0], pos[1]])

# Udržuje zásobu normálních a případně jedovatých jablek v oblasti
def spawn_food():
    global food
    cfg = mode_config[current_mode]
    positions = available_positions()
    random.shuffle(positions)

    # Ve výběru udržuj alespoň jedno normální jablko a podle módu přidej i jedovatá.
    total_apples = 1
    ensure_poison = False
    if cfg["poison"]:
        total_apples = 2 + max(0, len(snake) // 5)
        ensure_poison = True

    food = [f for f in food if tuple(f["pos"]) in positions]
    normals = sum(1 for f in food if f["type"] == "normal")
    poisons = sum(1 for f in food if f["type"] == "poison")

    for pos in positions:
        if len(food) >= total_apples:
            break
        ftype = "normal"
        if cfg["poison"]:
            if normals == 0:
                ftype = "normal"
                normals += 1
            elif poisons == 0 and ensure_poison:
                ftype = "poison"
                poisons += 1
            else:
                ftype = random.choice(["normal", "poison"])
                if ftype == "normal":
                    normals += 1
                else:
                    poisons += 1
        else:
            normals += 1
        food.append({"pos": [pos[0], pos[1]], "type": ftype})


# ===============================
# Kreslení obrazovek
# ===============================
def draw_menu():
    global leaderboard_mode
    WIN.fill(BG_COLOR)
    ensure_leaderboard_loaded()

    title_y = HEIGHT // 6
    mode_y = title_y + 40
    draw_text(WIN, "Snake Game", (WIDTH // 2, title_y), FONT)
    draw_text(WIN, f"Vybraný mód: {mode_config[selected_mode]['label']}", (WIDTH // 2, mode_y), FONT)

    start_y = mode_y + 80
    spacing = 90

    btn_w, btn_h = 200, 54
    btn_x = max(60, WIDTH // 8)
    play_rect = pygame.Rect(btn_x, start_y + 0 * spacing, btn_w, btn_h)
    mode_rect = pygame.Rect(btn_x, start_y + 1 * spacing, btn_w, btn_h)
    controls_rect = pygame.Rect(btn_x, start_y + 2 * spacing, btn_w, btn_h)
    login_rect = pygame.Rect(btn_x, start_y + 3 * spacing, btn_w, btn_h)
    register_rect = pygame.Rect(btn_x, start_y + 4 * spacing, btn_w, btn_h)
    end_rect = pygame.Rect(btn_x, start_y + 5 * spacing, btn_w, btn_h)

    global account_rect, leaderboard_left_rect, leaderboard_right_rect
    account_rect = pygame.Rect(WIDTH - 190, 20, 170, 45)
    button(WIN, "Můj účet", account_rect, open_account_page)

    button(WIN, "Play", play_rect, start_game)
    button(WIN, "Gamemode", mode_rect, lambda: change_screen("mode_select"))
    button(WIN, "Ovládání", controls_rect, lambda: change_screen("controls"))
    button(WIN, "Přihlášení", login_rect, lambda: change_screen("login"))
    button(WIN, "Registrace", register_rect, lambda: change_screen("register"))
    button(WIN, "Konec", end_rect, lambda: sys.exit())

    panel_w = 360
    panel_h = 32 * 11 + 50
    panel_x = WIDTH - panel_w - 40
    panel_y = max(mode_y + 20, start_y - 30)
    pygame.draw.rect(WIN, BUTTON_BAR_BG, (panel_x, panel_y, panel_w, panel_h), border_radius=8)
    pygame.draw.rect(WIN, ACTIVE_BORDER, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=8)

    modes = list(mode_config.keys())
    if leaderboard_mode not in modes:
        leaderboard_mode = modes[0]
    current_idx = modes.index(leaderboard_mode)
    title = f"Top 10 — {mode_config[leaderboard_mode]['label']}"
    draw_text(WIN, title, (panel_x + panel_w // 2, panel_y + 18), SMALL_FONT)

    arrow_size = 28
    leaderboard_left_rect = pygame.Rect(panel_x + 10, panel_y + 6, arrow_size, arrow_size)
    leaderboard_right_rect = pygame.Rect(panel_x + panel_w - arrow_size - 10, panel_y + 6, arrow_size, arrow_size)

    pygame.draw.polygon(WIN, TEXT_COLOR, [
        (leaderboard_left_rect.right, leaderboard_left_rect.top),
        (leaderboard_left_rect.left, leaderboard_left_rect.centery),
        (leaderboard_left_rect.right, leaderboard_left_rect.bottom)
    ], 0)
    pygame.draw.polygon(WIN, TEXT_COLOR, [
        (leaderboard_right_rect.left, leaderboard_right_rect.top),
        (leaderboard_right_rect.right, leaderboard_right_rect.centery),
        (leaderboard_right_rect.left, leaderboard_right_rect.bottom)
    ], 0)

    entries = leaderboard_data.get(leaderboard_mode, [])
    list_start_y = panel_y + 40
    row_h = 32
    if leaderboard_msg:
        draw_text(WIN, leaderboard_msg, (panel_x + panel_w // 2, panel_y + panel_h // 2), SMALL_FONT, ERROR_COLOR if not leaderboard_loading else TEXT_COLOR)
    else:
        for i in range(10):
            if i < len(entries):
                row = entries[i]
                username = row.get('username', '---')
                sc = row.get('score', 0)
                line = f"{i+1:>2}. {username[:14]:14}  {sc}"
            else:
                line = f"{i+1:>2}. ---"
            line_surf = SMALL_FONT.render(line, True, TEXT_COLOR)
            WIN.blit(line_surf, (panel_x + 14, list_start_y + i * row_h))
    button(WIN, "Registrace", register_rect, lambda: change_screen("register"))
    button(WIN, "Konec", end_rect, lambda: sys.exit())


def draw_controls():
    WIN.fill(BG_COLOR)
    draw_text(WIN, "Ovládání hry", (WIDTH // 2, HEIGHT // 4), FONT)
    draw_text(WIN, "Šipky / W,A,S,D: pohyb hada", (WIDTH // 2, HEIGHT // 2 - 40), FONT)
    draw_text(WIN, "SPACE / P: pauza", (WIDTH // 2, HEIGHT // 2), FONT)
    draw_text(WIN, "ENTER: návrat do menu", (WIDTH // 2, HEIGHT // 2 + 40), FONT)
    back_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 100, 150, 50)
    button(WIN, "Zpět", back_rect, lambda: change_screen("menu"))


def draw_login():
    WIN.fill(BG_COLOR)
    global username_rect, password_rect, login_show_rect, login_back_rect, login_confirm_rect

    card_w = min(520, WIDTH - 160)
    card_x = (WIDTH - card_w) // 2
    card_y = HEIGHT // 6
    top_y = card_y + 140
    spacing = 110
    field_h = 58
    btn_h = 58
    btn_gap = 16
    btn_y = top_y + 2 * spacing + 30

    draw_text(WIN, "Přihlášení", (WIDTH // 2, card_y + 26), FONT)

    draw_text(WIN, "Uživatelské jméno nebo e-mail", (WIDTH // 2, top_y), FONT, LABEL_COLOR)
    username_rect = pygame.Rect(card_x, top_y + 22, card_w, field_h)

    draw_text(WIN, "Heslo", (WIDTH // 2, top_y + spacing), FONT, LABEL_COLOR)
    password_rect = pygame.Rect(card_x, top_y + spacing + 22, card_w, field_h)
    login_show_rect = pygame.Rect(password_rect.right - 44, password_rect.top + 10, 38, 38)

    username_color = ACTIVE_BORDER if active_input == "login_username" else TEXT_COLOR
    password_color = ACTIVE_BORDER if active_input == "login_password" else TEXT_COLOR
    pygame.draw.rect(WIN, username_color, username_rect, 2, border_radius=8)
    pygame.draw.rect(WIN, password_color, password_rect, 2, border_radius=8)

    username_surface = FONT.render(username, True, TEXT_COLOR)
    WIN.blit(username_surface, username_surface.get_rect(center=username_rect.center))

    display_pass = password if show_password_login else "*" * len(password)
    password_surface = FONT.render(display_pass, True, TEXT_COLOR)
    WIN.blit(password_surface, password_surface.get_rect(center=password_rect.center))

    mouse_pos = pygame.mouse.get_pos()
    eye_color = EYE_HOVER if login_show_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.ellipse(WIN, eye_color, login_show_rect, 2)
    if show_password_login:
        pygame.draw.circle(WIN, eye_color, login_show_rect.center, 5)
    else:
        pygame.draw.line(WIN, eye_color, (login_show_rect.left + 5, login_show_rect.centery), (login_show_rect.right - 5, login_show_rect.centery), 3)

    button_bar_rect = pygame.Rect(card_x, btn_y - 14, card_w, btn_h + 28)
    pygame.draw.rect(WIN, BUTTON_BAR_BG, button_bar_rect, border_radius=10)

    btn_w = (card_w - 2 * btn_gap) // 3
    login_confirm_rect = pygame.Rect(card_x, btn_y, btn_w, btn_h)
    login_register_rect = pygame.Rect(card_x + btn_w + btn_gap, btn_y, btn_w, btn_h)
    login_back_rect = pygame.Rect(card_x + 2 * (btn_w + btn_gap), btn_y, btn_w, btn_h)

    button(WIN, "Přihlásit se", login_confirm_rect, login_user)
    button(WIN, "Registrovat", login_register_rect, lambda: change_screen("register"))
    button(WIN, "Zpět", login_back_rect, lambda: change_screen("menu"))

    if login_msg:
        draw_text(WIN, login_msg, (WIDTH // 2, login_back_rect.bottom + 30), FONT, login_msg_color)


def draw_register():
    WIN.fill(BG_COLOR)
    draw_text(WIN, "Registrace", (WIDTH // 2, HEIGHT // 7), FONT)

    global reg_username_rect, reg_password_rect, reg_password2_rect, reg_show_rect, reg_show_rect2, reg_back_rect, reg_confirm_rect, reg_email_rect, reg_login_rect

    card_w = min(520, WIDTH - 160)
    card_x = (WIDTH - card_w) // 2
    card_y = HEIGHT // 6
    spacing = 110
    field_w = card_w
    field_h = 58
    field_x = card_x
    top_y = card_y + 40

    draw_text(WIN, "Email:", (WIDTH // 2, top_y), FONT, LABEL_COLOR)
    reg_email_rect = pygame.Rect(field_x, top_y + 20, field_w, field_h)

    draw_text(WIN, "Uživatelské jméno:", (WIDTH // 2, top_y + spacing), FONT, LABEL_COLOR)
    reg_username_rect = pygame.Rect(field_x, top_y + spacing + 20, field_w, field_h)

    draw_text(WIN, "Heslo:", (WIDTH // 2, top_y + 2 * spacing), FONT, LABEL_COLOR)
    reg_password_rect = pygame.Rect(field_x, top_y + 2 * spacing + 20, field_w, field_h)

    draw_text(WIN, "Potvrzení hesla:", (WIDTH // 2, top_y + 3 * spacing), FONT, LABEL_COLOR)
    reg_password2_rect = pygame.Rect(field_x, top_y + 3 * spacing + 20, field_w, field_h)

    reg_show_rect = pygame.Rect(reg_password_rect.right - 44, reg_password_rect.top + 10, 38, 38)
    reg_show_rect2 = pygame.Rect(reg_password2_rect.right - 44, reg_password2_rect.top + 10, 38, 38)
    buttons_y = top_y + 4 * spacing + 36
    btn_gap = 12
    btn_w = (card_w - 2 * btn_gap) // 3
    reg_confirm_rect = pygame.Rect(card_x, buttons_y, btn_w, 52)
    reg_login_rect = pygame.Rect(card_x + btn_w + btn_gap, buttons_y, btn_w, 52)
    reg_back_rect = pygame.Rect(card_x + 2 * (btn_w + btn_gap), buttons_y, btn_w, 52)

    email_color = ACTIVE_BORDER if active_input == "reg_email" else TEXT_COLOR
    username_color = ACTIVE_BORDER if active_input == "reg_username" else TEXT_COLOR
    password_color = ACTIVE_BORDER if active_input == "reg_password" else TEXT_COLOR
    password2_color = ACTIVE_BORDER if active_input == "reg_password2" else TEXT_COLOR
    pygame.draw.rect(WIN, email_color, reg_email_rect, 3, border_radius=5)
    pygame.draw.rect(WIN, username_color, reg_username_rect, 3, border_radius=5)
    pygame.draw.rect(WIN, password_color, reg_password_rect, 3, border_radius=5)
    pygame.draw.rect(WIN, password2_color, reg_password2_rect, 3, border_radius=5)

    email_surface = FONT.render(reg_email, True, TEXT_COLOR)
    WIN.blit(email_surface, email_surface.get_rect(center=reg_email_rect.center))

    username_surface = FONT.render(reg_username, True, TEXT_COLOR)
    WIN.blit(username_surface, username_surface.get_rect(center=reg_username_rect.center))

    display_pass = reg_password if show_password_reg else "*" * len(reg_password)
    password_surface = FONT.render(display_pass, True, TEXT_COLOR)
    WIN.blit(password_surface, password_surface.get_rect(center=reg_password_rect.center))

    display_pass2 = reg_password2 if show_password_reg2 else "*" * len(reg_password2)
    password2_surface = FONT.render(display_pass2, True, TEXT_COLOR)
    WIN.blit(password2_surface, password2_surface.get_rect(center=reg_password2_rect.center))

    mouse_pos = pygame.mouse.get_pos()
    eye_color1 = EYE_HOVER if reg_show_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    eye_color2 = EYE_HOVER if reg_show_rect2.collidepoint(mouse_pos) else BUTTON_COLOR

    pygame.draw.ellipse(WIN, eye_color1, reg_show_rect, 2)
    if show_password_reg:
        pygame.draw.circle(WIN, eye_color1, reg_show_rect.center, 5)
    else:
        pygame.draw.line(WIN, eye_color1, (reg_show_rect.left + 5, reg_show_rect.top + reg_show_rect.height // 2), (reg_show_rect.right - 5, reg_show_rect.top + reg_show_rect.height // 2), 3)

    pygame.draw.ellipse(WIN, eye_color2, reg_show_rect2, 2)
    if show_password_reg2:
        pygame.draw.circle(WIN, eye_color2, reg_show_rect2.center, 5)
    else:
        pygame.draw.line(WIN, eye_color2, (reg_show_rect2.left + 5, reg_show_rect2.top + reg_show_rect.height // 2), (reg_show_rect2.right - 5, reg_show_rect2.top + reg_show_rect.height // 2), 3)

    button_bar_rect = pygame.Rect(card_x, buttons_y - 14, card_w, 52 + 28)
    pygame.draw.rect(WIN, BUTTON_BAR_BG, button_bar_rect, border_radius=10)

    button(WIN, "Registrovat", reg_confirm_rect, register_user)
    button(WIN, "Přihlásit se", reg_login_rect, lambda: change_screen("login"))
    button(WIN, "Zpět", reg_back_rect, lambda: change_screen("menu"))

    if register_msg:
        draw_text(WIN, register_msg, (WIDTH // 2, reg_back_rect.bottom + 40), FONT, register_msg_color)


def draw_account():
    WIN.fill(BG_COLOR)
    draw_text(WIN, "Můj účet", (WIDTH // 2, HEIGHT // 6), FONT)

    info_y = HEIGHT // 3
    line_gap = 40

    if auth_token and account_data:
        draw_text(WIN, f"Uživatel: {account_data.get('username','')}" , (WIDTH // 2, info_y), FONT)
        draw_text(WIN, f"Email: {account_data.get('email','')}" , (WIDTH // 2, info_y + line_gap), FONT)
        created = format_created_at(account_data.get('created_at',''))
        draw_text(WIN, f"Vytvořeno: {created}" , (WIDTH // 2, info_y + 2 * line_gap), FONT)

        scores = account_data.get('best_scores') or []
        scores_y = info_y + 2 * line_gap + 70
        draw_text(WIN, "Nejlepší skóre podle módu", (WIDTH // 2, scores_y), FONT)
        list_y = scores_y + 36
        if not scores:
            draw_text(WIN, "Zatím žádná skóre", (WIDTH // 2, list_y), SMALL_FONT)
        else:
            for idx, item in enumerate(scores):
                label = item.get('label') or item.get('mode') or 'Mód'
                value = item.get('score', 0)
                draw_text(WIN, f"{label}: {value}", (WIDTH // 2, list_y + idx * 32), SMALL_FONT)
    else:
        msg = account_msg or "Přihlaš se, aby ses podíval na účet."
        draw_text(WIN, msg, (WIDTH // 2, info_y), FONT, account_msg_color)

    if auth_token:
        logout_rect = pygame.Rect(WIDTH // 2 - 90, HEIGHT - 210, 180, 54)
        button(WIN, "Odhlásit", logout_rect, logout_user)

    back_rect = pygame.Rect(WIDTH // 2 - 90, HEIGHT - 140, 180, 54)
    button(WIN, "Zpět", back_rect, lambda: change_screen("menu"))


def draw_mode_select():
    WIN.fill(BG_COLOR)
    draw_text(WIN, "Výběr módu", (WIDTH // 2, HEIGHT // 4), FONT)
    modes = list(mode_config.keys())
    global mode_buttons, start_rect, mode_back_rect
    mode_buttons = []

    start_y = HEIGHT // 2 - 120
    for idx, key in enumerate(modes):
        rect = pygame.Rect(WIDTH // 2 - 160, start_y + idx * 70, 320, 50)
        mode_buttons.append((rect, key))
        color = ACTIVE_BORDER if selected_mode == key else TEXT_COLOR
        pygame.draw.rect(WIN, BUTTON_COLOR, rect, border_radius=8)
        pygame.draw.rect(WIN, color, rect, 3, border_radius=8)
        draw_text(WIN, mode_config[key]["label"], rect.center, FONT)

    start_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 150, 150, 50)
    mode_back_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 80, 150, 50)

    button(WIN, "Spustit", start_rect, start_game)
    button(WIN, "Zpět", mode_back_rect, lambda: change_screen("menu"))


def draw_game(delta_time):
    global snake, dx, dy, food, score, snake_timer
    WIN.blit(background_img, (0, 0))

    # Výraznější červený panel se skóre
    score_rect = pygame.Rect(12, 12, 210, 54)
    pygame.draw.rect(WIN, BORDER_COLOR, score_rect, border_radius=12)
    inner_rect = score_rect.inflate(-6, -6)
    pygame.draw.rect(WIN, BG_COLOR, inner_rect, border_radius=10)
    draw_text(WIN, f"Skóre: {score}", inner_rect.center, FONT, TEXT_COLOR)

    border = BORDER_THICKNESS
    pygame.draw.rect(WIN, BORDER_COLOR, (PLAY_AREA.left - border, PLAY_AREA.top - border, PLAY_AREA.width + border * 2, border))
    pygame.draw.rect(WIN, BORDER_COLOR, (PLAY_AREA.left - border, PLAY_AREA.bottom, PLAY_AREA.width + border * 2, border))
    pygame.draw.rect(WIN, BORDER_COLOR, (PLAY_AREA.left - border, PLAY_AREA.top, border, PLAY_AREA.height))
    pygame.draw.rect(WIN, BORDER_COLOR, (PLAY_AREA.right, PLAY_AREA.top, border, PLAY_AREA.height))

    if not paused:
        snake_timer += delta_time
        if snake_timer >= snake_speed:
            snake_timer = 0
            new_head = [snake[0][0] + dx, snake[0][1] + dy]
            snake.insert(0, new_head)

            ate_normal = False
            ate_poison = False
            for f in list(food):
                if new_head == f["pos"]:
                    # jedna se o cervene jablko nebo teda food
                    if f["type"] == "normal":
                        score += 1
                        ate_normal = True
                        food.remove(f)
                        spawn_food()
                        snake.append(snake[-1][:])
                    else:
                        ate_poison = True
                        break
                      # jedna se o zelene jablko nebo teda poison, hra končí
            if ate_poison:
                submit_score_current()
                draw_text(WIN, f"Sebral jsi zelené jablko! Skóre: {score}", (WIDTH // 2, HEIGHT // 2), FONT)
                pygame.display.update()
                pygame.time.delay(2000)
                change_screen("menu")
                return

            if not ate_normal:
                if snake:
                    snake.pop()

            if (
                new_head[0] < PLAY_AREA_COLLISION.left
                or new_head[0] >= PLAY_AREA_COLLISION.right - BLOCK_SIZE
                or new_head[1] < PLAY_AREA_COLLISION.top
                or new_head[1] >= PLAY_AREA_COLLISION.bottom - BLOCK_SIZE
                or new_head in snake[1:]
                or new_head in pillars
            ):
                submit_score_current()
                draw_text(WIN, f"Hra skončila! Skóre: {score}", (WIDTH // 2, HEIGHT // 2), FONT, ERROR_COLOR)
                pygame.display.update()
                pygame.time.delay(2000)
                change_screen("menu")
                return


    for p in pillars:
        WIN.blit(pillar_img, p)

    for f in food:
        if f["type"] == "normal":
            WIN.blit(apple_img, f["pos"])
        else:
            WIN.blit(poisoned_apple_img, f["pos"])

    for i, segment in enumerate(snake):
        if i == 0:
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
        elif i == len(snake) - 1:
            prev = snake[i - 1]
            if segment[0] < prev[0]:
                tail_rotated = pygame.transform.rotate(snake_tail_img, 270)
            elif segment[0] > prev[0]:
                tail_rotated = pygame.transform.rotate(snake_tail_img, 90)
            elif segment[1] < prev[1]:
                tail_rotated = pygame.transform.rotate(snake_tail_img, 180)
            else:
                tail_rotated = snake_tail_img
            WIN.blit(tail_rotated, segment)
        else:
            WIN.blit(snake_body_img, segment)


# ===============================
# Login/Register akce (stub)
# ===============================
def login_user():
    global login_msg, login_msg_color, auth_token, leaderboard_fetched, leaderboard_msg
    if not username or not password:
        login_msg = "Vyplň všechna pole"
        login_msg_color = ERROR_COLOR
        return

    ok, data = api_post("/login", {"identifier": username, "password": password})
    if not ok:
        login_msg = data
        login_msg_color = ERROR_COLOR
        return

    auth_token = data.get("token", "")
    login_msg = "Přihlášení úspěšné"
    login_msg_color = SUCCESS_COLOR
    leaderboard_fetched = False  # po přihlášení načti čerstvý žebříček
    leaderboard_msg = "Načítám žebříčky..."
    change_screen("menu")
    reset_inputs()
    fetch_account()
    fetch_leaderboard()


def register_user():
    global register_msg, register_msg_color
    if not reg_email or not reg_username or not reg_password or not reg_password2:
        register_msg = "Vyplň všechna pole"
        register_msg_color = ERROR_COLOR
        return

    ok, data = api_post("/register", {"email": reg_email, "username": reg_username, "password": reg_password})
    if not ok:
        register_msg = data
        register_msg_color = ERROR_COLOR
        return

    register_msg = "Registrace úspěšná"
    register_msg_color = SUCCESS_COLOR


def fetch_account():
    global account_data, account_msg, account_msg_color
    if not auth_token:
        account_data = None
        account_msg = "Nejste přihlášen."
        account_msg_color = ERROR_COLOR
        return

    ok, data = api_get("/me", auth_token)
    if not ok:
        account_data = None
        account_msg = data
        account_msg_color = ERROR_COLOR
        return

    account_msg = ""
    account_msg_color = TEXT_COLOR
    account_data = data


def submit_score_current():
    global leaderboard_msg
    if not auth_token:
        leaderboard_msg = "Přihlaš se pro ukládání skóre."
        return
    ok, err = api_post("/scores", {"mode": current_mode, "score": score}, auth_token)
    if ok:
        fetch_leaderboard()
    else:
        leaderboard_msg = f"Uložení skóre selhalo: {err}"
        print("Submit score failed:", err)


def logout_user():
    global auth_token, account_data, account_msg, leaderboard_data, leaderboard_msg, leaderboard_fetched
    auth_token = ""
    account_data = None
    account_msg = "Odhlášen."
    leaderboard_data = {}
    leaderboard_msg = "Přihlaš se pro zobrazení žebříčku."
    leaderboard_fetched = False
    change_screen("menu")


def fetch_leaderboard():
    global leaderboard_data, leaderboard_msg, leaderboard_loading, leaderboard_fetched
    leaderboard_loading = True
    leaderboard_msg = "Načítám žebříčky..."
    ok, data = api_get("/scores", auth_token)
    if not ok:
        leaderboard_data = {}
        leaderboard_msg = data
    else:
        leaderboard_data = data.get("scores", {})
        leaderboard_msg = "" if leaderboard_data else "Žádná data."
    leaderboard_loading = False
    leaderboard_fetched = True


def ensure_leaderboard_loaded():
    global leaderboard_fetched, leaderboard_msg
    if leaderboard_loading:
        return
    if not auth_token:
        if not leaderboard_fetched:
            leaderboard_msg = "Přihlaš se pro zobrazení žebříčku."
            leaderboard_fetched = True
        return
    if not leaderboard_fetched:
        fetch_leaderboard()


def main_loop():
    # ===============================
    # Hlavní smyčka
    # ===============================
    global active_input, show_password_login, show_password_reg, show_password_reg2
    global username, password, reg_email, reg_username, reg_password, reg_password2
    global selected_mode, leaderboard_mode, paused, dx, dy
    while True:
        delta_time = CLOCK.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if screen_state == "login":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if login_show_rect.collidepoint(event.pos):
                        show_password_login = not show_password_login
                    elif username_rect.collidepoint(event.pos):
                        active_input = "login_username"
                    elif password_rect.collidepoint(event.pos):
                        active_input = "login_password"
                    else:
                        active_input = None
                if event.type == pygame.KEYDOWN and active_input:
                    if event.key == pygame.K_BACKSPACE:
                        if active_input == "login_username":
                            username = username[:-1]
                        elif active_input == "login_password":
                            password = password[:-1]
                    elif event.key == pygame.K_RETURN:
                        login_user()
                if event.type == pygame.TEXTINPUT and active_input:
                    ch = event.text
                    if active_input == "login_username" and len(username) < 40:
                        username += ch
                    elif active_input == "login_password" and len(password) < 40:
                        password += ch

            if screen_state == "register":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if reg_show_rect.collidepoint(event.pos):
                        show_password_reg = not show_password_reg
                    elif reg_show_rect2.collidepoint(event.pos):
                        show_password_reg2 = not show_password_reg2
                    elif reg_email_rect.collidepoint(event.pos):
                        active_input = "reg_email"
                    elif reg_username_rect.collidepoint(event.pos):
                        active_input = "reg_username"
                    elif reg_password_rect.collidepoint(event.pos):
                        active_input = "reg_password"
                    elif reg_password2_rect.collidepoint(event.pos):
                        active_input = "reg_password2"
                    else:
                        active_input = None
                if event.type == pygame.KEYDOWN and active_input:
                    if event.key == pygame.K_BACKSPACE:
                        if active_input == "reg_email":
                            reg_email = reg_email[:-1]
                        elif active_input == "reg_username":
                            reg_username = reg_username[:-1]
                        elif active_input == "reg_password":
                            reg_password = reg_password[:-1]
                        elif active_input == "reg_password2":
                            reg_password2 = reg_password2[:-1]
                    elif event.key == pygame.K_RETURN:
                        register_user()
                if event.type == pygame.TEXTINPUT and active_input:
                    ch = event.text
                    if active_input == "reg_email" and len(reg_email) < 60:
                        reg_email += ch
                    elif active_input == "reg_username" and len(reg_username) < 40:
                        reg_username += ch
                    elif active_input == "reg_password" and len(reg_password) < 40:
                        reg_password += ch
                    elif active_input == "reg_password2" and len(reg_password2) < 40:
                        reg_password2 += ch

            if screen_state == "mode_select" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, key in mode_buttons:
                    if rect.collidepoint(event.pos):
                        selected_mode = key
                if start_rect.collidepoint(event.pos):
                    start_game()
                if mode_back_rect.collidepoint(event.pos):
                    change_screen("menu")

            if screen_state == "menu" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if leaderboard_left_rect.collidepoint(event.pos):
                    modes = list(mode_config.keys())
                    idx = modes.index(leaderboard_mode)
                    leaderboard_mode = modes[(idx - 1) % len(modes)]
                elif leaderboard_right_rect.collidepoint(event.pos):
                    modes = list(mode_config.keys())
                    idx = modes.index(leaderboard_mode)
                    leaderboard_mode = modes[(idx + 1) % len(modes)]

            if screen_state == "game" and event.type == pygame.KEYDOWN:
                if not paused:
                    if event.key in [pygame.K_UP, pygame.K_w] and dy == 0:
                        dx, dy = 0, -BLOCK_SIZE
                    elif event.key in [pygame.K_DOWN, pygame.K_s] and dy == 0:
                        dx, dy = 0, BLOCK_SIZE
                    elif event.key in [pygame.K_LEFT, pygame.K_a] and dx == 0:
                        dx, dy = -BLOCK_SIZE, 0
                    elif event.key in [pygame.K_RIGHT, pygame.K_d] and dx == 0:
                        dx, dy = BLOCK_SIZE, 0
                if event.key in [pygame.K_SPACE, pygame.K_p]:
                    paused = not paused
                elif event.key == pygame.K_RETURN:
                    change_screen("menu")
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if screen_state == "menu":
            draw_menu()
        elif screen_state == "login":
            draw_login()
        elif screen_state == "register":
            draw_register()
        elif screen_state == "controls":
            draw_controls()
        elif screen_state == "mode_select":
            draw_mode_select()
        elif screen_state == "game":
            draw_game(delta_time)
        elif screen_state == "account":
            draw_account()

        pygame.display.update()


def main():
    try:
        main_loop()
    except KeyboardInterrupt:
        pygame.quit()
        print("Aplikace byla přerušena.")
        sys.exit(0)
    except Exception:
        pygame.quit()
        print("Došlo k neočekávané chybě. Viz níže:")
        traceback.print_exc()
        input("Stiskni Enter pro ukončení aplikace...")
        sys.exit(1)


if __name__ == "__main__":
    main()