"""ui/dialogue.py — caixa de diálogo com até 6 choices em 2 linhas."""
import pygame
from config import SCREEN_W,SCREEN_H,YELLOW,WHITE,GRAY,BLACK,LIGHT_GRAY,ORANGE

def draw_dialogue(surface, npc):
    from UI.fonts import fonts
    if npc is None: return
    BOX_H=200; PAD=20
    br=pygame.Rect(PAD,SCREEN_H-BOX_H-PAD,SCREEN_W-PAD*2,BOX_H)
    node=npc.tree.current
    bg=pygame.Surface((br.w,br.h),pygame.SRCALPHA); bg.fill((10,10,30,240))
    surface.blit(bg,(br.x,br.y)); pygame.draw.rect(surface,YELLOW,br,2,border_radius=6)
    # Avatar
    ax,ay=br.x+36,br.y+72
    pygame.draw.circle(surface,npc.color,(ax,ay),20)
    pygame.draw.circle(surface,(220,220,200),(ax+6,ay-5),4)
    pygame.draw.circle(surface,BLACK,(ax+7,ay-5),2)
    pygame.draw.rect(surface,npc.color,(ax-14,ay+10,28,16),border_radius=3)
    # Speaker + linha
    spk=node.speaker if node.speaker else npc.name
    surface.blit(fonts.md.render(spk,True,YELLOW),(br.x+68,br.y+10))
    pygame.draw.line(surface,YELLOW,(br.x+68,br.y+34),(br.right-12,br.y+34),1)
    # Texto
    tw=br.w-80; words=node.text.split(); lines,cur=[],""
    for w in words:
        t=(cur+" "+w).strip()
        if fonts.md.size(t)[0]<tw: cur=t
        else: lines.append(cur); cur=w
    lines.append(cur)
    for i,line in enumerate(lines[:3]):
        surface.blit(fonts.md.render(line,True,WHITE),(br.x+68,br.y+42+i*24))
    # Choices
    cy_=br.y+BOX_H-70
    if node.is_leaf:
        surface.blit(fonts.sm.render("ENTER/E → fechar",True,GRAY),(br.right-200,br.bottom-20))
        return
    if not node.choices: return
    per=3; slot_w=(br.w-80)//per
    for i,(lbl,_) in enumerate(node.choices[:6]):
        row=i//per; col=i%per
        bx=br.x+68+col*slot_w; by=cy_+row*34
        pygame.draw.rect(surface,(30,30,60),(bx,by,slot_w-6,28),border_radius=4)
        pygame.draw.rect(surface,ORANGE if i<3 else YELLOW,(bx,by,slot_w-6,28),1,border_radius=4)
        surface.blit(fonts.sm.render(f"[{i+1}]",True,YELLOW),(bx+4,by+6))
        max_c=max(1,(slot_w-34)//7)
        txt=lbl if len(lbl)<=max_c else lbl[:max_c-1]+"."
        surface.blit(fonts.xs.render(txt,True,WHITE),(bx+28,by+8))
