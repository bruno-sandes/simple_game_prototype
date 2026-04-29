"""
world/tilemap.py

MUDANCAS:
  - Mapa 80x80 (era 50x50) — mais espaço, mais desafiador
  - Obstáculos mais densos e variados
  - Porta visual mais clara (contorno pulsante)
  - Método walkable_grass_pos() para spawn seguro de mobs/itens
"""

import random
import pygame
from config import (
    MAP_W, MAP_H, TILE_SIZE,
    TILE_GRASS, TILE_WATER, TILE_TREE, TILE_STONE, TILE_FLOOR, TILE_DOOR,
    TILE_COLORS, BROWN, SCREEN_W, SCREEN_H
)

_SZ_W = 22
_SZ_H = 14


class World:

    def __init__(self, seed: int = 42):
        self._rng  = random.Random(seed)
        self.tiles: list[list[int]] = []
        self._door_anim = 0.0

        self.sz_x = MAP_W // 2 - _SZ_W // 2
        self.sz_y = MAP_H // 2 - _SZ_H // 2

        self.door_tx = MAP_W // 2
        self.door_ty = self.sz_y + _SZ_H - 1

        self._generate()

    # ── Geração ───────────────────────────────────────────────────────
    def _generate(self) -> None:
        rng = self._rng
        self.tiles = [[TILE_GRASS] * MAP_W for _ in range(MAP_H)]

        # Borda
        for y in range(MAP_H):
            for x in range(MAP_W):
                if x == 0 or y == 0 or x == MAP_W - 1 or y == MAP_H - 1:
                    self.tiles[y][x] = TILE_STONE

        # Margem de proteção ao redor da zona segura
        safe_margin = 4
        sx1 = self.sz_x - safe_margin
        sx2 = self.sz_x + _SZ_W + safe_margin
        sy1 = self.sz_y - safe_margin
        sy2 = self.sz_y + _SZ_H + safe_margin

        def in_safe(tx, ty):
            return sx1 <= tx <= sx2 and sy1 <= ty <= sy2

        # Grupos de árvores (mais densos)
        for _ in range(60):
            gx = rng.randint(2, MAP_W - 3)
            gy = rng.randint(2, MAP_H - 3)
            if in_safe(gx, gy):
                continue
            size = rng.randint(1, 4)
            for dy in range(-size, size + 1):
                for dx in range(-size, size + 1):
                    tx, ty = gx + dx, gy + dy
                    if 1 <= tx < MAP_W - 1 and 1 <= ty < MAP_H - 1 and not in_safe(tx, ty):
                        self.tiles[ty][tx] = TILE_TREE

        # Grupos de pedra
        for _ in range(40):
            gx = rng.randint(2, MAP_W - 3)
            gy = rng.randint(2, MAP_H - 3)
            if in_safe(gx, gy):
                continue
            size = rng.randint(1, 3)
            for dy in range(-size, size + 1):
                for dx in range(-size, size + 1):
                    tx, ty = gx + dx, gy + dy
                    if 1 <= tx < MAP_W - 1 and 1 <= ty < MAP_H - 1 and not in_safe(tx, ty):
                        self.tiles[ty][tx] = TILE_STONE

        # Lagos
        for _ in range(15):
            gx = rng.randint(3, MAP_W - 4)
            gy = rng.randint(3, MAP_H - 4)
            if in_safe(gx, gy):
                continue
            for dy in range(-1, 2):
                for dx in range(-2, 3):
                    tx, ty = gx + dx, gy + dy
                    if 1 <= tx < MAP_W - 1 and 1 <= ty < MAP_H - 1 and not in_safe(tx, ty):
                        self.tiles[ty][tx] = TILE_WATER

        # Zona segura
        for ty in range(self.sz_y, self.sz_y + _SZ_H):
            for tx in range(self.sz_x, self.sz_x + _SZ_W):
                is_wall = (tx == self.sz_x or tx == self.sz_x + _SZ_W - 1 or
                           ty == self.sz_y or ty == self.sz_y + _SZ_H - 1)
                self.tiles[ty][tx] = TILE_STONE if is_wall else TILE_FLOOR

        # Porta na parede sul
        self.tiles[self.door_ty][self.door_tx] = TILE_DOOR

        # Corredor de saída
        for tx in range(self.door_tx - 1, self.door_tx + 2):
            for ty in range(self.door_ty + 1, self.door_ty + 6):
                if 0 < tx < MAP_W - 1 and 0 < ty < MAP_H - 1:
                    self.tiles[ty][tx] = TILE_GRASS

    # ── Utilidades ────────────────────────────────────────────────────
    def safe_zone_center_px(self) -> tuple[float, float]:
        cx = (self.sz_x + _SZ_W // 2) * TILE_SIZE
        cy = (self.sz_y + _SZ_H // 2) * TILE_SIZE
        return float(cx), float(cy)

    def door_px(self) -> tuple[float, float]:
        return (self.door_tx * TILE_SIZE + TILE_SIZE // 2,
                self.door_ty * TILE_SIZE + TILE_SIZE // 2)

    def is_walkable(self, tx: int, ty: int) -> bool:
        if 0 <= ty < MAP_H and 0 <= tx < MAP_W:
            return self.tiles[ty][tx] in (TILE_GRASS, TILE_FLOOR, TILE_DOOR)
        return False

    def is_grass(self, tx: int, ty: int) -> bool:
        """Apenas grama — para spawn de mobs e itens na zona de perigo."""
        if 0 <= ty < MAP_H and 0 <= tx < MAP_W:
            return self.tiles[ty][tx] == TILE_GRASS
        return False

    def walkable_grass_pos(self, rng: random.Random,
                           min_px: float = 0, max_px: float = None,
                           min_py: float = 0, max_py: float = None,
                           exclude_rect=None,
                           max_tries: int = 300) -> tuple[float, float] | None:
        """
        Retorna uma posição aleatória em tile TILE_GRASS dentro dos limites dados.
        Garante que o item/mob não nasça em tile bloqueante.
        """
        max_px = max_px or (MAP_W - 2) * TILE_SIZE
        max_py = max_py or (MAP_H - 2) * TILE_SIZE
        for _ in range(max_tries):
            px = rng.uniform(min_px, max_px)
            py = rng.uniform(min_py, max_py)
            tx = int(px // TILE_SIZE)
            ty = int(py // TILE_SIZE)
            if not self.is_grass(tx, ty):
                continue
            # Verifica 4 cantos do hitbox
            h = 12
            corners_ok = all(
                self.is_grass(int((px + ddx) // TILE_SIZE),
                              int((py + ddy) // TILE_SIZE))
                for ddx, ddy in [(-h,-h),(h,-h),(-h,h),(h,h)]
            )
            if not corners_ok:
                continue
            if exclude_rect and exclude_rect.collidepoint(px, py):
                continue
            return px, py
        return None

    # ── Render ────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        self._door_anim += dt

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
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

        # Destaca a porta com animação pulsante
        drx = self.door_tx * TILE_SIZE - int(cam_x)
        dry = self.door_ty * TILE_SIZE - int(cam_y)
        import math
        pulse = abs(math.sin(self._door_anim * 3))
        border_clr = (
            int(200 + 55 * pulse),
            int(180 + 40 * pulse),
            30,
        )
        pygame.draw.rect(surface, border_clr,
                         (drx, dry, TILE_SIZE, TILE_SIZE), 3)
        font = pygame.font.SysFont("Arial", 9, bold=True)
        lbl  = font.render("PORTA", True, (0, 0, 0))
        surface.blit(lbl, (drx + TILE_SIZE // 2 - lbl.get_width() // 2,
                           dry + TILE_SIZE // 2 - lbl.get_height() // 2))

    @staticmethod
    def _draw_detail(surface, tile, rect, rx, ry):
        ts = TILE_SIZE
        cx = rx + ts // 2
        cy = ry + ts // 2

        if tile == TILE_GRASS:
            pygame.draw.rect(surface, (65, 145, 65), rect, 1)
        elif tile == TILE_FLOOR:
            pygame.draw.rect(surface, (160, 140, 100), rect, 1)
            mid = ts // 2
            pygame.draw.line(surface, (150, 130, 90),
                             (rx + 4, ry + mid), (rx + ts - 4, ry + mid), 1)
            pygame.draw.line(surface, (150, 130, 90),
                             (rx + mid, ry + 4), (rx + mid, ry + ts - 4), 1)
        elif tile == TILE_TREE:
            pygame.draw.rect(surface, BROWN, (cx - 4, cy + 2, 8, 14))
            pygame.draw.circle(surface, (30, 100, 30), (cx, cy - 4), 16)
            pygame.draw.circle(surface, (50, 130, 50), (cx - 5, cy - 8), 9)
        elif tile == TILE_WATER:
            pygame.draw.rect(surface, (60, 110, 220), rect, 1)
        elif tile == TILE_STONE:
            pygame.draw.rect(surface, (90, 80, 70), rect, 1)
        elif tile == TILE_DOOR:
            inner = rect.inflate(-6, -4)
            pygame.draw.rect(surface, (180, 140, 40), inner, border_radius=3)