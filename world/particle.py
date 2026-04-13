"""
world/particle.py
=================
Partículas de texto flutuante para feedback visual.

Exemplos de uso:
  Particle(x, y, "+20 XP", YELLOW)   — ganho de experiência
  Particle(x, y, "-30",    RED)       — dano causado
  Particle(x, y, "GEM",   TEAL)      — item coletado

A partícula sobe, desacelera e some gradualmente via alpha.
"""

import pygame
from config import YELLOW


class Particle:
    """
    Parâmetros:
        x, y    — posição inicial no mundo
        text    — texto exibido
        color   — cor do texto
    """

    def __init__(self, x: float, y: float,
                 text: str, color: tuple = YELLOW):
        self.x        = float(x)
        self.y        = float(y)
        self.vy       = -65.0          # velocidade inicial para cima
        self.text     = text
        self.color    = color
        self.life     = 90             # frames de duração
        self.max_life = 90

    # ------------------------------------------------------------------ #
    def update(self, dt: float) -> None:
        self.y  += self.vy * dt
        self.vy *= 0.96                # desaceleração exponencial
        self.life -= 1

    # ------------------------------------------------------------------ #
    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        if self.life <= 0:
            return
        alpha = int(255 * self.life / self.max_life)
        sx    = int(self.x - cam_x)
        sy    = int(self.y - cam_y)
        font  = pygame.font.SysFont("Arial", 14, bold=True)
        surf  = font.render(self.text, True, self.color)
        surf.set_alpha(alpha)
        surface.blit(surf, (sx - surf.get_width() // 2, sy))

    @property
    def alive(self) -> bool:
        return self.life > 0