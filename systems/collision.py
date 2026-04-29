"""
systems/collision.py

BUG CORRIGIDO:
  _is_walkable_rect() só aceitava TILE_GRASS como transitável.
  TILE_FLOOR (chão da zona segura) e TILE_DOOR não estavam na lista,
  então o player ficava travado ao nascer na zona segura.

  FIX: _WALKABLE agora inclui TILE_GRASS, TILE_FLOOR e TILE_DOOR.
"""

from config import TILE_SIZE, TILE_GRASS, TILE_FLOOR, TILE_DOOR

# Tiles que o player (e pathfinder) pode pisar
_WALKABLE = {TILE_GRASS, TILE_FLOOR, TILE_DOOR}


class CollisionSystem:

    HITBOX = 14   # raio do hitbox em pixels

    def __init__(self, world):
        self.world = world

    def resolve_move(self, entity, dx: float, dy: float, dt: float) -> tuple[float, float]:
        """
        Retorna (dx_final, dy_final) após resolução de colisão.
        Testa X e Y separadamente para permitir deslizamento em paredes.
        """
        nx = entity.x + dx * entity.speed * dt
        ny = entity.y + dy * entity.speed * dt

        final_dx = dx if self._is_walkable_rect(nx, entity.y) else 0.0
        final_dy = dy if self._is_walkable_rect(entity.x, ny) else 0.0
        return final_dx, final_dy

    def can_move(self, entity, dx: float, dy: float, dt: float) -> bool:
        nx = entity.x + dx * entity.speed * dt
        ny = entity.y + dy * entity.speed * dt
        return self._is_walkable_rect(nx, ny)

    def is_point_clear(self, px: float, py: float) -> bool:
        """Usado pelo Pathfinder."""
        return self._tile_at(px, py) in _WALKABLE

    # ── Internos ──────────────────────────────────────────────────────

    def _tile_at(self, px: float, py: float) -> int:
        tx = int(px // TILE_SIZE)
        ty = int(py // TILE_SIZE)
        tiles = self.world.tiles
        if 0 <= ty < len(tiles) and 0 <= tx < len(tiles[0]):
            return tiles[ty][tx]
        return -1

    def _is_walkable_rect(self, cx: float, cy: float) -> bool:
        """Verifica os 4 cantos do hitbox centrado em (cx, cy)."""
        h = self.HITBOX
        return all(
            self._tile_at(px, py) in _WALKABLE
            for px, py in [
                (cx - h, cy - h),
                (cx + h, cy - h),
                (cx - h, cy + h),
                (cx + h, cy + h),
            ]
        )