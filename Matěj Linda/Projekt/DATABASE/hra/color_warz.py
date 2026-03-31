import pygame
import sys
import os
import random
import time
import pygame.gfxdraw
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
from Shared import shared_db

pygame.init()

# === Nastavení ===
CELL_SIZE = 130
ROWS, COLS = 6, 6
BOARD_WIDTH, BOARD_HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE
PANEL_HEIGHT = 100
WIDTH, HEIGHT = BOARD_WIDTH, BOARD_HEIGHT + PANEL_HEIGHT

# === Barvy ===
BG_COLOR = (255, 245, 235)
LINE_COLOR = (128, 128, 128)
PLAYER_COLORS = [(235, 100, 100), (100, 160, 235)]
DOT_COLOR = (245, 245, 240)
# Převzaté odstíny z poskytnutých vzorků (fotka.1 a fotka.2)
BG_RED_DARK = (58, 36, 44)
BG_BLUE_DARK = (39, 49, 74)

# === Inicializace ===
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Color Warz")
font = pygame.font.SysFont(None, 36)
win_font = pygame.font.SysFont("Comic Sans MS", 80, bold=True)
clock = pygame.time.Clock()

# === Herní data ===
board = [[{'owner': None, 'dots': 0} for _ in range(COLS)] for _ in range(ROWS)]
current_player = 0
starting_phase = True
starting_positions_selected = [False, False]
game_over = False
winner = None
scores = [0, 0]
turn_count = 0
logging_enabled = False
logged_username = None
bg_current = list(BG_RED_DARK)
bg_target = list(BG_RED_DARK)
AI_PLAYER = 1
ai_wait_until_ms = None

# === Pauza ===
paused = False
in_settings = False
volume_level = 0.5
slider_dragging = False


# === Funkce ===

def draw_board():
    screen.fill(tuple(bg_current))

    line_w = 14
    node_r = 14
    for c in range(COLS + 1):
        x = c * CELL_SIZE
        pygame.draw.line(screen, LINE_COLOR, (x, 0), (x, BOARD_HEIGHT), width=line_w)
    for r in range(ROWS + 1):
        y = r * CELL_SIZE
        pygame.draw.line(screen, LINE_COLOR, (0, y), (BOARD_WIDTH, y), width=line_w)
    for r in range(ROWS + 1):
        for c in range(COLS + 1):
            cx, cy = c * CELL_SIZE, r * CELL_SIZE
            pygame.gfxdraw.aacircle(screen, cx, cy, node_r, LINE_COLOR)
            pygame.gfxdraw.filled_circle(screen, cx, cy, node_r, LINE_COLOR)

    # --- Kreslení buněk a teček ---
    for r in range(ROWS):
        for c in range(COLS):
            cell = board[r][c]
            if cell['owner'] is not None and cell['dots'] > 0:
                center = (c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2)
                radius = CELL_SIZE // 2 - 10
                pygame.draw.circle(screen, PLAYER_COLORS[cell['owner']], center, radius)

                # Tečky
                dot_positions = []
                offset = 18
                cx, cy = center
                if cell['dots'] == 1:
                    dot_positions = [(cx, cy)]
                elif cell['dots'] == 2:
                    dot_positions = [(cx - offset, cy - offset), (cx + offset, cy + offset)]
                elif cell['dots'] == 3:
                    dot_positions = [(cx - offset, cy - offset), (cx, cy), (cx + offset, cy + offset)]
                elif cell['dots'] == 4:
                    dot_positions = [
                        (cx - offset, cy - offset),
                        (cx + offset, cy - offset),
                        (cx - offset, cy + offset),
                        (cx + offset, cy + offset)
                    ]

                for pos in dot_positions:
                    pygame.draw.circle(screen, DOT_COLOR, pos, 9)

    # --- Dolní panel ---
    panel_rect = pygame.Rect(0, BOARD_HEIGHT, WIDTH, PANEL_HEIGHT)
    panel_color = (
        min(255, bg_current[0] + 40),
        min(255, bg_current[1] + 40),
        min(255, bg_current[2] + 40),
    )
    pygame.draw.rect(screen, panel_color, panel_rect)

    # Tlačítko pauzy
    global pause_button_rect
    pause_button_rect = pygame.Rect(WIDTH - 70, BOARD_HEIGHT + 15, 60, 60)
    pygame.draw.circle(screen, (128, 128, 128), pause_button_rect.center, 30)
    pygame.draw.rect(screen, (128, 128, 128), (pause_button_rect.centerx - 12, pause_button_rect.centery - 15, 8, 30))
    pygame.draw.rect(screen, (128, 128, 128), (pause_button_rect.centerx + 4, pause_button_rect.centery - 15, 8, 30))

    if not game_over:
        lum = 0.299 * panel_color[0] + 0.587 * panel_color[1] + 0.114 * panel_color[2]
        text_color = (40, 40, 40) if lum > 160 else (240, 240, 240)
        if starting_phase:
            who = "Hráč 1 (hráč)" if current_player != AI_PLAYER else "Hráč 2 (AI)"
            label = f"Volba startovní pozice – na tahu: {who}"
        else:
            who = "Hráč 1 (hráč)" if current_player != AI_PLAYER else "Hráč 2 (AI)"
            label = f"Na tahu: {who}"
        text = font.render(label, True, text_color)
        screen.blit(text, (10, BOARD_HEIGHT + PANEL_HEIGHT // 2 - 15))


def neighbors(r, c):
    for nr, nc in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            yield nr, nc


def animate_explosion(r, c, owner):
    """Animuje rozlet kuliček do sousedních buněk."""
    center_x = c * CELL_SIZE + CELL_SIZE // 2
    center_y = r * CELL_SIZE + CELL_SIZE // 2
    dirs = []
    for nr, nc in neighbors(r, c):
        dirs.append(((center_x, center_y),
                     (nc * CELL_SIZE + CELL_SIZE // 2, nr * CELL_SIZE + CELL_SIZE // 2)))

    steps = 10
    for step in range(1, steps + 1):
        draw_board()
        for start, end in dirs:
            x = start[0] + (end[0] - start[0]) * step / steps
            y = start[1] + (end[1] - start[1]) * step / steps
            pygame.draw.circle(screen, PLAYER_COLORS[owner], (int(x), int(y)), 10)
        pygame.display.flip()
        clock.tick(40)


def explode(r, c):
    """Rozdělení buňky na sousedy s animací."""
    cell = board[r][c]
    owner = cell['owner']
    if cell['dots'] < 4:
        return
    board[r][c]['dots'] = 0
    board[r][c]['owner'] = None
    animate_explosion(r, c, owner)
    for nr, nc in neighbors(r, c):
        board[nr][nc]['dots'] += 1
        board[nr][nc]['owner'] = owner
        if board[nr][nc]['dots'] >= 4:
            explode(nr, nc)


def can_place(r, c, player):
    cell = board[r][c]
    return cell['owner'] == player


def place_dot(r, c, player):
    if not can_place(r, c, player):
        return False
    board[r][c]['dots'] += 1
    explode(r, c)
    return True


def check_winner():
    owners = set()
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c]['owner'] is not None:
                owners.add(board[r][c]['owner'])
    if len(owners) == 1 and not starting_phase:
        return owners.pop()
    return None


def handle_starting_position(r, c):
    global current_player, starting_phase
    cell = board[r][c]
    if cell['owner'] is None:
        board[r][c] = {'owner': current_player, 'dots': 3}
        starting_positions_selected[current_player] = True
        if all(starting_positions_selected):
            starting_phase = False
            current_player = 0
        else:
            current_player = 1 - current_player


def reset_game():
    global board, starting_phase, starting_positions_selected, current_player, game_over, winner, turn_count, ai_wait_until_ms
    board = [[{'owner': None, 'dots': 0} for _ in range(COLS)] for _ in range(ROWS)]
    starting_phase = True
    starting_positions_selected = [False, False]
    current_player = 0
    game_over = False
    winner = None
    turn_count = 0
    bg_target[:] = BG_RED_DARK
    ai_wait_until_ms = None


# === Pauza ===

def show_pause_menu():
    """Ztmavení a zobrazení menu."""
    global paused, in_settings, slider_dragging
    paused = True
    in_settings = False
    slider_dragging = False

    blur_surface = screen.copy()
    for alpha in range(0, 160, 8):
        blur = pygame.Surface((WIDTH, HEIGHT))
        blur.fill((0, 0, 0))
        blur.set_alpha(alpha)
        screen.blit(blur_surface, (0, 0))
        screen.blit(blur, (0, 0))
        pygame.display.flip()
        clock.tick(30)

    show_pause_buttons()


def show_pause_buttons():
    global in_settings, volume_level, slider_dragging

    def draw_buttons():
        screen.fill((0, 0, 0, 0))
        btn_color = (220, 220, 220)
        texts = ["Pokračovat", "Restart", "Nastavení", "Odhlásit", "Odejít"]
        btn_rects = []
        for i, txt in enumerate(texts):
            rect = pygame.Rect(WIDTH // 2 - 120, 120 + i * 90, 240, 60)
            pygame.draw.rect(screen, btn_color, rect, border_radius=20)
            label = font.render(txt, True, (40, 40, 40))
            screen.blit(label, label.get_rect(center=rect.center))
            btn_rects.append((txt, rect))
        return btn_rects

    def draw_settings():
        slider_rect = pygame.Rect(WIDTH // 2 - 150, 200, 300, 8)
        knob_x = slider_rect.x + int(slider_rect.width * volume_level)
        pygame.draw.rect(screen, (200, 200, 200), slider_rect)
        pygame.draw.circle(screen, (255, 255, 255), (knob_x, slider_rect.centery), 12)
        label = font.render("Zvuk:", True, (230, 230, 230))
        screen.blit(label, (WIDTH // 2 - 180, 180))
        back_rect = pygame.Rect(WIDTH // 2 - 80, 300, 160, 50)
        pygame.draw.rect(screen, (220, 220, 220), back_rect, border_radius=20)
        screen.blit(font.render("Zpět", True, (40, 40, 40)), font.render("Zpět", True, (40, 40, 40)).get_rect(center=back_rect.center))
        return slider_rect, back_rect

    running = True
    while running and paused:
        screen.fill((0, 0, 0))
        if in_settings:
            slider_rect, back_rect = draw_settings()
        else:
            btn_rects = draw_buttons()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                if in_settings:
                    if slider_rect.collidepoint(x, y):
                        slider_dragging = True
                        volume_level = max(0, min(1, (x - slider_rect.x) / slider_rect.width))
                    elif back_rect.collidepoint(x, y):
                        in_settings = False
                else:
                    for txt, rect in btn_rects:
                        if rect.collidepoint(x, y):
                            if txt == "Pokračovat":
                                running = False
                            elif txt == "Restart":
                                reset_game(); running = False
                            elif txt == "Nastavení":
                                in_settings = True
                            elif txt == "Odhlásit":
                                reset_game()
                                show_login_dialog()
                                running = False
                            elif txt == "Odejít":
                                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                slider_dragging = False
            elif event.type == pygame.MOUSEMOTION and slider_dragging:
                x, _ = pygame.mouse.get_pos()
                volume_level = max(0, min(1, (x - slider_rect.x) / slider_rect.width))


# === Výhra ===

def show_winner_effect(winner):
    """Zobrazí výherní obrazovku po konci hry."""
    global game_over
    draw_board()
    pygame.display.flip()
    pygame.time.delay(1000)

    blur_surface = screen.copy()
    for alpha in range(0, 160, 8):
        blur = pygame.Surface((WIDTH, HEIGHT))
        blur.fill((0, 0, 0))
        blur.set_alpha(alpha)
        screen.blit(blur_surface, (0, 0))
        screen.blit(blur, (0, 0))
        pygame.display.flip()
        clock.tick(30)

    win_text = win_font.render(f"Hráč {winner + 1} vyhrál!", True, PLAYER_COLORS[winner])
    text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(win_text, text_rect)

    restart_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 20, 160, 60)


    
    pygame.draw.rect(screen, LINE_COLOR, restart_rect, border_radius=15)
    pygame.draw.rect(screen, PLAYER_COLORS[winner], restart_rect, width=4, border_radius=15)
    restart_text = font.render("Restart", True, PLAYER_COLORS[winner])
    text_pos = restart_text.get_rect(center=restart_rect.center)
    screen.blit(restart_text, text_pos)

    score_text = font.render(f"{scores[0]} : {scores[1]}", True, (230, 230, 230))
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    screen.blit(score_text, score_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                if restart_rect.collidepoint(x, y):
                    waiting = False
                    reset_game()
    game_over = False

def prompt_input(title, password=False):
    input_str = ""
    running = True
    while running:
        draw_board()
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        t = font.render(title, True, (255, 255, 255))
        v = font.render(("*" * len(input_str)) if password else input_str, True, (255, 255, 0))
        screen.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
        screen.blit(v, v.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))
        pygame.display.flip()
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = False
                    break
                elif event.key == pygame.K_ESCAPE:
                    input_str = ""
                    running = False
                    break
                elif event.key == pygame.K_BACKSPACE:
                    input_str = input_str[:-1]
                else:
                    ch = event.unicode
                    if ch and ch.isprintable() and len(input_str) < 32:
                        input_str += ch
    return input_str

def show_login_dialog():
    global logging_enabled, logged_username
    shared_db.init_db()
    username = ""
    password = ""
    focus = "username"
    error = ""
    selecting = True
    panel_w, panel_h = 480, 320
    panel = pygame.Rect(0, 0, panel_w, panel_h)
    panel.center = (WIDTH // 2, HEIGHT // 2)
    u_rect = pygame.Rect(panel.x + 60, panel.y + 110, panel_w - 120, 44)
    p_rect = pygame.Rect(panel.x + 60, panel.y + 170, panel_w - 120, 44)
    login_btn = pygame.Rect(panel.x + 60, panel.y + 230, 160, 48)
    host_btn = pygame.Rect(panel.x + panel_w - 60 - 160, panel.y + 230, 160, 48)
    while selecting:
        draw_board()
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        card = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        card.fill((255, 255, 255, 230))
        pygame.draw.rect(card, (220, 210, 200), card.get_rect(), width=2, border_radius=18)
        screen.blit(card, panel.topleft)
        title = win_font.render("Přihlášení", True, (60, 50, 40))
        screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 52)))
        pygame.draw.rect(screen, (240, 235, 230) if focus == "username" else (232, 228, 224), u_rect, border_radius=10)
        pygame.draw.rect(screen, (240, 235, 230) if focus == "password" else (232, 228, 224), p_rect, border_radius=10)
        u_label = font.render("Uživatelské jméno", True, (70, 60, 50))
        p_label = font.render("Heslo", True, (70, 60, 50))
        screen.blit(u_label, (u_rect.x, u_rect.y - 28))
        screen.blit(p_label, (p_rect.x, p_rect.y - 28))
        u_text = username if username else ""
        p_text = "*" * len(password) if password else ""
        screen.blit(font.render(u_text, True, (40, 40, 40)), (u_rect.x + 10, u_rect.y + 10))
        screen.blit(font.render(p_text, True, (40, 40, 40)), (p_rect.x + 10, p_rect.y + 10))
        pygame.draw.rect(screen, (60, 150, 80), login_btn, border_radius=10)
        pygame.draw.rect(screen, (60, 80, 150), host_btn, border_radius=10)
        screen.blit(font.render("Přihlásit", True, (255, 255, 255)), font.render("Přihlásit", True, (255, 255, 255)).get_rect(center=login_btn.center))
        screen.blit(font.render("Host", True, (255, 255, 255)), font.render("Host", True, (255, 255, 255)).get_rect(center=host_btn.center))
        if error:
            err = font.render(error, True, (200, 60, 60))
            screen.blit(err, err.get_rect(center=(panel.centerx, panel.y + panel_h - 24)))
        pygame.display.flip()
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                if u_rect.collidepoint(x, y):
                    focus = "username"
                elif p_rect.collidepoint(x, y):
                    focus = "password"
                elif login_btn.collidepoint(x, y):
                    if username and password and shared_db.verify_login(username, password):
                        logging_enabled = True
                        logged_username = username
                        selecting = False
                    else:
                        error = "Špatné jméno nebo heslo"
                elif host_btn.collidepoint(x, y):
                    logging_enabled = False
                    logged_username = None
                    selecting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    focus = "password" if focus == "username" else "username"
                elif event.key == pygame.K_RETURN:
                    if username and password and shared_db.verify_login(username, password):
                        logging_enabled = True
                        logged_username = username
                        selecting = False
                    else:
                        error = "Špatné jméno nebo heslo"
                elif event.key == pygame.K_ESCAPE:
                    logging_enabled = False
                    logged_username = None
                    selecting = False
                elif event.key == pygame.K_BACKSPACE:
                    if focus == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]
                else:
                    ch = event.unicode
                    if ch and ch.isprintable():
                        if focus == "username" and len(username) < 32:
                            username += ch
                        elif focus == "password" and len(password) < 64:
                            password += ch
    bg_target[:] = BG_RED_DARK if not logging_enabled else BG_RED_DARK

def update_bg():
    for i in range(3):
        diff = bg_target[i] - bg_current[i]
        if diff != 0:
            bg_current[i] += int(max(-3, min(3, diff)))

def set_bg_for_player(p):
    if p == AI_PLAYER:
        bg_target[:] = BG_BLUE_DARK
    else:
        bg_target[:] = BG_RED_DARK

def ai_choose_start():
    empties = [(r, c) for r in range(ROWS) for c in range(COLS) if board[r][c]['owner'] is None]
    if not empties:
        return
    r, c = random.choice(empties)
    handle_starting_position(r, c)

def ai_choose_move():
    cells = []
    for r in range(ROWS):
        for c in range(COLS):
            if can_place(r, c, AI_PLAYER):
                cells.append((r, c, board[r][c]['dots']))
    if not cells:
        return False
    cells.sort(key=lambda x: x[2], reverse=True)
    r, c, _ = cells[0]
    if place_dot(r, c, AI_PLAYER):
        return True
    return False


# === Main ===

def main():
    global current_player, game_over, winner, turn_count, ai_wait_until_ms
    show_login_dialog()

    running = True
    while running:
        set_bg_for_player(current_player)
        update_bg()
        draw_board()
        panel_color = (
            min(255, bg_current[0] + 40),
            min(255, bg_current[1] + 40),
            min(255, bg_current[2] + 40),
        )
        lum = 0.299 * panel_color[0] + 0.587 * panel_color[1] + 0.114 * panel_color[2]
        status_color = (40, 40, 40) if lum > 160 else (240, 240, 240)
        status = f"Režim: Host" if not logging_enabled else f"Přihlášen: {logged_username}"
        screen.blit(font.render(status, True, status_color), (10, BOARD_HEIGHT + 10))
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()

                if pause_button_rect.collidepoint(x, y):
                    show_pause_menu()

                elif not game_over and y < BOARD_HEIGHT and current_player != AI_PLAYER:
                    c = x // CELL_SIZE
                    r = y // CELL_SIZE
                    if starting_phase:
                        handle_starting_position(r, c)
                        if current_player == AI_PLAYER:
                            ai_wait_until_ms = pygame.time.get_ticks() + 2000
                    else:
                        if place_dot(r, c, current_player):
                            turn_count += 1
                            current_player = 1 - current_player
                            if current_player == AI_PLAYER:
                                ai_wait_until_ms = pygame.time.get_ticks() + 2000
                            winner = check_winner()
                            if winner is not None:
                                scores[winner] += 1
                                game_over = True
                                if logging_enabled and logged_username:
                                    try:
                                        shared_db.save_result(logged_username, turn_count)
                                    except Exception:
                                        pass
                                show_winner_effect(winner)
        if not game_over:
            if starting_phase and current_player == AI_PLAYER:
                if ai_wait_until_ms is None:
                    ai_wait_until_ms = pygame.time.get_ticks() + 2000
                elif pygame.time.get_ticks() >= ai_wait_until_ms:
                    ai_wait_until_ms = None
                    ai_choose_start()
            elif not starting_phase and current_player == AI_PLAYER:
                if ai_wait_until_ms is None:
                    ai_wait_until_ms = pygame.time.get_ticks() + 2000
                elif pygame.time.get_ticks() >= ai_wait_until_ms:
                    if ai_choose_move():
                        turn_count += 1
                        current_player = 1 - current_player
                        winner = check_winner()
                        if winner is not None:
                            scores[winner] += 1
                            game_over = True
                            if logging_enabled and logged_username:
                                try:
                                    shared_db.save_result(logged_username, turn_count)
                                except Exception:
                                    pass
                            show_winner_effect(winner)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
