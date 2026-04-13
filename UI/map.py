"""
ui/minimap.py
=============
Mini-mapa exibido no canto superior direito durante o gameplay.

Mostra em escala reduzida:
  • Jogador    — ponto azul com contorno branco
  • NPCs       — ponto amarelo
  • Monstros   — ponto vermelho (apenas vivos)
  • Itens      — ponto da cor do item (apenas não coletados)

O fundo é semi-transparente via pygame.SRCALPHA.
"""

import pygame
from config import (
    MAP_W, MAP_H, TILE_SIZE,
    WHITE, GRAY, YELLOW, RED, LIGHT_GRAY
)
from ui.fonts import fonts


class MiniMap:
    """
    Parâmetros:
        x, y    — posição do canto superior esquerdo na tela
        w, h    — dimensões em pixels
    """

    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        # Superfície de fundo reutilizável
        self._bg = pygame.Surface((w, h), pygame.SRCALPHA)
        self._bg.fill((10, 10, 20, 185))

    # ------------------------------------------------------------------ #
    def draw(self, surface: pygame.Surface,
             player, npcs: list, monsters: list, items: list) -> None:

        surface.blit(self._bg, (self.x, self.y))
        pygame.draw.rect(surface, GRAY, (self.x, self.y, self.w, self.h), 1)

        # Escala mundo → minimap
        sx = self.w / (MAP_W * TILE_SIZE)
        sy = self.h / (MAP_H * TILE_SIZE)

        def to_mm(wx: float, wy: float) -> tuple[int, int]:
            return (int(self.x + wx * sx), int(self.y + wy * sy))

        # Itens (menores)
        for item in items:
            if not item.collected:
                px, py = to_mm(item.x, item.y)
                pygame.draw.circle(surface, item.color, (px, py), 2)

        # NPCs
        for npc in npcs:
            px, py = to_mm(npc.x, npc.y)
            pygame.draw.circle(surface, YELLOW, (px, py), 3)

        # Monstros
        for m in monsters:
            if not m.dead:
                px, py = to_mm(m.x, m.y)
                pygame.draw.circle(surface, RED, (px, py), 3)

        # Jogador (destaque maior)
        px, py = to_mm(player.x, player.y)
        pygame.draw.circle(surface, player.color, (px, py), 5)
        pygame.draw.circle(surface, WHITE,         (px, py), 5, 1)

        # ── Legenda ───────────────────────────────────────────────────
        legends = [
            ("■ Você",    player.color),
            ("■ NPC",     YELLOW),
            ("■ Inimigo", RED),
        ]
        for i, (txt, clr) in enumerate(legends):
            s = fonts.xxs.render(txt, True, clr)
            surface.blit(s, (self.x + 2, self.y + self.h - 10 - (2 - i) * 11))

        # Título
        title = fonts.xxs.render("MAPA", True, LIGHT_GRAY)
        surface.blit(title,
                     (self.x + self.w // 2 - title.get_width() // 2, self.y + 2))