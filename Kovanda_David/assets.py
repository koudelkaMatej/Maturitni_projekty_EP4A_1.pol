# -*- coding: utf-8 -*-
import os

import pygame


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")


def load_assets():
    # Načte základní obrázky; pokud něco chybí, vyhodí výjimku při loadu.
    assets = {
        "head": pygame.image.load(os.path.join(IMAGES_DIR, "head.png")).convert_alpha(),
        "body": pygame.image.load(os.path.join(IMAGES_DIR, "body.png")).convert_alpha(),
        "tail": pygame.image.load(os.path.join(IMAGES_DIR, "ass.png")).convert_alpha(),
        "apple": pygame.image.load(os.path.join(IMAGES_DIR, "Jablko.png")).convert_alpha(),
        "poisoned": pygame.image.load(os.path.join(IMAGES_DIR, "poisoned_apple.png")).convert_alpha(),
        "pillar": pygame.image.load(os.path.join(IMAGES_DIR, "sloup.png")).convert_alpha(),
        "background": pygame.image.load(os.path.join(IMAGES_DIR, "had pozadi.png")).convert(),
    }
    return assets
