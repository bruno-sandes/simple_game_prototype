"""
world/tilemap.py
Mapa 50x50 com zona segura menor (16x10), bordas circulares,
clusters de árvores/pedra para paisagem, sem labirintos.
"""
import random, math, pygame
from config import (MAP_W,MAP_H,TILE_SIZE,
    TILE_GRASS,TILE_WATER,TILE_TREE,TILE_STONE,TILE_FLOOR,TILE_DOOR,
    TILE_COLORS,BROWN,SCREEN_W,SCREEN_H)

_SZ_W = 16   # zona segura menor (era 22)
_SZ_H = 10   # era 14

class World:
    def __init__(self, seed=42):
        self._rng       = random.Random(seed)
        self.tiles      = []
        self._door_anim = 0.0
        self.sz_x = MAP_W//2 - _SZ_W//2
        self.sz_y = MAP_H//2 - _SZ_H//2
        self.door_tx = MAP_W//2
        self.door_ty = self.sz_y + _SZ_H - 1
        self._generate()

    def _generate(self):
        rng = self._rng
        # Base: tudo grama
        self.tiles = [[TILE_GRASS]*MAP_W for _ in range(MAP_H)]

        # ── Borda CIRCULAR (sem labirinto de pedras) ─────────────────
        cx, cy = MAP_W/2, MAP_H/2
        # Raio interno de grama: 23 tiles. Fora disso → pedra/água de borda
        r_inner = 22
        for y in range(MAP_H):
            for x in range(MAP_W):
                d = math.hypot(x-cx, y-cy)
                if d >= r_inner:
                    self.tiles[y][x] = TILE_STONE

        # ── Margem de proteção da zona segura ─────────────────────────
        margin = 3
        sx1,sx2 = self.sz_x-margin, self.sz_x+_SZ_W+margin
        sy1,sy2 = self.sz_y-margin, self.sz_y+_SZ_H+margin
        def in_safe(tx,ty): return sx1<=tx<=sx2 and sy1<=ty<=sy2

        # ── Clusters de ÁRVORES (decoração, não labirinto) ────────────
        for _ in range(18):
            gx = rng.randint(4, MAP_W-5)
            gy = rng.randint(4, MAP_H-5)
            if in_safe(gx,gy): continue
            if math.hypot(gx-cx,gy-cy) >= r_inner-2: continue
            size = rng.randint(1,3)
            for dy in range(-size,size+1):
                for dx in range(-size,size+1):
                    # Não forma paredes longas — pula aleatoriamente
                    if rng.random()<0.35: continue
                    tx,ty = gx+dx,gy+dy
                    if 2<=tx<MAP_W-2 and 2<=ty<MAP_H-2 and not in_safe(tx,ty):
                        if math.hypot(tx-cx,ty-cy)<r_inner-1:
                            self.tiles[ty][tx] = TILE_TREE

        # ── Clusters de PEDRA (rochas ambientais, esparsas) ──────────
        for _ in range(10):
            gx = rng.randint(4, MAP_W-5)
            gy = rng.randint(4, MAP_H-5)
            if in_safe(gx,gy): continue
            if math.hypot(gx-cx,gy-cy) >= r_inner-2: continue
            for dy in range(-1,2):
                for dx in range(-1,2):
                    if rng.random()<0.45: continue
                    tx,ty = gx+dx,gy+dy
                    if 2<=tx<MAP_W-2 and 2<=ty<MAP_H-2 and not in_safe(tx,ty):
                        if math.hypot(tx-cx,ty-cy)<r_inner-1:
                            self.tiles[ty][tx] = TILE_STONE

        # ── Lagozinhos (2-3 tiles de água) ────────────────────────────
        for _ in range(6):
            gx = rng.randint(4, MAP_W-5)
            gy = rng.randint(4, MAP_H-5)
            if in_safe(gx,gy): continue
            if math.hypot(gx-cx,gy-cy) >= r_inner-3: continue
            for dy in range(-1,2):
                for dx in range(-1,2):
                    if rng.random()<0.5: continue
                    tx,ty = gx+dx,gy+dy
                    if 2<=tx<MAP_W-2 and 2<=ty<MAP_H-2 and not in_safe(tx,ty):
                        self.tiles[ty][tx] = TILE_WATER

        # ── Zona segura ───────────────────────────────────────────────
        for ty in range(self.sz_y, self.sz_y+_SZ_H):
            for tx in range(self.sz_x, self.sz_x+_SZ_W):
                wall = (tx==self.sz_x or tx==self.sz_x+_SZ_W-1 or
                        ty==self.sz_y or ty==self.sz_y+_SZ_H-1)
                self.tiles[ty][tx] = TILE_STONE if wall else TILE_FLOOR

        # ── Porta na parede sul ───────────────────────────────────────
        self.tiles[self.door_ty][self.door_tx] = TILE_DOOR
        # Corredor de saída
        for tx in range(self.door_tx-1, self.door_tx+2):
            for ty in range(self.door_ty+1, self.door_ty+5):
                if 0<tx<MAP_W-1 and 0<ty<MAP_H-1:
                    self.tiles[ty][tx] = TILE_GRASS

    # ── Utilitários ───────────────────────────────────────────────────
    def safe_zone_center_px(self):
        return float((self.sz_x+_SZ_W//2)*TILE_SIZE), float((self.sz_y+_SZ_H//2)*TILE_SIZE)

    def door_px(self):
        return (self.door_tx*TILE_SIZE+TILE_SIZE//2,
                self.door_ty*TILE_SIZE+TILE_SIZE//2)

    def is_walkable(self,tx,ty):
        if 0<=ty<MAP_H and 0<=tx<MAP_W:
            return self.tiles[ty][tx] in (TILE_GRASS,TILE_FLOOR,TILE_DOOR)
        return False

    def is_grass(self,tx,ty):
        return 0<=ty<MAP_H and 0<=tx<MAP_W and self.tiles[ty][tx]==TILE_GRASS

    def walkable_grass_pos(self,rng,min_px=0,max_px=None,min_py=0,max_py=None,
                           exclude_rect=None,max_tries=400):
        max_px = max_px or (MAP_W-2)*TILE_SIZE
        max_py = max_py or (MAP_H-2)*TILE_SIZE
        for _ in range(max_tries):
            px = rng.uniform(min_px,max_px)
            py = rng.uniform(min_py,max_py)
            tx,ty = int(px//TILE_SIZE),int(py//TILE_SIZE)
            if not self.is_grass(tx,ty): continue
            h=12
            if not all(self.is_grass(int((px+ddx)//TILE_SIZE),int((py+ddy)//TILE_SIZE))
                       for ddx,ddy in [(-h,-h),(h,-h),(-h,h),(h,h)]):
                continue
            if exclude_rect and exclude_rect.collidepoint(px,py): continue
            return px,py
        return None

    def update(self,dt): self._door_anim+=dt

    # ── Render ────────────────────────────────────────────────────────
    def draw(self,surface,cam_x,cam_y):
        x0=max(0,int(cam_x//TILE_SIZE)); y0=max(0,int(cam_y//TILE_SIZE))
        x1=min(MAP_W,x0+SCREEN_W//TILE_SIZE+2); y1=min(MAP_H,y0+SCREEN_H//TILE_SIZE+2)
        for ty in range(y0,y1):
            for tx in range(x0,x1):
                tile=self.tiles[ty][tx]
                rx=tx*TILE_SIZE-int(cam_x); ry=ty*TILE_SIZE-int(cam_y)
                rect=pygame.Rect(rx,ry,TILE_SIZE,TILE_SIZE)
                pygame.draw.rect(surface,TILE_COLORS[tile],rect)
                self._detail(surface,tile,rect,rx,ry)
        # Porta pulsante
        import math as _m
        drx=self.door_tx*TILE_SIZE-int(cam_x); dry=self.door_ty*TILE_SIZE-int(cam_y)
        pulse=abs(_m.sin(self._door_anim*3))
        bc=(int(200+55*pulse),int(180+40*pulse),30)
        pygame.draw.rect(surface,bc,(drx,dry,TILE_SIZE,TILE_SIZE),3)
        font=pygame.font.SysFont("Arial",9,bold=True)
        lbl=font.render("PORTA",True,(0,0,0))
        surface.blit(lbl,(drx+TILE_SIZE//2-lbl.get_width()//2,dry+TILE_SIZE//2-lbl.get_height()//2))

    @staticmethod
    def _detail(surface,tile,rect,rx,ry):
        ts=TILE_SIZE; cx=rx+ts//2; cy=ry+ts//2
        if tile==TILE_GRASS:
            pygame.draw.rect(surface,(65,145,65),rect,1)
        elif tile==TILE_FLOOR:
            pygame.draw.rect(surface,(160,140,100),rect,1)
            mid=ts//2
            pygame.draw.line(surface,(150,130,90),(rx+4,ry+mid),(rx+ts-4,ry+mid),1)
            pygame.draw.line(surface,(150,130,90),(rx+mid,ry+4),(rx+mid,ry+ts-4),1)
        elif tile==TILE_TREE:
            pygame.draw.rect(surface,BROWN,(cx-4,cy+2,8,14))
            pygame.draw.circle(surface,(30,100,30),(cx,cy-4),15)
            pygame.draw.circle(surface,(50,130,50),(cx-4,cy-7),8)
        elif tile==TILE_WATER:
            pygame.draw.rect(surface,(60,110,220),rect,1)
        elif tile==TILE_STONE:
            pygame.draw.rect(surface,(90,80,70),rect,1)
        elif tile==TILE_DOOR:
            inner=rect.inflate(-6,-4)
            pygame.draw.rect(surface,(180,140,40),inner,border_radius=3)
