"""
ui/inventory.py

CORREÇÃO:
  ORANGE estava sendo usado na linha do botão de ordenação mas não estava
  importado de config -> NameError ao abrir o inventário com [I].
  Adicionado ORANGE ao import de config.
"""

import pygame
from config import SCREEN_W, SCREEN_H, YELLOW, WHITE, GRAY, DARK_GRAY, LIGHT_GRAY, ORANGE

# IMPORT GLOBAL DA FONTE REMOVIDO DAQUI

_SORT_LABELS = {"label": "A-Z", "count": "Qtd", "type": "Tipo"}


def draw_inventory(surface: pygame.Surface, player) -> None:
    from ui.fonts import fonts  # <--- IMPORT MOVIDO PARA CÁ!
    
    IW, IH = 340, 420
    ix = SCREEN_W // 2 - IW // 2
    iy = SCREEN_H // 2 - IH // 2

    inv = player.inventory  # InventoryManager

    # Fundo
    bg = pygame.Surface((IW, IH), pygame.SRCALPHA)
    bg.fill((15, 15, 35, 235))
    surface.blit(bg, (ix, iy))
    pygame.draw.rect(surface, YELLOW, (ix, iy, IW, IH), 2, border_radius=10)

    # Título
    title = fonts.lg.render("INVENTARIO", True, YELLOW)
    surface.blit(title, (ix + IW // 2 - title.get_width() // 2, iy + 12))

    # Botão de ordenação
    sort_lbl = _SORT_LABELS.get(inv.current_sort, inv.current_sort)
    sort_s = fonts.xs.render(f"[O] Ordem: {sort_lbl}", True, ORANGE)
    surface.blit(sort_s, (ix + IW - sort_s.get_width() - 12, iy + 14))

    pygame.draw.line(surface, YELLOW, (ix + 10, iy + 42), (ix + IW - 10, iy + 42))

    # Itens via sorted_display() — retorna list[dict]
    rows = inv.sorted_display()

    if not rows:
        et = fonts.md.render("Inventário vazio", True, GRAY)
        surface.blit(et, (ix + IW // 2 - et.get_width() // 2, iy + 90))
    else:
        COLS, SLOT, GAP = 4, 76, 6
        for idx, row in enumerate(rows):
            col = idx % COLS
            r   = idx // COLS
            sx  = ix + 14 + col * (SLOT + GAP)
            sy  = iy + 52  + r   * (SLOT + GAP)

            if sy + SLOT > iy + IH - 48:
                break

            slot_r = pygame.Rect(sx, sy, SLOT, SLOT)
            pygame.draw.rect(surface, DARK_GRAY, slot_r, border_radius=7)
            pygame.draw.rect(surface, GRAY,      slot_r, 1, border_radius=7)

            cx_i = sx + SLOT // 2
            cy_i = sy + SLOT // 2 - 10
            pygame.draw.circle(surface, row["color"], (cx_i, cy_i), 17)
            bright = tuple(min(255, c + 70) for c in row["color"])
            pygame.draw.circle(surface, bright, (cx_i - 5, cy_i - 5), 6)

            ic = fonts.xxs.render(row["icon"][:2], True, WHITE)
            surface.blit(ic, (cx_i - ic.get_width() // 2, cy_i - ic.get_height() // 2))

            count_s = fonts.sm.render(f"x{row['count']}", True, YELLOW)
            surface.blit(count_s, (sx + SLOT - count_s.get_width() - 3, sy + 3))

            nm = fonts.xxs.render(row["label"][:10], True, WHITE)
            surface.blit(nm, (sx + SLOT // 2 - nm.get_width() // 2, sy + SLOT - 15))

    # Rodapé
    pygame.draw.line(surface, GRAY, (ix + 10, iy + IH - 34), (ix + IW - 10, iy + IH - 34))
    tip = fonts.xs.render("F=pocao  O=ordenar  I=fechar", True, LIGHT_GRAY)
    surface.blit(tip, (ix + IW // 2 - tip.get_width() // 2, iy + IH - 24))

    tot = fonts.xs.render(f"{inv.unique_types} tipo(s)  |  {inv.total} item(ns)", True, GRAY)
    surface.blit(tot, (ix + IW - tot.get_width() - 12, iy + IH - 24))