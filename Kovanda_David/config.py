# -*- coding: utf-8 -*-
import pygame

# Barvy a vzhled
BG_COLOR = (7, 16, 39)
TEXT_COLOR = (234, 246, 255)
BUTTON_COLOR = (30, 167, 255)
BUTTON_HOVER = (13, 141, 229)
ACTIVE_BORDER = (255, 200, 50)
EYE_HOVER = (255, 200, 50)
BORDER_COLOR = (200, 40, 40)
BUTTON_BAR_BG = (20, 40, 70)
ERROR_COLOR = (255, 80, 80)
SUCCESS_COLOR = (80, 200, 120)
LABEL_COLOR = (180, 200, 220)

BLOCK_SIZE = 20
TOP_MARGIN = 60

# Nastavení displeje

def init_display_fullscreen():
    # Můžete přepnout na fullscreen přes pygame.FULLSCREEN
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    width, height = screen.get_size()
    return screen, width, height

# Konfigurace herních módů
mode_config = {
    "classic": {"label": "Classic", "poison": False, "pillars": 0, "speed": 120},
    "poison": {"label": "Poison", "poison": True, "pillars": 0, "speed": 120},
    "pillars": {"label": "Pillars", "poison": False, "pillars": 20, "speed": 140},
    # Hardcore: rychlejší had, jedovatá jablka i sloupy
    "hardcore": {"label": "Hardcore", "poison": True, "pillars": 30, "speed": 90},
}
