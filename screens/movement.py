"""screens/movement.py — WASD com colisão de tile."""
import math, pygame
from systems.collision import CollisionSystem
from config import TILE_SIZE

class MovementController:
    WAYPOINT_REACH=TILE_SIZE*0.6

    def __init__(self,world):
        self._col=CollisionSystem(world)
        self.path=[]

    def handle_click(self,wx,wy,player):
        """Pathfinding via clique (simplificado: linha reta verificando tiles)."""
        self.path=[(wx,wy)]

    def clear_path(self): self.path=[]

    def update(self,player,dt,keys):
        dx=dy=0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy-=1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy+=1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx-=1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx+=1
        if dx!=0 or dy!=0:
            self.path=[]
            rdx,rdy=self._col.resolve_move(player,dx,dy,dt)
            player.move(rdx,rdy,dt)
        elif self.path:
            wx,wy=self.path[0]
            diffx=wx-player.x; diffy=wy-player.y
            dist=math.hypot(diffx,diffy)
            if dist<=self.WAYPOINT_REACH:
                self.path.pop(0); player.moving=False; return
            ndx=diffx/dist; ndy=diffy/dist
            rdx,rdy=self._col.resolve_move(player,ndx,ndy,dt)
            if rdx==0 and rdy==0: self.path=[]; player.moving=False; return
            player.move(rdx,rdy,dt)
            if diffx!=0: player.facing=1 if diffx>0 else -1
        else:
            player.moving=False

    def draw_path(self,surface,cam_x,cam_y):
        if not self.path: return
        dx=int(self.path[-1][0]-cam_x); dy=int(self.path[-1][1]-cam_y)
        pygame.draw.circle(surface,(255,220,50),(dx,dy),7)
        pygame.draw.circle(surface,(255,255,255),(dx,dy),7,2)
