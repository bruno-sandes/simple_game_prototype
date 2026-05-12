"""entities/player.py — Player com skill_damage, lantern_radius, skill_radius upgradáveis."""
import math, pygame
from config import (PLAYER_SPEED, PLAYER_MAX_HP, PLAYER_SKILL_CD, PLAYER_INVINCIBLE,
                    MAP_W, MAP_H, TILE_SIZE, SKILL_DAMAGE, SKILL_RADIUS,
                    LANTERN_DEFAULT_RADIUS, WHITE, RED)
from entities.sprite import AnimatedSprite
from entities.skill  import Skill
from systems.inventory_manager import InventoryManager

class Player(AnimatedSprite):
    def __init__(self, x, y, name="Heroi", color=(70,130,210)):
        super().__init__(color, x, y, size=22)
        self.name          = name
        self.hp            = PLAYER_MAX_HP
        self.max_hp        = PLAYER_MAX_HP
        self.speed         = PLAYER_SPEED
        self.inventory     = InventoryManager()
        self.skills        = []
        self.skill_cd      = 0
        self.skill_max_cd  = PLAYER_SKILL_CD
        self.skill_damage  = SKILL_DAMAGE
        self.skill_radius  = SKILL_RADIUS   # upgradável no mercador
        self.lantern_radius= LANTERN_DEFAULT_RADIUS
        self.invincible    = 0
        self.damage_flash  = 0
        self.xp            = 0
        self.level         = 1
        self.xp_next       = 50
        self._world        = None   # injetado pelo game após setup

    def move(self, dx, dy, dt):
        if dx!=0 and dy!=0: dx*=0.7071; dy*=0.7071
        margin=30
        self.x = max(margin, min(MAP_W*TILE_SIZE-margin, self.x+dx*self.speed*dt))
        self.y = max(margin, min(MAP_H*TILE_SIZE-margin, self.y+dy*self.speed*dt))
        if dx!=0: self.facing = 1 if dx>0 else -1
        self.moving = (dx!=0 or dy!=0)

    def use_skill(self, wx, wy):
        if self.skill_cd > 0: return False
        dx = wx-self.x; dy = wy-self.y
        dist = math.hypot(dx,dy)
        if dist<1: return False
        self.skills.append(Skill(self.x, self.y, dx/dist, dy/dist,
                                 damage=self.skill_damage,
                                 world=self._world,
                                 radius=self.skill_radius))
        self.skill_cd = self.skill_max_cd
        return True

    def take_damage(self, amount):
        if self.invincible>0: return
        self.hp           = max(0, self.hp-amount)
        self.invincible   = PLAYER_INVINCIBLE
        self.damage_flash = 12

    def use_potion(self):
        if self.inventory.use_potion():
            self.hp = min(self.max_hp, self.hp+40); return True
        return False

    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_next:
            self.xp     -= self.xp_next
            self.level  += 1
            self.xp_next = int(self.xp_next*1.4)
            self.inventory.add("coin", 1)
            leveled = True
        return leveled

    def update(self, dt):
        super().update(dt)
        if self.skill_cd>0:    self.skill_cd-=1
        if self.invincible>0:  self.invincible-=1
        if self.damage_flash>0:self.damage_flash-=1
        self.skills = [p for p in self.skills if p.alive]
        for p in self.skills: p.update(dt)

    def draw(self, surface, cam_x, cam_y):
        sx, sy = int(self.x-cam_x), int(self.y-cam_y)
        c = RED if self.damage_flash>0 and self.damage_flash%4<2 else self.color
        self._draw_character(surface, sx, sy, c)
        font = pygame.font.SysFont("Arial",11)
        ns = font.render(self.name, True, WHITE)
        surface.blit(ns, (sx-ns.get_width()//2, sy-self.size-30))
        for p in self.skills: p.draw(surface, cam_x, cam_y)

    @property
    def is_dead(self): return self.hp<=0
