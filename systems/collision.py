"""systems/collision.py — colisão tile-based. TILE_FLOOR e TILE_DOOR são walkable."""
from config import TILE_SIZE, TILE_GRASS, TILE_FLOOR, TILE_DOOR

_WALKABLE = {TILE_GRASS, TILE_FLOOR, TILE_DOOR}

class CollisionSystem:
    HITBOX = 14

    def __init__(self, world):
        self.world = world

    def resolve_move(self, entity, dx, dy, dt):
        nx = entity.x + dx * entity.speed * dt
        ny = entity.y + dy * entity.speed * dt
        final_dx = dx if self._ok(nx, entity.y) else 0.0
        final_dy = dy if self._ok(entity.x, ny) else 0.0
        return final_dx, final_dy

    def is_point_clear(self, px, py):
        return self._tile(px, py) in _WALKABLE

    def _tile(self, px, py):
        tx, ty = int(px // TILE_SIZE), int(py // TILE_SIZE)
        t = self.world.tiles
        if 0 <= ty < len(t) and 0 <= tx < len(t[0]):
            return t[ty][tx]
        return -1

    def _ok(self, cx, cy):
        h = self.HITBOX
        return all(self._tile(px, py) in _WALKABLE
                   for px, py in [(cx-h,cy-h),(cx+h,cy-h),(cx-h,cy+h),(cx+h,cy+h)])
