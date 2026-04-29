"""
entities/npc.py
<<<<<<< Updated upstream
===============
Classe NPC — personagem não-jogável com diálogo e ação.

Comportamentos:
  - Flutuação suave (bob via seno)
  - Diálogo com múltiplas falas (avanço por tecla)
  - Entrega um item ao jogador na primeira conversa
  - Exibe dica [E] quando o jogador está próximo
=======

MUDANCAS:
  - Loja do mercador tem opcao "Sair da loja" (volta ao root)
  - Sábio tem "Sair" em todas as sub-árvores
  - DialogueTree: select() nunca fecha o diálogo diretamente —
    o fechamento é responsabilidade de _ev_dialogue em game.py
>>>>>>> Stashed changes
"""

import math
import pygame
<<<<<<< Updated upstream
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
=======
from config import (
    NPC_INTERACT_RANGE, YELLOW, WHITE, BLACK,
    SHOP_PRICE_SPEED, SHOP_PRICE_FIRERATE,
    SHOP_PRICE_DAMAGE, SHOP_PRICE_LANTERN, SHOP_PRICE_POTION,
    LANTERN_DEFAULT_RADIUS,
)
from entities.sprite import AnimatedSprite


# ══════════════════════════════════════════════════════
# ÁRVORE DE DIÁLOGO
# ══════════════════════════════════════════════════════

class DialogueNode:
    def __init__(self, text: str, speaker: str = "NPC",
                 choices: list = None, action=None):
        self.text    = text
        self.speaker = speaker
        self.choices = choices or []
        self.action  = action

    @property
    def is_leaf(self) -> bool:
        return len(self.choices) == 0


class DialogueTree:
    def __init__(self, root: DialogueNode):
        self.root     = root
        self.current  = root
        self.done     = False
        self.last_msg = None

    def reset(self) -> None:
        self.current  = self.root
        self.done     = False
        self.last_msg = None

    def select(self, choice_idx: int) -> None:
        """
        Navega para o próximo nó.
        Se next_node é None → fecha o diálogo (opção "Sair" explícita).
        Se next_node é leaf → vai até lá (texto exibido até ENTER/E).
        Nunca fecha o diálogo quando vai para um nó com texto, apenas
        quando next_node é None.
        """
        if self.done or choice_idx >= len(self.current.choices):
            return

        _label, next_node = self.current.choices[choice_idx]

        if self.current.action:
            msg = self.current.action()
            if msg:
                self.last_msg = msg

        if next_node is None:
            # Opção de fechar explicitamente
            self.done    = True
            self.current = self.root
            return

        self.current = next_node

        if self.current.action:
            msg = self.current.action()
            if msg:
                self.last_msg = msg
        # Não marca done=True — _ev_dialogue faz isso ao detectar is_leaf + ENTER


# ══════════════════════════════════════════════════════
# CLASSE NPC
# ══════════════════════════════════════════════════════

class NPC(AnimatedSprite):
    def __init__(self, x: float, y: float,
                 name: str, color: tuple, tree: DialogueTree):
        super().__init__(color, x, y, size=20)
        self.name           = name
        self.tree           = tree
        self.interact_range = NPC_INTERACT_RANGE
        self._bob           = 0.0
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
    # ------------------------------------------------------------------ #
    #  Desenho                                                             #
    # ------------------------------------------------------------------ #
    def draw(self, surface: pygame.Surface,
             cam_x: float, cam_y: float,
             player_close: bool = False) -> None:
        # Flutuação vertical suave
        sy_offset = int(math.sin(self._bob * 2) * 3)
=======
    def draw(self, surface: pygame.Surface,
             cam_x: float, cam_y: float,
             player_close: bool = False) -> None:
        offset = int(math.sin(self._bob * 2) * 3)
>>>>>>> Stashed changes
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y) + offset

        self._draw_character(surface, sx, sy, self.color)

<<<<<<< Updated upstream
        font_bold = pygame.font.SysFont("Arial", 13, bold=True)
        font_hint = pygame.font.SysFont("Arial", 11)

        # Nome (amarelo, acima)
        ns = font_bold.render(self.name, True, YELLOW)
=======
        font_b = pygame.font.SysFont("Arial", 13, bold=True)
        ns = font_b.render(self.name, True, YELLOW)
>>>>>>> Stashed changes
        surface.blit(ns, (sx - ns.get_width() // 2, sy - self.size - 32))

        # Dica de interação quando perto
        if player_close:
<<<<<<< Updated upstream
            hint = font_hint.render("[E] Falar", True, WHITE)
=======
            fh = pygame.font.SysFont("Arial", 11)
            hint = fh.render("[E] Falar", True, WHITE)
>>>>>>> Stashed changes
            bw, bh = hint.get_width() + 10, hint.get_height() + 6
            bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            hx, hy = sx - bw // 2, sy - self.size - 52
            surface.blit(bg, (hx, hy))
<<<<<<< Updated upstream
            surface.blit(hint, (hx + 5, hy + 3))
=======
            surface.blit(hint, (hx + 5, hy + 3))


# ══════════════════════════════════════════════════════
# FÁBRICAS
# ══════════════════════════════════════════════════════

def make_sage(x: float, y: float, inventory) -> NPC:
    _given = {"potion": False}

    def give_potion():
        if not _given["potion"]:
            inventory.add("hp_potion", 1)
            _given["potion"] = True
            return "Sabio deu: Pocao de Vida!"
        return "Voce ja recebeu sua pocao inicial."

    leaf_bye      = DialogueNode("Boa sorte! Volte quando precisar.", speaker="Sabio Aldren")
    leaf_controls = DialogueNode(
        "WASD move. Clique Dir ataca. F usa pocao. I abre inventario. E interage. ESC fecha dialogo.",
        speaker="Sabio Aldren"
    )
    leaf_danger   = DialogueNode(
        "Mate mobs para XP e moedas. Subir de nivel da moedas extras. Ache a Chave e use na Porta!",
        speaker="Sabio Aldren"
    )
    leaf_level    = DialogueNode(
        "Cada nivel que voce sobe da +1 moeda. Use-as no Mercador Zek para ficar mais forte!",
        speaker="Sabio Aldren"
    )
    leaf_gem      = DialogueNode(
        "Gemas dao +10 XP ao serem coletadas. Acumule XP para subir de nivel e ganhar moedas!",
        speaker="Sabio Aldren"
    )
    leaf_potion   = DialogueNode(
        "Aqui esta sua pocao inicial. Pocoes recuperam 40 HP. Compre mais no Mercador com moedas.",
        speaker="Sabio Aldren",
        action=give_potion
    )

    node_ask = DialogueNode(
        "O que deseja saber?",
        speaker="Sabio Aldren",
        choices=[
            ("Como me controlo?",        leaf_controls),
            ("O que devo fazer?",         leaf_danger),
            ("Para que serve o nivel?",   leaf_level),
            ("O que sao as gemas?",       leaf_gem),
            ("Pode me dar algo?",         leaf_potion),
            ("Ate logo.",                 None),   # None = fecha dialogo
        ]
    )
    root = DialogueNode(
        "Bem-vindo! Sou o Sabio Aldren. Este vilarejo e seguro — fora das paredes ha perigo.",
        speaker="Sabio Aldren",
        choices=[
            ("Preciso de orientacao.", node_ask),
            ("Estou bem, obrigado.",   None),
        ]
    )
    return NPC(x, y, "Sabio Aldren", (80, 160, 200), DialogueTree(root))


def make_merchant(x: float, y: float, player) -> NPC:
    inv = player.inventory
    MAX_UP = 5

    def _buy(cost, apply_fn, label):
        def action():
            coins = inv.count("coin")
            if coins < cost:
                return f"Sem moedas! Precisa de {cost}, tem {coins}."
            inv.remove("coin", cost)
            result = apply_fn()
            return result or f"{label} melhorado!"
        return action

    def up_speed():
        if player.speed >= 160 + 20 * MAX_UP:
            return "Velocidade ja no maximo!"
        player.speed += 20
        return f"Velocidade: {player.speed}"

    def up_firerate():
        if player.skill_max_cd <= 15:
            return "Cadencia ja no maximo!"
        player.skill_max_cd = max(15, player.skill_max_cd - 8)
        return f"Cadencia: {player.skill_max_cd} frames"

    def up_damage():
        if player.skill_damage >= 30 + 10 * MAX_UP:
            return "Dano ja no maximo!"
        player.skill_damage += 10
        return f"Dano: {player.skill_damage}"

    def up_lantern():
        if player.lantern_radius >= LANTERN_DEFAULT_RADIUS + 40 * MAX_UP:
            return "Lanterna ja no maximo!"
        player.lantern_radius += 40
        return f"Raio lanterna: {player.lantern_radius}px"

    def buy_potion():
        inv.add("hp_potion", 1)
        return "Comprou Pocao de Vida!"

    leaf_bye = DialogueNode(
        "Volte quando tiver moedas! Orcs e Goblins dropam chaves.", speaker="Mercador Zek"
    )

    # Folhas da loja (exibem resultado da compra)
    leaf_speed    = DialogueNode(f"Velocidade +20. Custo: {SHOP_PRICE_SPEED}$.",
                                  speaker="Mercador Zek",
                                  action=_buy(SHOP_PRICE_SPEED,    up_speed,    "Velocidade"))
    leaf_firerate = DialogueNode(f"Cadencia de disparo -8 frames. Custo: {SHOP_PRICE_FIRERATE}$.",
                                  speaker="Mercador Zek",
                                  action=_buy(SHOP_PRICE_FIRERATE, up_firerate, "Cadencia"))
    leaf_damage   = DialogueNode(f"Dano da magia +10. Custo: {SHOP_PRICE_DAMAGE}$.",
                                  speaker="Mercador Zek",
                                  action=_buy(SHOP_PRICE_DAMAGE,   up_damage,   "Dano"))
    leaf_lantern  = DialogueNode(f"Raio de visao +40px. Custo: {SHOP_PRICE_LANTERN}$.",
                                  speaker="Mercador Zek",
                                  action=_buy(SHOP_PRICE_LANTERN,  up_lantern,  "Lanterna"))
    leaf_potion   = DialogueNode(f"Pocao de Vida (+40 HP). Custo: {SHOP_PRICE_POTION}$.",
                                  speaker="Mercador Zek",
                                  action=_buy(SHOP_PRICE_POTION,   buy_potion,  "Pocao"))

    node_shop = DialogueNode(
        "Loja de upgrades — permanentes nesta run!",
        speaker="Mercador Zek",
        choices=[
            (f"Velocidade     ({SHOP_PRICE_SPEED}$)",    leaf_speed),
            (f"Cadencia       ({SHOP_PRICE_FIRERATE}$)", leaf_firerate),
            (f"Dano magia     ({SHOP_PRICE_DAMAGE}$)",   leaf_damage),
            (f"Lanterna       ({SHOP_PRICE_LANTERN}$)",  leaf_lantern),
            (f"Pocao de Vida  ({SHOP_PRICE_POTION}$)",   leaf_potion),
            ("Sair da loja",                              None),   # voltar / fechar
        ]
    )
    root = DialogueNode(
        "Mercador Zek! Upgrades permanentes por moedas. Orcs e Goblins dropam chaves!",
        speaker="Mercador Zek",
        choices=[
            ("Ver loja.", node_shop),
            ("Nao, obrigado.", None),
        ]
    )
    return NPC(x, y, "Mercador Zek", (220, 130, 50), DialogueTree(root))
>>>>>>> Stashed changes
