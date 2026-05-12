"""
entities/skill.py
Projétil da skill — para ao atingir tile bloqueante.
Hitbox fino (radius=5). Range limitada por SKILL_MAX_RANGE.
"""
import math, pygame
from config import SKILL_SPEED, SKILL_DAMAGE, SKILL_LIFE, SKILL_RADIUS, SKILL_MAX_RANGE
from config import YELLOW, WHITE, TILE_SIZE, TILE_GRASS, TILE_FLOOR, TILE_DOOR

_PASS = {TILE_GRASS, TILE_FLOOR, TILE_DOOR}

def _tile_at(world, px, py):
    tx, ty = int(px//TILE_SIZE), int(py//TILE_SIZE)
    if world and 0<=ty<len(world.tiles) and 0<=tx<len(world.tiles[0]):
        return world.tiles[ty][tx]
    return TILE_GRASS

class Skill:
    def __init__(self, x, y, dx, dy, damage=SKILL_DAMAGE,
                 color=YELLOW, world=None, radius=None):
        self.x, self.y   = float(x), float(y)
        self.ox, self.oy = float(x), float(y)   # origem (para calcular range)
        self.dx, self.dy = dx, dy
        self.speed        = SKILL_SPEED
        self.lifetime     = SKILL_LIFE
        self.radius       = radius if radius else SKILL_RADIUS
        self.damage       = damage
        self.color        = color
        self._world       = world
        self._anim        = 0

    def update(self, dt):
        nx = self.x + self.dx * self.speed * dt
        ny = self.y + self.dy * self.speed * dt
        # Para se bater em tile bloqueante
        if _tile_at(self._world, nx, ny) not in _PASS:
            self.lifetime = 0
            return
        # Para se ultrapassar o alcance máximo
        if math.hypot(nx-self.ox, ny-self.oy) > SKILL_MAX_RANGE:
            self.lifetime = 0
            return
        self.x, self.y = nx, ny
        self.lifetime -= 1
        self._anim    += 1

    def draw(self, surface, cam_x, cam_y):
        sx, sy = int(self.x-cam_x), int(self.y-cam_y)
        pygame.draw.circle(surface, WHITE, (sx,sy), self.radius+2, 1)
        pygame.draw.circle(surface, self.color, (sx,sy), self.radius)
        if self.radius > 3:
            pygame.draw.circle(surface, WHITE, (sx,sy), max(1,self.radius-3))

    def get_rect(self):
        r = self.radius
        return pygame.Rect(self.x-r, self.y-r, r*2, r*2)

    @property
    def alive(self): return self.lifetime > 0
