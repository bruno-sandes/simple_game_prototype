"""
ui/dialogue.py

CORREÇÃO:
  Quando o nó é folha (is_leaf), o hint mostrava "[1] Encerrar" mas pressionar
  [1] não fazia nada (game.py só processa K_1 quando not node.is_leaf).
  Corrigido: hint agora mostra "ENTER / E → fechar" para nós folha,
  e "[1] [2] ..." apenas para nós com escolhas.
"""
import pygame
from config import SCREEN_W, SCREEN_H, YELLOW, WHITE, GRAY, BLACK, LIGHT_GRAY

# IMPORT GLOBAL REMOVIDO DAQUI


def draw_dialogue(surface: pygame.Surface, npc) -> None:
    from ui.fonts import fonts  # <--- IMPORT MOVIDO PARA CÁ!
    
    BOX_H = 170
    PAD   = 20
    br    = pygame.Rect(PAD, SCREEN_H - BOX_H - PAD, SCREEN_W - PAD * 2, BOX_H)
    node  = npc.tree.current

    bg = pygame.Surface((br.w, br.h), pygame.SRCALPHA)
    bg.fill((10, 10, 30, 235))
    surface.blit(bg, (br.x, br.y))
    pygame.draw.rect(surface, YELLOW, br, 2, border_radius=6)

    # Avatar do NPC
    ax, ay = br.x + 35, br.y + 60
    pygame.draw.circle(surface, npc.color,       (ax, ay), 18)
    pygame.draw.circle(surface, (200, 200, 200), (ax - 7, ay - 6), 5)
    pygame.draw.circle(surface, BLACK,           (ax - 8, ay - 6), 2)
    pygame.draw.circle(surface, (200, 200, 200), (ax + 7, ay - 6), 5)
    pygame.draw.circle(surface, BLACK,           (ax + 8, ay - 6), 2)
    pygame.draw.rect(surface, npc.color, (ax - 16, ay + 10, 32, 18), border_radius=4)

    speaker_name = node.speaker if node.speaker else npc.name
    name_s = fonts.md.render(speaker_name, True, YELLOW)
    surface.blit(name_s, (br.x + 80, br.y + 12))

    pygame.draw.line(surface, YELLOW, (br.x + 80, br.y + 36),
                     (br.right - 12, br.y + 36), 1)

    # Texto com quebra de linha
    text_area_w = br.w - 95
    words  = node.text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if fonts.md.size(test)[0] < text_area_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)

    for i, line in enumerate(lines[:3]):
        s = fonts.md.render(line, True, WHITE)
        surface.blit(s, (br.x + 80, br.y + 45 + i * 25))

    opcoes_y = br.y + 45 + len(lines[:3]) * 25 + 8

    if node.is_leaf:
        # CORRIGIDO: hint correto para fechar com E/ENTER
        hint = fonts.sm.render("ENTER / E → fechar", True, GRAY)
        surface.blit(hint, (br.right - hint.get_width() - 20, br.bottom - 25))
    else:
        offset_x = 0
        for i, choice in enumerate(node.choices):
            c_text = fonts.sm.render(f"[{i+1}] {choice[0]}", True, LIGHT_GRAY)
            surface.blit(c_text, (br.x + 80 + offset_x, opcoes_y))
            offset_x += c_text.get_width() + 30