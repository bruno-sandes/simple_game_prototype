"""
entities/mob.py

MUDANCAS:
  - Boss muito mais forte: dash CD 200f (era 300), pulse CD 150f (era 220),
    summon CD 320f (era 480), andar 2+ dash range maior (+120px),
    andar 4+ triple-shot de pulso, escala hp/dmg mais agressiva
  - Mob count reduzido: FLOOR_MOB_BASE=6, STEP=3 (evita travamento)
  - Ghost bloqueado por TILE_STONE (zonas seguras)
  - Orc nao dropa chave (removido no config)
"""
import pygame, math, random
from config import (MOB_DEFS, MOB_AGGRO_RANGE, MOB_ATTACK_CD,
                    TILE_SIZE, TILE_GRASS, TILE_TREE, TILE_WATER,
                    BOSS_HP_BASE, BOSS_DMG_BASE, BOSS_SPEED_BASE,
                    GREEN, WHITE, RED, YELLOW, PURPLE)

_MOB_WALKABLE = {TILE_GRASS}
_GHOST_PASS   = {TILE_GRASS, TILE_TREE, TILE_WATER}

def _tile(world, px, py):
    if not world: return TILE_GRASS
    tx,ty=int(px//TILE_SIZE),int(py//TILE_SIZE)
    if 0<=ty<len(world.tiles) and 0<=tx<len(world.tiles[0]):
        return world.tiles[ty][tx]
    return -1

def _mob_ok(w,px,py):   return _tile(w,px,py) in _MOB_WALKABLE
def _ghost_ok(w,px,py): return _tile(w,px,py) in _GHOST_PASS


class Mob:
    HITBOX=12
    def __init__(self,x,y,monster_type="slime",dmg_mult=1.0,player_level=1,world=None):
        cfg=MOB_DEFS.get(monster_type,MOB_DEFS["slime"])
        lm=1.0+0.10*max(0,player_level-1)
        self.x,self.y=float(x),float(y)
        self.color=cfg["color"]; self.size=cfg["size"]; self.monster_type=monster_type
        self.hp=int(cfg["hp"]*lm); self.max_hp=self.hp
        self.speed=cfg["speed"]; self.base_speed=cfg["speed"]
        self.damage=int(cfg["dmg"]*dmg_mult*lm); self.base_damage=self.damage
        self.xp_reward=int(cfg["xp"]*(1+0.15*max(0,player_level-1)))
        self.dead=False; self.attack_cd=0; self.damage_flash=0
        self.aggro_range=MOB_AGGRO_RANGE; self.facing=1; self.moving=False
        self._anim_t=0.0; self._world=world
        self._is_ghost=(monster_type=="ghost"); self._intang=90 if self._is_ghost else 0
        self._charging=False; self._charge_t=0
        self._acd_base=MOB_ATTACK_CD//2 if monster_type=="goblin" else MOB_ATTACK_CD
        self._retreat_t=0   # timer de recuo quando player na safe zone

    def update(self,dt,player,player_in_safe=False):
        if self.dead: return
        self._anim_t+=dt

        # Dispersão quando player entra na zona segura
        if player_in_safe:
            self.moving=False
            dx=self.x-player.x; dy=self.y-player.y; dist=math.hypot(dx,dy)
            if dist>0 and dist<250:
                self.x+=(dx/dist)*self.speed*dt*0.35
                self.y+=(dy/dist)*self.speed*dt*0.35
            if self.attack_cd>0: self.attack_cd-=1
            if self.damage_flash>0: self.damage_flash-=1
            return

        if self._intang>0:
            self._intang-=1; self._move(player,dt,True); return
        dx=player.x-self.x; dy=player.y-self.y; dist=math.hypot(dx,dy)
        if self.monster_type=="orc":
            if dist<110 and not self._charging and self._charge_t<=0:
                self._charging=True; self._charge_t=40
                self.speed=self.base_speed*2.8; self.damage=int(self.base_damage*1.5)
            if self._charging:
                self._charge_t-=1
                if self._charge_t<=0:
                    self._charging=False; self.speed=self.base_speed; self.damage=self.base_damage
        self._move(player,dt,self._is_ghost)
        if self.attack_cd>0: self.attack_cd-=1
        if dist<32 and self.attack_cd<=0:
            player.take_damage(self.damage); self.attack_cd=self._acd_base
        if self.damage_flash>0: self.damage_flash-=1

    def _move(self,player,dt,ghost=False):
        dx=player.x-self.x; dy=player.y-self.y; dist=math.hypot(dx,dy)
        if dist<1 or dist>=self.aggro_range: self.moving=False; return
        nx,ny=dx/dist,dy/dist; sx,sy=nx*self.speed*dt,ny*self.speed*dt; h=self.HITBOX
        ck=_ghost_ok if ghost else _mob_ok
        if ck(self._world,self.x+sx+h*(1 if sx>0 else -1),self.y): self.x+=sx
        if ck(self._world,self.x,self.y+sy+h*(1 if sy>0 else -1)): self.y+=sy
        self.facing=1 if dx>0 else -1; self.moving=True

    def take_damage(self,amount):
        if self.dead: return
        if self._intang>0: return
        if self.monster_type=="goblin" and random.random()<0.20: return
        self.hp-=amount; self.damage_flash=8
        if self.hp<=0: self.hp=0; self.dead=True

    def draw(self,surface,cam_x,cam_y):
        if self.dead: return
        sx,sy=int(self.x-cam_x),int(self.y-cam_y)
        c=WHITE if self.damage_flash>0 and self.damage_flash%4<2 else self.color
        if self._charging: c=(min(255,c[0]+80),max(0,c[1]-40),max(0,c[2]-40))
        s=self.size; lc=tuple(max(0,x-40) for x in c)
        sw=int(math.sin(self._anim_t*8)*6) if self.moving else 0
        pygame.draw.rect(surface,lc,(sx-s//3,sy+s//2,s//3,10+sw),border_radius=2)
        pygame.draw.rect(surface,lc,(sx,sy+s//2,s//3,10-sw),border_radius=2)
        pygame.draw.rect(surface,c,(sx-s//2,sy-s//2,s,s),border_radius=4)
        pygame.draw.circle(surface,c,(sx,sy-s),s//2)
        pygame.draw.circle(surface,WHITE,(sx+4*self.facing,sy-s-2),3)
        pygame.draw.circle(surface,(0,0,0),(sx+5*self.facing,sy-s-2),1)
        bw=38; bx,by=sx-bw//2,sy-s-22
        pygame.draw.rect(surface,(100,0,0),(bx,by,bw,5),border_radius=2)
        pygame.draw.rect(surface,GREEN,(bx,by,max(0,int(bw*self.hp/self.max_hp)),5),border_radius=2)
        font=pygame.font.SysFont("Arial",10)
        lbl=self.monster_type.upper()+(" !" if self._charging else "")
        ts=font.render(lbl,True,self.color); surface.blit(ts,(sx-ts.get_width()//2,by-12))

    def get_rect(self): return pygame.Rect(self.x-16,self.y-16,32,32)


class Boss:
    """
    Boss escalado por andar com habilidades progressivas:
      Andar 1: movimento + ataque + pulso de área
      Andar 2: + DASH (CD 200f, range +120px)
      Andar 3: + INVOCAÇÃO de minions (CD 320f)
      Andar 4: + PULSO DUPLO (2 pulsos simultâneos, raio maior)
      Andar 5+: + velocidade extra, dano adicional
    """
    HITBOX=22
    def __init__(self,x,y,floor=1,world=None):
        fm=1.0+0.55*(floor-1)           # escala mais agressiva (+55% por andar)
        self.x,self.y=float(x),float(y)
        self.hp=int(BOSS_HP_BASE*fm); self.max_hp=self.hp
        self.speed=int(BOSS_SPEED_BASE+floor*8)   # mais rápido
        self.damage=int(BOSS_DMG_BASE*fm)
        self.dead=False; self.attack_cd=0; self.damage_flash=0
        self._anim_t=0.0; self._world=world
        self.aggro_range=9999; self.facing=1; self.moving=False
        self.monster_type="boss"; self.xp_reward=200+floor*80

        # Habilidades por andar
        self._has_dash   = floor>=2
        self._dash_cd    = 0
        self._dash_dist  = 80 + floor*20   # range do dash cresce

        self._has_summon = floor>=3
        self._summon_cd  = 0

        self._pulse_cd   = 150   # mais frequente (era 220)
        self._pulse_range= 110 + floor*15
        self._double_pulse = floor>=4   # pulso duplo andar 4+

        # Andar 5+: bônus extra
        if floor >= 5:
            self.speed   += 15
            self.damage  += 8

    def update(self,dt,player,spawn_mob_cb=None,player_in_safe=False):
        if self.dead: return
        self._anim_t+=dt
        # Boss nao respeita safe zone — continua se movendo sempre
        dx=player.x-self.x; dy=player.y-self.y; dist=math.hypot(dx,dy)

        # Dash — mais frequente e maior range
        if self._has_dash:
            if self._dash_cd>0: self._dash_cd-=1
            elif dist>50:
                nx,ny=dx/dist,dy/dist
                self.x+=nx*self._dash_dist; self.y+=ny*self._dash_dist
                self._dash_cd=200   # era 300

        # Movimento direto
        if dist>1:
            nx,ny=dx/dist,dy/dist; self.x+=nx*self.speed*dt; self.y+=ny*self.speed*dt
            self.facing=1 if dx>0 else -1; self.moving=True

        if self.attack_cd>0: self.attack_cd-=1
        if dist<44 and self.attack_cd<=0:
            player.take_damage(self.damage); self.attack_cd=60

        # Pulso de área — mais frequente
        if self._pulse_cd>0: self._pulse_cd-=1
        if self._pulse_cd<=0:
            if dist<self._pulse_range:
                player.take_damage(int(self.damage*0.5))
            if self._double_pulse and dist<self._pulse_range*1.5:
                player.take_damage(int(self.damage*0.3))  # segundo pulso
            self._pulse_cd=150

        # Invocação de minions
        if self._has_summon and spawn_mob_cb:
            if self._summon_cd>0: self._summon_cd-=1
            if self._summon_cd<=0:
                spawn_mob_cb(self.x+90,self.y)
                spawn_mob_cb(self.x-90,self.y)
                if self._double_pulse:   # andar 4+ invoca 4 minions
                    spawn_mob_cb(self.x,self.y+90)
                    spawn_mob_cb(self.x,self.y-90)
                self._summon_cd=320   # era 480

        if self.damage_flash>0: self.damage_flash-=1

    def take_damage(self,amount):
        if self.dead: return
        self.hp-=amount; self.damage_flash=10
        if self.hp<=0: self.hp=0; self.dead=True

    def draw(self,surface,cam_x,cam_y):
        if self.dead: return
        sx,sy=int(self.x-cam_x),int(self.y-cam_y); t=self._anim_t
        c=WHITE if self.damage_flash>0 and self.damage_flash%4<2 else (160,40,200)
        s=32; lc=(100,20,140)
        sw=int(math.sin(t*6)*8) if self.moving else 0
        pygame.draw.rect(surface,lc,(sx-s//3,sy+s//2,s//3,14+sw),border_radius=3)
        pygame.draw.rect(surface,lc,(sx,sy+s//2,s//3,14-sw),border_radius=3)
        pygame.draw.rect(surface,c,(sx-s//2,sy-s//2,s,s),border_radius=6)
        pygame.draw.circle(surface,c,(sx,sy-s),s//2+2)
        for i in range(5):
            a=math.pi+i*(math.pi/4)
            pygame.draw.circle(surface,YELLOW,(sx+int(math.cos(a)*(s//2+6)),sy-s+int(math.sin(a)*(s//2+6))),4)
        pygame.draw.circle(surface,RED,(sx+6*self.facing,sy-s-3),5)
        pygame.draw.circle(surface,WHITE,(sx+6*self.facing,sy-s-3),2)
        bw=60; bx,by=sx-bw//2,sy-s-28
        pygame.draw.rect(surface,(80,0,0),(bx,by,bw,8),border_radius=3)
        pygame.draw.rect(surface,(200,50,200),(bx,by,max(0,int(bw*self.hp/self.max_hp)),8),border_radius=3)
        font=pygame.font.SysFont("Arial",12,bold=True)
        lbl=font.render("★ BOSS ★",True,YELLOW); surface.blit(lbl,(sx-lbl.get_width()//2,by-16))

    def get_rect(self): return pygame.Rect(self.x-22,self.y-22,44,44)
