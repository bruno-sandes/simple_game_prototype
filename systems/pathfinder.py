"""
systems/pathfinder.py
=====================
Algoritmo A* sobre a grade de tiles do mapa (50 × 50).

Estrutura de dados usada:
  • array 2D (lista de listas) — grade de tiles do World
  • heapq (fila de prioridade) — fronteira do A*
  • dict — came_from, g_score, f_score

O resultado é uma lista de waypoints em pixels
[(wx1,wy1), (wx2,wy2), ...] da posição atual até o destino,
já convertidos para o centro de cada tile.

Uso:
    pf = Pathfinder(world)
    path = pf.find(player.x, player.y, target_x, target_y)
    # path = [] se não houver caminho
"""

import heapq
import math
from config import TILE_SIZE, MAP_W, MAP_H, TILE_GRASS


class Pathfinder:
    """
    Parâmetros:
        world — instância de World com attr .tiles (list[list[int]])
    """

    def __init__(self, world):
        self.world = world

    # ------------------------------------------------------------------ #
    #  API pública                                                         #
    # ------------------------------------------------------------------ #
    def find(self, sx: float, sy: float,
             gx: float, gy: float) -> list[tuple[float, float]]:
        """
        Calcula o caminho de (sx,sy) até (gx,gy) em pixels.
        Retorna lista de pontos centrais de tiles em pixels.
        Retorna [] se não houver caminho ou destino bloqueado.
        """
        start = self._to_tile(sx, sy)
        goal  = self._to_tile(gx, gy)

        if not self._walkable(*start) or not self._walkable(*goal):
            return []
        if start == goal:
            return []

        # ── A* ──────────────────────────────────────────────────────
        open_heap = []
        heapq.heappush(open_heap, (0, start))

        came_from: dict[tuple, tuple | None] = {start: None}
        g_score: dict[tuple, float]          = {start: 0}

        while open_heap:
            _, current = heapq.heappop(open_heap)

            if current == goal:
                return self._reconstruct(came_from, goal)

            for nbr in self._neighbors(*current):
                new_g = g_score[current] + self._cost(current, nbr)
                if nbr not in g_score or new_g < g_score[nbr]:
                    g_score[nbr]  = new_g
                    f             = new_g + self._heuristic(nbr, goal)
                    heapq.heappush(open_heap, (f, nbr))
                    came_from[nbr] = current

        return []  # sem caminho

    # ------------------------------------------------------------------ #
    #  Internos                                                            #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _to_tile(px: float, py: float) -> tuple[int, int]:
        return (int(px // TILE_SIZE), int(py // TILE_SIZE))

    @staticmethod
    def _to_world(tx: int, ty: int) -> tuple[float, float]:
        """Centro do tile em pixels."""
        return (tx * TILE_SIZE + TILE_SIZE / 2, ty * TILE_SIZE + TILE_SIZE / 2)

    def _walkable(self, tx: int, ty: int) -> bool:
        if 0 <= ty < MAP_H and 0 <= tx < MAP_W:
            return self.world.tiles[ty][tx] == TILE_GRASS
        return False

    def _neighbors(self, tx: int, ty: int) -> list[tuple[int, int]]:
        """Vizinhos ortogonais e diagonais transitáveis."""
        results = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),
                        (-1,-1),(1,-1),(-1,1),(1,1)]:
            nx, ny = tx + dx, ty + dy
            # Diagonais só permitidas se ambos os tiles adjacentes são livres
            if dx != 0 and dy != 0:
                if not (self._walkable(tx + dx, ty) and
                        self._walkable(tx, ty + dy)):
                    continue
            if self._walkable(nx, ny):
                results.append((nx, ny))
        return results

    @staticmethod
    def _cost(a: tuple[int,int], b: tuple[int,int]) -> float:
        """Custo diagonal = √2, ortogonal = 1."""
        return 1.414 if a[0] != b[0] and a[1] != b[1] else 1.0

    @staticmethod
    def _heuristic(a: tuple[int,int], b: tuple[int,int]) -> float:
        """Heurística octil (melhor para grades com diagonais)."""
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        return max(dx, dy) + (1.414 - 1) * min(dx, dy)

    def _reconstruct(self, came_from: dict,
                     goal: tuple[int,int]) -> list[tuple[float, float]]:
        path = []
        cur  = goal
        while cur is not None:
            path.append(self._to_world(*cur))
            cur = came_from[cur]
        path.reverse()
        return path  # primeiro elemento = próximo waypoint