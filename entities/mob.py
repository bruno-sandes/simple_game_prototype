"""
entities/mob.py
Orc aparece somente após nível 2 do player.
Comportamentos únicos por tipo. Boss separado.
"""
import pygame, math, random
from config import (MOB_DEFS, MOB_AGGRO_RANGE, MOB_ATTACK_CD,
                    TILE_SIZE, TILE_GRASS,
                    BOSS_HP_BASE, BOSS_DMG_BASE, BOSS_SPEED_BASE,
                    GREEN, WHITE, RED, YELLOW, PURPLE)

_MW = {TILE_GRASS}

def _tile(world, px, py):
    if not world: return TILE_GRASS
    tx,ty=int(px//TILE_SIZE),int(py//TILE_SIZE)
    if 0<=ty<len(world.tiles) and 0<=tx<len(world.tiles[0]):
        return world.tiles[ty][tx]
    return -1

def _ok(world,px,py): return _tile(world,px,py) in _MW

class Mob:
    HITBOX=12
    def __init__(self,x,y,monster_type="slime",dmg_mult=1.0,player_level=1,world=None):
        cfg=MOB_DEFS.get(monster_type,MOB_DEFS["slime"])
        lm=1.0+0.10*max(0,player_level-1)
        self.x,self.y=float(x),float(y)
        self.color=cfg["color"]; self.size=cfg["size"]
        self.monster_type=monster_type
        self.hp=int(cfg["hp"]*lm); self.max_hp=self.hp
        self.speed=cfg["speed"]; self.base_speed=cfg["speed"]
        self.damage=int(cfg["dmg"]*dmg_mult*lm); self.base_damage=self.damage
        self.xp_reward=int(cfg["xp"]*(1+0.15*max(0,player_level-1)))
        self.dead=False; self.attack_cd=0; self.damage_flash=0
        self.aggro_range=MOB_AGGRO_RANGE; self.facing=1; self.moving=False
        self._anim_t=0.0; self._world=world
        self._phase=monster_type=="ghost"
        self._intang=90 if monster_type=="ghost" else 0
        self._charging=False; self._charge_t=0
        self._acd_base=MOB_ATTACK_CD//2 if monster_type=="goblin" else MOB_ATTACK_CD

    def update(self,dt,player):
        if self.dead: return
        self._anim_t+=dt
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
        self._move(player,dt,self._phase)
        if self.attack_cd>0: self.attack_cd-=1
        if dist<32 and self.attack_cd<=0:
            player.take_damage(self.damage); self.attack_cd=self._acd_base
        if self.damage_flash>0: self.damage_flash-=1

    def _move(self,player,dt,ignore):
        dx=player.x-self.x; dy=player.y-self.y; dist=math.hypot(dx,dy)
        if dist<1 or dist>=self.aggro_range: self.moving=False; return
        nx,ny=dx/dist,dy/dist; sx=nx*self.speed*dt; sy=ny*self.speed*dt; h=self.HITBOX
        if ignore: self.x+=sx; self.y+=sy
        else:
            if _ok(self._world,self.x+sx+h*(1 if sx>0 else -1),self.y): self.x+=sx
            if _ok(self._world,self.x,self.y+sy+h*(1 if sy>0 else -1)): self.y+=sy
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
    HITBOX=22
    def __init__(self,x,y,floor=1,world=None):
        fm=1.0+0.45*(floor-1)
        self.x,self.y=float(x),float(y)
        self.hp=int(BOSS_HP_BASE*fm); self.max_hp=self.hp
        self.speed=int(BOSS_SPEED_BASE+floor*6)
        self.damage=int(BOSS_DMG_BASE*fm)
        self.dead=False; self.attack_cd=0; self.damage_flash=0
        self._anim_t=0.0; self._pulse_cd=220; self._world=world
        self.aggro_range=9999; self.facing=1; self.moving=False
        self.monster_type="boss"
        self.xp_reward=150+floor*60
        # Habilidades especiais por andar
        self._has_dash   = floor>=2   # dash rápido a cada 5s
        self._dash_cd    = 0
        self._has_summon = floor>=3   # invoca slime a cada 8s
        self._summon_cd  = 0
        self._summoned   = []         # lista de mobs invocados

    def update(self,dt,player,spawn_mob_cb=None):
        if self.dead: return
        self._anim_t+=dt
        dx=player.x-self.x; dy=player.y-self.y; dist=math.hypot(dx,dy)
        # Dash (andar 2+): teleporta 80px na direção do player a cada 5s
        if self._has_dash:
            if self._dash_cd>0: self._dash_cd-=1
            elif dist>60:
                nx,ny=dx/dist,dy/dist
                self.x+=nx*80; self.y+=ny*80
                self._dash_cd=300
        # Movimento
        if dist>1:
            nx,ny=dx/dist,dy/dist; h=self.HITBOX
            sx,sy=nx*self.speed*dt,ny*self.speed*dt
            self.x+=sx; self.y+=sy
            self.facing=1 if dx>0 else -1; self.moving=True
        if self.attack_cd>0: self.attack_cd-=1
        if dist<44 and self.attack_cd<=0:
            player.take_damage(self.damage); self.attack_cd=65
        # Pulso de área (dano)
        if self._pulse_cd>0: self._pulse_cd-=1
        if self._pulse_cd<=0:
            if dist<130: player.take_damage(int(self.damage*0.55))
            self._pulse_cd=220
        # Invocação (andar 3+)
        if self._has_summon and spawn_mob_cb:
            if self._summon_cd>0: self._summon_cd-=1
            if self._summon_cd<=0:
                spawn_mob_cb(self.x+80,self.y)
                spawn_mob_cb(self.x-80,self.y)
                self._summon_cd=480
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
        lbl=font.render("★ BOSS ★",True,YELLOW)
        surface.blit(lbl,(sx-lbl.get_width()//2,by-16))

    def get_rect(self): return pygame.Rect(self.x-22,self.y-22,44,44)
