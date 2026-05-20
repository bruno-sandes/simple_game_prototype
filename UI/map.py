"""
ui/map.py — minimap com fog of war.
Entidades só aparecem no minimap se estiverem dentro do lantern_radius × MULT.
NPCs e player sempre visíveis.
"""
import math, pygame
from config import MAP_W, MAP_H, TILE_SIZE, WHITE, GRAY, YELLOW, RED, LIGHT_GRAY

MINIMAP_REVEAL_MULT = 2.0   # mostra entidades até 2× o raio da lanterna

class MiniMap:
    def __init__(self, x, y, w, h):
        self.x=x; self.y=y; self.w=w; self.h=h
        self._bg = pygame.Surface((w, h), pygame.SRCALPHA)
        self._bg.fill((10, 10, 20, 185))

    def draw(self, surface, player, npcs, monsters, items):
        from ui.fonts import fonts
        surface.blit(self._bg, (self.x, self.y))
        pygame.draw.rect(surface, GRAY, (self.x, self.y, self.w, self.h), 1)

        sx = self.w / (MAP_W * TILE_SIZE)
        sy = self.h / (MAP_H * TILE_SIZE)
        reveal = player.lantern_radius * MINIMAP_REVEAL_MULT

        def mm(wx, wy):
            return (int(self.x + wx*sx), int(self.y + wy*sy))

        def visible(ex, ey):
            return math.hypot(ex-player.x, ey-player.y) <= reveal

        # Itens — apenas se dentro do alcance da lanterna
        for item in items:
            if not item.collected and visible(item.x, item.y):
                pygame.draw.circle(surface, item.color, mm(item.x, item.y), 2)

        # NPCs — sempre visíveis (zona segura)
        for npc in npcs:
            pygame.draw.circle(surface, YELLOW, mm(npc.x, npc.y), 3)

        # Mobs — apenas se visíveis
        for m in monsters:
            if not m.dead and visible(m.x, m.y):
                clr = (255, 80, 80) if m.monster_type=="boss" else RED
                r   = 4 if m.monster_type=="boss" else 3
                pygame.draw.circle(surface, clr, mm(m.x, m.y), r)

        # Player
        px, py = mm(player.x, player.y)
        pygame.draw.circle(surface, player.color, (px, py), 5)
        pygame.draw.circle(surface, WHITE,         (px, py), 5, 1)

        # Legenda
        for i,(txt,clr) in enumerate([("■ Você",player.color),("■ NPC",YELLOW),("■ Mob",RED)]):
            s = fonts.xxs.render(txt, True, clr)
            surface.blit(s, (self.x+2, self.y+self.h-10-(2-i)*11))

        title = fonts.xxs.render("MAPA", True, LIGHT_GRAY)
        surface.blit(title, (self.x+self.w//2-title.get_width()//2, self.y+2))
