"""
systems/collision.py
====================
Sistema de colisão baseado em tiles do mapa.

Tiles walkable (transitável):
  TILE_GRASS — único tipo caminhável

Tiles bloqueantes:
  TILE_WATER, TILE_TREE, TILE_STONE

Uso principal:
    col = CollisionSystem(world)
    if col.can_move(player, dx, dy, dt):
        player.move(dx, dy, dt)

O sistema verifica os 4 cantos do hitbox do personagem,
evitando atravessar obstáculos mesmo em movimento diagonal.
"""

from config import TILE_SIZE, TILE_GRASS


class CollisionSystem:
    """
    Parâmetros:
        world — instância de World (precisa do attr .tiles)
    """

    # Raio do hitbox do personagem em pixels
    HITBOX = 14

    def __init__(self, world):
        self.world = world

    # ------------------------------------------------------------------ #
    #  API pública                                                         #
    # ------------------------------------------------------------------ #
    def can_move(self, entity, dx: float, dy: float, dt: float) -> bool:
        """
        Retorna True se o movimento (dx, dy) × dt é válido para a entidade.
        Testa separadamente X e Y para deslizamento lateral em paredes.
        """
        nx = entity.x + dx * entity.speed * dt
        ny = entity.y + dy * entity.speed * dt
        return self._is_walkable_rect(nx, ny)

    def resolve_move(self, entity, dx: float, dy: float, dt: float) -> tuple[float, float]:
        """
        Retorna (dx_final, dy_final) após resolução de colisão.
        Permite deslizamento: testa X e Y separadamente.
        """
        nx = entity.x + dx * entity.speed * dt
        ny = entity.y + dy * entity.speed * dt
        h = self.HITBOX

        final_dx = dx if self._is_walkable_rect(nx, entity.y) else 0.0
        final_dy = dy if self._is_walkable_rect(entity.x, ny) else 0.0
        return final_dx, final_dy

    def is_tile_walkable(self, px: float, py: float) -> bool:
        """Verifica se o ponto (px, py) em pixels está em tile transitável."""
        return self._tile_at(px, py) == TILE_GRASS

    def is_point_clear(self, px: float, py: float) -> bool:
        """Alias semântico para uso no pathfinder."""
        return self._tile_at(px, py) == TILE_GRASS

    # ------------------------------------------------------------------ #
    #  Internos                                                            #
    # ------------------------------------------------------------------ #
    def _tile_at(self, px: float, py: float) -> int:
        tx = int(px // TILE_SIZE)
        ty = int(py // TILE_SIZE)
        tiles = self.world.tiles
        if 0 <= ty < len(tiles) and 0 <= tx < len(tiles[0]):
            return tiles[ty][tx]
        return -1  # fora do mapa → bloqueante

    def _is_walkable_rect(self, cx: float, cy: float) -> bool:
        """Verifica os 4 cantos do hitbox centrado em (cx, cy)."""
        h = self.HITBOX
        return all(
            self._tile_at(px, py) == TILE_GRASS
            for px, py in [
                (cx - h, cy - h),
                (cx + h, cy - h),
                (cx - h, cy + h),
                (cx + h, cy + h),
            ]
        )