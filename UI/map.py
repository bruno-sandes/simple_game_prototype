"""
ui/map.py — minimap com tiles visíveis, fog de entidades, boss indicator, quickbar.
"""
import math, pygame
from config import (MAP_W, MAP_H, TILE_SIZE, WHITE, GRAY, YELLOW, RED,
                    LIGHT_GRAY, DARK_GRAY,
                    TILE_GRASS, TILE_WATER, TILE_TREE, TILE_STONE,
                    TILE_FLOOR, TILE_DOOR,
                    SCREEN_W, SCREEN_H)

MINIMAP_REVEAL_MULT = 2.5

_TILE_MM = {
    TILE_GRASS: (75,  145, 65),
    TILE_WATER: (45,  95,  180),
    TILE_TREE:  (30,  100, 30),
    TILE_STONE: (90,  80,  70),
    TILE_FLOOR: (170, 150, 110),
    TILE_DOOR:  (220, 180, 50),
}

class MiniMap:
    def __init__(self, x, y, w, h):
        self.x=x; self.y=y; self.w=w; self.h=h
        self._tile_surf=None; self._tile_seed=None

    def _build_tile_surf(self, world):
        surf=pygame.Surface((self.w,self.h)); surf.fill((20,20,20))
        sx=self.w/MAP_W; sy=self.h/MAP_H
        for ty in range(MAP_H):
            for tx in range(MAP_W):
                t=world.tiles[ty][tx]; clr=_TILE_MM.get(t,(50,50,50))
                pygame.draw.rect(surf,clr,(int(tx*sx),int(ty*sy),max(1,int(sx)),max(1,int(sy))))
        return surf

    def draw(self, surface, world, player, npcs, monsters, items, boss=None):
        from ui.fonts import fonts
        wid=id(world)
        if self._tile_seed!=wid:
            self._tile_surf=self._build_tile_surf(world); self._tile_seed=wid

        mm_surf=self._tile_surf.copy(); mm_surf.set_alpha(210)
        surface.blit(mm_surf,(self.x,self.y))
        pygame.draw.rect(surface,GRAY,(self.x,self.y,self.w,self.h),1)

        sx=self.w/(MAP_W*TILE_SIZE); sy=self.h/(MAP_H*TILE_SIZE)
        reveal=player.lantern_radius*MINIMAP_REVEAL_MULT

        def mm(wx,wy): return (int(self.x+wx*sx),int(self.y+wy*sy))
        def vis(ex,ey): return math.hypot(ex-player.x,ey-player.y)<=reveal

        for item in items:
            if not item.collected and vis(item.x,item.y):
                pygame.draw.circle(surface,item.color,mm(item.x,item.y),2)

        for npc in npcs:
            pygame.draw.circle(surface,YELLOW,mm(npc.x,npc.y),3)

        for m in monsters:
            if not m.dead and vis(m.x,m.y):
                pygame.draw.circle(surface,RED,mm(m.x,m.y),3)

        if boss and not boss.dead:
            bx,by=mm(boss.x,boss.y)
            pygame.draw.circle(surface,(180,40,220),(bx,by),5)
            pygame.draw.circle(surface,WHITE,(bx,by),5,1)
            bs=fonts.xxs.render("★",True,(255,80,255))
            surface.blit(bs,(bx-bs.get_width()//2,by-bs.get_height()-3))

        px,py=mm(player.x,player.y)
        pygame.draw.circle(surface,player.color,(px,py),5)
        pygame.draw.circle(surface,WHITE,(px,py),5,1)

        title=fonts.xxs.render("MAPA",True,LIGHT_GRAY)
        surface.blit(title,(self.x+self.w//2-title.get_width()//2,self.y+2))

        self._draw_quickbar(surface,player,fonts)

    def _draw_quickbar(self, surface, player, fonts):
        inv=player.inventory
        coins=inv.count("coin"); pots=inv.count("hp_potion"); has_k=inv.has("key")
        qy=self.y+self.h+6; qx=self.x
        bars=[ ((255,220,0), f"$$ {coins}", "Moedas"),
               ((255,80,80),  f"HP {pots}",  "Pocoes") ]
        if has_k: bars.append(((255,255,50),"KEY ★","Chave"))
        for i,(clr,txt,_) in enumerate(bars):
            by=qy+i*18
            bg=pygame.Surface((self.w,16),pygame.SRCALPHA); bg.fill((10,10,20,180))
            surface.blit(bg,(qx,by))
            pygame.draw.circle(surface,clr,(qx+7,by+8),5)
            s=fonts.xxs.render(txt,True,clr); surface.blit(s,(qx+15,by+2))
