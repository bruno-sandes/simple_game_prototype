"""
Class Player 

  - Movimento WASD (recebe dx/dy do estado de jogo)
  - Skill: disparo de projétil em direção ao mouse
  - Receber/tratar dano (com frames de invencibilidade)
  - Inventário de itens
  - Sistema de XP e níveis
  - Desenho com flash de dano
"""

import math
import pygame
from config import (
    PLAYER_SPEED, PLAYER_MAX_HP, PLAYER_SKILL_CD, PLAYER_INVINCIBLE,
    MAP_W, MAP_H, TILE_SIZE,
    WHITE, RED
)
from entities.sprite import AnimatedSprite
from entities.skill import Skill
from systems.inventory_manager import InventoryManager


class Player(AnimatedSprite):

    def __init__(self, x: float, y: float,
                 name: str = "Herói", color: tuple = (70, 130, 210)):
        super().__init__(color, x, y, size=22)
        self.name         = name
        self.hp           = PLAYER_MAX_HP
        self.max_hp       = PLAYER_MAX_HP
        self.speed        = PLAYER_SPEED
        self.inventory    = InventoryManager()          # list[Item]  (objetos coletados)
        self.skills       = []          # lista[Skill]
        self.skill_cd     = 0           # frames até próximo disparo
        self.skill_max_cd = PLAYER_SKILL_CD
        self.invincible   = 0           # frames de invencibilidade
        self.damage_flash = 0           # frames de flash vermelho
        self.xp           = 0
        self.level        = 1
        self.xp_next      = 60         # XP necessário para próximo nível

    #  Movimento                                                           #
    def move(self, dx: float, dy: float, dt: float) -> None:
        """
        dx, dy  ∈ {-1, 0, 1} — direção desejada.
        Normalizar antes de aplicar velocidade.
        Manter player ns limites do mapa.
        """
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        margin = 30
        self.x = max(margin,
                     min(MAP_W * TILE_SIZE - margin, self.x + dx * self.speed * dt))
        self.y = max(margin,
                     min(MAP_H * TILE_SIZE - margin, self.y + dy * self.speed * dt))

        if dx != 0:
            self.facing = 1 if dx > 0 else -1
        self.moving = (dx != 0 or dy != 0)

    # ------------------------------------------------------------------ #
    #  Skill                                                               #
    # ------------------------------------------------------------------ #
    def use_skill(self, world_mx: float, world_my: float) -> bool:
        """
        direção a (world_mx, world_my)
        retorna True se o disparo foi realizado
        """
        if self.skill_cd > 0:
            return False
        dx = world_mx - self.x
        dy = world_my - self.y
        dist = math.hypot(dx, dy)
        if dist < 1:
            return False
        self.skills.append(Skill(self.x, self.y, dx / dist, dy / dist))
        self.skill_cd = self.skill_max_cd
        return True

    # ------------------------------------------------------------------ #
    #  Dano                                                                #
    # ------------------------------------------------------------------ #
    def take_damage(self, amount: int) -> None:
        if self.invincible > 0:
            return
        self.hp           = max(0, self.hp - amount)
        self.invincible   = PLAYER_INVINCIBLE
        self.damage_flash = 12

    # ------------------------------------------------------------------ #
    #  Inventário                                                          #
    # ------------------------------------------------------------------ #
    def use_potion(self) -> bool:
        """
        FIX 2: delega para InventoryManager.use_potion() que opera no dict.
        Retorna True se a poção foi usada.
        """
        return self.inventory.use_potion()

    # ------------------------------------------------------------------ #
    #  XP / Nível                                                          #
    # ------------------------------------------------------------------ #
    def gain_xp(self, amount: int) -> bool:
        """Add XP - UP level. retorna True se subiu."""
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_next:
            self.xp     -= self.xp_next
            self.level  += 1
            self.max_hp += 20
            self.hp      = self.max_hp
            self.xp_next = int(self.xp_next * 1.5)
            leveled = True
        return leveled

    # ------------------------------------------------------------------ #
    #  Update                                                              #
    # ------------------------------------------------------------------ #
    def update(self, dt: float) -> None:
        super().update(dt)
        if self.skill_cd    > 0: self.skill_cd    -= 1
        if self.invincible  > 0: self.invincible  -= 1
        if self.damage_flash > 0: self.damage_flash -= 1

        # remove projéteis mortos
        self.skills = [p for p in self.skills if p.alive]
        for p in self.skills:
            p.update(dt)

    # ------------------------------------------------------------------ #
    #  Desenho                                                             #
    # ------------------------------------------------------------------ #
    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)

        # Flash vermelho quando recém danificado
        draw_color = (RED
                      if self.damage_flash > 0 and self.damage_flash % 4 < 2
                      else self.color)
        self._draw_character(surface, sx, sy, draw_color)

        # Nome sobre o personagem
        font = pygame.font.SysFont("Arial", 11)
        ns   = font.render(self.name, True, WHITE)
        surface.blit(ns, (sx - ns.get_width() // 2, sy - self.size - 30))

        # Projéteis
        for p in self.skills:
            p.draw(surface, cam_x, cam_y)

    @property
    def is_dead(self) -> bool:
        return self.hp <= 0