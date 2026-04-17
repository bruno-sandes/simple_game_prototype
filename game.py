import random
import math
import pygame

from config import (
    SCREEN_W, SCREEN_H, FPS, TITLE,
    MAP_W, MAP_H, TILE_SIZE,
    STATE_CUSTOMIZE, STATE_PLAYING, STATE_DIALOGUE,
    STATE_INVENTORY, STATE_GAMEOVER,
    WHITE, BLACK, YELLOW, RED, GRAY, GREEN, LIGHT_GRAY,
    MOB_RESPAWN_COUNT,
)

from ui.fonts     import init_fonts, fonts
from ui.hud       import draw_hud
from ui.map       import MiniMap
from ui.dialogue  import draw_dialogue
from ui.inventory import draw_inventory


from entities         import Player, Mob
from entities.npc     import create_tutorial_npc
from world import World, Item, Particle

from screens.custom    import CustomizeScreen
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

        self.state  = STATE_CUSTOMIZE
        self._custom_screen = CustomizeScreen()
        self._fade: ScreenFade | None = None
        self._next_state: str | None  = None

        # Entidades (inicializadas em _setup_world)
        self.player   = Player
        self.world    = None
        self.npcs     = []
        self.mobs     = []
        self.items    = []
        self.particles: list[Particle] = []
        self.messages:  list[list]     = []  # [[texto, timer], ...]
        self.active_npc = None
        self.show_inv   = False

        self.cam_x = 0.0
        self.cam_y = 0.0
        self._movement: MovementController | None = None
        self._minimap  = MiniMap(SCREEN_W - 165, 10, 155, 130)
        self._lvl_up: LevelUpEffect | None = None

    # ==================================================================
    # SETUP
    # ==================================================================
    def _setup_world(self, name: str, color: tuple) -> None:
        cx = MAP_W * TILE_SIZE // 2
        cy = MAP_H * TILE_SIZE // 2
        seed = random.randint(1, 99999)

        # Player com InventoryManager
        self.player = Player(float(cx), float(cy), name, color)
        self.player.inventory = InventoryManager()

        self.world      = World(seed=seed)
        self._movement  = MovementController(self.world)
        self.cam_x      = float(cx - SCREEN_W // 2)
        self.cam_y      = float(cy - SCREEN_H // 2)
        
        self.npcs = [
            create_tutorial_npc(cx + 150, cy - 120, self.player.inventory),
            create_tutorial_npc(cx - 200, cy +  90, self.player.inventory),
        ]

        # 3 NPCs com arvores de dialogo distintas
        #npc_guia = create_tutorial_npc(150, 150, self.player.inventory)
        #self.npcs.append(npc_guia)

        # Mobs espalhados
        mob_types = ["slime", "goblin", "ghost", "orc"]
        self.mobs = []
        for _ in range(10):
            mx, my = self._random_spawn(cx, cy, min_dist=250)
            self.mobs.append(Mob(mx, my, random.choice(mob_types)))

        # Itens coletaveis (pelo menos 4 tipos distintos de materiais)
        mat_types = ["gem", "coin", "scroll", "hp_potion", "sword", "shield", "key"]
        self.items = []
        for _ in range(22):
            ix = random.randint(200, MAP_W * TILE_SIZE - 200)
            iy = random.randint(200, MAP_H * TILE_SIZE - 200)
            self.items.append(Item(float(ix), float(iy), random.choice(mat_types)))

        self.particles  = []
        self.messages   = []
        self.active_npc = None
        self.show_inv   = False

    @staticmethod
    def _random_spawn(cx: float, cy: float,
                      min_dist: float = 200) -> tuple[float, float]:
        while True:
            mx = random.randint(200, MAP_W * TILE_SIZE - 200)
            my = random.randint(200, MAP_H * TILE_SIZE - 200)
            if math.hypot(mx - cx, my - cy) >= min_dist:
                return float(mx), float(my)

    # ==================================================================
    # MENSAGENS / PARTICULAS
    # ==================================================================
    def _msg(self, text: str) -> None:
        self.messages.append([text, 220])

    def _particle(self, x: float, y: float,
                  text: str, color: tuple = YELLOW) -> None:
        self.particles.append(Particle(x, y, text, color))

    # ==================================================================
    # EVENTOS
    # ==================================================================
    def handle_events(self) -> bool:
        """Retorna False se o jogador fechou a janela."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.state == STATE_CUSTOMIZE:
                self._ev_customize(event)
            elif self.state == STATE_PLAYING:
                self._ev_playing(event)
            elif self.state == STATE_DIALOGUE:
                self._ev_dialogue(event)
            elif self.state == STATE_GAMEOVER:
                self._ev_gameover(event)
        return True

    # ── Customize ─────────────────────────────────────────────────────
    def _ev_customize(self, event: pygame.event.Event) -> None:
        result = self._custom_screen.handle_event(event)
        if result == "start":
            cfg = self._custom_screen.get_config()
            self._setup_world(cfg["name"], cfg["color"])
            self._begin_fade(STATE_PLAYING)

    # ── Playing ───────────────────────────────────────────────────────
    def _ev_playing(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_ESCAPE:
                self._begin_fade(STATE_CUSTOMIZE)

            elif key == pygame.K_i:
                self.show_inv = not self.show_inv

            elif key == pygame.K_o and self.show_inv:
                new_mode = self.player.inventory.cycle_sort()
                self._msg(f"Ordenado por: {new_mode}")

            elif key == pygame.K_f:
                inv = self.player.inventory
                if inv.use_potion():
                    self.player.hp = min(self.player.max_hp, self.player.hp + 40)
                    self._msg("+40 HP  (Pocao usada)")
                else:
                    self._msg("Sem pocoes no inventario!")

            elif key == pygame.K_e:
                self._try_interact_npc()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.show_inv:
                mx, my = event.pos
                wx = mx + self.cam_x
                wy = my + self.cam_y

                # Shift + clique = skill; clique normal = pathfinder
                keys = pygame.key.get_mods()
                if keys & pygame.KMOD_SHIFT:
                    self.player.use_skill(wx, wy)
                else:
                    self._movement.handle_click(wx, wy, self.player)

            elif event.button == 3:
                # Clique direito = skill
                mx, my = event.pos
                self.player.use_skill(mx + self.cam_x, my + self.cam_y)

    def _try_interact_npc(self) -> None:
        from config import NPC_INTERACT_RANGE
        for npc in self.npcs:
            dist = math.hypot(npc.x - self.player.x, npc.y - self.player.y)
            if dist < NPC_INTERACT_RANGE:
                npc.interact()
                self.active_npc = npc
                self.show_inv   = False
                self.state      = STATE_DIALOGUE
                return

    # ── Dialogue ──────────────────────────────────────────────────────
    def _ev_dialogue(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        npc  = self.active_npc
        if not npc:
            self.state = STATE_PLAYING
            return

        tree = npc.tree
        node = tree.current
        key  = event.key
        inv  = self.player.inventory

        # Teclas numericas para selecionar choices
        choice_keys = {
            pygame.K_1: 0, pygame.K_2: 1,
            pygame.K_3: 2, pygame.K_4: 3,
        }

        if key in choice_keys and not node.is_leaf:
            idx = choice_keys[key]
            if idx < len(node.choices):
                tree.select(idx)
            

        elif key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
            if node.is_leaf:
                tree.done = True
            elif len(node.choices) == 1:
                tree.select(0)

        if tree.done:
            self.active_npc = None
            self.state      = STATE_PLAYING

    # ── Game over ─────────────────────────────────────────────────────
    def _ev_gameover(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._custom_screen = CustomizeScreen()
                self._begin_fade(STATE_CUSTOMIZE)
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

    # ==================================================================
    # TRANSICAO
    # ==================================================================
    def _begin_fade(self, next_state: str) -> None:
        self._fade       = ScreenFade(fade_in=False, speed=8)
        self._next_state = next_state

    def _update_fade(self) -> None:
        if self._fade is None:
            return
        done = self._fade.update()
        if done:
            self.state       = self._next_state
            self._fade       = ScreenFade(fade_in=True, speed=8)
            self._next_state = None

    # ==================================================================
    # UPDATE
    # ==================================================================
    def update(self, dt: float) -> None:
        self._update_fade()

        if self.state == STATE_CUSTOMIZE:
            self._custom_screen.update(dt)

        elif self.state in (STATE_PLAYING, STATE_INVENTORY):
            self._update_playing(dt)

        if self.state == STATE_DIALOGUE:
            for npc in self.npcs:
                npc.update(dt)

    def _update_playing(self, dt: float) -> None:
        keys = pygame.key.get_pressed()

        # Movimento (WASD + pathfinder)
        self._movement.update(self.player, dt, keys)
        self.player.update(dt)

        # Camera suave
        tcx = self.player.x - SCREEN_W / 2
        tcy = self.player.y - SCREEN_H / 2
        lerp = min(1.0, dt * 8.0)
        self.cam_x += (tcx - self.cam_x) * lerp
        self.cam_y += (tcy - self.cam_y) * lerp
        self.cam_x  = max(0, min(MAP_W * TILE_SIZE - SCREEN_W, self.cam_x))
        self.cam_y  = max(0, min(MAP_H * TILE_SIZE - SCREEN_H, self.cam_y))

        # NPCs
        for npc in self.npcs:
            npc.update(dt)

        # Mobs
        for mob in self.mobs:
            mob.update(dt, self.player)

        # Itens: coleta automatica por contato
        player_rect = self.player.get_rect()
        for item in self.items:
            if not item.collected:
                item.update(dt)
                if item.get_rect().colliderect(player_rect):
                    item.collected = True
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
                        self._msg(f"+{mob.xp_reward} XP!" + (" ★ LEVEL UP!" if leveled else ""))
                        if leveled:
                            self._lvl_up = LevelUpEffect(self.player.level)
                        # Drop aleatorio
                        if random.random() < 0.55:
                            drop_t = random.choice(["gem", "coin", "hp_potion"])
                            dx = mob.x + random.randint(-20, 20)
                            dy = mob.y + random.randint(-20, 20)
                            self.items.append(Item(dx, dy, drop_t))
                    break

        # Particulas
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update(dt)

        # Mensagens HUD
        for m in self.messages:
            m[1] -= 1
        self.messages = [m for m in self.messages if m[1] > 0]

        # Level up effect
        if self._lvl_up:
            self._lvl_up.update()
            if not self._lvl_up.alive:
                self._lvl_up = None

        # Respawn de mobs
        if all(m.dead for m in self.mobs):
            self._msg("Novos inimigos aparecem!")
            cx = MAP_W * TILE_SIZE // 2
            cy = MAP_H * TILE_SIZE // 2
            for _ in range(MOB_RESPAWN_COUNT):
                mx, my = self._random_spawn(cx, cy, 300)
                self.mobs.append(
                    Mob(mx, my, random.choice(["slime", "goblin", "ghost", "orc"]))
                )

        # Game over
        if self.player.is_dead:
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

        elif self.state == STATE_GAMEOVER:
            self._draw_gameover()

        # Fade overlay
        if self._fade:
            self._fade.draw(self.screen)

        pygame.display.flip()

    # ── World draw ────────────────────────────────────────────────────
    def _draw_world(self) -> None:
        cx, cy = self.cam_x, self.cam_y

        # Mapa de tiles
        self.world.draw(self.screen, cx, cy)

        # Caminho do pathfinder
        self._movement.draw_path(self.screen, cx, cy)

        # Itens
        for item in self.items:
            item.draw(self.screen, cx, cy)

        # NPCs
        for npc in self.npcs:
            dist = math.hypot(npc.x - self.player.x, npc.y - self.player.y)
            npc.draw(self.screen, cx, cy, player_close=(dist < npc.interact_range))

        # Mobs
        for mob in self.mobs:
            mob.draw(self.screen, cx, cy)

        # Player
        self.player.draw(self.screen, cx, cy)

        # Particulas
        for p in self.particles:
            p.draw(self.screen, cx, cy)

        # HUD + minimap
        draw_hud(self.screen, self.player, self.messages)
        self._minimap.draw(self.screen, self.player,
                           self.npcs, self.mobs, self.items)

    # ── Game over ─────────────────────────────────────────────────────
    def _draw_gameover(self) -> None:
        self.screen.fill((8, 4, 4))
        p = self.player
        font_xl = fonts.xl
        font_md = fonts.md
        font_xs = fonts.xs

        go = font_xl.render("GAME OVER", True, RED)
        self.screen.blit(go, (SCREEN_W // 2 - go.get_width() // 2, SCREEN_H // 2 - 90))

        lines = [
            f"Nivel alcancado: {p.level}",
            f"XP acumulado:    {p.xp}",
            f"Tipos coletados: {p.inventory.unique_types}",
            f"Total de itens:  {p.inventory.total}",
        ]
        for i, ln in enumerate(lines):
            s = font_md.render(ln, True, LIGHT_GRAY)
            self.screen.blit(s, (SCREEN_W // 2 - s.get_width() // 2,
                                  SCREEN_H // 2 - 10 + i * 30))

        hint = font_xs.render("R = reiniciar     ESC = sair", True, GRAY)
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2,
                                 SCREEN_H // 2 + 130))

    # ==================================================================
    # LOOP PRINCIPAL
    # ==================================================================
    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            running = self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    pygame.init()
    Game().run()