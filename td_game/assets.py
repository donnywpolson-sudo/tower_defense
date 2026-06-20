import pygame

from .config import ASSET_DIR


def load_image(relative_path, scale=None):
    path = ASSET_DIR / relative_path
    if not path.exists():
        return None
    try:
        image = pygame.image.load(str(path)).convert_alpha()
        if scale:
            image = pygame.transform.scale(image, scale)
        return image
    except pygame.error:
        return None


def load_sound(relative_path):
    path = ASSET_DIR / relative_path
    if not path.exists():
        return None
    try:
        return pygame.mixer.Sound(str(path))
    except pygame.error:
        return None


def draw_sprite_centered(surface, sprite, x, y):
    if sprite is None:
        return False
    rect = sprite.get_rect(center=(int(x), int(y)))
    surface.blit(sprite, rect)
    return True
