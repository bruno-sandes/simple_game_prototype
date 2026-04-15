"""
screens/animation.py
====================
Efeitos visuais de tela: fade-in/out entre estados e
animacao de level-up.

Classes:
    ScreenFade   — superfície preta com alpha que sobe/desce
    LevelUpEffect — texto animado exibido ao subir de nivel

Uso tipico no game.py:
    self._fade = ScreenFade(fade_in=True)
    ...
    if not self._fade.update():
        self._fade.draw(surface)
    else:
        self._fade = None    # animacao concluida
"""

import pygame
from config import SCREEN_W, SCREEN_H, YELLOW, WHITE


# ======================================================================
class ScreenFade:
    """
    Fade de tela inteira (preto transparente).

    Parametros:
        fade_in  — True  = tela escura -> visivel (entrada)
                   False = visivel -> tela escura (saida)
        speed    — incremento de alpha por frame (0-255)
    """

    def __init__(self, fade_in: bool = True, speed: int = 6):
        self._fade_in = fade_in
        self._speed   = speed
        self._alpha   = 255 if fade_in else 0
        self._done    = False
        self._surf    = pygame.Surface((SCREEN_W, SCREEN_H))
        self._surf.fill((0, 0, 0))

    @property
    def done(self) -> bool:
        return self._done

    def update(self) -> bool:
        """Atualiza o alpha. Retorna True quando a animacao termina."""
        if self._done:
            return True
        if self._fade_in:
            self._alpha = max(0,   self._alpha - self._speed)
            if self._alpha == 0:
                self._done = True
        else:
            self._alpha = min(255, self._alpha + self._speed)
            if self._alpha == 255:
                self._done = True
        return self._done

    def draw(self, surface: pygame.Surface) -> None:
        if self._done and self._fade_in:
            return
        self._surf.set_alpha(self._alpha)
        surface.blit(self._surf, (0, 0))


# ======================================================================
class LevelUpEffect:
    """
    Animacao de level-up: texto grande que aparece, expande e some.

    Parametros:
        level — nivel atingido (exibido no texto)
        duration — duracao em frames
    """

    def __init__(self, level: int, duration: int = 120):
        self.level    = level
        self.life     = duration
        self.max_life = duration
        self._font_lg = pygame.font.SysFont("Arial", 48, bold=True)
        self._font_sm = pygame.font.SysFont("Arial", 22, bold=True)

    @property
    def alive(self) -> bool:
        return self.life > 0

    def update(self) -> None:
        self.life -= 1

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return
        ratio = self.life / self.max_life
        alpha = int(255 * min(1.0, ratio * 3))   # aparece rapido, some devagar

        # Texto principal
        txt1 = self._font_lg.render("LEVEL UP!", True, YELLOW)
        txt2 = self._font_sm.render(f"Nivel {self.level} alcancado!", True, WHITE)

        cx = SCREEN_W // 2
        cy = SCREEN_H // 2 - 40 - int((1 - ratio) * 30)

        for surf, dy in [(txt1, 0), (txt2, 52)]:
            surf.set_alpha(alpha)
            surface.blit(surf, (cx - surf.get_width() // 2, cy + dy))


# ======================================================================
class WalkPathRenderer:
    """
    Renderiza o caminho calculado pelo pathfinder na tela.
    Exibe pontos ao longo da rota e uma seta no destino.
    """

    DOT_COLOR  = (100, 220, 255)
    DEST_COLOR = (255, 220, 50)

    def draw(self, surface: pygame.Surface,
             path: list, cam_x: float, cam_y: float) -> None:
        """
        Parametros:
            path   — lista de (wx, wy) em coords de mundo
            cam_x, cam_y — offset da camera
        """
        if not path:
            return

        # Pontos intermediarios
        for i, (wx, wy) in enumerate(path[:-1]):
            if i % 3 != 0:
                continue   # exibe 1 a cada 3 para nao poluir
            sx = int(wx - cam_x)
            sy = int(wy - cam_y)
            pygame.draw.circle(surface, self.DOT_COLOR, (sx, sy), 3)

        # Destino (ultimo waypoint)
        dx = int(path[-1][0] - cam_x)
        dy = int(path[-1][1] - cam_y)
        pygame.draw.circle(surface, self.DEST_COLOR, (dx, dy), 7)
        pygame.draw.circle(surface, (255, 255, 255), (dx, dy), 7, 2)