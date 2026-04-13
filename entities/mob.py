"""
entities/monster.py
===================
Classe Monster — inimigos que perseguem o jogador.

Tipos disponíveis (definidos em config.MONSTER_DEFS):
  slime, goblin, ghost, orc

IA simples: se dentro do aggro_range, move-se em linha reta
ao jogador e ataca ao encostar. Respeita cooldown de ataque.
"""

import pygame
from config import (
    MONSTER_DEFS, MONSTER_AGGRO_RANGE, MONSTER_ATTACK_CD,
    GREEN, RED, WHITE
)
from entities.base import AnimatedSprite
import math


class Monster(AnimatedSprite):

    def __init__(self, x: float, y: float, monster_type: str = "slime"):
        cfg = MONSTER_DEFS.get(monster_type, MONSTER_DEFS["slime"])
        super().__init__(cfg["color"], x, y, size=cfg["size"])
        self.monster_type = monster_type
        self.hp           = cfg["hp"]
        self.max_hp       = cfg["hp"]
        self.speed        = cfg["speed"]
        self.damage       = cfg["dmg"]
        self.xp_reward    = cfg["xp"]
        self.dead         = False
        self.attack_cd    = 0
        self.damage_flash = 0
        self.aggro_range  = MONSTER_AGGRO_RANGE

    # ------------------------------------------------------------------ #
    #  IA de perseguição                                                   #
    # ------------------------------------------------------------------ #
    def update(self, dt: float, player) -> None:
        """
        Recebe o Player para calcular distância e direção.
        Não importa Player diretamente para evitar ciclo de importação;
        usa duck-typing (qualquer objeto com .x, .y, take_damage).
        """
        if self.dead:
            return
        super().update(dt)

        dx   = player.x - self.x
        dy   = player.y - self.y
        dist = math.hypot(dx, dy)

        # Perseguição
        if 1 < dist < self.aggro_range:
            nx, ny = dx / dist, dy / dist
            self.x     += nx * self.speed * dt
            self.y     += ny * self.speed * dt
            self.facing = 1 if dx > 0 else -1
            self.moving = True
        else:
            self.moving = False

        # Cooldown de ataque
        if self.attack_cd > 0:
            self.attack_cd -= 1

        # Ataque ao encostar no jogador
        if dist < 32 and self.attack_cd <= 0:
            player.take_damage(self.damage)
            self.attack_cd = MONSTER_ATTACK_CD

        # Flash de dano
        if self.damage_flash > 0:
            self.damage_flash -= 1

    # ------------------------------------------------------------------ #
    #  Receber dano                                                        #
    # ------------------------------------------------------------------ #
    def take_damage(self, amount: int) -> None:
        if self.dead:
            return
        self.hp           -= amount
        self.damage_flash  = 8
        if self.hp <= 0:
            self.hp   = 0
            self.dead = True

    # ------------------------------------------------------------------ #
    #  Desenho                                                             #
    # ------------------------------------------------------------------ #
    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        if self.dead:
            return
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)

        # Flash branco ao tomar dano
        color = (WHITE
                 if self.damage_flash > 0 and self.damage_flash % 4 < 2
                 else self.color)
        self._draw_character(surface, sx, sy, color)

        # ── Barra de vida ──────────────────────────────────────────────
        bw = 36
        bx = sx - bw // 2
        by = sy - self.size - 24
        pygame.draw.rect(surface, (100, 0, 0), (bx, by, bw, 5), border_radius=2)
        hp_w = max(0, int(bw * self.hp / self.max_hp))
        pygame.draw.rect(surface, GREEN, (bx, by, hp_w, 5), border_radius=2)

        # ── Rótulo do tipo ────────────────────────────────────────────
        font = pygame.font.SysFont("Arial", 10)
        ts   = font.render(self.monster_type.upper(), True, self.color)
        surface.blit(ts, (sx - ts.get_width() // 2, by - 12))