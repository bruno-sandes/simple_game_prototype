"""
screens/custom.py
=================
Tela de customizacao do personagem antes do jogo comecar.

Responsabilidades:
  - Digitar nome do personagem
  - Selecionar cor (clique ou setas)
  - Preview do personagem
  - Botao "Jogar" -> retorna config ao Game

Uso no game.py:
    screen = CustomizeScreen()
    ...
    result = screen.handle_event(event)   # retorna "start" | None
    screen.update(dt)
    screen.draw(surface)
    config = screen.get_config()          # {"name": str, "color": tuple}
"""

import math
import pygame
from config import (
    SCREEN_W, SCREEN_H, PLAYER_COLORS,
    WHITE, BLACK, YELLOW, GRAY, DARK_GRAY, LIGHT_GRAY, GREEN
)

# A importação global foi removida daqui para evitar o AttributeError (NoneType)


class CustomizeScreen:
    BTN_PLAY = pygame.Rect(SCREEN_W // 2 - 100, SCREEN_H // 2 + 160, 200, 48)

    def __init__(self):
        self.player_name  = "Heroi"
        self.sel_color    = 0
        self.typing_name  = False
        self._cursor_t    = 0.0       # timer para piscar cursor
        self._preview_t   = 0.0       # timer animacao do preview

    # ------------------------------------------------------------------ #
    #  Getters                                                             #
    # ------------------------------------------------------------------ #
    @property
    def selected_color(self) -> tuple:
        return PLAYER_COLORS[self.sel_color]

    def get_config(self) -> dict:
        return {
            "name":  self.player_name or "Heroi",
            "color": self.selected_color,
        }

    # ------------------------------------------------------------------ #
    #  Eventos                                                             #
    # ------------------------------------------------------------------ #
    def handle_event(self, event: pygame.event.Event):
        """
        Retorna "start" se o jogador confirmou o personagem, None caso contrario.
        """
        if event.type == pygame.KEYDOWN:
            return self._on_key(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._on_click(event.pos)
        return None

    def _on_key(self, event: pygame.event.Event):
        if self.typing_name:
            if event.key == pygame.K_RETURN:
                self.typing_name = False
            elif event.key == pygame.K_ESCAPE:
                self.typing_name = False
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif len(self.player_name) < 14 and event.unicode.isprintable():
                self.player_name += event.unicode
        else:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "start"
            elif event.key == pygame.K_n:
                self.typing_name = True
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.sel_color = (self.sel_color - 1) % len(PLAYER_COLORS)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.sel_color = (self.sel_color + 1) % len(PLAYER_COLORS)
        return None

    def _on_click(self, pos: tuple):
        # Botao jogar
        if self.BTN_PLAY.collidepoint(pos):
            return "start"
        
        # Caixinha de nome
        name_r = pygame.Rect(SCREEN_W // 2 - 120, SCREEN_H // 2 - 60, 240, 36)
        if name_r.collidepoint(pos):
            self.typing_name = True
            return None
            
        # Botoes de cor
        n = len(PLAYER_COLORS)
        for i in range(n):
            bx = SCREEN_W // 2 - n * 22 + i * 44
            by = SCREEN_H // 2 + 40
            if pygame.Rect(bx, by, 38, 38).collidepoint(pos):
                self.sel_color = i
                return None
        return None

    # ------------------------------------------------------------------ #
    #  Update                                                              #
    # ------------------------------------------------------------------ #
    def update(self, dt: float) -> None:
        self._cursor_t  += dt
        self._preview_t += dt

    # ------------------------------------------------------------------ #
    #  Draw                                                                #
    # ------------------------------------------------------------------ #
    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((18, 18, 38))
        self._draw_stars(surface)
        self._draw_title(surface)
        self._draw_name_field(surface)
        self._draw_color_picker(surface)
        self._draw_preview(surface)
        self._draw_play_button(surface)
        self._draw_hints(surface)

    # ── Sub-renders ───────────────────────────────────────────────────
    def _draw_stars(self, surface: pygame.Surface) -> None:
        import random
        rng = random.Random(42)
        for _ in range(60):
            x = rng.randint(0, SCREEN_W)
            y = rng.randint(0, SCREEN_H)
            r = rng.choice([1, 1, 2])
            pygame.draw.circle(surface, (rng.randint(60, 120), 60, 120), (x, y), r)

    def _draw_title(self, surface: pygame.Surface) -> None:
        # Importação movida para dentro da função que a utiliza
        from ui.fonts import fonts 
        
        title = fonts.xl.render("+ RPGame Lite +", True, YELLOW)
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 60))
        
        sub = fonts.xs.render("Customize seu heroi antes de partir!", True, GRAY)
        surface.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 108))

    def _draw_name_field(self, surface: pygame.Surface) -> None:
        # Importação movida para dentro da função que a utiliza
        from ui.fonts import fonts 
        
        lbl = fonts.sm.render("Nome  [N para editar]:", True, LIGHT_GRAY)
        surface.blit(lbl, (SCREEN_W // 2 - 120, SCREEN_H // 2 - 82))
        
        nr = pygame.Rect(SCREEN_W // 2 - 120, SCREEN_H // 2 - 60, 240, 36)
        pygame.draw.rect(surface, DARK_GRAY, nr, border_radius=6)
        
        border_color = YELLOW if self.typing_name else GRAY
        pygame.draw.rect(surface, border_color, nr, 2, border_radius=6)
        
        cursor = "|" if (self.typing_name and int(self._cursor_t * 2) % 2 == 0) else ""
        ns = fonts.md.render(self.player_name + cursor, True, WHITE)
        surface.blit(ns, (nr.x + 8, nr.y + 6))

    def _draw_color_picker(self, surface: pygame.Surface) -> None:
        # Importação movida para dentro da função que a utiliza
        from ui.fonts import fonts 
        
        lbl = fonts.sm.render("Cor  [<- ->]:", True, LIGHT_GRAY)
        surface.blit(lbl, (SCREEN_W // 2 - 120, SCREEN_H // 2 + 14))
        
        n = len(PLAYER_COLORS)
        for i, clr in enumerate(PLAYER_COLORS):
            bx = SCREEN_W // 2 - n * 22 + i * 44
            by = SCREEN_H // 2 + 40
            r  = pygame.Rect(bx, by, 38, 38)
            pygame.draw.rect(surface, clr, r, border_radius=7)
            if i == self.sel_color:
                pygame.draw.rect(surface, WHITE, r, 3, border_radius=7)
                arrow = fonts.sm.render("v", True, WHITE)
                surface.blit(arrow, (bx + 13, by + 42))

    def _draw_preview(self, surface: pygame.Surface) -> None:
        """Desenha um mini-personagem animado como preview."""
        t    = self._preview_t
        clr  = self.selected_color
        s    = 20
        px   = SCREEN_W // 2
        py   = SCREEN_H // 2 + 115
        
        swing  = int(math.sin(t * 8) * 6)
        arm_sw = int(math.sin(t * 8 + math.pi) * 3)
        leg_c  = tuple(max(0, c - 40) for c in clr)
        arm_c  = tuple(max(0, c - 20) for c in clr)
        
        # Pernas
        pygame.draw.rect(surface, leg_c,
            (px - s // 3, py + s // 2, s // 3, 10 + swing), border_radius=2)
        pygame.draw.rect(surface, leg_c,
            (px,           py + s // 2, s // 3, 10 - swing), border_radius=2)
            
        # Corpo
        pygame.draw.rect(surface, clr,
            (px - s // 2, py - s // 2, s, s), border_radius=4)
            
        # Bracos
        pygame.draw.rect(surface, arm_c,
            (px - s // 2 - 5, py - s // 4 + arm_sw, 5, s // 2), border_radius=2)
        pygame.draw.rect(surface, arm_c,
            (px + s // 2,     py - s // 4 - arm_sw, 5, s // 2), border_radius=2)
            
        # Cabeca
        pygame.draw.circle(surface, clr, (px, py - s), s // 2)
        
        # Olhos
        pygame.draw.circle(surface, WHITE, (px + 5, py - s - 2), 4)
        pygame.draw.circle(surface, BLACK, (px + 6, py - s - 2), 2)

    def _draw_play_button(self, surface: pygame.Surface) -> None:
        # Importação movida para dentro da função que a utiliza
        from ui.fonts import fonts 
        
        pygame.draw.rect(surface, (50, 180, 80), self.BTN_PLAY, border_radius=10)
        pygame.draw.rect(surface, WHITE,         self.BTN_PLAY, 2, border_radius=10)
        bt = fonts.md.render("JOGAR!", True, BLACK)
        surface.blit(bt, (self.BTN_PLAY.centerx - bt.get_width() // 2,
                           self.BTN_PLAY.centery - bt.get_height() // 2))

    def _draw_hints(self, surface: pygame.Surface) -> None:
        # Importação movida para dentro da função que a utiliza
        from ui.fonts import fonts 
        
        hint = fonts.xs.render(
            "ENTER = jogar   N = editar nome   <- -> = cor",
            True, GRAY
        )
        surface.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 36))