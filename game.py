<<<<<<< Updated upstream
=======
"""
game.py — loop principal e máquina de estados.

CORREÇÕES E ADIÇÕES vs. versão anterior:
  1. GAME OVER BUG: _begin_fade chamada todo frame → adicionado `and self._fade is None`
  2. NPCs distintos: Sábio Aldren (tutorial) + Mercador Zek (loja)
  3. Mobs spawnando longe: spawn agora relativo ao player, dentro do aggro_range
  4. Sistema de andares (floors): chave cai de mob, porta avança o andar
  5. Lanterna: overlay escuro com luz circular ao redor do player
  6. Level up agora dá moeda (propósito real) em vez de curar HP
  7. Mob scaling: mais mobs e mais dano por andar
"""

import random
import math
import pygame

from config import (
    SCREEN_W, SCREEN_H, FPS, TITLE,
    MAP_W, MAP_H, TILE_SIZE,
    STATE_CUSTOMIZE, STATE_PLAYING, STATE_DIALOGUE,
    STATE_INVENTORY, STATE_GAMEOVER, STATE_PAUSE,
    WHITE, BLACK, YELLOW, RED, GRAY, LIGHT_GRAY,
    MOB_AGGRO_RANGE, MOB_RESPAWN_COUNT,
    FLOOR_MOB_BASE, FLOOR_MOB_STEP, FLOOR_DMG_MULT,
    BOSS_UNLOCK_LEVEL, MOB_SPAWN_MIN_DIST, MOB_SPAWN_MAX_DIST,
    ITEM_EFFECTS,
    TILE_DOOR,
)

from ui.fonts     import init_fonts, fonts
from ui.hud       import draw_hud
from ui.map       import MiniMap
from ui.dialogue  import draw_dialogue
from ui.inventory import draw_inventory

from entities         import Player, Mob
from entities.mob     import Boss
from entities.npc     import make_sage, make_merchant
from world            import World, Item, Particle
from world.lantern    import Lantern

from screens.custom      import CustomizeScreen
from screens.pause_menu  import PauseMenu
from screens.movement  import MovementController
from screens.animation import ScreenFade, LevelUpEffect

from systems.inventory_manager import InventoryManager


class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock  = pygame.time.Clock()
        init_fonts()

        self.state          = STATE_CUSTOMIZE
        self._custom_screen = CustomizeScreen()
        self._fade          = None
        self._next_state    = None

        # Inicializados em _setup_world / _load_floor
        self.player     = None
        self.world      = None
        self.npcs       = []
        self.mobs       = []
        self.items      = []
        self.particles  = []
        self.messages   = []
        self.active_npc = None
        self.show_inv   = False
        self.cam_x      = 0.0
        self.cam_y      = 0.0
        self.boss               = None
        self._boss_reward_given = False
        self.floor      = 1         # andar atual

        self._movement  = None
        self._minimap    = MiniMap(SCREEN_W - 165, 10, 155, 130)
        self._lvl_up     = None
        self._lantern    = Lantern()
        self._pause_menu = PauseMenu()
        self.boss        = None   # Boss do andar atual

    # ==================================================================
    # SETUP
    # ==================================================================
    def _setup_world(self, name: str, color: tuple) -> None:
        """Chamado uma única vez ao iniciar nova partida."""
        self.floor  = 1
        self.world  = World(seed=random.randint(1, 99999))
        self._movement = MovementController(self.world)

        cx, cy = self.world.safe_zone_center_px()
        self.player = Player(cx, cy, name, color)
        self.player.inventory = InventoryManager()

        self.cam_x = cx - SCREEN_W / 2
        self.cam_y = cy - SCREEN_H / 2

        # NPCs distintos dentro da zona segura
        self.npcs = [
            make_sage(cx - 80, cy - 30, self.player.inventory),
            make_merchant(cx + 80, cy - 30, self.player),
        ]

        self._load_floor(reset_player=False)

    def _load_floor(self, reset_player: bool = True) -> None:
        """
        Carrega (ou recarrega) o andar atual.
        Gera mobs, itens e a chave do andar.
        """
        if reset_player:
            cx, cy = self.world.safe_zone_center_px()
            self.player.x = cx
            self.player.y = cy
            self.player.hp = self.player.max_hp   # cura ao avançar andar

        n_mobs = FLOOR_MOB_BASE + (self.floor - 1) * FLOOR_MOB_STEP
        mob_types = ["slime", "goblin", "ghost", "orc"]

        self.mobs  = []
        self.items = []
        self.particles = []
        self.messages  = []

        # Spawna mobs na zona de perigo (fora da zona segura)
        for _ in range(n_mobs):
            mx, my = self._danger_spawn()
            self.mobs.append(Mob(mx, my, random.choice(mob_types),
                                 dmg_mult=1 + (self.floor - 1) * FLOOR_DMG_MULT,
                                 player_level=self.player.level,
                                 world=self.world))

        # Itens espalhados na zona de perigo
        mat_types = ["gem", "coin", "coin", "scroll", "hp_potion", "sword", "shield"]
        for _ in range(12):
            ix, iy = self._danger_spawn()
            self.items.append(Item(float(ix), float(iy), random.choice(mat_types)))

        self.boss               = None
        self._boss_reward_given = False
        self._msg(f"Andar {self.floor} — Encontre a Chave e vá até a Porta!")

    def _danger_spawn(self) -> tuple[float, float]:
        """
        Spawn em tile TILE_GRASS garantido, fora da zona segura.
        Usa world.walkable_grass_pos para evitar tiles bloqueantes.
        Distância: 550-1200px do centro da zona segura (fora das paredes ~480px).
        """
        sz_cx, sz_cy = self.world.safe_zone_center_px()
        rng = random.Random()
        for _ in range(300):
            angle = rng.uniform(0, 2 * math.pi)
            dist  = rng.uniform(MOB_SPAWN_MIN_DIST, MOB_SPAWN_MAX_DIST)
            mx = sz_cx + math.cos(angle) * dist
            my = sz_cy + math.sin(angle) * dist
            mx = max(80, min(MAP_W * TILE_SIZE - 80, mx))
            my = max(80, min(MAP_H * TILE_SIZE - 80, my))
            tx, ty = int(mx // TILE_SIZE), int(my // TILE_SIZE)
            if self.world.is_grass(tx, ty):
                return mx, my
        # Fallback garantido
        return (sz_cx + random.choice([-700, 700]),
                sz_cy + random.choice([-300, 300]))

    def _in_safe_zone(self, wx: float, wy: float) -> bool:
        from config import TILE_FLOOR
        tx = int(wx // TILE_SIZE)
        ty = int(wy // TILE_SIZE)
        if 0 <= ty < MAP_H and 0 <= tx < MAP_W:
            return self.world.tiles[ty][tx] == TILE_FLOOR
        return False

    @staticmethod
    def _random_spawn(cx, cy, min_dist=200):
        while True:
            mx = random.randint(200, MAP_W * TILE_SIZE - 200)
            my = random.randint(200, MAP_H * TILE_SIZE - 200)
            if math.hypot(mx - cx, my - cy) >= min_dist:
                return float(mx), float(my)

    # ==================================================================
    # MENSAGENS / PARTÍCULAS
    # ==================================================================
    def _msg(self, text: str) -> None:
        self.messages.append([text, 240])

    def _particle(self, x, y, text, color=YELLOW) -> None:
        self.particles.append(Particle(x, y, text, color))

    # ==================================================================
    # EVENTOS
    # ==================================================================
    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.state == STATE_CUSTOMIZE:
                self._ev_customize(event)
            elif self.state == STATE_PLAYING:
                self._ev_playing(event)
            elif self.state == STATE_DIALOGUE:
                self._ev_dialogue(event)
            elif self.state == STATE_PAUSE:
                self._ev_pause(event)
            elif self.state == STATE_GAMEOVER:
                self._ev_gameover(event)
        return True

    def _ev_customize(self, event):
        result = self._custom_screen.handle_event(event)
        if result == "start":
            cfg = self._custom_screen.get_config()
            self._setup_world(cfg["name"], cfg["color"])
            self._begin_fade(STATE_PLAYING)

    def _ev_playing(self, event):
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_ESCAPE:
                self.state = STATE_PAUSE
                self._pause_menu.reset()
            elif key == pygame.K_i:
                self.show_inv = not self.show_inv
            elif key == pygame.K_o and self.show_inv:
                mode = self.player.inventory.cycle_sort()
                self._msg(f"Ordenado por: {mode}")
            elif key == pygame.K_f:
                if self.player.use_potion():
                    self._msg("+40 HP  (Pocao usada)")
                else:
                    self._msg("Sem pocoes no inventario!")
            elif key == pygame.K_e:
                self._try_interact()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.show_inv:
                mx, my = event.pos
                wx, wy = mx + self.cam_x, my + self.cam_y
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    self.player.use_skill(wx, wy)
                else:
                    self._movement.handle_click(wx, wy, self.player)
            elif event.button == 3:
                mx, my = event.pos
                self.player.use_skill(mx + self.cam_x, my + self.cam_y)

    def _try_interact(self):
        from config import NPC_INTERACT_RANGE
        # Checar NPC
        for npc in self.npcs:
            if math.hypot(npc.x - self.player.x, npc.y - self.player.y) < NPC_INTERACT_RANGE:
                npc.interact()
                self.active_npc = npc
                self.show_inv   = False
                self.state      = STATE_DIALOGUE
                return
        # Checar porta (TILE_DOOR)
        px_t = int(self.player.x // TILE_SIZE)
        py_t = int(self.player.y // TILE_SIZE)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                tx, ty = px_t + dx, py_t + dy
                if 0 <= ty < MAP_H and 0 <= tx < MAP_W:
                    if self.world.tiles[ty][tx] == TILE_DOOR:
                        if self._spawn_boss_if_ready():
                            self._use_door()
                        return

    def _spawn_boss_if_ready(self) -> bool:
        """Spawna boss se player.level >= BOSS_UNLOCK_LEVEL e boss não existe."""
        if self.boss and not self.boss.dead:
            return True  # boss já ativo
        if self.boss and self.boss.dead:
            return False  # boss morreu, pode pegar chave
        if self.player.level < BOSS_UNLOCK_LEVEL:
            self._msg(f"Precisa ser Nível {BOSS_UNLOCK_LEVEL} para enfrentar o Boss!")
            return False
        # Spawna boss próximo à porta
        dpx, dpy = self.world.door_px()
        bx = dpx + random.choice([-180, 180])
        by = dpy - 200
        self.boss = Boss(bx, by, floor=self.floor, world=self.world)
        self._boss_reward_given = False
        self._msg(f"★ BOSS APARECEU! Derrote-o para pegar a Chave do Andar!")
        return False

    def _use_door(self):
        if not self.player.inventory.has("key"):
            self._msg("Voce precisa da Chave do Andar para abrir a porta!")
            return
        self.player.inventory.remove("key")
        self.floor += 1
        self.world = World(seed=random.randint(1, 99999))
        self._movement = MovementController(self.world)
        cx, cy = self.world.safe_zone_center_px()
        self.npcs = [
            make_sage(cx - 80, cy - 30, self.player.inventory),
            make_merchant(cx + 80, cy - 30, self.player),
        ]
        self._load_floor(reset_player=True)
        self._begin_fade(STATE_PLAYING)

    def _ev_dialogue(self, event):
        if event.type != pygame.KEYDOWN:
            return
        npc = self.active_npc
        if not npc:
            self.state = STATE_PLAYING
            return
        tree = npc.tree
        node = tree.current
        key  = event.key

        # ESC fecha dialogo imediatamente
        if key == pygame.K_ESCAPE:
            npc.tree.done = True
            npc.tree.current = npc.tree.root
            self.active_npc = None
            self.state = STATE_PLAYING
            return

        choice_keys = {pygame.K_1: 0, pygame.K_2: 1,
                       pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4}

        if key in choice_keys and not node.is_leaf:
            idx = choice_keys[key]
            if idx < len(node.choices):
                tree.select(idx)
                if tree.last_msg:
                    self._msg(tree.last_msg)
                    tree.last_msg = None
        elif key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
            if node.is_leaf:
                tree.done = True
            elif len(node.choices) == 1:
                tree.select(0)
                if tree.last_msg:
                    self._msg(tree.last_msg)
                    tree.last_msg = None

        if tree.done:
            self.active_npc = None
            self.state      = STATE_PLAYING

    def _ev_pause(self, event) -> None:
        result = self._pause_menu.handle_event(event)
        if result == "resume":
            self.state = STATE_PLAYING
        elif result == "quit":
            pygame.quit()
            raise SystemExit

    def _ev_gameover(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._custom_screen = CustomizeScreen()
                self._begin_fade(STATE_CUSTOMIZE)
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

    # ==================================================================
    # FADE
    # ==================================================================
    def _begin_fade(self, next_state: str) -> None:
        self._fade       = ScreenFade(fade_in=False, speed=8)
        self._next_state = next_state

    def _update_fade(self) -> None:
        if self._fade is None:
            return
        done = self._fade.update()
        if done:
            if self._next_state is not None:
                self.state       = self._next_state
                self._fade       = ScreenFade(fade_in=True, speed=8)
                self._next_state = None
            else:
                self._fade = None

    # ==================================================================
    # UPDATE
    # ==================================================================
    def update(self, dt: float) -> None:
        self._update_fade()

        if self.state == STATE_CUSTOMIZE:
            self._custom_screen.update(dt)
        elif self.state in (STATE_PLAYING, STATE_INVENTORY):
            self._update_playing(dt)

        # NPC animation continues in pause/dialogue
        if self.state in (STATE_PAUSE,):
            for npc in self.npcs:
                npc.update(dt)

        if self.state == STATE_DIALOGUE:
            for npc in self.npcs:
                npc.update(dt)

    def _update_playing(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        self._movement.update(self.player, dt, keys)
        self.player.update(dt)

        # Câmera suave
        tcx = self.player.x - SCREEN_W / 2
        tcy = self.player.y - SCREEN_H / 2
        lerp = min(1.0, dt * 8.0)
        self.cam_x += (tcx - self.cam_x) * lerp
        self.cam_y += (tcy - self.cam_y) * lerp
        self.cam_x  = max(0, min(MAP_W * TILE_SIZE - SCREEN_W, self.cam_x))
        self.cam_y  = max(0, min(MAP_H * TILE_SIZE - SCREEN_H, self.cam_y))

        for npc in self.npcs:
            npc.update(dt)

        for mob in self.mobs:
            mob.update(dt, self.player)

        # Boss update
        if self.boss and not self.boss.dead:
            self.boss.update(dt, self.player)
        elif self.boss and self.boss.dead and not getattr(self, '_boss_reward_given', False):
            self._boss_reward_given = True
            leveled = self.player.gain_xp(self.boss.xp_reward)
            if leveled:
                self._msg(f"★ LEVEL UP Nv.{self.player.level}! +1 moeda!")
                self._lvl_up = LevelUpEffect(self.player.level)
            # Chave garantida do boss
            pos = self.world.walkable_grass_pos(
                random.Random(),
                min_px=self.boss.x - 50, max_px=self.boss.x + 50,
                min_py=self.boss.y - 50, max_py=self.boss.y + 50)
            kx, ky = pos if pos else (self.boss.x, self.boss.y + 20)
            self.items.append(Item(kx, ky, "key"))
            self._msg("★ BOSS DERROTADO! A Chave do Andar caiu!")

        # Skill vs boss
        if self.boss and not self.boss.dead:
            for skill in self.player.skills[:]:
                if skill.get_rect().colliderect(self.boss.get_rect()):
                    self.boss.take_damage(skill.damage)
                    self._particle(self.boss.x, self.boss.y - 36, f"-{skill.damage}", RED)
                    if skill in self.player.skills:
                        self.player.skills.remove(skill)

        # Coleta de itens
        player_rect = self.player.get_rect()
        for item in self.items:
            if not item.collected:
                item.update(dt)
                if item.get_rect().colliderect(player_rect):
                    item.collected = True
                    if item.item_type == "gem":
                        # Gema: converte em XP diretamente (nao entra no inventario)
                        from config import GEM_XP_VALUE
                        leveled = self.player.gain_xp(GEM_XP_VALUE)
                        if leveled:
                            self._msg(f"Gema! +{GEM_XP_VALUE} XP | LEVEL UP! Nv.{self.player.level} +1 moeda!")
                            self._lvl_up = LevelUpEffect(self.player.level)
                        else:
                            self._msg(f"Gema! +{GEM_XP_VALUE} XP")
                        self._particle(item.x, item.y - 20, f"+{GEM_XP_VALUE}XP", item.color)
                    elif item.item_type in ("sword", "shield", "scroll"):
                        # Efeitos imediatos — não entram no inventário
                        effect = ITEM_EFFECTS.get(item.item_type, {})
                        if "skill_damage" in effect:
                            self.player.skill_damage += effect["skill_damage"]
                        if "max_hp" in effect:
                            self.player.max_hp += effect["max_hp"]
                            self.player.hp = min(self.player.hp + effect["max_hp"], self.player.max_hp)
                        if "xp" in effect:
                            self.player.gain_xp(effect["xp"])
                        msg = effect.get("msg", f"Coletado: {item.label}")
                        self._msg(msg)
                        self._particle(item.x, item.y - 20, msg[:12], item.color)
                    else:
                        self.player.inventory.add(item.item_type)
                        self._msg(f"Coletado: {item.label}")
                        self._particle(item.x, item.y - 20, f"+{item.label[:8]}", item.color)

        # Skills vs mobs
        for skill in self.player.skills[:]:
            for mob in self.mobs:
                if not mob.dead and skill.get_rect().colliderect(mob.get_rect()):
                    mob.take_damage(skill.damage)
                    self._particle(mob.x, mob.y - 28, f"-{skill.damage}", RED)
                    if skill in self.player.skills:
                        self.player.skills.remove(skill)
                    if mob.dead:
                        leveled = self.player.gain_xp(mob.xp_reward)
                        if leveled:
                            self._msg(f"★ LEVEL UP! Nv.{self.player.level} — +1 moeda!")
                            self._lvl_up = LevelUpEffect(self.player.level)
                        else:
                            self._msg(f"+{mob.xp_reward} XP!")
                        # Drop ponderado por tipo de mob
                        from config import MOB_DROPS
                        drop_table = MOB_DROPS.get(mob.monster_type, [("coin", 80), ("nothing", 20)])
                        items_pool  = [d[0] for d in drop_table]
                        weights     = [d[1] for d in drop_table]
                        drop_choice = random.choices(items_pool, weights=weights, k=1)[0]

                        if drop_choice == "key_chance":
                            # Orc/Goblin: drop de chave se player não tiver
                            if not self.player.inventory.has("key"):
                                pos = self.world.walkable_grass_pos(
                                    random.Random(),
                                    min_px=mob.x - 30, max_px=mob.x + 30,
                                    min_py=mob.y - 30, max_py=mob.y + 30)
                                ix, iy = pos if pos else (mob.x, mob.y + 10)
                                self.items.append(Item(ix, iy, "key"))
                                self._msg("★ Chave do Andar dropada! Va ate a Porta!")
                            else:
                                # Tem chave: drop moeda no lugar
                                self.items.append(Item(mob.x, mob.y, "coin"))
                        elif drop_choice != "nothing":
                            # Spawn item em tile de grama próximo
                            pos = self.world.walkable_grass_pos(
                                random.Random(),
                                min_px=mob.x - 40, max_px=mob.x + 40,
                                min_py=mob.y - 40, max_py=mob.y + 40)
                            if pos:
                                self.items.append(Item(pos[0], pos[1], drop_choice))
                            else:
                                self.items.append(Item(mob.x, mob.y, drop_choice))
                    break

        # Partículas e mensagens
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update(dt)
        for m in self.messages:
            m[1] -= 1
        self.messages = [m for m in self.messages if m[1] > 0]

        if self._lvl_up:
            self._lvl_up.update()
            if not self._lvl_up.alive:
                self._lvl_up = None

        # Respawn de mobs quando poucos vivos
        alive = [m for m in self.mobs if not m.dead]
        min_mobs = max(2, (FLOOR_MOB_BASE + (self.floor - 1) * FLOOR_MOB_STEP) // 3)
        if len(alive) < min_mobs:
            mob_types = ["slime", "goblin", "ghost", "orc"]
            for _ in range(MOB_RESPAWN_COUNT):
                mx, my = self._danger_spawn()
                self.mobs.append(Mob(mx, my, random.choice(mob_types),
                                     dmg_mult=1 + (self.floor - 1) * FLOOR_DMG_MULT,
                                     player_level=self.player.level,
                                     world=self.world))

        # FIX 1: verifica _fade is None antes de acionar game over
        # sem isso, _begin_fade era chamada todo frame, resetando a animação
        if self.player.is_dead and self._fade is None:
            self._begin_fade(STATE_GAMEOVER)

    # ==================================================================
    # DRAW
    # ==================================================================
    def draw(self) -> None:
        self.screen.fill(BLACK)

        if self.state == STATE_CUSTOMIZE:
            self._custom_screen.draw(self.screen)

        elif self.state in (STATE_PLAYING, STATE_DIALOGUE, STATE_INVENTORY):
            self._draw_world()
            if self.state == STATE_DIALOGUE:
                draw_dialogue(self.screen, self.active_npc)
            if self.show_inv:
                draw_inventory(self.screen, self.player)
            if self._lvl_up:
                self._lvl_up.draw(self.screen)

        elif self.state == STATE_PAUSE:
            self._draw_world()
            self._pause_menu.draw(self.screen)

        elif self.state == STATE_GAMEOVER:
            self._draw_gameover()

        if self._fade:
            self._fade.draw(self.screen)

        pygame.display.flip()

    def _draw_world(self) -> None:
        cx, cy = self.cam_x, self.cam_y

        self.world.draw(self.screen, cx, cy)
        self._movement.draw_path(self.screen, cx, cy)

        for item in self.items:
            item.draw(self.screen, cx, cy)

        self.player.draw(self.screen, cx, cy)

        for npc in self.npcs:
            dist = math.hypot(npc.x - self.player.x, npc.y - self.player.y)
            npc.draw(self.screen, cx, cy, player_close=(dist < npc.interact_range))

        for mob in self.mobs:
            mob.draw(self.screen, cx, cy)

        if self.boss and not self.boss.dead:
            self.boss.draw(self.screen, cx, cy)

        for p in self.particles:
            p.draw(self.screen, cx, cy)

        # Lanterna: overlay escuro com luz ao redor do player
        self._lantern.draw(self.screen, self.player, cx, cy)

        # HUD e minimap por cima da escuridão
        draw_hud(self.screen, self.player, self.messages, self.floor)
        self._minimap.draw(self.screen, self.player, self.npcs, self.mobs, self.items)

    def _draw_gameover(self) -> None:
        from ui.fonts import fonts
        self.screen.fill((8, 4, 4))
        p = self.player

        go = fonts.xl.render("GAME OVER", True, RED)
        self.screen.blit(go, (SCREEN_W // 2 - go.get_width() // 2, SCREEN_H // 2 - 100))

        lines = [
            f"Andar alcancado: {self.floor}",
            f"Nivel: {p.level}",
            f"XP acumulado: {p.xp}",
            f"Moedas gastas no mercador: {max(0, p.level - 1)}",
        ]
        for i, ln in enumerate(lines):
            s = fonts.md.render(ln, True, LIGHT_GRAY)
            self.screen.blit(s, (SCREEN_W // 2 - s.get_width() // 2,
                                  SCREEN_H // 2 - 20 + i * 32))

        hint = fonts.xs.render("R = reiniciar     ESC = sair", True, GRAY)
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2,
                                 SCREEN_H // 2 + 140))

    # ==================================================================
    # LOOP
    # ==================================================================
    def run(self) -> None:
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            running = self.handle_events()
            self.update(dt)
            self.draw()
>>>>>>> Stashed changes
