"""
world/lantern.py

CORRECOES:
  - Penumbra visível ao redor da área iluminada: o mapa não fica totalmente
    escuro — existe uma zona de penumbra (~40% do raio extra) onde o cenário
    e mobs ficam parcialmente visíveis. Apenas além disso fica escuro total.
  - Gradiente suave de 3 zonas: luz plena → penumbra → escuridão.
  - Tecnica SRCALPHA com preenchimento por camadas (sem BLEND_RGBA_MULT).
"""
import pygame
from config import SCREEN_W, SCREEN_H, LANTERN_DARKNESS_ALPHA

class Lantern:
    # Zona de penumbra: quantos % do raio a mais ficam semi-visíveis
    PENUMBRA_RATIO = 0.45   # 45% extra de raio como penumbra

    def __init__(self, darkness=LANTERN_DARKNESS_ALPHA):
        self._darkness = darkness

    def draw(self, surface, player, cam_x, cam_y):
        radius = player.lantern_radius
        px = int(player.x - cam_x)
        py = int(player.y - cam_y)

        # Raio total incluindo penumbra
        outer = int(radius * (1 + self.PENUMBRA_RATIO))

        # Surface SRCALPHA cobre a tela toda
        fog = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

        # Preenche com escuridão máxima
        fog.fill((0, 0, 0, self._darkness))

        # Zona de luz plena: alpha=0 (transparente) → cenário 100% visível
        # Desenhamos do externo para o interno sobrescrevendo o alpha
        steps = 32
        for i in range(steps + 1):
            ratio = i / steps          # 0=borda externa, 1=centro
            # Raio decresce do outer para 0 conforme vai para o centro
            r = int(outer * (1.0 - ratio))
            if r <= 0:
                continue

            if r <= radius:
                # Dentro do raio de luz: totalmente transparente
                a = 0
            else:
                # Zona de penumbra: alpha cresce de 0 → darkness
                t = (r - radius) / (outer - radius)   # 0=borda luz, 1=borda escuro
                a = int(self._darkness * t)

            pygame.draw.circle(fog, (0, 0, 0, a), (px, py), r)

        # Núcleo totalmente limpo
        pygame.draw.circle(fog, (0, 0, 0, 0), (px, py), max(4, radius // 6))

        surface.blit(fog, (0, 0))
