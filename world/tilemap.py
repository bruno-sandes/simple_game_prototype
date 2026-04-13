"""
world/tilemap.py
================
Geração e renderização do mapa de tiles (50 × 50).

Tiles disponíveis (ver config.py):
  TILE_GRASS  — chão verde padrão
  TILE_WATER  — água (intransponível visualmente)
  TILE_TREE   — árvore decorativa
  TILE_STONE  — pedra / borda do mapa

A geração é procedural com semente aleatória, garantindo
um caminho central livre de obstáculos para o início do jogo.
Só renderiza os tiles visíveis pela câmera (culling básico).
"""

import random
import pygame
from config import (
    MAP_W, MAP_H, TILE_SIZE,
    TILE_GRASS, TILE_WATER, TILE_TREE, TILE_STONE,
    TILE_COLORS, BROWN, SCREEN_W, SCREEN_H
)


class World:
    """
    Parâmetros:
        seed — semente para o gerador aleatório (reprodutível)
    """

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)
        self.tiles: list[list[int]] = []
        self._generate()

    # ------------------------------------------------------------------ #
    #  Geração procedural                                                  #
    # ------------------------------------------------------------------ #
    def _generate(self) -> None:
        rng = self._rng

        for y in range(MAP_H):
            row = []
            for x in range(MAP_W):
                # Borda sempre é pedra
                if x == 0 or y == 0 or x == MAP_W - 1 or y == MAP_H - 1:
                    row.append(TILE_STONE)
                    continue
                r = rng.random()
                if   r < 0.06:  row.append(TILE_WATER)
                elif r < 0.13:  row.append(TILE_TREE)
                elif r < 0.17:  row.append(TILE_STONE)
                else:            row.append(TILE_GRASS)
            self.tiles.append(row)

        # Área central limpa ao redor do spawn do jogador
        cx, cy = MAP_W // 2, MAP_H // 2
        for dy in range(-4, 5):
            for dx in range(-12, 13):
                self.tiles[cy + dy][cx + dx] = TILE_GRASS

    # ------------------------------------------------------------------ #
    #  Renderização                                                        #
    # ------------------------------------------------------------------ #
    def draw(self, surface: pygame.Surface,
             cam_x: float, cam_y: float) -> None:
        """
        Renderiza apenas os tiles dentro do viewport (câmera culling).
        Adiciona detalhes visuais por tipo de tile.
        """
        x0 = max(0, int(cam_x // TILE_SIZE))
        y0 = max(0, int(cam_y // TILE_SIZE))
        x1 = min(MAP_W, x0 + SCREEN_W // TILE_SIZE + 2)
        y1 = min(MAP_H, y0 + SCREEN_H // TILE_SIZE + 2)

        for ty in range(y0, y1):
            for tx in range(x0, x1):
                tile  = self.tiles[ty][tx]
                color = TILE_COLORS[tile]
                rx    = tx * TILE_SIZE - int(cam_x)
                ry    = ty * TILE_SIZE - int(cam_y)
                rect  = pygame.Rect(rx, ry, TILE_SIZE, TILE_SIZE)

                pygame.draw.rect(surface, color, rect)
                self._draw_detail(surface, tile, rect, rx, ry)

    # ------------------------------------------------------------------ #
    #  Detalhes por tile                                                   #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _draw_detail(surface: pygame.Surface, tile: int,
                     rect: pygame.Rect, rx: int, ry: int) -> None:
        ts = TILE_SIZE
        cx = rx + ts // 2
        cy = ry + ts // 2

        if tile == TILE_GRASS:
            pygame.draw.rect(surface, (65, 145, 65), rect, 1)

        elif tile == TILE_TREE:
            # Tronco
            pygame.draw.rect(surface, BROWN, (cx - 4, cy + 2, 8, 14))
            # Copa (dois círculos sobrepostos)
            pygame.draw.circle(surface, (30, 100, 30), (cx, cy - 4), 16)
            pygame.draw.circle(surface, (50, 130, 50), (cx - 5, cy - 8), 9)

        elif tile == TILE_WATER:
            # Linha de brilho simulando ondas
            pygame.draw.rect(surface, (60, 110, 220), rect, 1)

        elif tile == TILE_STONE:
            pygame.draw.rect(surface, (110, 100, 90), rect, 1)