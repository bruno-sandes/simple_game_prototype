"""
entities/base.py
================
Classe base AnimatedSprite.

Todos os personagens (Jogador, Monstros, NPC) herdam daqui.
Implementa o desenho procedural com pygame.draw:
  - Cabeça circular
  - Corpo retangular
  - Braços e pernas com animação senoidal de caminhada
"""

import math
import pygame
from config import WHITE, BLACK


class AnimatedSprite:
    """
    Personagem desenhado com formas geométricas básicas.
    Animação de caminhada gerada por math.sin no anim_timer.
    """

    def __init__(self, color: tuple, x: float, y: float, size: int = 22):
        self.color  = color
        self.x      = float(x)
        self.y      = float(y)
        self.size   = size          # "raio" do corpo
        self.anim_timer: float = 0.0
        self.facing: int = 1        # 1 = direita, -1 = esquerda
        self.moving: bool = False

    # ------------------------------------------------------------------ #
    #  Desenho procedural                                                  #
    # ------------------------------------------------------------------ #
    def _draw_character(self, surface: pygame.Surface, sx: int, sy: int,
                        color: tuple) -> None:
        """
        Desenha o personagem centrado em (sx, sy) na tela.
        - sy representa o centro do corpo.
        - Pernas ficam abaixo do corpo; cabeça acima.
        """
        s = self.size
        t = self.anim_timer
        leg_color  = tuple(max(0, c - 40) for c in color)
        arm_color  = tuple(max(0, c - 20) for c in color)

        # ── Animação de caminhada ──────────────────────────────────────
        swing     = int(math.sin(t * 8) * 7) if self.moving else 0
        arm_swing = int(math.sin(t * 8 + math.pi) * 4) if self.moving else 0

        # ── Pernas ────────────────────────────────────────────────────
        pygame.draw.rect(surface, leg_color,
            (sx - s // 3, sy + s // 2, s // 3, 12 + swing), border_radius=3)
        pygame.draw.rect(surface, leg_color,
            (sx,          sy + s // 2, s // 3, 12 - swing), border_radius=3)

        # ── Corpo ─────────────────────────────────────────────────────
        pygame.draw.rect(surface, color,
            (sx - s // 2, sy - s // 2, s, s), border_radius=5)

        # ── Braços ────────────────────────────────────────────────────
        pygame.draw.rect(surface, arm_color,
            (sx - s // 2 - 6, sy - s // 4 + arm_swing, 6, s // 2),
            border_radius=2)
        pygame.draw.rect(surface, arm_color,
            (sx + s // 2,     sy - s // 4 - arm_swing, 6, s // 2),
            border_radius=2)

        # ── Cabeça ────────────────────────────────────────────────────
        head_y = sy - s // 2 - s // 2
        pygame.draw.circle(surface, color, (sx, head_y), s // 2)

        # ── Olhos ─────────────────────────────────────────────────────
        eye_x = sx + (5 * self.facing)
        pygame.draw.circle(surface, WHITE, (eye_x, head_y - 2), 4)
        pygame.draw.circle(surface, BLACK, (eye_x + self.facing, head_y - 2), 2)

    # ------------------------------------------------------------------ #
    #  Update base                                                         #
    # ------------------------------------------------------------------ #
    def update(self, dt: float) -> None:
        """Avança o timer de animação apenas enquanto em movimento."""
        if self.moving:
            self.anim_timer += dt

    # ------------------------------------------------------------------ #
    #  Rect auxiliar (override nas subclasses se necessário)               #
    # ------------------------------------------------------------------ #
    def get_rect(self) -> pygame.Rect:
        half = 16
        return pygame.Rect(self.x - half, self.y - half, half * 2, half * 2)