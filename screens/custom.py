"""screens/custom.py — tela de customização de personagem."""
import math, random, pygame
from config import SCREEN_W,SCREEN_H,PLAYER_COLORS,WHITE,BLACK,YELLOW,GRAY,DARK_GRAY,LIGHT_GRAY

class CustomizeScreen:
    BTN = pygame.Rect(SCREEN_W//2-100, SCREEN_H//2+170, 200, 48)

    def __init__(self):
        self.player_name="Heroi"; self.sel_color=0
        self.typing=False; self._cur=0.0; self._prev=0.0

    @property
    def selected_color(self): return PLAYER_COLORS[self.sel_color]

    def get_config(self): return {"name":self.player_name or "Heroi","color":self.selected_color}

    def handle_event(self,event):
        if event.type==pygame.KEYDOWN:
            if self.typing:
                if event.key==pygame.K_RETURN: self.typing=False
                elif event.key==pygame.K_ESCAPE: self.typing=False
                elif event.key==pygame.K_BACKSPACE: self.player_name=self.player_name[:-1]
                elif len(self.player_name)<14 and event.unicode.isprintable():
                    self.player_name+=event.unicode
            else:
                if event.key in (pygame.K_RETURN,pygame.K_SPACE): return "start"
                elif event.key==pygame.K_n: self.typing=True
                elif event.key in (pygame.K_LEFT,pygame.K_a): self.sel_color=(self.sel_color-1)%len(PLAYER_COLORS)
                elif event.key in (pygame.K_RIGHT,pygame.K_d): self.sel_color=(self.sel_color+1)%len(PLAYER_COLORS)
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if self.BTN.collidepoint(event.pos): return "start"
            nr=pygame.Rect(SCREEN_W//2-120,SCREEN_H//2-70,240,36)
            if nr.collidepoint(event.pos): self.typing=True
            n=len(PLAYER_COLORS)
            for i in range(n):
                bx=SCREEN_W//2-n*22+i*44; by=SCREEN_H//2+50
                if pygame.Rect(bx,by,38,38).collidepoint(event.pos): self.sel_color=i
        return None

    def update(self,dt): self._cur+=dt; self._prev+=dt

    def draw(self,surface):
        from ui.fonts import fonts
        surface.fill((18,18,38))
        # Estrelas
        rng=random.Random(42)
        for _ in range(60):
            pygame.draw.circle(surface,(rng.randint(60,120),60,120),(rng.randint(0,SCREEN_W),rng.randint(0,SCREEN_H)),rng.choice([1,1,2]))
        # Título
        t=fonts.xl.render("+ RPGame Lite +",True,YELLOW)
        surface.blit(t,(SCREEN_W//2-t.get_width()//2,60))
        sub=fonts.xs.render("Customize seu heroi antes de partir!",True,GRAY)
        surface.blit(sub,(SCREEN_W//2-sub.get_width()//2,108))
        # Campo de nome
        lbl=fonts.sm.render("Nome  [N para editar]:",True,(200,200,200))
        surface.blit(lbl,(SCREEN_W//2-120,SCREEN_H//2-92))
        nr=pygame.Rect(SCREEN_W//2-120,SCREEN_H//2-70,240,36)
        pygame.draw.rect(surface,DARK_GRAY,nr,border_radius=6)
        pygame.draw.rect(surface,YELLOW if self.typing else GRAY,nr,2,border_radius=6)
        cursor="|" if self.typing and int(self._cur*2)%2==0 else ""
        ns=fonts.md.render(self.player_name+cursor,True,WHITE)
        surface.blit(ns,(nr.x+8,nr.y+6))
        # Cores
        cl=fonts.sm.render("Cor  [← →]:",True,(200,200,200))
        surface.blit(cl,(SCREEN_W//2-120,SCREEN_H//2+20))
        n=len(PLAYER_COLORS)
        for i,clr in enumerate(PLAYER_COLORS):
            bx=SCREEN_W//2-n*22+i*44; by=SCREEN_H//2+50
            r=pygame.Rect(bx,by,38,38)
            pygame.draw.rect(surface,clr,r,border_radius=7)
            if i==self.sel_color:
                pygame.draw.rect(surface,WHITE,r,3,border_radius=7)
        # Preview
        c=self.selected_color; px=SCREEN_W//2; py=SCREEN_H//2+130
        s=18; lc=tuple(max(0,x-40) for x in c)
        pygame.draw.rect(surface,lc,(px-s//3,py+s//2,s//3,10),border_radius=2)
        pygame.draw.rect(surface,lc,(px,py+s//2,s//3,10),border_radius=2)
        pygame.draw.rect(surface,c,(px-s//2,py-s//2,s,s),border_radius=4)
        pygame.draw.circle(surface,c,(px,py-s),s//2)
        pygame.draw.circle(surface,WHITE,(px+5,py-s-2),4)
        pygame.draw.circle(surface,BLACK,(px+6,py-s-2),2)
        # Botão
        pygame.draw.rect(surface,(50,180,80),self.BTN,border_radius=10)
        pygame.draw.rect(surface,WHITE,self.BTN,2,border_radius=10)
        bt=fonts.md.render("JOGAR!",True,BLACK)
        surface.blit(bt,(self.BTN.centerx-bt.get_width()//2,self.BTN.centery-bt.get_height()//2))
        hint=fonts.xs.render("ENTER=jogar  N=nome  ←→=cor",True,GRAY)
        surface.blit(hint,(SCREEN_W//2-hint.get_width()//2,SCREEN_H-36))
