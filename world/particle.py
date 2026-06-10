"""world/particle.py — texto flutuante de feedback."""
import pygame
from config import YELLOW

class Particle:
    def __init__(self, x, y, text, color=YELLOW):
        self.x=float(x); self.y=float(y)
        self.vy=-65.0; self.text=text; self.color=color
        self.life=90; self.max_life=90

    def update(self, dt):
        self.y+=self.vy*dt; self.vy*=0.96; self.life-=1

    def draw(self, surface, cam_x, cam_y):
        if self.life<=0: return
        alpha=int(255*self.life/self.max_life)
        sx=int(self.x-cam_x); sy=int(self.y-cam_y)
        font=pygame.font.SysFont("Arial",14,bold=True)
        s=font.render(self.text,True,self.color); s.set_alpha(alpha)
        surface.blit(s,(sx-s.get_width()//2,sy))

    @property
    def alive(self): return self.life>0
