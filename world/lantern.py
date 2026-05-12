"""world/lantern.py — overlay escuro com luz correta: centro claro, borda escura."""
import pygame
from config import SCREEN_W, SCREEN_H, LANTERN_DARKNESS_ALPHA

class Lantern:
    STEPS = 32

    def __init__(self, darkness=LANTERN_DARKNESS_ALPHA):
        self._darkness = darkness
        self._fog = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

    def draw(self, surface, player, cam_x, cam_y):
        radius = player.lantern_radius
        px = int(player.x - cam_x)
        py = int(player.y - cam_y)

        # 1. Névoa cobre tudo
        self._fog.fill((0, 0, 0, self._darkness))

        # 2. Surface de luz: começa toda alpha=255 (preserva névoa integralmente)
        diam = radius * 2 + 10
        light = pygame.Surface((diam, diam), pygame.SRCALPHA)
        light.fill((0, 0, 0, 255))

        cx = cy = radius + 5
        steps = self.STEPS

        # 3. Círculos do maior (borda) para o menor (centro)
        #    alpha decrescente: borda=255 (escuro), centro=0 (claro)
        for i in range(steps + 1):
            ratio = i / steps                     # 0 = círculo maior, 1 = menor
            r     = int(radius * (1.0 - ratio))   # raio decresce
            a     = int(255 * (1.0 - ratio))       # alpha decresce → centro limpa névoa
            if r > 0:
                pygame.draw.circle(light, (0, 0, 0, a), (cx, cy), r)

        # Núcleo 100% transparente (sem penumbra no centro)
        pygame.draw.circle(light, (0, 0, 0, 0), (cx, cy), max(3, radius // 10))

        # 4. BLEND_RGBA_MULT: fog_alpha × light_alpha / 255
        #    light=255 → mantém escuridão | light=0 → apaga escuridão
        self._fog.blit(light, (px - radius - 5, py - radius - 5),
                       special_flags=pygame.BLEND_RGBA_MULT)

        # 5. Aplica névoa sobre a cena
        surface.blit(self._fog, (0, 0))
