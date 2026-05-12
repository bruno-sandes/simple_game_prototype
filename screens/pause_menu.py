"""screens/pause_menu.py — menu de pausa (ESC em jogo). Não reinicia, não vai ao menu inicial."""
import pygame
from config import SCREEN_W, SCREEN_H, WHITE, BLACK, GRAY, YELLOW, DARK_GRAY

class PauseMenu:
    def __init__(self):
        self._options   = ["CONTINUAR", "CONTROLES", "SAIR"]
        self._selected  = 0
        self._show_ctrl = False
        self._btn_rects = []

    def reset(self):
        self._selected  = 0
        self._show_ctrl = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:        return "resume"
            if event.key in (pygame.K_UP,   pygame.K_w):
                self._selected = (self._selected-1) % len(self._options)
                self._show_ctrl = False
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._selected = (self._selected+1) % len(self._options)
                self._show_ctrl = False
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._activate()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._btn_rects):
                if r.collidepoint(event.pos):
                    self._selected = i
                    return self._activate()
        return None

    def _activate(self):
        opt = self._options[self._selected]
        if opt == "CONTINUAR":   return "resume"
        if opt == "CONTROLES":   self._show_ctrl = not self._show_ctrl; return None
        if opt == "SAIR":        return "quit"
        return None

    def draw(self, surface):
        from UI.fonts import fonts
        # Overlay
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 175)); surface.blit(ov, (0, 0))
        # Painel
        pw, ph = 340, 280
        px = SCREEN_W//2 - pw//2; py = SCREEN_H//2 - ph//2
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA); bg.fill((20, 20, 40, 230))
        surface.blit(bg, (px, py))
        pygame.draw.rect(surface, YELLOW, (px, py, pw, ph), 2, border_radius=10)

        title = fonts.xl.render("PAUSADO", True, YELLOW)
        surface.blit(title, (SCREEN_W//2-title.get_width()//2, py+14))
        pygame.draw.line(surface, YELLOW, (px+20, py+60), (px+pw-20, py+60))

        self._btn_rects = []
        for i, opt in enumerate(self._options):
            bx = px+30; by = py+72+i*58; bw = pw-60; bh = 46
            br = pygame.Rect(bx, by, bw, bh); self._btn_rects.append(br)
            bg_c = (60, 60, 100) if i==self._selected else (30, 30, 55)
            bc_c = YELLOW        if i==self._selected else GRAY
            pygame.draw.rect(surface, bg_c, br, border_radius=8)
            pygame.draw.rect(surface, bc_c, br, 2, border_radius=8)
            if i == self._selected:
                arrow = fonts.md.render("▶", True, YELLOW)
                surface.blit(arrow, (bx+8, by+bh//2-arrow.get_height()//2))
            lbl = fonts.md.render(opt, True, YELLOW if i==self._selected else WHITE)
            surface.blit(lbl, (SCREEN_W//2-lbl.get_width()//2, by+bh//2-lbl.get_height()//2))

        hint = fonts.xs.render("ESC=retomar  ↑↓=navegar  ENTER=selecionar", True, GRAY)
        surface.blit(hint, (SCREEN_W//2-hint.get_width()//2, py+ph+8))

        if self._show_ctrl:
            lines = ["WASD — Mover","E — Interagir / Porta",
                     "Clique Dir — Skill","Shift+Click — Skill",
                     "F — Usar pocao","I — Inventario",
                     "O — Ordenar inventario","1-6 — Escolher fala NPC",
                     "ESC — Pausar"]
            cw=300; ch=len(lines)*18+16; cx_=SCREEN_W//2-cw//2; cy_=py+ph+30
            cbg=pygame.Surface((cw,ch),pygame.SRCALPHA); cbg.fill((15,15,35,220))
            surface.blit(cbg,(cx_,cy_))
            pygame.draw.rect(surface,GRAY,(cx_,cy_,cw,ch),1,border_radius=6)
            for j,line in enumerate(lines):
                s=fonts.xs.render(line,True,(190,190,190)); surface.blit(s,(cx_+10,cy_+8+j*18))
