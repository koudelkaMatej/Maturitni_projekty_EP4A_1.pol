import pygame
import sys
import random
import math
import os
import requests

def posli_skore(username, password, skore):
    url = "http://127.0.0.1:8000/api/update_score/"
    data = {
        "username": username,
        "password": password,
        "skore": skore
    }

    try:
        response = requests.post(url, json=data)
        result = response.json()
        if result["status"] == "ok":
            print("Skóre úspěšně aktualizováno!")
        else:
            print("Chyba při aktualizaci skóre:", result["message"])
    except Exception as e:
        print("Chyba při spojení s API:", e)

def load_animation(path):
        frames = []
        if not os.path.exists(path):
            print(f"Warning: Folder '{path}' does not exist!")
            return frames
        for filename in sorted(os.listdir(path)):
            if filename.endswith(".png"):
                try:
                    frame = pygame.image.load(os.path.join(path, filename)).convert_alpha()
                    frames.append(frame)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        return frames
def death_screen(screen, font, score):
    while True:
        screen.fill((0, 0, 0))

        title = font.render("GAME OVER", True, (255, 0, 0))
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        restart_text = font.render("ENTER - New Game", True, (255, 255, 255))
        menu_text = font.render("ESC - Back to Menu", True, (255, 255, 255))

        screen.blit(title, (800, 400))
        screen.blit(score_text, (820, 450))
        screen.blit(restart_text, (780, 520))
        screen.blit(menu_text, (780, 560))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "restart"
                if event.key == pygame.K_ESCAPE:
                    return "menu"
def game_loop():
    pygame.init()

    # === DIRECTORIES ===
    BASE_DIR = os.path.dirname(__file__)
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")

    # === WINDOW ===
    WIDTH, HEIGHT = 1920, 1080
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Animace pohybu + dash")

    # === COLORS ===
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    # === SKORE ===
    SCORE = 0

    # === FUNCTION TO LOAD ANIMATION FRAMES ===
    def load_animation(path):
        frames = []
        if not os.path.exists(path):
            print(f"Warning: Folder '{path}' does not exist!")
            return frames
        for filename in sorted(os.listdir(path)):
            if filename.endswith(".png"):
                try:
                    frame = pygame.image.load(os.path.join(path, filename)).convert_alpha()
                    frames.append(frame)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        return frames

    # === LOAD ANIMATIONS ===
    animations = {
        "up": load_animation(os.path.join(ASSETS_DIR, "Hráč_nahoru")),
        "down": load_animation(os.path.join(ASSETS_DIR, "Hráč_dolu")),
        "left": load_animation(os.path.join(ASSETS_DIR, "Hráč_nalevo")),
        "right": load_animation(os.path.join(ASSETS_DIR, "Hráč_napravo")),
        "idle": load_animation(os.path.join(ASSETS_DIR, "Hráč_Idle"))
    }

    # Debug: print number of frames loaded
    for key, frames in animations.items():
        print(f"Loaded {len(frames)} frames for '{key}'")

    # === PLAYER ===
    player_x, player_y = WIDTH // 2, HEIGHT // 2
    player_speed = 5
    dash_distance = 200
    dash_cooldown = 1000
    last_dash_time = -dash_cooldown

    direction = "down"
    state = "idle"
    current_frame = 0
    frame_delay = 100
    last_frame_update = pygame.time.get_ticks()

    # === ENEMIES ===
    enemy_size = 40
    enemies = []
    enemy_spawn_delay = 1000
    last_spawn_time = pygame.time.get_ticks()
    enemy_speed = 2

    # === TEXT AND CLOCK ===
    font = pygame.font.SysFont(None, 40)
    clock = pygame.time.Clock()

    # === UPDATE ANIMATION ===
    def update_animation():
        nonlocal current_frame, last_frame_update
        now = pygame.time.get_ticks()
        if now - last_frame_update > frame_delay:
            frames = animations.get(direction, [])
            if frames:
                current_frame = (current_frame + 1) % len(frames)
            last_frame_update = now

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        # --- EVENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # --- PLAYER MOVEMENT ---
        keys = pygame.key.get_pressed()
        moving = False
        dx, dy = 0, 0
        old_direction = direction

        if keys[pygame.K_a]:
            dx -= 1
            moving = True
        if keys[pygame.K_d]:
            dx += 1
            moving = True
        if keys[pygame.K_w]:
            dy -= 1
            moving = True
        if keys[pygame.K_s]:
            dy += 1
            moving = True

        # Normalize diagonal movement
        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx, dy = dx / length, dy / length
            player_x += dx * player_speed
            player_y += dy * player_speed

        # --- DIRECTION AND STATE ---
        if moving:
            if abs(dx) >= abs(dy):
                direction = "right" if dx > 0 else "left"
            else:
                direction = "down" if dy > 0 else "up"
            state = "walk"
        else:
            state = "idle"

        # Reset frame on direction change
        if direction != old_direction:
            current_frame = 0

        # --- DASH ---
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0] and current_time - last_dash_time >= dash_cooldown:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dash_dx = mouse_x - player_x
            dash_dy = mouse_y - player_y
            distance = math.hypot(dash_dx, dash_dy)
            if distance != 0:
                dash_dx, dash_dy = dash_dx / distance, dash_dy / distance
                start_x, start_y = player_x, player_y
                player_x += dash_dx * dash_distance
                player_y += dash_dy * dash_distance
                last_dash_time = current_time

                # Keep player on screen
                player_x = max(0, min(WIDTH - 64, player_x))
                player_y = max(0, min(HEIGHT - 64, player_y))

                # Dash kills enemies
                dash_rect = pygame.Rect(min(start_x, player_x), min(start_y, player_y),
                                        abs(player_x - start_x) + 64,
                                        abs(player_y - start_y) + 64)
                for enemy in enemies[:]:
                    if dash_rect.colliderect(enemy['rect']):
                        enemies.remove(enemy)
                        SCORE += 1

        # --- BOUNDARY CHECK ---
        player_x = max(0, min(WIDTH - 64, player_x))
        player_y = max(0, min(HEIGHT - 64, player_y))

        # --- SPAWN ENEMIES ---
        if current_time - last_spawn_time > enemy_spawn_delay:
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                x = random.randint(0, WIDTH - enemy_size)
                y = -enemy_size
            elif side == 'bottom':
                x = random.randint(0, WIDTH - enemy_size)
                y = HEIGHT
            elif side == 'left':
                x = -enemy_size
                y = random.randint(0, HEIGHT - enemy_size)
            else:
                x = WIDTH
                y = random.randint(0, HEIGHT - enemy_size)
            enemies.append({'rect': pygame.Rect(x, y, enemy_size, enemy_size)})
            last_spawn_time = current_time

        # --- DRAWING ---
        screen.fill(WHITE)

        # Animation frame selection
        if state == "idle":
            idle_frames = animations.get("idle", [])
            if idle_frames:
                image = idle_frames[min(current_frame, len(idle_frames) - 1)]
            else:
                fallback_frames = animations.get(direction, [])
                if fallback_frames:
                    image = fallback_frames[0]
                else:
                    image = pygame.Surface((64, 64))
                    image.fill((255, 0, 0))
        else:
            update_animation()
            frames = animations.get(direction, [])
            if frames:
                image = frames[current_frame]
            else:
                image = pygame.Surface((64, 64))
                image.fill((255, 0, 0))

        player_rect = pygame.Rect(player_x, player_y, image.get_width(), image.get_height())
        screen.blit(image, (player_x, player_y))

        # --- ENEMY MOVEMENT ---
        for enemy in enemies[:]:
            enemy_rect = enemy['rect']
            ex, ey = player_x - enemy_rect.x, player_y - enemy_rect.y
            dist = math.hypot(ex, ey)
            if dist != 0:
                ex, ey = ex / dist, ey / dist
            enemy_rect.x += ex * enemy_speed
            enemy_rect.y += ey * enemy_speed
            pygame.draw.rect(screen, BLUE, enemy_rect)

            if player_rect.colliderect(enemy_rect):
                smrt = death_screen(screen, font, SCORE)
                return smrt

        # --- DASH COOLDOWN DISPLAY ---
        time_since_dash = max(0, dash_cooldown - (current_time - last_dash_time))
        cooldown_text = font.render(f"Dash cooldown: {time_since_dash/1000}s", True, (0, 0, 0))
        screen.blit(cooldown_text, (10, 10))
        score_text = font.render(f"Score: {SCORE}", True, (0, 0, 0))
        screen.blit(score_text, (10, 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


# To run the game directly
if __name__ == "__main__":
    game_loop()


