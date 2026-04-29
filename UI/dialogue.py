"""
ui/dialogue.py
==============
Renderização da caixa de diálogo com o NPC.

<<<<<<< Updated upstream
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
=======
MUDANCA: suporta ate 5 choices (mercador tem 5 opcoes de loja).
Choices renderizados em 2 linhas de 3 se necessario.
"""
import pygame
from config import SCREEN_W, SCREEN_H, YELLOW, WHITE, GRAY, BLACK, LIGHT_GRAY, ORANGE


def draw_dialogue(surface: pygame.Surface, npc) -> None:
    from ui.fonts import fonts
    if npc is None:
        return

    BOX_H = 200
    PAD   = 20
    br    = pygame.Rect(PAD, SCREEN_H - BOX_H - PAD, SCREEN_W - PAD * 2, BOX_H)
    node  = npc.tree.current
>>>>>>> Stashed changes

    # ── Fundo ────────────────────────────────────────────────────────
    bg = pygame.Surface((br.w, br.h), pygame.SRCALPHA)
    bg.fill((10, 10, 30, 240))
    surface.blit(bg, (br.x, br.y))
    pygame.draw.rect(surface, YELLOW, br, 2, border_radius=10)

<<<<<<< Updated upstream
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
=======
    # Avatar
    ax, ay = br.x + 36, br.y + 72
    pygame.draw.circle(surface, npc.color, (ax, ay), 20)
    pygame.draw.circle(surface, (220, 220, 200), (ax + 6, ay - 5), 4)
    pygame.draw.circle(surface, BLACK,           (ax + 7, ay - 5), 2)
    pygame.draw.rect(surface, npc.color, (ax - 14, ay + 10, 28, 16), border_radius=3)

    # Speaker
    speaker = node.speaker if node.speaker else npc.name
    surface.blit(fonts.md.render(speaker, True, YELLOW), (br.x + 68, br.y + 10))
    pygame.draw.line(surface, YELLOW, (br.x + 68, br.y + 34), (br.right - 12, br.y + 34), 1)

    # Texto com quebra de linha automatica
    text_w = br.w - 80
    words  = node.text.split()
>>>>>>> Stashed changes
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if fonts.md.size(test)[0] < text_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    for i, line in enumerate(lines[:3]):
<<<<<<< Updated upstream
        ls = fonts.md.render(line, True, WHITE)
        surface.blit(ls, (br.x + 80, br.y + 44 + i * 30))

    # ── Indicadores de progresso e instrução ─────────────────────────
    pg = fonts.xs.render(npc.progress, True, GRAY)
    surface.blit(pg, (br.x + 10, br.y + BOX_H - 18))

    hint = fonts.xs.render("ENTER / E → próxima fala", True, GRAY)
    surface.blit(hint, (br.right - hint.get_width() - 10,
                        br.y + BOX_H - 18))
=======
        surface.blit(fonts.md.render(line, True, WHITE), (br.x + 68, br.y + 42 + i * 24))

    # Choices
    choices_y = br.y + BOX_H - 70

    if node.is_leaf:
        hint = fonts.sm.render("ENTER / E -> fechar", True, GRAY)
        surface.blit(hint, (br.right - hint.get_width() - 12, br.bottom - 20))
        return

    choices = node.choices
    if not choices:
        return

    per_line = 3   # maximo 3 choices por linha, 2 linhas = 6 total
    slot_w   = (br.w - 80) // per_line

    for i, (label, _) in enumerate(choices[:6]):
        row = i // per_line
        col = i %  per_line
        bx = br.x + 68 + col * slot_w
        by = choices_y + row * 34

        # Fundo do botao
        pygame.draw.rect(surface, (30, 30, 60),
                         (bx, by, slot_w - 6, 28), border_radius=4)
        pygame.draw.rect(surface, ORANGE if i < 3 else YELLOW,
                         (bx, by, slot_w - 6, 28), 1, border_radius=4)

        # Numero da tecla
        surface.blit(fonts.sm.render(f"[{i+1}]", True, YELLOW), (bx + 4, by + 6))

        # Texto truncado
        max_c = max(1, (slot_w - 34) // 7)
        txt   = label if len(label) <= max_c else label[:max_c - 1] + "."
        surface.blit(fonts.xs.render(txt, True, WHITE), (bx + 28, by + 8))
>>>>>>> Stashed changes
