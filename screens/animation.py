"""screens/animation.py — ScreenFade e LevelUpEffect."""
import pygame, math
from config import SCREEN_W,SCREEN_H,YELLOW,WHITE,RED

class ScreenFade:
    def __init__(self,fade_in=True,speed=6):
        self._in=fade_in; self._speed=speed
        self._alpha=255 if fade_in else 0; self._done=False
        self._surf=pygame.Surface((SCREEN_W,SCREEN_H)); self._surf.fill((0,0,0))
    @property
    def done(self): return self._done
    def update(self):
        if self._done: return True
        if self._in: self._alpha=max(0,self._alpha-self._speed)
        else: self._alpha=min(255,self._alpha+self._speed)
        if self._alpha in (0,255): self._done=True
        return self._done
    def draw(self,surface):
        if self._done and self._in: return
        self._surf.set_alpha(self._alpha); surface.blit(self._surf,(0,0))

class LevelUpEffect:
    def __init__(self,level,duration=120):
        self.level=level; self.life=duration; self.max_life=duration
        self._fl=pygame.font.SysFont("Arial",48,bold=True)
        self._fs=pygame.font.SysFont("Arial",22,bold=True)
    @property
    def alive(self): return self.life>0
    def update(self): self.life-=1
    def draw(self,surface):
        if not self.alive: return
        ratio=self.life/self.max_life
        alpha=int(255*min(1.0,ratio*3))
        cx=SCREEN_W//2; cy=SCREEN_H//2-40-int((1-ratio)*30)
        for surf,dy in [(self._fl.render("LEVEL UP!",True,YELLOW),0),
                        (self._fs.render(f"Nivel {self.level} — +1 moeda!",True,WHITE),52)]:
            surf.set_alpha(alpha); surface.blit(surf,(cx-surf.get_width()//2,cy+dy))
