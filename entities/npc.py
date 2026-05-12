"""entities/npc.py — Sábio Aldren + Mercador Zek com DialogueTree."""
import math, pygame
from config import (NPC_INTERACT_RANGE, YELLOW, WHITE, BLACK,
                    SHOP_PRICE_SPEED, SHOP_PRICE_FIRERATE, SHOP_PRICE_DAMAGE,
                    SHOP_PRICE_LANTERN, SHOP_PRICE_POTION, SHOP_PRICE_SKILL_RANGE,
                    LANTERN_DEFAULT_RADIUS)
from entities.sprite import AnimatedSprite

class DialogueNode:
    def __init__(self, text, speaker="NPC", choices=None, action=None):
        self.text=text; self.speaker=speaker
        self.choices=choices or []; self.action=action
    @property
    def is_leaf(self): return len(self.choices)==0

class DialogueTree:
    def __init__(self, root):
        self.root=root; self.current=root; self.done=False; self.last_msg=None
    def reset(self):
        self.current=self.root; self.done=False; self.last_msg=None
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
    def __init__(self,x,y,name,color,tree):
        super().__init__(color,x,y,size=20)
        self.name=name; self.tree=tree
        self.interact_range=NPC_INTERACT_RANGE; self._bob=0.0
    def interact(self): self.tree.reset()
    def update(self,dt): self._bob+=dt
    def draw(self,surface,cam_x,cam_y,player_close=False):
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

def make_sage(x,y,inventory,boss_callback=None):
    """Sábio Aldren — tutorial + opção de invocar boss."""
    _g={"pot":False}
    def give():
        if not _g["pot"]:
            inventory.add("hp_potion",1); _g["pot"]=True
            return "Sabio deu: Pocao de Vida!"
        return "Voce ja recebeu sua pocao."
    def challenge_boss():
        if boss_callback: boss_callback()
        return "O Boss foi invocado! Derrote-o para conseguir a Chave!"

    leaf_bye    = DialogueNode("Boa sorte! Volte quando precisar.",speaker="Sabio Aldren")
    leaf_ctrl   = DialogueNode("WASD move. Clique Dir ataca. F=pocao. I=inventario. E=interagir. ESC=pausar.",speaker="Sabio Aldren")
    leaf_goal   = DialogueNode("Mate mobs para XP e moedas. Suba de nivel para ganhar moedas. Derrote o Boss para pegar a Chave e passar pela Porta!",speaker="Sabio Aldren")
    leaf_level  = DialogueNode("Cada nivel sobe 1 moeda. Use no Mercador para ficar mais forte!",speaker="Sabio Aldren")
    leaf_gem    = DialogueNode("Gemas dao +50 XP ao coletar. Pergaminhos dao +40 XP. Espada +dano. Escudo +HP.",speaker="Sabio Aldren")
    leaf_pot    = DialogueNode("Aqui esta sua pocao inicial!",speaker="Sabio Aldren",action=give)
    leaf_boss   = DialogueNode("O Boss foi invocado! Ele esta longe, na zona de perigo. Boa sorte!",speaker="Sabio Aldren",action=challenge_boss)
    leaf_boss_no= DialogueNode("Entendido. Volte quando estiver pronto. Precisa de nivel 2 para invocar o Boss.",speaker="Sabio Aldren")

    node_boss = DialogueNode("Deseja invocar o Boss deste andar? Ele dropa a Chave garantida!",speaker="Sabio Aldren",
        choices=[("Sim, quero enfrentar!",leaf_boss),("Ainda nao estou pronto.",leaf_boss_no)])
    node_ask = DialogueNode("O que deseja saber?",speaker="Sabio Aldren",
        choices=[
            ("Como me controlo?",leaf_ctrl),
            ("O que devo fazer?",leaf_goal),
            ("Para que serve o nivel?",leaf_level),
            ("Gemas/itens do chao?",leaf_gem),
            ("Pode me dar algo?",leaf_pot),
            ("Ate logo.",None)])
    root = DialogueNode("Bem-vindo! Sou o Sabio Aldren. Este vilarejo e sua zona segura.",speaker="Sabio Aldren",
        choices=[
            ("Preciso de orientacao.",node_ask),
            ("Invocar o Boss deste andar.",node_boss),
            ("Estou bem, obrigado.",None)])
    return NPC(x,y,"Sabio Aldren",(80,160,200),DialogueTree(root))

def make_merchant(x,y,player):
    """Mercador Zek — loja com 6 upgrades + opção sair."""
    inv=player.inventory; MAX=5
    def _buy(cost,fn,lbl):
        def a():
            c=inv.count("coin")
            if c<cost: return f"Sem moedas! Precisa {cost}, tem {c}."
            inv.remove("coin",cost); r=fn()
            return r or f"{lbl} melhorado!"
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
        player.skill_radius+=2; return f"Raio magia:{player.skill_radius}"
    def buy_pot():
        inv.add("hp_potion",1); return "Comprou Pocao de Vida!"

    from config import SKILL_DAMAGE as SD, PLAYER_SPEED
    leaf_bye  = DialogueNode("Volte com moedas!",speaker="Mercador Zek")
    leaf_spd  = DialogueNode(f"Velocidade +20. Custo:{SHOP_PRICE_SPEED}$",speaker="Mercador Zek",action=_buy(SHOP_PRICE_SPEED,up_spd,"Vel"))
    leaf_cd   = DialogueNode(f"Cadencia -8f. Custo:{SHOP_PRICE_FIRERATE}$",speaker="Mercador Zek",action=_buy(SHOP_PRICE_FIRERATE,up_cd,"Cad"))
    leaf_dmg  = DialogueNode(f"Dano +10. Custo:{SHOP_PRICE_DAMAGE}$",speaker="Mercador Zek",action=_buy(SHOP_PRICE_DAMAGE,up_dmg,"Dano"))
    leaf_lan  = DialogueNode(f"Lanterna +40px. Custo:{SHOP_PRICE_LANTERN}$",speaker="Mercador Zek",action=_buy(SHOP_PRICE_LANTERN,up_lan,"Lan"))
    leaf_rng  = DialogueNode(f"Raio magia +2. Custo:{SHOP_PRICE_SKILL_RANGE}$",speaker="Mercador Zek",action=_buy(SHOP_PRICE_SKILL_RANGE,up_range,"Raio"))
    leaf_pot  = DialogueNode(f"Pocao +40HP. Custo:{SHOP_PRICE_POTION}$",speaker="Mercador Zek",action=_buy(SHOP_PRICE_POTION,buy_pot,"Pot"))

    shop = DialogueNode("Upgrades permanentes! O que deseja?",speaker="Mercador Zek",
        choices=[
            (f"Velocidade ({SHOP_PRICE_SPEED}$)",leaf_spd),
            (f"Cadencia   ({SHOP_PRICE_FIRERATE}$)",leaf_cd),
            (f"Dano magia ({SHOP_PRICE_DAMAGE}$)",leaf_dmg),
            (f"Lanterna   ({SHOP_PRICE_LANTERN}$)",leaf_lan),
            (f"Raio magia ({SHOP_PRICE_SKILL_RANGE}$)",leaf_rng),
            (f"Pocao      ({SHOP_PRICE_POTION}$)",leaf_pot)])
    root = DialogueNode("Mercador Zek! Upgrades por moedas.",speaker="Mercador Zek",
        choices=[("Ver loja.",shop),("Nao obrigado.",None)])
    return NPC(x,y,"Mercador Zek",(220,130,50),DialogueTree(root))
