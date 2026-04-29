"""
<<<<<<< Updated upstream
entities/monster.py
===================
Classe Monster — inimigos que perseguem o jogador.

Tipos disponíveis (definidos em config.MONSTER_DEFS):
  slime, goblin, ghost, orc

IA simples: se dentro do aggro_range, move-se em linha reta
ao jogador e ataca ao encostar. Respeita cooldown de ataque.
=======
entities/mob.py

MUDANCAS vs versão anterior:
  - orc charge: dano 1.5x em vez de 2x (era one-shot)
  - Classe Boss adicionada: HP/dano/velocidade escalados por andar,
    drop garante chave ao morrer
  - player_level esperado pelo game.py para escalar stats
>>>>>>> Stashed changes
"""

import pygame
import math
import random
from config import (
<<<<<<< Updated upstream
    MONSTER_DEFS, MONSTER_AGGRO_RANGE, MONSTER_ATTACK_CD,
    GREEN, RED, WHITE
)
from entities.base import AnimatedSprite
import math


class Monster(AnimatedSprite):

    def __init__(self, x: float, y: float, monster_type: str = "slime"):
        cfg = MONSTER_DEFS.get(monster_type, MONSTER_DEFS["slime"])
        super().__init__(cfg["color"], x, y, size=cfg["size"])
=======
    MOB_DEFS, MOB_AGGRO_RANGE, MOB_ATTACK_CD,
    TILE_SIZE, TILE_GRASS,
    BOSS_HP_BASE, BOSS_DMG_BASE, BOSS_SPEED_BASE,
    GREEN, WHITE, RED, YELLOW, PURPLE,
)

_MOB_WALKABLE = {TILE_GRASS}


def _tile_at(world, px: float, py: float) -> int:
    if world is None:
        return TILE_GRASS
    tx, ty = int(px // TILE_SIZE), int(py // TILE_SIZE)
    if 0 <= ty < len(world.tiles) and 0 <= tx < len(world.tiles[0]):
        return world.tiles[ty][tx]
    return -1


def _is_mob_walkable(world, px, py) -> bool:
    return _tile_at(world, px, py) in _MOB_WALKABLE


# ══════════════════════════════════════════════════════
class Mob:

    HITBOX = 12

    def __init__(self, x: float, y: float,
                 monster_type: str = "slime",
                 dmg_mult: float = 1.0,
                 player_level: int = 1,
                 world=None):
        cfg = MOB_DEFS.get(monster_type, MOB_DEFS["slime"])

        level_mult = 1.0 + 0.08 * max(0, player_level - 1)
        total_mult = dmg_mult * level_mult

        self.x            = float(x)
        self.y            = float(y)
        self.color        = cfg["color"]
        self.size         = cfg["size"]
>>>>>>> Stashed changes
        self.monster_type = monster_type
        self.hp           = int(cfg["hp"] * level_mult)
        self.max_hp       = self.hp
        self.speed        = cfg["speed"]
        self.base_speed   = cfg["speed"]
        self.damage       = int(cfg["dmg"] * total_mult)
        self.base_damage  = self.damage
        self.xp_reward    = cfg["xp"]
        self.dead         = False
        self.attack_cd    = 0
        self.damage_flash = 0
<<<<<<< Updated upstream
        self.aggro_range  = MONSTER_AGGRO_RANGE
=======
        self.aggro_range  = MOB_AGGRO_RANGE
        self.facing       = 1
        self.moving       = False
        self._anim_t      = 0.0
        self._world       = world

        self._phase_walls  = (monster_type == "ghost")
        self._intangible_t = 90 if monster_type == "ghost" else 0
        self._charging     = False
        self._charge_t     = 0
        self._atk_cd_base  = MOB_ATTACK_CD // 2 if monster_type == "goblin" else MOB_ATTACK_CD
>>>>>>> Stashed changes

    def update(self, dt: float, player) -> None:
        if self.dead:
            return
        self._anim_t += dt

        if self._intangible_t > 0:
            self._intangible_t -= 1
            self._move_toward(player, dt, ignore_walls=True)
            return

        dx   = player.x - self.x
        dy   = player.y - self.y
        dist = math.hypot(dx, dy)

        # Orc charge: 1.5x dano (não one-shot)
        if self.monster_type == "orc":
            if dist < 110 and not self._charging and self._charge_t <= 0:
                self._charging = True
                self._charge_t = 40
                self.speed     = self.base_speed * 2
                self.damage    = int(self.base_damage * 1.5)   # era 2x, agora 1.5x
            if self._charging:
                self._charge_t -= 1
                if self._charge_t <= 0:
                    self._charging = False
                    self.speed  = self.base_speed
                    self.damage = self.base_damage

        self._move_toward(player, dt, ignore_walls=self._phase_walls)

        if self.attack_cd > 0:
            self.attack_cd -= 1

        if dist < 32 and self.attack_cd <= 0:
            player.take_damage(self.damage)
<<<<<<< Updated upstream
            self.attack_cd = MONSTER_ATTACK_CD
=======
            self.attack_cd = self._atk_cd_base
>>>>>>> Stashed changes

        if self.damage_flash > 0:
            self.damage_flash -= 1

    def _move_toward(self, player, dt: float, ignore_walls: bool = False) -> None:
        dx   = player.x - self.x
        dy   = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 1 or dist >= self.aggro_range:
            self.moving = False
            return

        nx, ny = dx / dist, dy / dist
        sx, sy = nx * self.speed * dt, ny * self.speed * dt
        h = self.HITBOX

        if ignore_walls:
            self.x += sx
            self.y += sy
        else:
            if _is_mob_walkable(self._world,
                                self.x + sx + h * (1 if sx > 0 else -1),
                                self.y):
                self.x += sx
            if _is_mob_walkable(self._world,
                                self.x,
                                self.y + sy + h * (1 if sy > 0 else -1)):
                self.y += sy

        self.facing = 1 if dx > 0 else -1
        self.moving = True

    def take_damage(self, amount: int) -> None:
        if self.dead:
            return
        if self._intangible_t > 0:
            return
        if self.monster_type == "goblin" and random.random() < 0.20:
            return   # goblin esquiva 20%
        self.hp           -= amount
        self.damage_flash  = 8
        if self.hp <= 0:
            self.hp   = 0
            self.dead = True

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        if self.dead:
            return
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)

        color = WHITE if (self.damage_flash > 0 and self.damage_flash % 4 < 2) else self.color
        if self._charging:
            color = (min(255, color[0] + 80), max(0, color[1] - 40), max(0, color[2] - 40))
        s = self.size

        leg_c = tuple(max(0, c - 40) for c in color)
        swing = int(math.sin(self._anim_t * 8) * 6) if self.moving else 0
        pygame.draw.rect(surface, leg_c,
            (sx - s // 3, sy + s // 2, s // 3, 10 + swing), border_radius=2)
        pygame.draw.rect(surface, leg_c,
            (sx,           sy + s // 2, s // 3, 10 - swing), border_radius=2)
        pygame.draw.rect(surface, color,
            (sx - s // 2, sy - s // 2, s, s), border_radius=4)
        pygame.draw.circle(surface, color, (sx, sy - s), s // 2)
        pygame.draw.circle(surface, WHITE, (sx + 4 * self.facing, sy - s - 2), 3)
        pygame.draw.circle(surface, (0, 0, 0), (sx + 5 * self.facing, sy - s - 2), 1)

        bw = 38
        bx, by = sx - bw // 2, sy - s - 22
        pygame.draw.rect(surface, (100, 0, 0), (bx, by, bw, 5), border_radius=2)
        hp_w = max(0, int(bw * self.hp / self.max_hp))
        pygame.draw.rect(surface, GREEN, (bx, by, hp_w, 5), border_radius=2)

        font = pygame.font.SysFont("Arial", 10)
        lbl  = self.monster_type.upper() + (" !" if self._charging else "")
        ts   = font.render(lbl, True, self.color)
        surface.blit(ts, (sx - ts.get_width() // 2, by - 12))

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - 16, self.y - 16, 32, 32)


# ══════════════════════════════════════════════════════
# BOSS — nasce em sala reservada, dropa a chave garantida
# ══════════════════════════════════════════════════════
class Boss:
    """
    Boss que guarda a chave do andar.
    Spawna apenas quando player.level >= BOSS_UNLOCK_LEVEL.
    HP/dano escalam por andar (floor).
    Comportamento: perseguição direta + ataque em área (pulso) a cada 4s.
    """

    HITBOX = 22

    def __init__(self, x: float, y: float, floor: int = 1, world=None):
        floor_mult = 1.0 + 0.4 * (floor - 1)
        self.x           = float(x)
        self.y           = float(y)
        self.hp          = int(BOSS_HP_BASE * floor_mult)
        self.max_hp      = self.hp
        self.speed       = int(BOSS_SPEED_BASE + floor * 5)
        self.damage      = int(BOSS_DMG_BASE * floor_mult)
        self.dead        = False
        self.attack_cd   = 0
        self.damage_flash= 0
        self._anim_t     = 0.0
        self._pulse_cd   = 240   # 4s a 60fps
        self._world      = world
        self.aggro_range = 9999  # sempre persegue
        self.facing      = 1
        self.moving      = False
        self.monster_type= "boss"
        self.xp_reward   = 100 + floor * 40

    def update(self, dt: float, player) -> None:
        if self.dead:
            return
        self._anim_t += dt

        dx   = player.x - self.x
        dy   = player.y - self.y
        dist = math.hypot(dx, dy)

        # Movimento direto (boss ignora paredes menores)
        if dist > 1:
            nx, ny = dx / dist, dy / dist
            h = self.HITBOX
            sx_step = nx * self.speed * dt
            sy_step = ny * self.speed * dt
            if _is_mob_walkable(self._world,
                                self.x + sx_step + h * (1 if sx_step > 0 else -1),
                                self.y):
                self.x += sx_step
            else:
                self.x += sx_step  # boss força passagem se bloqueado
            if _is_mob_walkable(self._world,
                                self.x,
                                self.y + sy_step + h * (1 if sy_step > 0 else -1)):
                self.y += sy_step
            else:
                self.y += sy_step
            self.facing = 1 if dx > 0 else -1
            self.moving = True

        # Ataque direto
        if self.attack_cd > 0:
            self.attack_cd -= 1
        if dist < 40 and self.attack_cd <= 0:
            player.take_damage(self.damage)
            self.attack_cd = 70

        # Pulso de área a cada 4s
        if self._pulse_cd > 0:
            self._pulse_cd -= 1
        if self._pulse_cd <= 0:
            if dist < 120:
                player.take_damage(int(self.damage * 0.6))
            self._pulse_cd = 240

        if self.damage_flash > 0:
            self.damage_flash -= 1

    def take_damage(self, amount: int) -> None:
        if self.dead:
            return
        self.hp          -= amount
        self.damage_flash = 10
        if self.hp <= 0:
            self.hp   = 0
            self.dead = True

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        if self.dead:
            return
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        t  = self._anim_t

        color = WHITE if (self.damage_flash > 0 and self.damage_flash % 4 < 2) else (160, 40, 200)
        s = 32

        # Corpo maior e mais detalhado
        leg_c = (100, 20, 140)
        swing = int(math.sin(t * 6) * 8) if self.moving else 0
        pygame.draw.rect(surface, leg_c,
            (sx - s // 3, sy + s // 2, s // 3, 14 + swing), border_radius=3)
        pygame.draw.rect(surface, leg_c,
            (sx,           sy + s // 2, s // 3, 14 - swing), border_radius=3)
        pygame.draw.rect(surface, color,
            (sx - s // 2, sy - s // 2, s, s), border_radius=6)
        pygame.draw.circle(surface, color, (sx, sy - s), s // 2 + 2)

        # Coroa de picos
        for i in range(5):
            angle = math.pi + i * (math.pi / 4)
            px_ = sx + int(math.cos(angle) * (s // 2 + 6))
            py_ = (sy - s) + int(math.sin(angle) * (s // 2 + 6))
            pygame.draw.circle(surface, YELLOW, (px_, py_), 4)

        # Olhos brilhantes
        pygame.draw.circle(surface, RED, (sx + 6 * self.facing, sy - s - 3), 5)
        pygame.draw.circle(surface, WHITE, (sx + 6 * self.facing, sy - s - 3), 2)

        # Barra de HP maior
        bw = 60
        bx, by = sx - bw // 2, sy - s - 28
        pygame.draw.rect(surface, (80, 0, 0), (bx, by, bw, 8), border_radius=3)
        hp_w = max(0, int(bw * self.hp / self.max_hp))
        pygame.draw.rect(surface, (200, 50, 200), (bx, by, hp_w, 8), border_radius=3)

        font = pygame.font.SysFont("Arial", 12, bold=True)
        lbl  = font.render("★ BOSS ★", True, YELLOW)
        surface.blit(lbl, (sx - lbl.get_width() // 2, by - 16))

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - 22, self.y - 22, 44, 44)