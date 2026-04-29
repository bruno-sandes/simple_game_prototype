"""
ui/map.py

MUDANCA: minimap com fog of war.
Entidades (mobs, itens) só aparecem no minimap se estiverem
dentro do lantern_radius do player × MINIMAP_REVEAL_MULT.
NPCs e o próprio player sempre aparecem.
Isso torna a lanterna essencial: sem ela, o player não vê
os mobs chegando nem no minimap.
"""

import math
import pygame
<<<<<<< Updated upstream
from config import (
    MAP_W, MAP_H, TILE_SIZE,
    WHITE, GRAY, YELLOW, RED, LIGHT_GRAY
)
from ui.fonts import fonts
=======
from config import MAP_W, MAP_H, TILE_SIZE, WHITE, GRAY, YELLOW, RED, LIGHT_GRAY

# Multiplicador: entidade visível no minimap se dist < lantern_radius * MULT
MINIMAP_REVEAL_MULT = 2.2
>>>>>>> Stashed changes


class MiniMap:

    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self._bg = pygame.Surface((w, h), pygame.SRCALPHA)
        self._bg.fill((10, 10, 20, 185))

    def draw(self, surface: pygame.Surface,
             player, npcs: list, monsters: list, items: list) -> None:
<<<<<<< Updated upstream
=======
        from ui.fonts import fonts
>>>>>>> Stashed changes

        surface.blit(self._bg, (self.x, self.y))
        pygame.draw.rect(surface, GRAY, (self.x, self.y, self.w, self.h), 1)

        sx = self.w / (MAP_W * TILE_SIZE)
        sy = self.h / (MAP_H * TILE_SIZE)
        reveal_dist = player.lantern_radius * MINIMAP_REVEAL_MULT

        def to_mm(wx, wy):
            return (int(self.x + wx * sx), int(self.y + wy * sy))

        def in_range(ex, ey):
            return math.hypot(ex - player.x, ey - player.y) <= reveal_dist

        # Itens — apenas se visíveis
        for item in items:
            if not item.collected and in_range(item.x, item.y):
                px, py = to_mm(item.x, item.y)
                pygame.draw.circle(surface, item.color, (px, py), 2)

        # NPCs — sempre visíveis (zona segura)
        for npc in npcs:
            px, py = to_mm(npc.x, npc.y)
            pygame.draw.circle(surface, YELLOW, (px, py), 3)

        # Mobs — apenas se visíveis
        for m in monsters:
            if not m.dead and in_range(m.x, m.y):
                clr = (255, 80, 80) if m.monster_type == "boss" else RED
                r   = 4 if m.monster_type == "boss" else 3
                px, py = to_mm(m.x, m.y)
                pygame.draw.circle(surface, clr, (px, py), r)

        # Player — sempre visível, com contorno
        px, py = to_mm(player.x, player.y)
        pygame.draw.circle(surface, player.color, (px, py), 5)
        pygame.draw.circle(surface, WHITE,         (px, py), 5, 1)

        # Legenda
        legends = [("■ Você", player.color), ("■ NPC", YELLOW), ("■ Inimigo", RED)]
        for i, (txt, clr) in enumerate(legends):
            s = fonts.xxs.render(txt, True, clr)
            surface.blit(s, (self.x + 2, self.y + self.h - 10 - (2 - i) * 11))

        title = fonts.xxs.render("MAPA", True, LIGHT_GRAY)
        surface.blit(title, (self.x + self.w // 2 - title.get_width() // 2, self.y + 2))