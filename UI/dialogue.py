"""
ui/dialogue.py
==============
Renderização da caixa de diálogo com o NPC.

Layout:
  ┌─────────────────────────────────────────────────────┐
  │  [Avatar]  Nome do NPC                              │
  │            "Texto da fala atual..."                 │
  │                                                     │
  │  1/6                      ENTER / E para continuar  │
  └─────────────────────────────────────────────────────┘

O texto é quebrado automaticamente para caber na caixa.
Avatar é um mini-desenho simplificado do NPC.
"""

import pygame
from config import SCREEN_W, SCREEN_H, YELLOW, WHITE, GRAY, BLACK
from ui.fonts import fonts


def draw_dialogue(surface: pygame.Surface, npc) -> None:
    """
    Desenha a caixa de diálogo para o NPC ativo.
    Deve ser chamado após draw_world (fica sobre o mundo).
    """
    BOX_H  = 160
    PAD    = 20
    br     = pygame.Rect(PAD, SCREEN_H - BOX_H - PAD,
                         SCREEN_W - PAD * 2, BOX_H)

    # ── Fundo ────────────────────────────────────────────────────────
    bg = pygame.Surface((br.w, br.h), pygame.SRCALPHA)
    bg.fill((10, 10, 30, 235))
    surface.blit(bg, (br.x, br.y))
    pygame.draw.rect(surface, YELLOW, br, 2, border_radius=10)

    # ── Avatar simplificado do NPC ───────────────────────────────────
    ax = br.x + 44
    ay = br.y + BOX_H // 2
    pygame.draw.circle(surface, npc.color, (ax, ay), 26)
    pygame.draw.circle(surface, (255, 255, 200), (ax + 7, ay - 6), 5)
    pygame.draw.circle(surface, BLACK,           (ax + 8, ay - 6), 2)
    pygame.draw.rect(surface, npc.color,
                     (ax - 16, ay + 10, 32, 18), border_radius=4)

    # ── Nome do NPC ──────────────────────────────────────────────────
    name_s = fonts.md.render(npc.name, True, YELLOW)
    surface.blit(name_s, (br.x + 80, br.y + 12))

    # ── Separador ────────────────────────────────────────────────────
    pygame.draw.line(surface, YELLOW,
                     (br.x + 80, br.y + 36),
                     (br.right - 12, br.y + 36), 1)

    # ── Texto com quebra de linha automática ─────────────────────────
    text_area_w = br.w - 95
    words   = npc.current_line.split()
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
        ls = fonts.md.render(line, True, WHITE)
        surface.blit(ls, (br.x + 80, br.y + 44 + i * 30))

    # ── Indicadores de progresso e instrução ─────────────────────────
    pg = fonts.xs.render(npc.progress, True, GRAY)
    surface.blit(pg, (br.x + 10, br.y + BOX_H - 18))

    hint = fonts.xs.render("ENTER / E → próxima fala", True, GRAY)
    surface.blit(hint, (br.right - hint.get_width() - 10,
                        br.y + BOX_H - 18))