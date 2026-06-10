"""ui/inventory.py — grade de inventário usando InventoryManager."""
import pygame
from config import SCREEN_W,SCREEN_H,YELLOW,WHITE,GRAY,DARK_GRAY,LIGHT_GRAY,ORANGE

def draw_inventory(surface, player):
    from ui.fonts import fonts
    IW,IH=380,420; ix=SCREEN_W//2-IW//2; iy=SCREEN_H//2-IH//2
    inv=player.inventory
    bg=pygame.Surface((IW,IH),pygame.SRCALPHA); bg.fill((15,15,35,238))
    surface.blit(bg,(ix,iy)); pygame.draw.rect(surface,YELLOW,(ix,iy,IW,IH),2,border_radius=10)
    title=fonts.lg.render("INVENTARIO",True,YELLOW)
    surface.blit(title,(ix+IW//2-title.get_width()//2,iy+10))
    sl=fonts.xs.render(f"[O] Ordem:{inv.current_sort}",True,ORANGE)
    surface.blit(sl,(ix+IW-sl.get_width()-12,iy+14))
    pygame.draw.line(surface,YELLOW,(ix+10,iy+42),(ix+IW-10,iy+42))
    rows=inv.sorted_display()
    if not rows:
        et=fonts.md.render("Inventario vazio",True,GRAY)
        surface.blit(et,(ix+IW//2-et.get_width()//2,iy+90))
    else:
        COLS,SLOT,GAP=4,80,6
        for idx,row in enumerate(rows):
            col=idx%COLS; r=idx//COLS
            sx_=ix+14+col*(SLOT+GAP); sy_=iy+52+r*(SLOT+GAP)
            if sy_+SLOT>iy+IH-48: break
            sr=pygame.Rect(sx_,sy_,SLOT,SLOT)
            pygame.draw.rect(surface,DARK_GRAY,sr,border_radius=7)
            pygame.draw.rect(surface,GRAY,sr,1,border_radius=7)
            cxi=sx_+SLOT//2; cyi=sy_+SLOT//2-10
            pygame.draw.circle(surface,row["color"],(cxi,cyi),17)
            bright=tuple(min(255,c+70) for c in row["color"])
            pygame.draw.circle(surface,bright,(cxi-5,cyi-5),6)
            ic=fonts.xxs.render(row["icon"][:2],True,WHITE)
            surface.blit(ic,(cxi-ic.get_width()//2,cyi-ic.get_height()//2))
            cs=fonts.sm.render(f"x{row['count']}",True,YELLOW)
            surface.blit(cs,(sx_+SLOT-cs.get_width()-3,sy_+3))
            nm=fonts.xxs.render(row["label"][:10],True,WHITE)
            surface.blit(nm,(sx_+SLOT//2-nm.get_width()//2,sy_+SLOT-15))
    pygame.draw.line(surface,GRAY,(ix+10,iy+IH-34),(ix+IW-10,iy+IH-34))
    tip=fonts.xs.render("F=pocao  O=ordenar  I=fechar",True,LIGHT_GRAY)
    surface.blit(tip,(ix+IW//2-tip.get_width()//2,iy+IH-24))
    tot=fonts.xs.render(f"{inv.unique_types} tipo(s) | {inv.total} item(ns)",True,GRAY)
    surface.blit(tot,(ix+IW-tot.get_width()-12,iy+IH-24))
