import pygame
import sys

pygame.init()

# === Nastavení ===
CELL_SIZE = 100
ROWS, COLS = 6, 6
BOARD_WIDTH, BOARD_HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE
PANEL_HEIGHT = 100
WIDTH, HEIGHT = BOARD_WIDTH, BOARD_HEIGHT + PANEL_HEIGHT

# === Barvy ===
BG_COLOR = (255, 245, 235)
LINE_COLOR = (200, 180, 150)
PLAYER_COLORS = [(235, 100, 100), (100, 160, 235)]
DOT_COLOR = (255, 255, 255)

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

# === Pauza ===
paused = False
in_settings = False
volume_level = 0.5
slider_dragging = False


# === Funkce ===

def draw_board():
    screen.fill(BG_COLOR)

    # --- Mřížka ---
    border_thickness = 4
    border_radius = 12
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(
                c * CELL_SIZE + 1,
                r * CELL_SIZE + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            )
            pygame.draw.rect(screen, LINE_COLOR, rect, width=border_thickness, border_radius=border_radius)

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
                offset = 12
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
                    pygame.draw.circle(screen, DOT_COLOR, pos, 6)

    # --- Dolní panel ---
    panel_rect = pygame.Rect(0, BOARD_HEIGHT, WIDTH, PANEL_HEIGHT)
    pygame.draw.rect(screen, (240, 230, 210), panel_rect)

    # Tlačítko pauzy
    global pause_button_rect
    pause_button_rect = pygame.Rect(WIDTH - 70, BOARD_HEIGHT + 15, 60, 60)
    pygame.draw.circle(screen, (180, 160, 140), pause_button_rect.center, 30)
    pygame.draw.rect(screen, (70, 50, 40), (pause_button_rect.centerx - 12, pause_button_rect.centery - 15, 8, 30))
    pygame.draw.rect(screen, (70, 50, 40), (pause_button_rect.centerx + 4, pause_button_rect.centery - 15, 8, 30))

    if not game_over:
        if starting_phase:
            text = font.render(f"Hráč {current_player + 1} zvol startovní pozici", True, (50, 50, 50))
        else:
            text = font.render(f"Hráč {current_player + 1} je na tahu", True, (50, 50, 50))
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
    global board, starting_phase, starting_positions_selected, current_player, game_over, winner
    board = [[{'owner': None, 'dots': 0} for _ in range(COLS)] for _ in range(ROWS)]
    starting_phase = True
    starting_positions_selected = [False, False]
    current_player = 0
    game_over = False
    winner = None


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
        texts = ["Pokračovat", "Restart", "Nastavení", "Odejít"]
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


# === Main ===

def main():
    global current_player, game_over, winner

    running = True
    while running:
        draw_board()
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()

                if pause_button_rect.collidepoint(x, y):
                    show_pause_menu()

                elif not game_over and y < BOARD_HEIGHT:
                    c = x // CELL_SIZE
                    r = y // CELL_SIZE
                    if starting_phase:
                        handle_starting_position(r, c)
                    else:
                        if place_dot(r, c, current_player):
                            current_player = 1 - current_player
                            winner = check_winner()
                            if winner is not None:
                                scores[winner] += 1
                                game_over = True
                                show_winner_effect(winner)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
