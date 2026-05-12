"""game.py — loop principal e máquina de estados. Versão limpa sem conflitos de merge."""
import random, math, pygame
from config import (
    SCREEN_W,SCREEN_H,FPS,TITLE,MAP_W,MAP_H,TILE_SIZE,
    STATE_CUSTOMIZE,STATE_PLAYING,STATE_DIALOGUE,STATE_INVENTORY,STATE_GAMEOVER,STATE_PAUSE,
    WHITE,BLACK,YELLOW,RED,GRAY,LIGHT_GRAY,
    MOB_AGGRO_RANGE,MOB_RESPAWN_COUNT,
    FLOOR_MOB_BASE,FLOOR_MOB_STEP,FLOOR_DMG_MULT,
    BOSS_UNLOCK_LEVEL,MOB_SPAWN_MIN_DIST,MOB_SPAWN_MAX_DIST,
    ITEM_EFFECTS,GEM_XP_VALUE,TILE_DOOR,TILE_FLOOR,
)
from config import BOSS_UNLOCK_LEVEL

from UI.fonts     import init_fonts, fonts
from UI.hud       import draw_hud
from UI.map       import MiniMap
from UI.dialogue  import draw_dialogue
from UI.inventory import draw_inventory

from entities         import Player, Mob
from entities.mob     import Boss
from entities.npc     import make_sage, make_merchant
from world            import World, Item, Particle
from world.lantern    import Lantern

from screens.custom    import CustomizeScreen
from screens.movement  import MovementController
from screens.animation import ScreenFade, LevelUpEffect
from screens.pause_menu import PauseMenu

from systems.inventory_manager import InventoryManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode((SCREEN_W,SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock=pygame.time.Clock()
        init_fonts()

        self.state          = STATE_CUSTOMIZE
        self._custom_screen = CustomizeScreen()
        self._fade          = None
        self._next_state    = None

        self.player=None; self.world=None
        self.npcs=[]; self.mobs=[]; self.items=[]
        self.particles=[]; self.messages=[]
        self.active_npc=None; self.show_inv=False
        self.cam_x=self.cam_y=0.0
        self.floor=1; self.boss=None
        self._boss_reward_given=False
        self._boss_requested   =False   # flag: sage pediu invocar boss

        self._movement  = None
        self._minimap   = MiniMap(SCREEN_W-165,10,155,130)
        self._lvl_up    = None
        self._lantern   = Lantern()
        self._pause_menu= PauseMenu()

    # ── Setup ────────────────────────────────────────────────────────
    def _setup_world(self,name,color):
        self.floor=1
        self._build_floor(name,color,first=True)

    def _build_floor(self,name=None,color=None,first=False):
        """Constrói/reconstrói o mapa e entidades do andar atual."""
        self.world     = World(seed=random.randint(1,99999))
        self._movement = MovementController(self.world)
        cx,cy          = self.world.safe_zone_center_px()

        if first:
            self.player            = Player(cx,cy,name,color)
            self.player.inventory  = InventoryManager()
        else:
            self.player.x  = cx; self.player.y = cy
            self.player.hp = self.player.max_hp

        self.player._world = self.world   # injeta world na skill

        self.cam_x = cx - SCREEN_W/2
        self.cam_y = cy - SCREEN_H/2

        # NPCs (sage recebe callback de boss)
        self.npcs=[
            make_sage    (cx-60, cy-20, self.player.inventory, self._request_boss),
            make_merchant(cx+60, cy-20, self.player),
        ]

        self.mobs=[]; self.items=[]
        self.particles=[]; self.messages=[]
        self.boss=None; self._boss_reward_given=False; self._boss_requested=False

        n_mobs = FLOOR_MOB_BASE + (self.floor-1)*FLOOR_MOB_STEP
        # Distribuição: andar 1 só slime/goblin; orc aparece a partir nível 2
        for _ in range(n_mobs):
            mx,my = self._danger_spawn()
            allowed = self._allowed_mobs()
            self.mobs.append(Mob(mx,my,random.choice(allowed),
                                 dmg_mult=1+(self.floor-1)*FLOOR_DMG_MULT,
                                 player_level=self.player.level,
                                 world=self.world))

        # Itens: mais moedas que o resto
        for _ in range(14+self.floor*2):
            pos=self.world.walkable_grass_pos(random.Random())
            if pos:
                t=random.choices(
                    ["coin","coin","coin","gem","scroll","hp_potion","sword","shield"],
                    weights=[40,40,40,20,15,5,8,8])[0]
                self.items.append(Item(pos[0],pos[1],t))

        self._msg(f"Andar {self.floor} — Invoque o Boss via Sabio Aldren e pegue a Chave!")

    def _allowed_mobs(self):
        """Retorna lista de tipos permitidos de acordo com o nível."""
        pl=self.player.level if self.player else 1
        types=["slime","goblin","ghost"]
        if pl>=2: types.append("orc")
        return types

    def _request_boss(self):
        """Callback chamado pelo NPC Sábio — spawna boss na zona de perigo."""
        if self.boss and not self.boss.dead: return
        if self.player.level < BOSS_UNLOCK_LEVEL:
            self._msg(f"Precisa de nivel {BOSS_UNLOCK_LEVEL} para invocar o Boss!")
            return
        # Spawna boss numa posição distante, na zona de perigo
        sz_cx,sz_cy=self.world.safe_zone_center_px()
        for _ in range(100):
            angle=random.uniform(0,2*math.pi)
            dist=random.uniform(MOB_SPAWN_MIN_DIST, MOB_SPAWN_MAX_DIST)
            bx=sz_cx+math.cos(angle)*dist
            by=sz_cy+math.sin(angle)*dist
            bx=max(60,min(MAP_W*TILE_SIZE-60,bx))
            by=max(60,min(MAP_H*TILE_SIZE-60,by))
            if self.world.is_grass(int(bx//TILE_SIZE),int(by//TILE_SIZE)):
                break
        self.boss=Boss(bx,by,floor=self.floor,world=self.world)
        self._boss_reward_given=False
        self._msg("★ BOSS INVOCADO! Derrote-o para pegar a Chave do Andar!")

    def _danger_spawn(self):
        sz_cx,sz_cy=self.world.safe_zone_center_px()
        rng=random.Random()
        for _ in range(300):
            angle=rng.uniform(0,2*math.pi)
            dist=rng.uniform(MOB_SPAWN_MIN_DIST,MOB_SPAWN_MAX_DIST)
            mx=sz_cx+math.cos(angle)*dist
            my=sz_cy+math.sin(angle)*dist
            mx=max(60,min(MAP_W*TILE_SIZE-60,mx))
            my=max(60,min(MAP_H*TILE_SIZE-60,my))
            tx,ty=int(mx//TILE_SIZE),int(my//TILE_SIZE)
            if self.world.is_grass(tx,ty): return mx,my
        return sz_cx+400,sz_cy+200

    # ── Mensagens / partículas ────────────────────────────────────────
    def _msg(self,text):  self.messages.append([text,260])
    def _part(self,x,y,t,c=YELLOW): self.particles.append(Particle(x,y,t,c))

    # ── Eventos ──────────────────────────────────────────────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT: return False
            if   self.state==STATE_CUSTOMIZE: self._ev_custom(event)
            elif self.state==STATE_PLAYING:   self._ev_playing(event)
            elif self.state==STATE_DIALOGUE:  self._ev_dialogue(event)
            elif self.state==STATE_PAUSE:     self._ev_pause(event)
            elif self.state==STATE_GAMEOVER:  self._ev_gameover(event)
        return True

    def _ev_custom(self,event):
        r=self._custom_screen.handle_event(event)
        if r=="start":
            cfg=self._custom_screen.get_config()
            self._setup_world(cfg["name"],cfg["color"])
            self._begin_fade(STATE_PLAYING)

    def _ev_playing(self,event):
        if event.type==pygame.KEYDOWN:
            k=event.key
            if k==pygame.K_ESCAPE:
                self.state=STATE_PAUSE; self._pause_menu.reset()
            elif k==pygame.K_i: self.show_inv=not self.show_inv
            elif k==pygame.K_o and self.show_inv:
                self._msg(f"Ordenado: {self.player.inventory.cycle_sort()}")
            elif k==pygame.K_f:
                if self.player.use_potion(): self._msg("+40 HP (Pocao usada)")
                else: self._msg("Sem pocoes no inventario!")
            elif k==pygame.K_e: self._try_interact()
        elif event.type==pygame.MOUSEBUTTONDOWN:
            if event.button==1 and not self.show_inv:
                mx,my=event.pos; wx,wy=mx+self.cam_x,my+self.cam_y
                if pygame.key.get_mods()&pygame.KMOD_SHIFT: self.player.use_skill(wx,wy)
                else: self._movement.handle_click(wx,wy,self.player)
            elif event.button==3:
                mx,my=event.pos; self.player.use_skill(mx+self.cam_x,my+self.cam_y)

    def _try_interact(self):
        # NPC
        for npc in self.npcs:
            if math.hypot(npc.x-self.player.x,npc.y-self.player.y)<npc.interact_range:
                npc.interact(); self.active_npc=npc
                self.show_inv=False; self.state=STATE_DIALOGUE; return
        # Porta
        px_t=int(self.player.x//TILE_SIZE); py_t=int(self.player.y//TILE_SIZE)
        for dy in range(-1,2):
            for dx in range(-1,2):
                tx,ty=px_t+dx,py_t+dy
                if 0<=ty<MAP_H and 0<=tx<MAP_W:
                    if self.world.tiles[ty][tx]==TILE_DOOR:
                        self._use_door(); return

    def _use_door(self):
        if not self.player.inventory.has("key"):
            self._msg("Voce precisa da Chave do Andar!"); return
        self.player.inventory.remove("key")
        self.floor+=1
        self._build_floor()
        self._begin_fade(STATE_PLAYING)

    def _ev_dialogue(self,event):
        if event.type!=pygame.KEYDOWN: return
        npc=self.active_npc
        if not npc: self.state=STATE_PLAYING; return
        tree=npc.tree; node=tree.current; key=event.key
        if key==pygame.K_ESCAPE:
            tree.done=True; tree.current=tree.root
            self.active_npc=None; self.state=STATE_PLAYING; return
        ckeys={pygame.K_1:0,pygame.K_2:1,pygame.K_3:2,pygame.K_4:3,pygame.K_5:4,pygame.K_6:5}
        if key in ckeys and not node.is_leaf:
            idx=ckeys[key]
            if idx<len(node.choices):
                tree.select(idx)
                if tree.last_msg: self._msg(tree.last_msg); tree.last_msg=None
        elif key in (pygame.K_e,pygame.K_RETURN,pygame.K_SPACE):
            if node.is_leaf: tree.done=True
            elif len(node.choices)==1:
                tree.select(0)
                if tree.last_msg: self._msg(tree.last_msg); tree.last_msg=None
        if tree.done: self.active_npc=None; self.state=STATE_PLAYING

    def _ev_pause(self,event):
        r=self._pause_menu.handle_event(event)
        if r=="resume": self.state=STATE_PLAYING
        elif r=="quit": pygame.quit(); raise SystemExit

    def _ev_gameover(self,event):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_r:
                self._custom_screen=CustomizeScreen(); self._begin_fade(STATE_CUSTOMIZE)
            elif event.key==pygame.K_ESCAPE: pygame.quit(); raise SystemExit

    # ── Fade ─────────────────────────────────────────────────────────
    def _begin_fade(self,ns):
        self._fade=ScreenFade(fade_in=False,speed=8); self._next_state=ns

    def _update_fade(self):
        if not self._fade: return
        if self._fade.update():
            if self._next_state:
                self.state=self._next_state
                self._fade=ScreenFade(fade_in=True,speed=8); self._next_state=None
            else: self._fade=None

    # ── Update ───────────────────────────────────────────────────────
    def update(self,dt):
        self._update_fade()
        if self.state==STATE_CUSTOMIZE: self._custom_screen.update(dt)
        elif self.state in (STATE_PLAYING,STATE_INVENTORY): self._update_playing(dt)
        elif self.state==STATE_DIALOGUE:
            for npc in self.npcs: npc.update(dt)
        self.world.update(dt) if self.world else None

    def _update_playing(self,dt):
        keys=pygame.key.get_pressed()
        self._movement.update(self.player,dt,keys)
        self.player.update(dt)

        # Câmera
        tcx=self.player.x-SCREEN_W/2; tcy=self.player.y-SCREEN_H/2
        lr=min(1.0,dt*8.0)
        self.cam_x+=(tcx-self.cam_x)*lr; self.cam_y+=(tcy-self.cam_y)*lr
        self.cam_x=max(0,min(MAP_W*TILE_SIZE-SCREEN_W,self.cam_x))
        self.cam_y=max(0,min(MAP_H*TILE_SIZE-SCREEN_H,self.cam_y))

        for npc in self.npcs: npc.update(dt)
        for mob in self.mobs: mob.update(dt,self.player)

        # Boss update
        if self.boss and not self.boss.dead:
            def _spawn_mob(x,y):
                self.mobs.append(Mob(x,y,random.choice(["slime","goblin"]),
                                     world=self.world,player_level=self.player.level))
            self.boss.update(dt,self.player,spawn_mob_cb=_spawn_mob)
        elif self.boss and self.boss.dead and not self._boss_reward_given:
            self._boss_reward_given=True
            lv=self.player.gain_xp(self.boss.xp_reward)
            if lv: self._msg(f"★ LEVEL UP! Nv.{self.player.level} +1 moeda!"); self._lvl_up=LevelUpEffect(self.player.level)
            pos=self.world.walkable_grass_pos(random.Random(),
                min_px=self.boss.x-50,max_px=self.boss.x+50,
                min_py=self.boss.y-50,max_py=self.boss.y+50)
            kx,ky=pos if pos else (self.boss.x,self.boss.y+20)
            self.items.append(Item(kx,ky,"key"))
            self._msg("★ BOSS DERROTADO! Chave do Andar dropada!")

        # Skill vs boss
        if self.boss and not self.boss.dead:
            for sk in self.player.skills[:]:
                if sk.get_rect().colliderect(self.boss.get_rect()):
                    self.boss.take_damage(sk.damage)
                    self._part(self.boss.x,self.boss.y-36,f"-{sk.damage}",RED)
                    if sk in self.player.skills: self.player.skills.remove(sk)

        # Coleta de itens
        pr=self.player.get_rect()
        for item in self.items:
            if not item.collected:
                item.update(dt)
                if item.get_rect().colliderect(pr):
                    item.collected=True
                    if item.item_type=="gem":
                        lv=self.player.gain_xp(GEM_XP_VALUE)
                        if lv: self._msg(f"Gema +{GEM_XP_VALUE}XP | LEVEL UP Nv.{self.player.level}!"); self._lvl_up=LevelUpEffect(self.player.level)
                        else: self._msg(f"Gema! +{GEM_XP_VALUE} XP")
                        self._part(item.x,item.y-20,f"+{GEM_XP_VALUE}XP",item.color)
                    elif item.item_type in ITEM_EFFECTS:
                        ef=ITEM_EFFECTS[item.item_type]
                        if "skill_damage" in ef: self.player.skill_damage+=ef["skill_damage"]
                        if "max_hp" in ef: self.player.max_hp+=ef["max_hp"]; self.player.hp=min(self.player.hp+ef["max_hp"],self.player.max_hp)
                        if "xp" in ef: self.player.gain_xp(ef["xp"])
                        self._msg(ef.get("msg",f"Coletado: {item.label}"))
                        self._part(item.x,item.y-20,ef.get("msg","")[:12],item.color)
                    else:
                        self.player.inventory.add(item.item_type)
                        self._msg(f"Coletado: {item.label}")
                        self._part(item.x,item.y-20,f"+{item.label[:8]}",item.color)

        # Skills vs mobs
        from config import MOB_DROPS
        for sk in self.player.skills[:]:
            for mob in self.mobs:
                if not mob.dead and sk.get_rect().colliderect(mob.get_rect()):
                    mob.take_damage(sk.damage)
                    self._part(mob.x,mob.y-28,f"-{sk.damage}",RED)
                    if sk in self.player.skills: self.player.skills.remove(sk)
                    if mob.dead:
                        lv=self.player.gain_xp(mob.xp_reward)
                        if lv: self._msg(f"★ LEVEL UP! Nv.{self.player.level} +1 moeda!"); self._lvl_up=LevelUpEffect(self.player.level)
                        else: self._msg(f"+{mob.xp_reward} XP!")
                        # Drop ponderado
                        dt_=MOB_DROPS.get(mob.monster_type,[("coin",80),("nothing",20)])
                        pool=[d[0] for d in dt_]; wts=[d[1] for d in dt_]
                        ch=random.choices(pool,weights=wts,k=1)[0]
                        if ch=="key_chance":
                            if not self.player.inventory.has("key"):
                                pos=self.world.walkable_grass_pos(random.Random(),
                                    min_px=mob.x-30,max_px=mob.x+30,
                                    min_py=mob.y-30,max_py=mob.y+30)
                                ix,iy=pos if pos else (mob.x,mob.y+10)
                                self.items.append(Item(ix,iy,"key"))
                                self._msg("★ Chave dropada! Va ate a Porta!")
                            else: self.items.append(Item(mob.x,mob.y,"coin"))
                        elif ch!="nothing":
                            pos=self.world.walkable_grass_pos(random.Random(),
                                min_px=mob.x-40,max_px=mob.x+40,
                                min_py=mob.y-40,max_py=mob.y+40)
                            ix,iy=pos if pos else (mob.x,mob.y)
                            self.items.append(Item(ix,iy,ch))
                    break

        # Partículas / mensagens
        self.particles=[p for p in self.particles if p.alive]
        for p in self.particles: p.update(dt)
        for m in self.messages: m[1]-=1
        self.messages=[m for m in self.messages if m[1]>0]
        if self._lvl_up:
            self._lvl_up.update()
            if not self._lvl_up.alive: self._lvl_up=None

        # Respawn de mobs — mantém mínimo constante, nascem longe do player
        alive=[m for m in self.mobs if not m.dead]
        min_mobs=max(4,(FLOOR_MOB_BASE+(self.floor-1)*FLOOR_MOB_STEP)//2)
        if len(alive)<min_mobs:
            allowed=self._allowed_mobs()
            for _ in range(MOB_RESPAWN_COUNT):
                mx,my=self._danger_spawn()
                # Garante distância mínima do player (400px)
                if math.hypot(mx-self.player.x,my-self.player.y)<400: continue
                self.mobs.append(Mob(mx,my,random.choice(allowed),
                    dmg_mult=1+(self.floor-1)*FLOOR_DMG_MULT,
                    player_level=self.player.level,world=self.world))

        # Game over
        if self.player.is_dead and self._fade is None:
            self._begin_fade(STATE_GAMEOVER)

    # ── Draw ─────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BLACK)
        if self.state==STATE_CUSTOMIZE:
            self._custom_screen.draw(self.screen)
        elif self.state in (STATE_PLAYING,STATE_DIALOGUE,STATE_INVENTORY):
            self._draw_world()
            if self.state==STATE_DIALOGUE: draw_dialogue(self.screen,self.active_npc)
            if self.show_inv: draw_inventory(self.screen,self.player)
            if self._lvl_up: self._lvl_up.draw(self.screen)
        elif self.state==STATE_PAUSE:
            self._draw_world(); self._pause_menu.draw(self.screen)
        elif self.state==STATE_GAMEOVER:
            self._draw_gameover()
        if self._fade: self._fade.draw(self.screen)
        pygame.display.flip()

    def _draw_world(self):
        cx,cy=self.cam_x,self.cam_y
        self.world.draw(self.screen,cx,cy)
        self._movement.draw_path(self.screen,cx,cy)
        for item in self.items: item.draw(self.screen,cx,cy)
        self.player.draw(self.screen,cx,cy)
        for npc in self.npcs:
            d=math.hypot(npc.x-self.player.x,npc.y-self.player.y)
            npc.draw(self.screen,cx,cy,player_close=(d<npc.interact_range))
        for mob in self.mobs: mob.draw(self.screen,cx,cy)
        if self.boss and not self.boss.dead: self.boss.draw(self.screen,cx,cy)
        for p in self.particles: p.draw(self.screen,cx,cy)
        self._lantern.draw(self.screen,self.player,cx,cy)
        draw_hud(self.screen,self.player,self.messages,self.floor)
        self._minimap.draw(self.screen,self.player,self.npcs,self.mobs,self.items)

    def _draw_gameover(self):
        self.screen.fill((8,4,4)); p=self.player
        go=fonts.xl.render("GAME OVER",True,RED)
        self.screen.blit(go,(SCREEN_W//2-go.get_width()//2,SCREEN_H//2-100))
        for i,ln in enumerate([f"Andar: {self.floor}",f"Nivel: {p.level}",f"XP: {p.xp}"]):
            s=fonts.md.render(ln,True,LIGHT_GRAY)
            self.screen.blit(s,(SCREEN_W//2-s.get_width()//2,SCREEN_H//2-10+i*32))
        h=fonts.xs.render("R=reiniciar  ESC=sair",True,GRAY)
        self.screen.blit(h,(SCREEN_W//2-h.get_width()//2,SCREEN_H//2+130))

    def run(self):
        running=True
        while running:
            dt=min(self.clock.tick(FPS)/1000.0,0.05)
            running=self.handle_events()
            self.update(dt)
            self.draw()
