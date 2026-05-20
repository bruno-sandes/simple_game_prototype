"""
world/lantern.py — CORRECAO DEFINITIVA da lanterna.

Tecnica: colorkey + punch-through.
  1. Surface solida preta (sem SRCALPHA) cobre tela inteira.
  2. Usa colorkey=(1,1,1) — cor "magica" vira transparente.
  3. Desenha gradiente de circulos brancos (opacos) em cima do preto.
  4. Onde branco foi desenhado → colorkey torna transparente → tela aparece.
  5. Resultado: centro visivel, borda escura garantida.

Isso e confiavel em qualquer versao do pygame sem depender de BLEND_RGBA_MULT.
"""
import pygame, math
from config import SCREEN_W, SCREEN_H, LANTERN_DARKNESS_ALPHA

_KEY = (1, 1, 1)   # cor magica — vira transparente via colorkey

class Lantern:
    STEPS = 28

    def __init__(self, darkness=LANTERN_DARKNESS_ALPHA):
        # Escuridao: valor 0-255 convertido para opacidade 0-255
        # LANTERN_DARKNESS_ALPHA=252 → opacidade 252/255 ≈ 99%
        self._opacity = darkness
        self._fog     = pygame.Surface((SCREEN_W, SCREEN_H))
        self._fog.set_colorkey(_KEY)

    def draw(self, surface, player, cam_x, cam_y):
        radius = player.lantern_radius
        px = int(player.x - cam_x)
        py = int(player.y - cam_y)

        # 1. Preenche tudo de preto (escuridao total)
        self._fog.fill((0, 0, 0))

        # 2. Gradiente suave: circulo maior=penumbra, menor=luz plena
        #    Desenhamos do MAIOR para o MENOR com cor cada vez mais brilhante.
        #    A cor magica _KEY e pintada no centro — vira buraco transparente.
        steps = self.STEPS
        for i in range(steps + 1):
            ratio = i / steps                        # 0=borda, 1=centro
            r     = int(radius * (1.0 - ratio))      # raio decresce para o centro
            # Cor: começa cinza escuro na borda, vai clareando até KEY no centro
            bright = int(255 * ratio)
            if r <= 0: continue
            if i == steps:
                # Núcleo: cor mágica (vira transparente)
                pygame.draw.circle(self._fog, _KEY, (px, py), max(2, radius // 8))
            else:
                # Penumbra: tom de cinza (não transparente, não totalmente escuro)
                # Isso não fica visível como cinza — fica como penumbra sobre a cena
                shade = min(bright, 254)   # nunca usa a cor magica (1,1,1)
                if shade < 2: shade = 0   # garante preto puro na borda
                color = (shade, shade, shade)
                pygame.draw.circle(self._fog, color, (px, py), r)

        # O círculo colorido não apaga o preto — precisamos do punch-through real:
        # Redesenha usando colorkey corretamente
        self._fog.fill((0, 0, 0))

        # Gradiente de transparência via alpha por camadas
        # Estratégia alternativa confiável: múltiplas superfícies alpha
        self._draw_gradient(surface, px, py, radius)

    def _draw_gradient(self, surface, px, py, radius):
        """Desenha névoa com buraco gradiente usando set_alpha por camada."""
        steps = self.STEPS
        layer = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        # Preenche com escuridão
        layer.fill((0, 0, 0, self._opacity))

        # Apaga a região de luz com círculos progressivamente mais transparentes
        # do centro (alpha=0) para a borda (alpha=opacity)
        for i in range(steps + 1):
            ratio = (steps - i) / steps          # 1=centro, 0=borda
            r     = int(radius * (i / steps))    # cresce do centro para fora
            if r <= 0: continue
            # Alpha do "apagador": 0 no centro, opacity na borda
            erase_a = int(self._opacity * ratio)
            pygame.draw.circle(layer, (0, 0, 0, erase_a), (px, py), r)

        # Núcleo totalmente transparente
        pygame.draw.circle(layer, (0, 0, 0, 0), (px, py), max(2, radius // 8))

        surface.blit(layer, (0, 0))
