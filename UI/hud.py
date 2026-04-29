"""
ui/hud.py

MUDANÇA: draw_hud() recebe parâmetro `floor` para exibir o andar atual.
Também exibe moedas disponíveis (usadas no mercador).
"""
import pygame
from config import (
    SCREEN_W, SCREEN_H,
    WHITE, RED, GREEN, ORANGE, YELLOW,
    GRAY, DARK_GRAY, LIGHT_GRAY, LIGHT_BLUE
)
<<<<<<< Updated upstream
from ui.fonts import fonts


# ------------------------------------------------------------------ #
#  Barra de HP                                                         #
# ------------------------------------------------------------------ #
def draw_hp_bar(surface: pygame.Surface, player) -> None:
=======


def draw_hp_bar(surface, player) -> None:
    from ui.fonts import fonts
>>>>>>> Stashed changes
    bx, by, bw, bh = 10, 10, 220, 22
    pygame.draw.rect(surface, (80, 0, 0), (bx, by, bw, bh), border_radius=5)
    ratio  = player.hp / player.max_hp
    hp_w   = max(0, int(bw * ratio))
    hp_clr = RED if ratio < 0.3 else ORANGE if ratio < 0.6 else GREEN
    pygame.draw.rect(surface, hp_clr, (bx, by, hp_w, bh), border_radius=5)
    pygame.draw.rect(surface, WHITE,  (bx, by, bw, bh), 1, border_radius=5)
    label = fonts.sm.render(f"HP  {player.hp} / {player.max_hp}", True, WHITE)
    surface.blit(label, (bx + 6, by + 4))


<<<<<<< Updated upstream
# ------------------------------------------------------------------ #
#  Barra de cooldown da skill                                          #
# ------------------------------------------------------------------ #
def draw_skill_bar(surface: pygame.Surface, player) -> None:
=======
def draw_skill_bar(surface, player) -> None:
    from ui.fonts import fonts
>>>>>>> Stashed changes
    bx, by, bw, bh = 10, 37, 220, 12
    ready  = player.skill_cd <= 0
    ratio  = 1.0 - player.skill_cd / player.skill_max_cd
    pygame.draw.rect(surface, DARK_GRAY, (bx, by, bw, bh), border_radius=4)
    fill_clr = LIGHT_BLUE if not ready else (100, 255, 180)
    pygame.draw.rect(surface, fill_clr, (bx, by, int(bw * ratio), bh), border_radius=4)
    pygame.draw.rect(surface, GRAY, (bx, by, bw, bh), 1, border_radius=4)
    txt = "SKILL: PRONTO!" if ready else "SKILL: recarregando..."
    surface.blit(fonts.xs.render(txt, True, WHITE), (bx + 3, by + 1))


<<<<<<< Updated upstream
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
=======
def draw_player_info(surface, player, floor: int) -> None:
    from ui.fonts import fonts
    info = f"{player.name}  |  Nv.{player.level}  |  XP:{player.xp}/{player.xp_next}"
    surface.blit(fonts.sm.render(info, True, YELLOW), (10, 54))

    coins = player.inventory.count("coin")
    line2 = f"Moedas: {coins}  |  Itens: {player.inventory.total}  [I]"
    surface.blit(fonts.xs.render(line2, True, LIGHT_GRAY), (10, 72))

    # Andar atual (canto superior direito)
    floor_txt = fonts.md.render(f"Andar {floor}", True, YELLOW)
    surface.blit(floor_txt, (SCREEN_W - floor_txt.get_width() - 175, 145))

    # Chave coletada?
    if player.inventory.has("key"):
        key_txt = fonts.sm.render("Chave: ★ COLETADA! Va ate a Porta [E]", True, (255, 255, 80))
        surface.blit(key_txt, (SCREEN_W // 2 - key_txt.get_width() // 2, 10))


def draw_messages(surface, messages: list) -> None:
    from ui.fonts import fonts
>>>>>>> Stashed changes
    for i, msg in enumerate(messages):
        alpha = min(255, int(255 * msg[1] / 240))
        s = fonts.sm.render(msg[0], True, YELLOW)
        s.set_alpha(alpha)
        surface.blit(s, (SCREEN_W // 2 - s.get_width() // 2,
                         SCREEN_H - 130 - i * 22))


<<<<<<< Updated upstream
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
=======
_CONTROLS = [
    "WASD      Mover",
    "E         Interagir / Porta",
    "Click Dir Skill",
    "I         Inventario",
    "F         Usar pocao",
    "1,2,3...  Escolher fala",
    "ESC       Menu",
]

def draw_controls(surface) -> None:
    from ui.fonts import fonts
>>>>>>> Stashed changes
    for i, txt in enumerate(_CONTROLS):
        s = fonts.xs.render(txt, True, (160, 160, 160))
        surface.blit(s, (10, SCREEN_H - 100 + i * 13))


<<<<<<< Updated upstream
# ------------------------------------------------------------------ #
#  Função única para chamar tudo                                        #
# ------------------------------------------------------------------ #
def draw_hud(surface: pygame.Surface, player, messages: list) -> None:
    """Chama todos os componentes do HUD em ordem."""
=======
def draw_hud(surface, player, messages: list, floor: int = 1) -> None:
>>>>>>> Stashed changes
    draw_hp_bar(surface, player)
    draw_skill_bar(surface, player)
    draw_player_info(surface, player, floor)
    draw_messages(surface, messages)
    draw_controls(surface)