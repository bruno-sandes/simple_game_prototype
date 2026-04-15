"""
entities/npc.py
"""
import math
import pygame
from config import NPC_INTERACT_RANGE, YELLOW, WHITE, BLACK
from entities.sprite import AnimatedSprite

class DialogueNode:
    def __init__(self, text: str, speaker: str = "NPC", choices: list = None, action=None):
        self.text = text
        self.speaker = speaker
        self.choices = choices or []   
        self.action = action           

    @property
    def is_leaf(self) -> bool:
        return len(self.choices) == 0

class DialogueTree:
    def __init__(self, root: DialogueNode):
        self.root = root
        self.current = root
        self.done = False

    def reset(self) -> None:
        self.current = self.root
        self.done = False

    def select(self, choice_idx: int):
        if self.done or choice_idx >= len(self.current.choices): return
        _label, next_node = self.current.choices[choice_idx]

        if self.current.action: self.current.action()

        if next_node is None:
            self.done = True
            self.current = self.root
        else:
            self.current = next_node
            if self.current.is_leaf:
                if self.current.action: self.current.action()
                self.done = True
                self.current = self.root

class NPC(AnimatedSprite):
    def __init__(self, x: float, y: float, name: str, tree: DialogueTree):
        super().__init__((220, 170, 100), x, y, size=20)
        self.name = name
        self.tree = tree
        self.interact_range = NPC_INTERACT_RANGE
        self._bob = 0.0

    def interact(self) -> None:
        self.tree.reset()

    def update(self, dt: float) -> None:
        self._bob += dt

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float, player_close: bool = False) -> None:
        sy_offset = int(math.sin(self._bob * 2) * 3)
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y) + sy_offset

        self._draw_character(surface, sx, sy, self.color)

        font_bold = pygame.font.SysFont("Arial", 13, bold=True)
        ns = font_bold.render(self.name, True, YELLOW)
        surface.blit(ns, (sx - ns.get_width() // 2, sy - self.size - 32))

        if player_close:
            font_hint = pygame.font.SysFont("Arial", 11)
            hint = font_hint.render("[E] Falar", True, WHITE)
            bw, bh = hint.get_width() + 10, hint.get_height() + 6
            bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            hx = sx - bw // 2
            hy = sy - self.size - 52
            surface.blit(bg, (hx, hy))
            surface.blit(hint, (hx + 5, hy + 3))

# FABRICA QUE INJETA NO INVENTÁRIO
def create_tutorial_npc(x: float, y: float, player_inventory) -> NPC:
    
    def give_potion():
        player_inventory.add("hp_potion", 1) # Adiciona item real!
        
    node_adeus = DialogueNode("Boa sorte na sua jornada!", speaker="Sábio")
    
    node_dica = DialogueNode(
        "Pressione I para abrir seu inventário. Pegue esta poção como ajuda!", 
        speaker="Sábio", action=give_potion,
        choices=[("Muito obrigado!", node_adeus)]
    )

    node_combate = DialogueNode(
        "Use o CLIQUE ESQUERDO para lançar magia! Colete itens brilhantes.", speaker="Sábio",
        choices=[("Entendi. Mais alguma dica?", node_dica)]
    )

    root = DialogueNode(
        "Olá, aventureiro! Este mundo está repleto de perigos...", speaker="Sábio",
        choices=[
            ("Como posso me defender?", node_combate),
            ("Estou com pressa, até logo!", node_adeus)
        ]
    )
    return NPC(x, y, "Sábio", DialogueTree(root))