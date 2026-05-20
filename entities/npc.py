"""
entities/npc.py — CORRECOES:
  1. SKILL_DAMAGE agora importado no topo do arquivo (era importado local causando NameError)
  2. Mercador verifica player.upgrade_count vs MAX_TOTAL_UPGRADES antes de vender
  3. Sage exibe cap de upgrades disponíveis
"""
import math, pygame
from config import (NPC_INTERACT_RANGE, YELLOW, WHITE, BLACK,
                    SHOP_PRICE_SPEED, SHOP_PRICE_FIRERATE, SHOP_PRICE_DAMAGE,
                    SHOP_PRICE_LANTERN, SHOP_PRICE_POTION, SHOP_PRICE_SKILL_RANGE,
                    LANTERN_DEFAULT_RADIUS, BOSS_UNLOCK_LEVEL,
                    SKILL_DAMAGE, PLAYER_SPEED,          # FIX: importado aqui
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


def make_sage(x, y, inventory, boss_callback=None):
    _g={"pot":False}
    def give():
        if not _g["pot"]: inventory.add("hp_potion",1); _g["pot"]=True; return "Sabio deu: Pocao de Vida!"
        return "Voce ja recebeu sua pocao."
    def challenge_boss():
        if boss_callback: boss_callback()
        return None

    leaf_bye    = DialogueNode("Boa sorte! Volte quando precisar.",speaker="Sabio Aldren")
    leaf_ctrl   = DialogueNode("WASD move. Clique Dir ataca. F=pocao. I=inventario. E=interagir. ESC=pausar.",speaker="Sabio Aldren")
    leaf_goal   = DialogueNode("Mate mobs p/ XP e moedas. Suba de nivel (ganha moedas). Invoque o Boss, derrote-o, pegue a Chave e use na Porta!",speaker="Sabio Aldren")
    leaf_level  = DialogueNode("Cada nivel concede +1 moeda. Use no Mercador para upgrades. Limite de upgrades existe: use com sabedoria!",speaker="Sabio Aldren")
    leaf_gem    = DialogueNode("Gemas=+50XP. Pergaminhos=+40XP. Espada=+dano permanente. Escudo=+HP max permanente.",speaker="Sabio Aldren")
    leaf_pot    = DialogueNode("Aqui esta sua pocao inicial!",speaker="Sabio Aldren",action=give)
    leaf_boss_ok= DialogueNode("O Boss foi invocado na zona de perigo. Boa sorte!",speaker="Sabio Aldren",action=challenge_boss)
    leaf_boss_no= DialogueNode(f"Voce precisa de nivel {BOSS_UNLOCK_LEVEL} para invocar o Boss.",speaker="Sabio Aldren")

    node_boss=DialogueNode("Deseja invocar o Boss deste andar? Ele dropa a Chave garantida!",speaker="Sabio Aldren",
        choices=[("Sim, quero enfrentar!",leaf_boss_ok),("Nao estou pronto.",leaf_boss_no)])
    node_ask=DialogueNode("O que deseja saber?",speaker="Sabio Aldren",
        choices=[("Como me controlo?",leaf_ctrl),("O que devo fazer?",leaf_goal),
                 ("Para que serve o nivel?",leaf_level),("Itens do chao?",leaf_gem),
                 ("Pode me dar algo?",leaf_pot),("Ate logo.",None)])
    root=DialogueNode("Bem-vindo! Sou o Sabio Aldren. Esta e sua zona segura.",speaker="Sabio Aldren",
        choices=[("Preciso de orientacao.",node_ask),
                 ("Invocar o Boss deste andar.",node_boss),
                 ("Estou bem, obrigado.",None)])
    return NPC(x,y,"Sabio Aldren",(80,160,200),DialogueTree(root))


def make_merchant(x, y, player):
    inv=player.inventory
    MAX=5   # max por atributo individual

    def _cap_check():
        """Retorna mensagem se o jogador atingiu o cap global de upgrades."""
        if player.upgrade_count >= MAX_TOTAL_UPGRADES:
            return f"Limite de {MAX_TOTAL_UPGRADES} upgrades atingido! Foco na estrategia."
        return None

    def _buy(cost, fn, lbl):
        def a():
            cap=_cap_check()
            if cap: return cap
            coins=inv.count("coin")
            if coins<cost: return f"Sem moedas! Precisa {cost}, tem {coins}."
            inv.remove("coin",cost)
            result=fn()
            if result and "maximo" not in result.lower():
                player.upgrade_count+=1   # conta upgrade bem-sucedido
            return result or f"{lbl} melhorado!"
        return a

    def up_spd():
        if player.speed>=PLAYER_SPEED+20*MAX: return "Velocidade maxima!"
        player.speed+=20; return f"Velocidade:{player.speed}"
    def up_cd():
        if player.skill_max_cd<=12: return "Cadencia maxima!"
        player.skill_max_cd=max(12,player.skill_max_cd-8); return f"Cadencia:{player.skill_max_cd}f"
    def up_dmg():
        if player.skill_damage>=SKILL_DAMAGE+10*MAX: return "Dano maximo!"
        player.skill_damage+=10; return f"Dano:{player.skill_damage}"
    def up_lan():
        if player.lantern_radius>=LANTERN_DEFAULT_RADIUS+40*MAX: return "Lanterna maxima!"
        player.lantern_radius+=40; return f"Lanterna:{player.lantern_radius}px"
    def up_range():
        if player.skill_radius>=15: return "Raio maximo!"
        player.skill_radius+=2; return f"Raio:{player.skill_radius}"
    def buy_pot():
        inv.add("hp_potion",1); return "Comprou Pocao de Vida!"

    leaf_bye=DialogueNode("Volte com moedas! Limite de upgrades disponivel.",speaker="Mercador Zek")
    leaf_spd   =DialogueNode(f"Velocidade +20. {SHOP_PRICE_SPEED}$",speaker="Mercador Zek",action=_buy(SHOP_PRICE_SPEED,up_spd,"Vel"))
    leaf_cd    =DialogueNode(f"Cadencia -8f. {SHOP_PRICE_FIRERATE}$",speaker="Mercador Zek",action=_buy(SHOP_PRICE_FIRERATE,up_cd,"Cad"))
    leaf_dmg   =DialogueNode(f"Dano +10. {SHOP_PRICE_DAMAGE}$",speaker="Mercador Zek",action=_buy(SHOP_PRICE_DAMAGE,up_dmg,"Dano"))
    leaf_lan   =DialogueNode(f"Lanterna +40px. {SHOP_PRICE_LANTERN}$",speaker="Mercador Zek",action=_buy(SHOP_PRICE_LANTERN,up_lan,"Lan"))
    leaf_rng   =DialogueNode(f"Raio magia +2. {SHOP_PRICE_SKILL_RANGE}$",speaker="Mercador Zek",action=_buy(SHOP_PRICE_SKILL_RANGE,up_range,"Raio"))
    leaf_pot   =DialogueNode(f"Pocao +40HP. {SHOP_PRICE_POTION}$",speaker="Mercador Zek",action=_buy(SHOP_PRICE_POTION,buy_pot,"Pot"))

    shop=DialogueNode("Upgrades (limite total na run!). O que deseja?",speaker="Mercador Zek",
        choices=[(f"Velocidade ({SHOP_PRICE_SPEED}$)",leaf_spd),
                 (f"Cadencia   ({SHOP_PRICE_FIRERATE}$)",leaf_cd),
                 (f"Dano magia ({SHOP_PRICE_DAMAGE}$)",leaf_dmg),
                 (f"Lanterna   ({SHOP_PRICE_LANTERN}$)",leaf_lan),
                 (f"Raio magia ({SHOP_PRICE_SKILL_RANGE}$)",leaf_rng),
                 (f"Pocao      ({SHOP_PRICE_POTION}$)",leaf_pot)])
    root=DialogueNode("Mercador Zek! Upgrades por moedas. Limite total existe!",speaker="Mercador Zek",
        choices=[("Ver loja.",shop),("Nao obrigado.",None)])
    return NPC(x,y,"Mercador Zek",(220,130,50),DialogueTree(root))
