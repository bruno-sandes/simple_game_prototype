"""
entities/npc.py
===============
Classe NPC — personagem não-jogável com diálogo e ação.

Comportamentos:
  - Flutuação suave (bob via seno)
  - Diálogo com múltiplas falas (avanço por tecla)
  - Entrega um item ao jogador na primeira conversa
  - Exibe dica [E] quando o jogador está próximo
"""

import math
import pygame
from config import NPC_INTERACT_RANGE, YELLOW, WHITE, BLACK
from entities.base import AnimatedSprite


class NPC(AnimatedSprite):
    """
    Crie instâncias com posição, nome e (opcionalmente) lista de diálogos.
    O Game verifica a distância e chama .interact() ao pressionar E.
    """

    DEFAULT_DIALOGUES = [
        "Olá, aventureiro! Bem-vindo a estas terras.",
        "Este mundo está repleto de criaturas perigosas...",
        "Use o CLIQUE ESQUERDO para lançar sua magia!",
        "Colete os itens brilhantes espalhados pelo mapa.",
        "Pressione I para o inventário e F para usar poções.",
        "Toma este item — vai precisar na jornada. [Poção de Vida]",
    ]

    def __init__(self, x: float, y: float,
                 name: str = "Aldeão Sábio",
                 dialogues: list[str] | None = None):
        super().__init__((220, 170, 100), x, y, size=20)
        self.name           = name
        self.dialogues      = dialogues or self.DEFAULT_DIALOGUES
        self.interact_range = NPC_INTERACT_RANGE
        self.in_dialogue    = False
        self.dialogue_idx   = 0
        self.gave_item      = False   # item entregue apenas uma vez
        self._bob           = 0.0    # timer da flutuação

    # ------------------------------------------------------------------ #
    #  Diálogo                                                             #
    # ------------------------------------------------------------------ #
    def interact(self) -> None:
        """Inicia o diálogo do início."""
        self.in_dialogue  = True
        self.dialogue_idx = 0

    def advance(self) -> bool:
        """
        Avança para a próxima fala.
        Retorna True se o diálogo chegou ao fim.
        """
        self.dialogue_idx += 1
        if self.dialogue_idx >= len(self.dialogues):
            self.in_dialogue  = False
            self.dialogue_idx = 0
            return True
        return False

    @property
    def current_line(self) -> str:
        idx = min(self.dialogue_idx, len(self.dialogues) - 1)
        return self.dialogues[idx]

    @property
    def progress(self) -> str:
        return f"{self.dialogue_idx + 1}/{len(self.dialogues)}"

    # ------------------------------------------------------------------ #
    #  Update                                                              #
    # ------------------------------------------------------------------ #
    def update(self, dt: float) -> None:
        self._bob += dt

    # ------------------------------------------------------------------ #
    #  Desenho                                                             #
    # ------------------------------------------------------------------ #
    def draw(self, surface: pygame.Surface,
             cam_x: float, cam_y: float,
             player_close: bool = False) -> None:
        # Flutuação vertical suave
        sy_offset = int(math.sin(self._bob * 2) * 3)
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y) + sy_offset

        self._draw_character(surface, sx, sy, self.color)

        font_bold = pygame.font.SysFont("Arial", 13, bold=True)
        font_hint = pygame.font.SysFont("Arial", 11)

        # Nome (amarelo, acima)
        ns = font_bold.render(self.name, True, YELLOW)
        surface.blit(ns, (sx - ns.get_width() // 2, sy - self.size - 32))

        # Dica de interação quando perto
        if player_close:
            hint = font_hint.render("[E] Falar", True, WHITE)
            bw, bh = hint.get_width() + 10, hint.get_height() + 6
            bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            hx = sx - bw // 2
            hy = sy - self.size - 52
            surface.blit(bg, (hx, hy))
            surface.blit(hint, (hx + 5, hy + 3))