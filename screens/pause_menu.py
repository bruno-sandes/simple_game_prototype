"""
screens/pause_menu.py  [NOVO ARQUIVO]

Menu de pausa acionado por ESC durante o jogo.
Não retorna ao início — apenas pausa e retoma.
Opções:
  CONTINUAR  — retoma o jogo
  CONTROLES  — exibe os controles na tela (toggle)
  SAIR       — fecha o jogo completamente
"""

import pygame
from config import SCREEN_W, SCREEN_H, WHITE, BLACK, GRAY, YELLOW, DARK_GRAY


class PauseMenu:

    def __init__(self):
        self._show_controls = False
        self._options = ["CONTINUAR", "CONTROLES", "SAIR"]
        self._selected = 0

    def reset(self):
        self._selected = 0
        self._show_controls = False

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """
        Retorna:
          'resume'  — continuar o jogo
          'quit'    — fechar o jogo
          None      — nenhuma ação
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "resume"
            if event.key in (pygame.K_UP, pygame.K_w):
                self._selected = (self._selected - 1) % len(self._options)
                self._show_controls = False
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._selected = (self._selected + 1) % len(self._options)
                self._show_controls = False
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._activate()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._check_mouse_click(event.pos)

        return None

    def _activate(self) -> str | None:
        opt = self._options[self._selected]
        if opt == "CONTINUAR":
            return "resume"
        elif opt == "CONTROLES":
            self._show_controls = not self._show_controls
            return None
        elif opt == "SAIR":
            return "quit"
        return None

    def _check_mouse_click(self, pos) -> str | None:
        for i, rect in enumerate(self._btn_rects):
            if rect.collidepoint(pos):
                self._selected = i
                return self._activate()
        return None

    def draw(self, surface: pygame.Surface) -> None:
        from ui.fonts import fonts

        # Overlay semi-transparente
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        # Painel central
        pw, ph = 340, 300
        px = SCREEN_W // 2 - pw // 2
        py = SCREEN_H // 2 - ph // 2
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((20, 20, 40, 230))
        surface.blit(panel, (px, py))
        pygame.draw.rect(surface, YELLOW, (px, py, pw, ph), 2, border_radius=10)

        # Título
        title = fonts.xl.render("PAUSADO", True, YELLOW)
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, py + 18))
        pygame.draw.line(surface, YELLOW, (px + 20, py + 64), (px + pw - 20, py + 64))

        # Botões
        self._btn_rects = []
        btn_start_y = py + 80
        btn_h = 46
        btn_gap = 12

        for i, opt in enumerate(self._options):
            bx = px + 30
            by = btn_start_y + i * (btn_h + btn_gap)
            bw = pw - 60
            br = pygame.Rect(bx, by, bw, btn_h)
            self._btn_rects.append(br)

            bg_clr = (60, 60, 100) if i == self._selected else (30, 30, 55)
            border_clr = YELLOW if i == self._selected else GRAY

            pygame.draw.rect(surface, bg_clr, br, border_radius=8)
            pygame.draw.rect(surface, border_clr, br, 2, border_radius=8)

            # Seta de seleção
            if i == self._selected:
                arrow = fonts.md.render("▶", True, YELLOW)
                surface.blit(arrow, (bx + 8, by + btn_h // 2 - arrow.get_height() // 2))

            lbl = fonts.md.render(opt, True, WHITE if i != self._selected else YELLOW)
            surface.blit(lbl, (SCREEN_W // 2 - lbl.get_width() // 2,
                                by + btn_h // 2 - lbl.get_height() // 2))

        # Painel de controles (toggle)
        if self._show_controls:
            self._draw_controls(surface, px, py + ph + 12, pw)

        # Dica
        hint = fonts.xs.render("ESC = retomar  |  ↑↓ = navegar  |  ENTER = selecionar",
                                True, GRAY)
        surface.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, py + ph + 10))

    def _draw_controls(self, surface: pygame.Surface, cx: int, cy: int, w: int) -> None:
        from ui.fonts import fonts
        lines = [
            "WASD         Mover",
            "Clique Dir   Lançar magia",
            "Shift+Click  Lançar magia",
            "E            Interagir / Porta",
            "F            Usar pocao",
            "I            Inventario",
            "O            Ordenar inventario",
            "1-5          Escolher fala NPC",
            "ESC          Pausar / fechar dialogo",
        ]
        panel_h = len(lines) * 18 + 16
        bg = pygame.Surface((w, panel_h), pygame.SRCALPHA)
        bg.fill((15, 15, 35, 220))
        surface.blit(bg, (cx, cy))
        pygame.draw.rect(surface, GRAY, (cx, cy, w, panel_h), 1, border_radius=6)
        for i, line in enumerate(lines):
            s = fonts.xs.render(line, True, (190, 190, 190))
            surface.blit(s, (cx + 10, cy + 8 + i * 18))