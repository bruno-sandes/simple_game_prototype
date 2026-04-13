"""
Skill do jogador.

Linha reta e desaparece ao atingir um monstro ou acabar
"""

import pygame
from config import (
    SKILL_SPEED, SKILL_DAMAGE, SKILL_LIFE,
    YELLOW, WHITE
)

class Skill:
    """
    Parâmetros:
        x, y    — posição de origem (coord.)
        dx, dy  — direção 
        damage  — dano causado
        color   — cor visual
    """

    def __init__(self, x: float, y: float, dx: float, dy: float,
                 damage: int = SKILL_DAMAGE,
                 color: tuple = YELLOW):
        self.x       = float(x)
        self.y       = float(y)
        self.dx      = dx
        self.dy      = dy
        self.speed   = SKILL_SPEED
        self.lifetime= SKILL_LIFE
        self.radius  = 8
        self.damage  = damage
        self.color   = color
        self._anim   = 0

    # ------------------------------------------------------------------ #
    def update(self, dt: float) -> None:
        self.x        += self.dx * self.speed * dt
        self.y        += self.dy * self.speed * dt
        self.lifetime -= 1
        self._anim    += 1

    # ------------------------------------------------------------------ #
    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        # Halo externo
        pygame.draw.circle(surface, WHITE, (sx, sy), self.radius + 3, 2)
        # Núcleo
        pygame.draw.circle(surface, self.color, (sx, sy), self.radius)
        # Ponto de brilho central
        pygame.draw.circle(surface, WHITE, (sx, sy), max(1, self.radius - 4))

    # ------------------------------------------------------------------ #
    def get_rect(self) -> pygame.Rect:
        r = self.radius
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

    @property
    def alive(self) -> bool:
        return self.lifetime > 0