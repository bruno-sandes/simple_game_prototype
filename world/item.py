"""
world/item.py
=============
Itens coletáveis espalhados pelo mundo.

7 tipos definidos em config.ITEM_DEFS:
  hp_potion, gem, sword, shield, key, coin, scroll

Animação: flutuação vertical suave via math.sin.
Coleta: o Game detecta colisão com o rect do jogador.
Itens coletados ficam com collected=True e não são mais desenhados.
"""

import math
import pygame
from config import ITEM_DEFS, ITEM_COLLECT_RADIUS, WHITE


class Item:
    """
    Parâmetros:
        x, y        — posição no mundo (pode ser 0,0 para itens de inventário)
        item_type   — chave em config.ITEM_DEFS
    """

    def __init__(self, x: float, y: float, item_type: str = "gem"):
        d = ITEM_DEFS.get(item_type, ITEM_DEFS["gem"])
        self.x         = float(x)
        self.y         = float(y)
        self.item_type = item_type
        self.color     = d["color"]
        self.label     = d["label"]
        self.icon      = d["icon"]   # 2 chars para exibir sobre o item
        self.collected = False
        self._anim     = 0.0

    # ------------------------------------------------------------------ #
    def update(self, dt: float) -> None:
        self._anim += dt

    # ------------------------------------------------------------------ #
    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        if self.collected:
            return

        # Flutuação suave
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y) + int(math.sin(self._anim * 3) * 4)

        # Sombra no chão
        shadow = pygame.Surface((22, 8), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 60))
        surface.blit(shadow, (sx - 11, sy + 13))

        # Círculo principal
        pygame.draw.circle(surface, self.color, (sx, sy), 11)
        pygame.draw.circle(surface, WHITE, (sx, sy), 11, 2)

        # Brilho interno
        bright = tuple(min(255, c + 80) for c in self.color)
        pygame.draw.circle(surface, bright, (sx - 3, sy - 3), 4)

        # Ícone (2 chars)
        font = pygame.font.SysFont("Arial", 9, bold=True)
        ic   = font.render(self.icon[:2], True, WHITE)
        surface.blit(ic, (sx - ic.get_width() // 2, sy - ic.get_height() // 2))

    # ------------------------------------------------------------------ #
    def get_rect(self) -> pygame.Rect:
        r = ITEM_COLLECT_RADIUS
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)