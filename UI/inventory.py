"""
ui/inventory.py
===============
Renderização da tela de inventário (overlay sobre o jogo).

Layout:
  Grade 4 × N de slots, cada slot mostra:
    - Círculo colorido com brilho (representando o item)
    - Nome curto do item abaixo

Aberto/fechado por [I].
Poções usadas por [F] (lógica no game.py).
"""

import pygame
from config import SCREEN_W, SCREEN_H, YELLOW, WHITE, GRAY, DARK_GRAY, LIGHT_GRAY
from ui.fonts import fonts


def draw_inventory(surface: pygame.Surface, player) -> None:
    """
    Renderiza o painel de inventário como overlay.
    Deve ser chamado após draw_world e draw_hud.
    """
    IW, IH  = 340, 420
    ix = SCREEN_W // 2 - IW // 2
    iy = SCREEN_H // 2 - IH // 2

    # ── Fundo ────────────────────────────────────────────────────────
    bg = pygame.Surface((IW, IH), pygame.SRCALPHA)
    bg.fill((15, 15, 35, 235))
    surface.blit(bg, (ix, iy))
    pygame.draw.rect(surface, YELLOW, (ix, iy, IW, IH), 2, border_radius=10)

    # ── Título ───────────────────────────────────────────────────────
    title = fonts.lg.render("INVENTARIO", True, YELLOW)
    surface.blit(title, (ix + IW // 2 - title.get_width() // 2, iy + 12))
    pygame.draw.line(surface, YELLOW, (ix + 20, iy + 44), (ix + IW - 20, iy + 44))

    # ── Itens ────────────────────────────────────────────────────────
    inv = player.inventory
    if not inv:
        et = fonts.md.render("Inventário vazio", True, GRAY)
        surface.blit(et, (ix + IW // 2 - et.get_width() // 2, iy + 90))
    else:
        COLS, SLOT = 4, 68
        for idx, item in enumerate(inv):
            row = idx // COLS
            col = idx % COLS
            sx  = ix + 16 + col * (SLOT + 5)
            sy  = iy + 55 + row * (SLOT + 8)

            # Slot (fundo escuro + borda)
            slot_r = pygame.Rect(sx, sy, SLOT, SLOT)
            pygame.draw.rect(surface, DARK_GRAY, slot_r, border_radius=7)
            pygame.draw.rect(surface, GRAY,      slot_r, 1, border_radius=7)

            # Ícone colorido
            cx = sx + SLOT // 2
            cy = sy + SLOT // 2 - 9
            pygame.draw.circle(surface, item.color, (cx, cy), 16)
            bright = tuple(min(255, c + 70) for c in item.color)
            pygame.draw.circle(surface, bright, (cx - 4, cy - 4), 5)

            # Nome curto
            nm = fonts.xxs.render(item.label[:10], True, WHITE)
            surface.blit(nm, (sx + SLOT // 2 - nm.get_width() // 2,
                               sy + SLOT - 16))

    # ── Dicas de uso ─────────────────────────────────────────────────
    tip = fonts.xs.render("F → usar poção    I → fechar", True, LIGHT_GRAY)
    surface.blit(tip, (ix + IW // 2 - tip.get_width() // 2, iy + IH - 22))

    # ── Contagem ─────────────────────────────────────────────────────
    count = fonts.xs.render(f"{len(inv)} / ∞ itens", True, GRAY)
    surface.blit(count, (ix + 12, iy + IH - 22))