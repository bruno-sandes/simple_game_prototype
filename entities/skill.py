"""
entities/projectile.py
======================
Projétil disparado pela skill do jogador.

Criado com direção normalizada, voa em linha reta e
desaparece ao atingir um monstro ou esgotar lifetime.
"""

import pygame
from config import (
    PROJECTILE_SPEED, PROJECTILE_DAMAGE, PROJECTILE_LIFE,
    YELLOW, WHITE
)


class Projectile:
    """
    Parâmetros:
        x, y    — posição de origem (coordenadas do mundo)
        dx, dy  — direção normalizada
        damage  — dano causado ao acertar
        color   — cor visual
    """

    def __init__(self, x: float, y: float, dx: float, dy: float,
                 damage: int = PROJECTILE_DAMAGE,
                 color: tuple = YELLOW):
        self.x       = float(x)
        self.y       = float(y)
        self.dx      = dx
        self.dy      = dy
        self.speed   = PROJECTILE_SPEED
        self.lifetime= PROJECTILE_LIFE
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