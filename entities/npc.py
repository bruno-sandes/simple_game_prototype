"""
entities/npc.py — CORRECOES:
  1. Poção do Sábio disponível a cada andar (não só uma vez)
  2. Nova opção explicando boss e andares progressivamente
  3. Texto de invocação informa nível necessário e dificuldade
  4. SKILL_DAMAGE e PLAYER_SPEED importados no topo (fix NameError)
"""
import math, pygame
from config import (NPC_INTERACT_RANGE, YELLOW, WHITE, BLACK,
                    SHOP_PRICE_SPEED, SHOP_PRICE_FIRERATE, SHOP_PRICE_DAMAGE,
                    SHOP_PRICE_LANTERN, SHOP_PRICE_POTION, SHOP_PRICE_SKILL_RANGE,
                    LANTERN_DEFAULT_RADIUS, BOSS_UNLOCK_LEVEL,
                    SKILL_DAMAGE, PLAYER_SPEED,
                    MAX_TOTAL_UPGRADES)
from entities.sprite import AnimatedSprite


class DialogueNode:
    def __init__(self, text, speaker="NPC", choices=None, action=None):
        self.text=text; self.speaker=speaker; self.choices=choices or []; self.action=action
    @property
    def is_leaf(self): return len(self.choices)==0


class DialogueTree:
    def __init__(self, root):
        self.root=root; self.current=root; self.done=False; self.last_msg=None
    def reset(self): self.current=self.root; self.done=False; self.last_msg=None
    def select(self, idx):
        if self.done or idx>=len(self.current.choices): return
        _,nxt=self.current.choices[idx]
        if self.current.action:
            m=self.current.action()
            if m: self.last_msg=m
        if nxt is None:
            self.done=True; self.current=self.root; return
        self.current=nxt
        if self.current.action:
            m=self.current.action()
            if m: self.last_msg=m


class NPC(AnimatedSprite):
    def __init__(self, x, y, name, color, tree):
        super().__init__(color, x, y, size=20)
        self.name=name; self.tree=tree; self.interact_range=NPC_INTERACT_RANGE; self._bob=0.0
    def interact(self): self.tree.reset()
    def update(self, dt): self._bob+=dt
    def draw(self, surface, cam_x, cam_y, player_close=False):
        off=int(math.sin(self._bob*2)*3)
        sx,sy=int(self.x-cam_x),int(self.y-cam_y)+off
        self._draw_character(surface,sx,sy,self.color)
        fb=pygame.font.SysFont("Arial",13,bold=True)
        ns=fb.render(self.name,True,YELLOW)
        surface.blit(ns,(sx-ns.get_width()//2,sy-self.size-32))
        if player_close:
            fh=pygame.font.SysFont("Arial",11)
            hint=fh.render("[E] Falar",True,WHITE)
            bw,bh=hint.get_width()+10,hint.get_height()+6
            bg=pygame.Surface((bw,bh),pygame.SRCALPHA); bg.fill((0,0,0,160))
            hx,hy=sx-bw//2,sy-self.size-52
            surface.blit(bg,(hx,hy)); surface.blit(hint,(hx+5,hy+3))


def make_sage(x, y, inventory, boss_callback=None, get_floor=None):
    """
    Sábio Aldren.
    get_floor: callable() que retorna o andar atual (para poção por andar).
    """
    # Poção disponível ONCE PER FLOOR (tracking por andar)
    _last_floor_given = {"floor": 0}

    def give_potion():
        current_floor = get_floor() if get_floor else 1
        if _last_floor_given["floor"] >= current_floor:
            return "Voce ja recebeu a pocao deste andar. Volte no proximo!"
        inventory.add("hp_potion", 1)
        _last_floor_given["floor"] = current_floor
        return f"Tome esta pocao do Andar {current_floor}! Boa sorte!"

    def challenge_boss():
        if boss_callback: boss_callback()
        return None

    leaf_bye     = DialogueNode("Boa sorte! Volte quando precisar.",speaker="Sabio Aldren")
    leaf_ctrl    = DialogueNode(
        "WASD move. Clique Dir ataca. F=pocao. I=inventario. E=interagir. ESC=pausar.",
        speaker="Sabio Aldren")
    leaf_goal    = DialogueNode(
        "Mate mobs p/ XP e moedas. Suba de nivel (ganha moeda). Invoque o Boss, "
        "derrote-o, pegue a Chave e use na Porta para avancar de andar!",
        speaker="Sabio Aldren")
    leaf_level   = DialogueNode(
        "Cada nivel concede +1 moeda para o Mercador. Limite de upgrades: "
        f"{MAX_TOTAL_UPGRADES} no total. Use com estrategia!",
        speaker="Sabio Aldren")
    leaf_itens   = DialogueNode(
        "Gemas=+50XP. Pergaminhos=+40XP. Espada=+dano permanente. Escudo=+HP max.",
        speaker="Sabio Aldren")
    leaf_pot     = DialogueNode(
        "Aqui esta uma Pocao de Vida (+40 HP). Ganho 1 por andar!",
        speaker="Sabio Aldren", action=give_potion)

    # Guia do boss e andares
    leaf_boss_guide = DialogueNode(
        f"O Boss guarda a Chave de cada andar. Voce precisa de nivel {BOSS_UNLOCK_LEVEL} "
        "para invoca-lo via dialogo. Cada andar o Boss fica mais forte e rapido — "
        "no andar 2 ele da DASH, no 3 invoca minions! "
        "Compre upgrades antes de enfrenta-lo.",
        speaker="Sabio Aldren")
    leaf_andares = DialogueNode(
        "Andar 1: apenas Slimes e Goblins. "
        "Andar 2: Orcs aparecem, Boss com Dash. "
        "Andar 3+: Boss invoca Slimes, mobs muito mais fortes. "
        "Compre Lanterna no Mercador — sem ela fica cego na escuridao!",
        speaker="Sabio Aldren")

    leaf_boss_ok = DialogueNode(
        "O Boss foi invocado fora da zona segura. Ele se aproxima... Boa sorte!",
        speaker="Sabio Aldren", action=challenge_boss)
    leaf_boss_no = DialogueNode(
        f"Entendido. Voce precisa de nivel {BOSS_UNLOCK_LEVEL} e upgrades suficientes. "
        "Compre Velocidade e Dano no Mercador antes de enfrentar!",
        speaker="Sabio Aldren")

    node_boss  = DialogueNode(
        f"Invocar o Boss? Ele esta mais forte a cada andar. "
        f"Recomendado: nivel {BOSS_UNLOCK_LEVEL}+ e pelo menos 3 upgrades.",
        speaker="Sabio Aldren",
        choices=[("Sim, estou pronto!", leaf_boss_ok),
                 ("Ainda nao estou pronto.", leaf_boss_no)])

    node_guia  = DialogueNode("O que deseja saber sobre a progressao?", speaker="Sabio Aldren",
        choices=[("Como funciona o Boss?", leaf_boss_guide),
                 ("O que muda em cada andar?", leaf_andares),
                 ("Voltar.", None)])

    node_ask   = DialogueNode("O que deseja saber?", speaker="Sabio Aldren",
        choices=[
            ("Como me controlo?",                leaf_ctrl),
            ("O que devo fazer?",                leaf_goal),
            ("Para que serve o nivel?",          leaf_level),
            ("Itens do chao?",                   leaf_itens),
            ("Guia de boss e andares.",          node_guia),
            ("Ate logo.",                        None)])

    root = DialogueNode(
        "Bem-vindo! Sou o Sabio Aldren. Esta e sua zona segura.",
        speaker="Sabio Aldren",
        choices=[
            ("Preciso de orientacao.",           node_ask),
            ("Quero minha pocao do andar.",      leaf_pot),
            ("Invocar o Boss deste andar.",      node_boss),
            ("Estou bem, obrigado.",             None)])

    return NPC(x, y, "Sabio Aldren", (80, 160, 200), DialogueTree(root))


def make_merchant(x, y, player):
    """Mercador Zek — 6 upgrades com cap global MAX_TOTAL_UPGRADES."""
    inv = player.inventory
    MAX = 5

    def _cap_check():
        if player.upgrade_count >= MAX_TOTAL_UPGRADES:
            return f"Limite de {MAX_TOTAL_UPGRADES} upgrades atingido!"
        return None

    def _buy(cost, fn, lbl):
        def a():
            cap = _cap_check()
            if cap: return cap
            coins = inv.count("coin")
            if coins < cost: return f"Sem moedas! Precisa {cost}, tem {coins}."
            inv.remove("coin", cost)
            result = fn()
            if result and "maximo" not in result.lower():
                player.upgrade_count += 1
            return result or f"{lbl} melhorado!"
        return a

    def up_spd():
        if player.speed >= PLAYER_SPEED+20*MAX: return "Velocidade maxima!"
        player.speed += 20; return f"Velocidade:{player.speed}"
    def up_cd():
        if player.skill_max_cd <= 12: return "Cadencia maxima!"
        player.skill_max_cd = max(12, player.skill_max_cd-8); return f"Cadencia:{player.skill_max_cd}f"
    def up_dmg():
        if player.skill_damage >= SKILL_DAMAGE+10*MAX: return "Dano maximo!"
        player.skill_damage += 10; return f"Dano:{player.skill_damage}"
    def up_lan():
        if player.lantern_radius >= LANTERN_DEFAULT_RADIUS+40*MAX: return "Lanterna maxima!"
        player.lantern_radius += 40; return f"Lanterna:{player.lantern_radius}px"
    def up_range():
        if player.skill_radius >= 15: return "Raio maximo!"
        player.skill_radius += 2; return f"Raio:{player.skill_radius}"
    def buy_pot():
        inv.add("hp_potion", 1); return "Comprou Pocao de Vida!"

    leaf_bye  = DialogueNode("Volte com moedas!", speaker="Mercador Zek")
    leaf_spd  = DialogueNode(f"Vel +20. {SHOP_PRICE_SPEED}$", speaker="Mercador Zek", action=_buy(SHOP_PRICE_SPEED, up_spd, "Vel"))
    leaf_cd   = DialogueNode(f"Cad -8f. {SHOP_PRICE_FIRERATE}$", speaker="Mercador Zek", action=_buy(SHOP_PRICE_FIRERATE, up_cd, "Cad"))
    leaf_dmg  = DialogueNode(f"Dano +10. {SHOP_PRICE_DAMAGE}$", speaker="Mercador Zek", action=_buy(SHOP_PRICE_DAMAGE, up_dmg, "Dano"))
    leaf_lan  = DialogueNode(f"Lanterna +40px. {SHOP_PRICE_LANTERN}$", speaker="Mercador Zek", action=_buy(SHOP_PRICE_LANTERN, up_lan, "Lan"))
    leaf_rng  = DialogueNode(f"Raio +2. {SHOP_PRICE_SKILL_RANGE}$", speaker="Mercador Zek", action=_buy(SHOP_PRICE_SKILL_RANGE, up_range, "Raio"))
    leaf_pot  = DialogueNode(f"Pocao +40HP. {SHOP_PRICE_POTION}$", speaker="Mercador Zek", action=_buy(SHOP_PRICE_POTION, buy_pot, "Pot"))

    shop = DialogueNode(f"Loja (limite: {MAX_TOTAL_UPGRADES} upgrades/run):", speaker="Mercador Zek",
        choices=[
            (f"Velocidade  ({SHOP_PRICE_SPEED}$)",    leaf_spd),
            (f"Cadencia    ({SHOP_PRICE_FIRERATE}$)", leaf_cd),
            (f"Dano magia  ({SHOP_PRICE_DAMAGE}$)",   leaf_dmg),
            (f"Lanterna    ({SHOP_PRICE_LANTERN}$)",  leaf_lan),
            (f"Raio magia  ({SHOP_PRICE_SKILL_RANGE}$)", leaf_rng),
            (f"Pocao Vida  ({SHOP_PRICE_POTION}$)",   leaf_pot)])

    root = DialogueNode("Mercador Zek! Upgrades por moedas.", speaker="Mercador Zek",
        choices=[("Ver loja.", shop), ("Nao obrigado.", None)])

    return NPC(x, y, "Mercador Zek", (220, 130, 50), DialogueTree(root))
