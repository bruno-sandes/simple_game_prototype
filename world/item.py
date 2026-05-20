"""world/item.py — itens coletáveis com animação flutuante."""
import math, pygame
from config import ITEM_DEFS, ITEM_COLLECT_RADIUS, WHITE

class Item:
    def __init__(self, x, y, item_type="gem"):
        d = ITEM_DEFS.get(item_type, ITEM_DEFS["gem"])
        self.x=float(x); self.y=float(y)
        self.item_type=item_type; self.color=d["color"]
        self.label=d["label"]; self.icon=d["icon"]
        self.collected=False; self._anim=0.0

    def update(self, dt): self._anim += dt

    def draw(self, surface, cam_x, cam_y):
        if self.collected: return
        sx=int(self.x-cam_x); sy=int(self.y-cam_y)+int(math.sin(self._anim*3)*4)
        shad=pygame.Surface((22,8),pygame.SRCALPHA); shad.fill((0,0,0,60))
        surface.blit(shad,(sx-11,sy+13))
        pygame.draw.circle(surface,self.color,(sx,sy),11)
        pygame.draw.circle(surface,WHITE,(sx,sy),11,2)
        bright=tuple(min(255,c+80) for c in self.color)
        pygame.draw.circle(surface,bright,(sx-3,sy-3),4)
        font=pygame.font.SysFont("Arial",9,bold=True)
        ic=font.render(self.icon[:2],True,WHITE)
        surface.blit(ic,(sx-ic.get_width()//2,sy-ic.get_height()//2))

    def get_rect(self):
        r=ITEM_COLLECT_RADIUS
        return pygame.Rect(self.x-r,self.y-r,r*2,r*2)
