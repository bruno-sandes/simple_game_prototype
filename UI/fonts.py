"""ui/fonts.py — FontManager singleton."""
import pygame

class FontManager:
    def __init__(self):
        self.xl  = pygame.font.SysFont("Arial", 36, bold=True)
        self.lg  = pygame.font.SysFont("Arial", 26, bold=True)
        self.md  = pygame.font.SysFont("Arial", 20)
        self.sm  = pygame.font.SysFont("Arial", 14)
        self.xs  = pygame.font.SysFont("Arial", 11)
        self.xxs = pygame.font.SysFont("Arial",  9, bold=True)

fonts: FontManager | None = None

def init_fonts():
    global fonts
    fonts = FontManager()
    return fonts
