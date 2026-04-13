"""
ui/hud.py
=========
Renderização do HUD (Head-Up Display) durante o gameplay.

Componentes:
  - Barra de HP (com gradiente de cor por nível de vida)
  - Barra de cooldown da skill
  - Nome, nível e XP do jogador
  - Contador de inventário
  - Mensagens flutuantes temporárias
  - Painel de controles (canto inferior esquerdo)

Todas as funções recebem `surface` e `player` como primeiros args.
"""

import pygame
from config import (
    SCREEN_W, SCREEN_H,
    WHITE, BLACK, RED, GREEN, ORANGE, YELLOW,
    GRAY, DARK_GRAY, LIGHT_GRAY, LIGHT_BLUE
)
from ui.fonts import fonts


# ------------------------------------------------------------------ #
#  Barra de HP                                                         #
# ------------------------------------------------------------------ #
def draw_hp_bar(surface: pygame.Surface, player) -> None:
    bx, by, bw, bh = 10, 10, 220, 22
    pygame.draw.rect(surface, (80, 0, 0),      (bx, by, bw, bh), border_radius=5)

    ratio   = player.hp / player.max_hp
    hp_w    = max(0, int(bw * ratio))
    hp_clr  = RED if ratio < 0.3 else ORANGE if ratio < 0.6 else GREEN
    pygame.draw.rect(surface, hp_clr, (bx, by, hp_w, bh), border_radius=5)
    pygame.draw.rect(surface, WHITE,  (bx, by, bw,  bh), 1, border_radius=5)

    label = fonts.sm.render(f"HP  {player.hp} / {player.max_hp}", True, WHITE)
    surface.blit(label, (bx + 6, by + 4))


# ------------------------------------------------------------------ #
#  Barra de cooldown da skill                                          #
# ------------------------------------------------------------------ #
def draw_skill_bar(surface: pygame.Surface, player) -> None:
    bx, by, bw, bh = 10, 37, 220, 12
    ready  = player.skill_cd <= 0
    ratio  = 1.0 - player.skill_cd / player.skill_max_cd

    pygame.draw.rect(surface, DARK_GRAY, (bx, by, bw, bh), border_radius=4)
    fill_clr = LIGHT_BLUE if not ready else (100, 255, 180)
    pygame.draw.rect(surface, fill_clr, (bx, by, int(bw * ratio), bh), border_radius=4)
    pygame.draw.rect(surface, GRAY, (bx, by, bw, bh), 1, border_radius=4)

    txt = "SKILL (Click): PRONTO!" if ready else "SKILL (Click): recarregando..."
    s   = fonts.xs.render(txt, True, WHITE)
    surface.blit(s, (bx + 3, by + 1))


# ------------------------------------------------------------------ #
#  Info do jogador                                                      #
# ------------------------------------------------------------------ #
def draw_player_info(surface: pygame.Surface, player) -> None:
    info = f"{player.name}  |  Nível {player.level}  |  XP: {player.xp}/{player.xp_next}"
    surface.blit(fonts.sm.render(info, True, YELLOW), (10, 54))

    inv_txt = f"Inventário: {len(player.inventory)} itens  [I]"
    surface.blit(fonts.xs.render(inv_txt, True, LIGHT_GRAY), (10, 72))


# ------------------------------------------------------------------ #
#  Mensagens flutuantes                                                #
# ------------------------------------------------------------------ #
def draw_messages(surface: pygame.Surface, messages: list) -> None:
    """
    messages: lista de [texto, timer] gerenciada pelo Game.
    Timer vai de 200 → 0; alpha proporcional.
    """
    for i, msg in enumerate(messages):
        alpha = min(255, int(255 * msg[1] / 200))
        s = fonts.sm.render(msg[0], True, YELLOW)
        s.set_alpha(alpha)
        surface.blit(s, (SCREEN_W // 2 - s.get_width() // 2,
                         SCREEN_H - 120 - i * 22))


# ------------------------------------------------------------------ #
#  Painel de controles                                                  #
# ------------------------------------------------------------------ #
_CONTROLS = [
    "WASD   → Mover",
    "E      → Falar com NPC",
    "Click  → Skill",
    "I      → Inventário",
    "F      → Usar poção",
    "ESC    → Menu",
]

def draw_controls(surface: pygame.Surface) -> None:
    for i, txt in enumerate(_CONTROLS):
        s = fonts.xs.render(txt, True, (170, 170, 170))
        surface.blit(s, (10, SCREEN_H - 95 + i * 14))


# ------------------------------------------------------------------ #
#  Função única para chamar tudo                                        #
# ------------------------------------------------------------------ #
def draw_hud(surface: pygame.Surface, player, messages: list) -> None:
    """Chama todos os componentes do HUD em ordem."""
    draw_hp_bar(surface, player)
    draw_skill_bar(surface, player)
    draw_player_info(surface, player)
    draw_messages(surface, messages)
    draw_controls(surface)