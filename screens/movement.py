"""
screens/movement.py
===================
MovementController — unifica movimentacao WASD e pathfinder por clique.

Comportamento:
  WASD / setas  -> move o player diretamente (cancela pathfinder ativo)
  Clique esq.   -> calcula rota A* ate o ponto clicado e move automaticamente
  Colisao       -> usa CollisionSystem para evitar tiles bloqueantes
  Deslizamento  -> testa X e Y separadamente (player desliza em paredes)

Renderizacao:
  draw_path() exibe a rota calculada como pontos azuis + destino amarelo.
  Chamado pelo Game.draw() antes do HUD.

Uso:
    ctrl = MovementController(world)
    ctrl.handle_click(mouse_world_x, mouse_world_y, player)
    ctrl.update(player, dt, keys)
    ctrl.draw_path(surface, cam_x, cam_y)
"""

import math
import pygame
from systems.pathfinder import Pathfinder
from systems.collision  import CollisionSystem
from config import TILE_SIZE


_WASD_KEYS = (
    pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,
    pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT,
)

# Cores do caminho renderizado
_DOT_CLR  = (100, 220, 255)
_DEST_CLR = (255, 220,  50)


class MovementController:
    """
    Parâmetros:
        world — instancia de World (repassada ao Pathfinder e CollisionSystem)
    """

    # Distancia (pixels) para considerar waypoint alcancado
    WAYPOINT_REACH = TILE_SIZE * 0.6

    def __init__(self, world):
        self._pf  = Pathfinder(world)
        self._col = CollisionSystem(world)
        self.path: list[tuple[float, float]] = []   # waypoints restantes

    # ------------------------------------------------------------------ #
    #  Pathfinder via clique                                               #
    # ------------------------------------------------------------------ #
    def handle_click(self, world_x: float, world_y: float, player) -> None:
        """
        Calcula um caminho ate (world_x, world_y) e inicia o percurso.
        Se o destino for bloqueado, cancela silenciosamente.
        """
        new_path = self._pf.find(player.x, player.y, world_x, world_y)
        self.path = new_path   # [] se nao ha caminho

    def clear_path(self) -> None:
        self.path = []

    # ------------------------------------------------------------------ #
    #  Update                                                              #
    # ------------------------------------------------------------------ #
    def update(self, player, dt: float, keys) -> None:
        """
        Deve ser chamado a cada frame antes de player.update(dt).

        Prioridade:
          1. WASD pressionado  -> movimento direto + cancela pathfinder
          2. Pathfinder ativo  -> move player ao longo do caminho
        """
        dx, dy = self._read_wasd(keys)
        wasd_active = (dx != 0 or dy != 0)

        if wasd_active:
            # WASD tem prioridade: cancela pathfinder
            if self.path:
                self.path = []
            rdx, rdy = self._col.resolve_move(player, dx, dy, dt)
            player.move(rdx, rdy, dt)

        elif self.path:
            # Seguir proximo waypoint
            self._follow_path(player, dt)

        else:
            player.moving = False

    # ------------------------------------------------------------------ #
    #  Renderizacao do caminho                                             #
    # ------------------------------------------------------------------ #
    def draw_path(self, surface: pygame.Surface,
                  cam_x: float, cam_y: float) -> None:
        if not self.path:
            return

        # Pontos intermediarios (1 a cada 2)
        for i, (wx, wy) in enumerate(self.path[:-1]):
            if i % 2 != 0:
                continue
            sx = int(wx - cam_x)
            sy = int(wy - cam_y)
            pygame.draw.circle(surface, _DOT_CLR, (sx, sy), 3)

        # Destino
        dx = int(self.path[-1][0] - cam_x)
        dy = int(self.path[-1][1] - cam_y)
        pygame.draw.circle(surface, _DEST_CLR, (dx, dy), 7)
        pygame.draw.circle(surface, (255, 255, 255), (dx, dy), 7, 2)

    # ------------------------------------------------------------------ #
    #  Internos                                                            #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _read_wasd(keys) -> tuple[float, float]:
        dx = dy = 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        return float(dx), float(dy)

    def _follow_path(self, player, dt: float) -> None:
        if not self.path:
            return

        wx, wy   = self.path[0]
        diff_x   = wx - player.x
        diff_y   = wy - player.y
        dist     = math.hypot(diff_x, diff_y)

        if dist <= self.WAYPOINT_REACH:
            self.path.pop(0)
            if not self.path:
                player.moving = False
            return

        # Normalizar direcao
        ndx = diff_x / dist
        ndy = diff_y / dist

        # Aplicar colisao e mover
        rdx, rdy = self._col.resolve_move(player, ndx, ndy, dt)
        if rdx == 0 and rdy == 0:
            # Bloqueado: descarta caminho para evitar loop
            self.path = []
            player.moving = False
            return

        player.move(rdx, rdy, dt)
        if diff_x != 0:
            player.facing = 1 if diff_x > 0 else -1