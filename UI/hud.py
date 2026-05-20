"""UI/hud.py — HUD com andar, moedas e contador de upgrades."""
import pygame
from config import (SCREEN_W,SCREEN_H,WHITE,RED,GREEN,ORANGE,YELLOW,
                    GRAY,DARK_GRAY,LIGHT_GRAY,LIGHT_BLUE,MAX_TOTAL_UPGRADES)

def draw_hud(surface, player, messages, floor=1):
    from ui.fonts import fonts
    # HP
    bx,by,bw,bh=10,10,220,22
    pygame.draw.rect(surface,(80,0,0),(bx,by,bw,bh),border_radius=5)
    ratio=player.hp/player.max_hp; hp_w=max(0,int(bw*ratio))
    hp_clr=RED if ratio<0.3 else ORANGE if ratio<0.6 else GREEN
    pygame.draw.rect(surface,hp_clr,(bx,by,hp_w,bh),border_radius=5)
    pygame.draw.rect(surface,WHITE,(bx,by,bw,bh),1,border_radius=5)
    surface.blit(fonts.sm.render(f"HP  {player.hp}/{player.max_hp}",True,WHITE),(bx+6,by+4))
    # Skill CD
    bx,by,bw,bh=10,37,220,12; ready=player.skill_cd<=0
    ratio_cd=1.0-player.skill_cd/player.skill_max_cd
    pygame.draw.rect(surface,DARK_GRAY,(bx,by,bw,bh),border_radius=4)
    pygame.draw.rect(surface,LIGHT_BLUE if not ready else (100,255,180),(bx,by,int(bw*ratio_cd),bh),border_radius=4)
    pygame.draw.rect(surface,GRAY,(bx,by,bw,bh),1,border_radius=4)
    surface.blit(fonts.xs.render("SKILL: PRONTO!" if ready else "SKILL: recarregando...",True,WHITE),(bx+3,by+1))
    # Info
    surface.blit(fonts.sm.render(f"{player.name}  Nv.{player.level}  XP:{player.xp}/{player.xp_next}",True,YELLOW),(10,54))
    coins=player.inventory.count("coin")
    up_left=MAX_TOTAL_UPGRADES-player.upgrade_count
    surface.blit(fonts.xs.render(f"Moedas:{coins}  Upgrades restantes:{up_left}/{MAX_TOTAL_UPGRADES}  [I]",True,LIGHT_GRAY),(10,72))
    # Andar
    ft=fonts.md.render(f"Andar {floor}",True,YELLOW)
    surface.blit(ft,(SCREEN_W-ft.get_width()-175,145))
    # Chave coletada
    if player.inventory.has("key"):
        kt=fonts.sm.render("Chave COLETADA! Pressione E na Porta!",True,(255,255,80))
        surface.blit(kt,(SCREEN_W//2-kt.get_width()//2,10))
    # Mensagens
    for i,msg in enumerate(messages):
        alpha=min(255,int(255*msg[1]/260))
        s=fonts.sm.render(msg[0],True,YELLOW); s.set_alpha(alpha)
        surface.blit(s,(SCREEN_W//2-s.get_width()//2,SCREEN_H-130-i*22))
    # Controles
    ctrls=["WASD Mover","E Interagir/Porta","Clique Dir Skill","I Inventario","F Pocao","ESC Pausar"]
    for i,t in enumerate(ctrls):
        surface.blit(fonts.xs.render(t,True,(160,160,160)),(10,SCREEN_H-90+i*13))
