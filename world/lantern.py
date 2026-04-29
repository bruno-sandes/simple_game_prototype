"""
world/lantern.py

CORRECAO COMPLETA:
  A versão anterior invertia o gradiente: centro escuro, borda clara.
  Causa: a ordem dos círculos e os valores de alpha estavam errados.

TECNICA CORRETA (BLEND_RGBA_MULT):
  1. Preenche surface de névoa com preto + alpha=darkness
  2. Cria surface de luz com alpha=255 em tudo (preserva névoa)
  3. Desenha círculos do MAIOR para o MENOR com alpha DECRESCENTE
     - Círculo externo (r=radius): alpha=255 → névoa preservada = ESCURO
     - Círculos internos menores: alpha cada vez menor → névoa reduzida
     - Centro (r pequeno): alpha≈0 → névoa apagada = CLARO
  4. Aplica com BLEND_RGBA_MULT: result_alpha = light_alpha * fog_alpha / 255
     - light=255 → preserva escuridão ✓
     - light=0   → zera escuridão = transparente = claro ✓
     - light=128 → meia escuridão = penumbra ✓

RESULTADO: centro brilhante, penumbra suave, borda escura.
O HUD é desenhado DEPOIS da lanterna e fica sempre visível.
"""

import pygame
from config import SCREEN_W, SCREEN_H, LANTERN_DARKNESS_ALPHA


class Lantern:

    STEPS = 100   # passos do gradiente (mais = mais suave)

    def __init__(self, darkness: int = LANTERN_DARKNESS_ALPHA):
        self._darkness = darkness
        # Superfície principal de névoa (reutilizada a cada frame)
        self._fog = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

    def draw(self, surface: pygame.Surface,
             player, cam_x: float, cam_y: float) -> None:
        radius = player.lantern_radius
        px = int(player.x - cam_x)
        py = int(player.y - cam_y)

        # 1. Névoa cobre tudo com a escuridão máxima
        self._fog.fill((0, 0, 0, self._darkness))

        # 2. Surface de luz: começa com tudo alpha=255 (preserva névoa)
        diam = radius * 2 + 2
        light = pygame.Surface((diam, diam), pygame.SRCALPHA)
        light.fill((0, 0, 0, 255))

        cx = cy = radius + 3
        steps = self.STEPS

        # 3. Círculos de MAIOR para MENOR com alpha DECRESCENTE
        #    → última camada sobre cada pixel é a menor que o cobre
        #    → pixels perto do centro ficam com alpha ≈ 0 (apaga névoa)
        #    → pixels na borda ficam com alpha = 255 (preserva névoa)
        for i in range(steps + 1):
            ratio = i / steps                     # 0=primeiro(grande), 1=último(pequeno)
            r     = int(radius * (1.0 - ratio))   # grande→pequeno
            a     = int(255  * (1.0 - ratio))     # 255→0 (borda escura, centro claro)
            if r > 0:
                pygame.draw.circle(light, (0, 0, 0, a), (cx, cy), r)

        # Garante centro 100% transparente (brilhante)
        pygame.draw.circle(light, (0, 0, 0, 0), (cx, cy), max(4, radius // 8))

        # 4. Aplica gradiente à névoa com BLEND_RGBA_MULT
        blit_x = px - radius - 3
        blit_y = py - radius - 3
        self._fog.blit(light, (blit_x, blit_y),
                       special_flags=pygame.BLEND_RGBA_MULT)

        # 5. Blit da névoa na tela
        surface.blit(self._fog, (0, 0))