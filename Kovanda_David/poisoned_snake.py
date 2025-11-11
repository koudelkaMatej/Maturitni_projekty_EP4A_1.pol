import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Segoe UI", 30)

# ===============================
# Barvy a konstanty
# ===============================
BG_COLOR = (7, 16, 39)
TEXT_COLOR = (234, 246, 255)
BUTTON_COLOR = (30, 167, 255)
BUTTON_HOVER = (13, 141, 229)
ACTIVE_BORDER = (255, 200, 50)
EYE_HOVER = (255, 200, 50)
BORDER_COLOR = (200, 40, 40)
BLOCK_SIZE = 20

# ===============================
# Stav aplikace
# ===============================
screen_state = "menu"
username = ""
password = ""
show_password = False
active_input = None
paused = False

# Snake proměnné
snake = []
dx = dy = 0
food = []  # [x, y, typ]
score = 0
snake_timer = 0
snake_speed = 150

# ===============================
# Načtení obrázků
# ===============================
snake_head_img = pygame.image.load("head.png").convert_alpha()
snake_body_img = pygame.image.load("body.png").convert_alpha()
snake_tail_img = pygame.image.load("ass.png").convert_alpha()
apple_img = pygame.image.load("Jablko.png").convert_alpha()  # červené
poisoned_apple_img = pygame.image.load("poisoned_apple.png").convert_alpha()  # zelené

# ===============================
# Funkce
# ===============================
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

def change_screen(state):
    global screen_state, active_input, username, password, paused
    screen_state = state
    paused = False
    if state == "menu":
        active_input = None
        username = ""
        password = ""

# ===============================
# Start hry
# ===============================
def start_game():
    global snake, dx, dy, score, paused
    snake = [[WIDTH//2, HEIGHT//2]]
    dx = dy = 0
    score = 0
    paused = False
    spawn_food()
    change_screen("game")

# ===============================
# Generování jablek
# ===============================
def spawn_food():
    global food
    num_extra = len(snake)//5
    total_apples = 2 + num_extra
    positions = set()
    while len(positions) < total_apples:
        x = random.randrange(1, (WIDTH - BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randrange(3, (HEIGHT - BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        positions.add((x,y))
    positions = list(positions)
    food = [
        [positions[0][0], positions[0][1], "normal"],
        [positions[1][0], positions[1][1], "poison"]
    ]
    for i in range(2,total_apples):
        t = random.choice(["normal","poison"])
        food.append([positions[i][0], positions[i][1], t])

# ===============================
# Menu, Login a Controls
# ===============================
def draw_menu():
    WIN.fill(BG_COLOR)
    draw_text(WIN, "Poisoned Snake", (WIDTH//2, HEIGHT//4), FONT)
    play_rect = pygame.Rect(WIDTH//2-75, HEIGHT//2-90,150,50)
    controls_rect = pygame.Rect(WIDTH//2-75, HEIGHT//2-20,150,50)
    login_rect = pygame.Rect(WIDTH//2-75, HEIGHT//2+50,150,50)
    end_rect = pygame.Rect(WIDTH//2-75, HEIGHT//2+120,150,50)
    button(WIN,"Play",play_rect,start_game)
    button(WIN,"Ovládání",controls_rect,lambda: change_screen("controls"))
    button(WIN,"Login",login_rect,lambda: change_screen("login"))
    button(WIN,"Konec",end_rect,lambda: sys.exit())

def draw_controls():
    WIN.fill(BG_COLOR)
    draw_text(WIN,"Ovládání hry",(WIDTH//2, HEIGHT//4),FONT)
    draw_text(WIN,"Šipky / W,A,S,D: pohyb hada",(WIDTH//2, HEIGHT//2-40),FONT)
    draw_text(WIN,"SPACE / P: pauza",(WIDTH//2, HEIGHT//2),FONT)
    draw_text(WIN,"ENTER: návrat do menu",(WIDTH//2, HEIGHT//2+40),FONT)
    back_rect = pygame.Rect(WIDTH//2-75, HEIGHT-100,150,50)
    button(WIN,"Zpět",back_rect,lambda: change_screen("menu"))

def draw_login():
    WIN.fill(BG_COLOR)
    draw_text(WIN,"Uživatelské jméno:",(WIDTH//2, HEIGHT//2-130),FONT)
    draw_text(WIN,"Heslo:",(WIDTH//2, HEIGHT//2-20),FONT)
    global username_rect,password_rect,show_rect,back_rect,confirm_rect
    username_rect = pygame.Rect(WIDTH//2-125, HEIGHT//2-100,250,50)
    password_rect = pygame.Rect(WIDTH//2-125, HEIGHT//2,250,50)
    show_rect = pygame.Rect(WIDTH//2+135, HEIGHT//2,50,50)
    confirm_rect = pygame.Rect(WIDTH//2-75, HEIGHT//2+70,150,50)
    back_rect = pygame.Rect(WIDTH//2-75, HEIGHT//2+140,150,50)
    username_color = ACTIVE_BORDER if active_input=="username" else TEXT_COLOR
    password_color = ACTIVE_BORDER if active_input=="password" else TEXT_COLOR
    pygame.draw.rect(WIN,username_color,username_rect,3,border_radius=5)
    pygame.draw.rect(WIN,password_color,password_rect,3,border_radius=5)
    username_surface = FONT.render(username,True,TEXT_COLOR)
    WIN.blit(username_surface,username_surface.get_rect(center=username_rect.center))
    display_pass = password if show_password else '*'*len(password)
    password_surface = FONT.render(display_pass,True,TEXT_COLOR)
    WIN.blit(password_surface,password_surface.get_rect(center=password_rect.center))
    mouse_pos = pygame.mouse.get_pos()
    eye_color = EYE_HOVER if show_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.ellipse(WIN,eye_color,show_rect,2)
    if show_password: pygame.draw.circle(WIN,eye_color,show_rect.center,5)
    else: pygame.draw.line(WIN,eye_color,
        (show_rect.left+5,show_rect.top+show_rect.height//2),
        (show_rect.right-5,show_rect.top+show_rect.height//2),3)
    button(WIN,"Potvrdit",confirm_rect,lambda: change_screen("menu"))
    button(WIN,"Zpět",back_rect,lambda: change_screen("menu"))

# ===============================
# Hra
# ===============================
def draw_game(delta):
    global snake, dx, dy, food, score, snake_timer, paused
    WIN.fill(BG_COLOR)
    # Skóre
    score_rect = pygame.Rect(10,10,140,40)
    pygame.draw.rect(WIN,(255,255,255),score_rect,2)
    draw_text(WIN,f"Skóre: {score}",score_rect.center,FONT)
    # Herní plocha
    play_area = pygame.Rect(0,60,WIDTH,HEIGHT-60)
    pygame.draw.rect(WIN,BORDER_COLOR,play_area,3)
    if not paused:
        snake_timer += delta
        if snake_timer>=snake_speed:
            snake_timer=0
            new_head=[snake[0][0]+dx,snake[0][1]+dy]
            snake.insert(0,new_head)
            eaten_red=False
            for f in food:
                if snake[0][:2]==f[:2]:
                    if f[2]=="normal":
                        score+=1
                        eaten_red=True
                        spawn_food()
                    else:
                        draw_text(WIN,f"Sebrali jste zelené! Skóre: {score}",(WIDTH//2,HEIGHT//2),FONT)
                        pygame.display.update()
                        pygame.time.delay(2000)
                        change_screen("menu")
            if not eaten_red: snake.pop()
            # Kolize s hranou a sebou
            if (new_head[0]<play_area.left or new_head[0]>=play_area.right-BLOCK_SIZE or
                new_head[1]<play_area.top or new_head[1]>=play_area.bottom-BLOCK_SIZE or
                new_head in snake[1:]):
                draw_text(WIN,f"Hra skončila! Skóre: {score}",(WIDTH//2,HEIGHT//2),FONT)
                pygame.display.update()
                pygame.time.delay(2000)
                change_screen("menu")
    # Vykreslení hada
    for i, seg in enumerate(snake):
        if i==0:
            if dx==BLOCK_SIZE: h=pygame.transform.rotate(snake_head_img,-90)
            elif dx==-BLOCK_SIZE: h=pygame.transform.rotate(snake_head_img,90)
            elif dy==-BLOCK_SIZE: h=snake_head_img
            elif dy==BLOCK_SIZE: h=pygame.transform.rotate(snake_head_img,180)
            else: h=snake_head_img
            WIN.blit(h,seg)
        elif i==len(snake)-1:
            prev = snake[i-1]
            if seg[0]<prev[0]: t=pygame.transform.rotate(snake_tail_img,270)
            elif seg[0]>prev[0]: t=pygame.transform.rotate(snake_tail_img,90)
            elif seg[1]<prev[1]: t=pygame.transform.rotate(snake_tail_img,180)
            else: t=snake_tail_img
            WIN.blit(t,seg)
        else:
            WIN.blit(snake_body_img,seg)
    # Vykreslení jablek
    for f in food:
        if f[2]=="normal": WIN.blit(apple_img,(f[0],f[1]))
        else: WIN.blit(poisoned_apple_img,(f[0],f[1]))

# ===============================
# Hlavní smyčka
# ===============================
while True:
    delta = CLOCK.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if screen_state=="login":
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if username_rect.collidepoint(event.pos): active_input="username"
                elif password_rect.collidepoint(event.pos): active_input="password"
                elif show_rect.collidepoint(event.pos): show_password=not show_password
                else: active_input=None
            if event.type==pygame.KEYDOWN and active_input:
                if event.key==pygame.K_BACKSPACE:
                    if active_input=="username": username=username[:-1]
                    else: password=password[:-1]
                elif event.key==pygame.K_RETURN: pass
                else:
                    if active_input=="username" and len(username)<20: username+=event.unicode
                    elif active_input=="password" and len(password)<20: password+=event.unicode
        if screen_state=="game" and event.type==pygame.KEYDOWN:
            if not paused:
                if event.key in [pygame.K_UP,pygame.K_w] and dy==0: dx,dy=0,-BLOCK_SIZE
                if event.key in [pygame.K_DOWN,pygame.K_s] and dy==0: dx,dy=0,BLOCK_SIZE
                if event.key in [pygame.K_LEFT,pygame.K_a] and dx==0: dx,dy=-BLOCK_SIZE,0
                if event.key in [pygame.K_RIGHT,pygame.K_d] and dx==0: dx,dy=BLOCK_SIZE,0
            if event.key in [pygame.K_SPACE,pygame.K_p]: paused=not paused
            if event.key==pygame.K_RETURN: change_screen("menu")
    if screen_state=="menu": draw_menu()
    elif screen_state=="login": draw_login()
    elif screen_state=="controls": draw_controls()
    elif screen_state=="game": draw_game(delta)
    pygame.display.update()
