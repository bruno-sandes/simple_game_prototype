"""
world/lantern.py — penumbra suave, sem quadriculado.

Usa pygame.draw.circle com antialiasing simulado por muitos
passos finos (STEPS=48) para evitar borda pixelada.
Três zonas:
  0..radius      → totalmente visível (alpha=0)
  radius..outer  → penumbra gradual  (alpha 0→darkness)
  outer..tela    → escuridão total   (alpha=darkness)
"""
import pygame
from config import SCREEN_W, SCREEN_H, LANTERN_DARKNESS_ALPHA

class Lantern:
    PENUMBRA_RATIO = 0.55   # zona de penumbra = 55% extra além do raio
    STEPS = 48              # mais passos = mais suave (sem quadriculado)

    def __init__(self, darkness=LANTERN_DARKNESS_ALPHA):
        self._darkness = darkness
        # Surface pré-alocada
        self._fog = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

    def draw(self, surface, player, cam_x, cam_y):
        radius = player.lantern_radius
        outer  = int(radius * (1.0 + self.PENUMBRA_RATIO))
        px = int(player.x - cam_x)
        py = int(player.y - cam_y)

        # Preenche tudo com escuridão máxima
        self._fog.fill((0, 0, 0, self._darkness))

        steps = self.STEPS
        # Desenha círculos do MAIOR ao MENOR sobrescrevendo o alpha
        # Tamanhos intermediários criam o gradiente suave
        for i in range(steps + 1):
            # r vai de outer → 0 conforme i vai 0 → steps
            r = int(outer * (1.0 - i / steps))
            if r <= 0:
                continue

            if r <= radius:
                # Dentro da luz: apaga a névoa completamente
                a = 0
            else:
                # Penumbra: alpha proporcional à distância da borda de luz
                t = (r - radius) / (outer - radius)   # 0=borda luz, 1=borda escuro
                # Curva suave (quadrática) para transição mais natural
                a = int(self._darkness * (t * t))

            pygame.draw.circle(self._fog, (0, 0, 0, a), (px, py), r)

        # Núcleo central: garante transparência total no centro
        pygame.draw.circle(self._fog, (0, 0, 0, 0), (px, py),
                           max(3, radius // 5))

        surface.blit(self._fog, (0, 0))
