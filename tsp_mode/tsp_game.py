"""
tsp_mode/tsp_game.py
====================
Loop principal do modo TSP.

FLUXO:
  1. Tela de configuração: escolhe N pontos de coleta
  2. Mapa gerado com N pontos espalhados em tile GRASS
  3. TSP calculado → rota ótima exibida com setas numeradas
  4. Jogador se move (WASD) coletando pontos em qualquer ordem
  5. Ao coletar tudo: tela de resultado com:
       - Distância percorrida pelo jogador
       - Distância ótima (TSP)
       - Eficiência %
       - Inventário ordenado por Heapsort
       - Algoritmo usado (Held-Karp ou 2-opt)
"""

import pygame
import math
import random
import sys
import os

# Garante import dos módulos do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import (SCREEN_W, SCREEN_H, FPS,
                    TILE_SIZE, MAP_W, MAP_H,
                    WHITE, BLACK, YELLOW, RED, GREEN,
                    GRAY, DARK_GRAY, LIGHT_GRAY, ORANGE,
                    TILE_GRASS, TILE_FLOOR, TILE_STONE)

from tsp_mode.tsp_algorithm  import solve_tsp, route_distance
from tsp_mode.inventory_heap import TSPInventory, ITEM_TYPES


# ── Constantes do TSP Mode ──────────────────────────────────────────────────
POINT_RADIUS   = 14
PLAYER_SPEED   = 200
COLLECT_RADIUS = 22
ARROW_COLOR    = (100, 220, 255)
VISITED_COLOR  = (60,  200, 60)
OPTIMAL_COLOR  = (255, 200, 50)

N_OPTIONS      = [6, 8, 10, 12, 15, 20]   # opções de pontos na tela de config


# ── Geração de pontos no mapa ───────────────────────────────────────────────

def _gen_points(n: int, margin: int = 80) -> list:
    """Gera N pontos aleatórios dentro da área jogável, com distância mínima."""
    pts  = []
    minD = 90
    area_w = SCREEN_W - 2 * margin
    area_h = SCREEN_H - 2 * margin - 120   # deixa espaço para HUD

    tries = 0
    while len(pts) < n and tries < 10000:
        tries += 1
        x = random.randint(margin, margin + area_w)
        y = random.randint(margin + 60, margin + 60 + area_h)
        ok = all(math.hypot(x - px, y - py) >= minD for px, py in pts)
        if ok:
            pts.append((x, y))

    return pts


# ── Classe do ponto de coleta ───────────────────────────────────────────────

class CollectPoint:
    def __init__(self, idx: int, x: float, y: float, item: dict):
        self.idx      = idx
        self.x        = x
        self.y        = y
        self.item     = item
        self.collected= False
        self._anim    = random.uniform(0, math.pi * 2)

    def update(self, dt: float):
        self._anim += dt * 3

    def draw(self, surface: pygame.Surface):
        if self.collected:
            return
        # Flutuação suave
        oy  = int(math.sin(self._anim) * 4)
        clr = self.item["color"]
        # Sombra
        pygame.draw.circle(surface, (0, 0, 0, 60),
                           (int(self.x), int(self.y) + POINT_RADIUS + 4), 8)
        # Círculo principal
        pygame.draw.circle(surface, clr,
                           (int(self.x), int(self.y) + oy), POINT_RADIUS)
        bright = tuple(min(255, c + 70) for c in clr)
        pygame.draw.circle(surface, bright,
                           (int(self.x) - 4, int(self.y) - 4 + oy), 5)
        pygame.draw.circle(surface, WHITE,
                           (int(self.x), int(self.y) + oy), POINT_RADIUS, 2)
        # Número do ponto
        font = pygame.font.SysFont("Arial", 11, bold=True)
        num  = font.render(str(self.idx + 1), True, WHITE)
        surface.blit(num, (int(self.x) - num.get_width() // 2,
                           int(self.y) + oy - num.get_height() // 2))


# ── Player simplificado (sem mapa de tiles) ─────────────────────────────────

class TSPPlayer:
    def __init__(self, x: float, y: float, color: tuple):
        self.x        = float(x)
        self.y        = float(y)
        self.color    = color
        self.speed    = PLAYER_SPEED
        self.facing   = 1
        self._anim    = 0.0
        self.moving   = False
        # Rastro de posições (para mostrar caminho percorrido)
        self.trail:   list = [(x, y)]
        self.dist_traveled: float = 0.0

    def move(self, dx: float, dy: float, dt: float):
        if dx != 0 and dy != 0:
            dx *= 0.7071; dy *= 0.7071
        margin = 20
        new_x = max(margin, min(SCREEN_W - margin, self.x + dx * self.speed * dt))
        new_y = max(60 + margin, min(SCREEN_H - margin, self.y + dy * self.speed * dt))
        dist  = math.hypot(new_x - self.x, new_y - self.y)
        self.dist_traveled += dist
        self.x, self.y      = new_x, new_y
        if dx != 0: self.facing = 1 if dx > 0 else -1
        self.moving = (dx != 0 or dy != 0)
        if self.moving:
            self._anim += dt
            # Grava trail a cada 20px percorridos
            if len(self.trail) == 0 or math.hypot(
                    self.x - self.trail[-1][0],
                    self.y - self.trail[-1][1]) >= 20:
                self.trail.append((self.x, self.y))

    def draw(self, surface: pygame.Surface):
        sx, sy = int(self.x), int(self.y)
        s      = 18
        t      = self._anim
        lc     = tuple(max(0, c - 40) for c in self.color)
        sw     = int(math.sin(t * 8) * 5) if self.moving else 0
        pygame.draw.rect(surface, lc, (sx-s//3, sy+s//2, s//3, 9+sw), border_radius=2)
        pygame.draw.rect(surface, lc, (sx,       sy+s//2, s//3, 9-sw), border_radius=2)
        pygame.draw.rect(surface, self.color, (sx-s//2, sy-s//2, s, s), border_radius=4)
        pygame.draw.circle(surface, self.color, (sx, sy-s), s//2)
        pygame.draw.circle(surface, WHITE, (sx+4*self.facing, sy-s-2), 3)
        pygame.draw.circle(surface, BLACK, (sx+5*self.facing, sy-s-2), 1)


# ── Seta entre dois pontos ──────────────────────────────────────────────────

def _draw_arrow(surface, x1, y1, x2, y2, color, width=2):
    dx = x2 - x1; dy = y2 - y1
    dist = math.hypot(dx, dy)
    if dist < 1: return
    nx, ny = dx / dist, dy / dist
    # Linha
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    pygame.draw.line(surface, color, (int(x1), int(y1)), (int(x2), int(y2)), width)
    # Ponta da seta no meio do segmento
    angle = math.atan2(dy, dx)
    aw    = 10
    for sign in (-1, 1):
        ax = mx - math.cos(angle + sign * 2.5) * aw
        ay = my - math.sin(angle + sign * 2.5) * aw
        pygame.draw.line(surface, color, (int(mx), int(my)), (int(ax), int(ay)), width)


# ── Tela de configuração ─────────────────────────────────────────────────────

def run_config_screen(screen: pygame.Surface, clock: pygame.time.Clock,
                      fonts) -> dict | None:
    """
    Exibe tela de configuração do TSP Mode.
    Retorna dict com {n_points, player_color} ou None se o usuário sair.
    """
    sel_n     = 2   # índice em N_OPTIONS (padrão: 10 pontos)
    sel_color = 0
    colors    = [(70,130,210),(210,70,70),(70,200,80),(200,200,70),(180,70,200)]
    running   = True

    while running:
        screen.fill((15, 15, 35))

        # Título
        t = fonts.xl.render("MODO TSP — Rota Ótima de Coleta", True, YELLOW)
        screen.blit(t, (SCREEN_W//2 - t.get_width()//2, 40))

        desc_lines = [
            "Colete todos os itens do mapa no menor caminho possivel!",
            "O algoritmo TSP calcula a rota otima — voce vencera se for eficiente.",
            f"n ≤ 15: Held-Karp (exato) | n > 15: 2-opt (heuristica)",
        ]
        for i, dl in enumerate(desc_lines):
            s = fonts.sm.render(dl, True, LIGHT_GRAY)
            screen.blit(s, (SCREEN_W//2 - s.get_width()//2, 110 + i * 24))

        # Seleção de N
        screen.blit(fonts.md.render("Numero de pontos de coleta:", True, WHITE),
                    (SCREEN_W//2 - 200, 200))
        nx0 = SCREEN_W//2 - len(N_OPTIONS) * 46 // 2
        for i, n in enumerate(N_OPTIONS):
            bx = nx0 + i * 46
            br = pygame.Rect(bx, 230, 40, 40)
            pygame.draw.rect(screen, (60,60,120) if i==sel_n else DARK_GRAY, br, border_radius=6)
            pygame.draw.rect(screen, YELLOW if i==sel_n else GRAY, br, 2, border_radius=6)
            ns = fonts.md.render(str(n), True, WHITE)
            screen.blit(ns, (bx+20-ns.get_width()//2, 242))
            algo = fonts.xs.render("Exato" if n<=15 else "Heur.", True,
                                   GREEN if n<=15 else ORANGE)
            screen.blit(algo, (bx+20-algo.get_width()//2, 275))

        # Cor do player
        screen.blit(fonts.md.render("Cor do personagem:", True, WHITE), (SCREEN_W//2-200, 320))
        for i, c in enumerate(colors):
            bx = SCREEN_W//2 - len(colors)*22 + i*44
            r  = pygame.Rect(bx, 350, 38, 38)
            pygame.draw.rect(screen, c, r, border_radius=7)
            if i == sel_color:
                pygame.draw.rect(screen, WHITE, r, 3, border_radius=7)

        # Botão iniciar
        btn = pygame.Rect(SCREEN_W//2-110, 430, 220, 50)
        pygame.draw.rect(screen, (50,180,80), btn, border_radius=10)
        pygame.draw.rect(screen, WHITE, btn, 2, border_radius=10)
        bt  = fonts.md.render("▶  INICIAR", True, BLACK)
        screen.blit(bt, (btn.centerx-bt.get_width()//2, btn.centery-bt.get_height()//2))

        hint = fonts.xs.render("ESC = voltar ao menu principal  |  ← → = pontos  |  ENTER = iniciar",
                               True, GRAY)
        screen.blit(hint, (SCREEN_W//2-hint.get_width()//2, SCREEN_H-36))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return {"n_points": N_OPTIONS[sel_n], "player_color": colors[sel_color]}
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    sel_n = (sel_n - 1) % len(N_OPTIONS)
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    sel_n = (sel_n + 1) % len(N_OPTIONS)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn.collidepoint(event.pos):
                    return {"n_points": N_OPTIONS[sel_n], "player_color": colors[sel_color]}
                for i,n in enumerate(N_OPTIONS):
                    bx = nx0+i*46
                    if pygame.Rect(bx,230,40,40).collidepoint(event.pos): sel_n=i
                for i,c in enumerate(colors):
                    bx=SCREEN_W//2-len(colors)*22+i*44
                    if pygame.Rect(bx,350,38,38).collidepoint(event.pos): sel_color=i

    return None


# ── Tela de resultado ────────────────────────────────────────────────────────

def run_result_screen(screen, clock, fonts, player_dist, optimal_dist,
                      method, inventory, n_points) -> bool:
    """
    Exibe resultado.
    Retorna True = jogar novamente, False = voltar ao menu.
    """
    efficiency = min(100.0, (optimal_dist / max(player_dist, 1)) * 100)
    medal      = "★★★" if efficiency>90 else "★★" if efficiency>70 else "★"

    sort_mode  = inventory.sort_mode
    inv_list   = inventory.get_sorted()

    show_inv   = False
    running    = True

    while running:
        screen.fill((10, 10, 25))

        title_clr = (80,220,80) if efficiency>80 else (220,180,50) if efficiency>60 else (220,80,80)
        t = fonts.xl.render(f"ROTA CONCLUÍDA  {medal}", True, title_clr)
        screen.blit(t, (SCREEN_W//2-t.get_width()//2, 30))

        lines = [
            (f"Pontos coletados: {n_points}/{n_points}", GREEN),
            (f"Distância percorrida: {player_dist:.0f} px",   WHITE),
            (f"Rota ótima (TSP):     {optimal_dist:.0f} px",  YELLOW),
            (f"Eficiência:           {efficiency:.1f}%",       title_clr),
            (f"Algoritmo usado:      {method}",                LIGHT_GRAY),
        ]
        for i, (txt, clr) in enumerate(lines):
            s = fonts.md.render(txt, True, clr)
            screen.blit(s, (SCREEN_W//2-s.get_width()//2, 110+i*36))

        # Barra de eficiência
        bx,by,bw,bh = SCREEN_W//2-200, 300, 400, 22
        pygame.draw.rect(screen, DARK_GRAY, (bx,by,bw,bh), border_radius=5)
        pygame.draw.rect(screen, title_clr, (bx,by,int(bw*efficiency/100),bh), border_radius=5)
        pygame.draw.rect(screen, WHITE, (bx,by,bw,bh), 1, border_radius=5)

        # Botão inventário
        inv_btn = pygame.Rect(SCREEN_W//2-220, 340, 200, 40)
        pygame.draw.rect(screen, (40,80,140), inv_btn, border_radius=8)
        pygame.draw.rect(screen, LIGHT_GRAY, inv_btn, 1, border_radius=8)
        ib = fonts.sm.render(f"[I] Inventário (Heapsort/{sort_mode})", True, WHITE)
        screen.blit(ib, (inv_btn.x+10, inv_btn.centery-ib.get_height()//2))

        # Botões ação
        btn_again = pygame.Rect(SCREEN_W//2-105, 410, 200, 48)
        btn_menu  = pygame.Rect(SCREEN_W//2+105, 410, 200, 48)
        pygame.draw.rect(screen, (50,180,80),  btn_again, border_radius=10)
        pygame.draw.rect(screen, (180,50,50),  btn_menu,  border_radius=10)
        pygame.draw.rect(screen, WHITE, btn_again, 2, border_radius=10)
        pygame.draw.rect(screen, WHITE, btn_menu,  2, border_radius=10)
        for btn, txt in [(btn_again,"▶ Jogar Novamente"),(btn_menu,"✕ Menu Principal")]:
            s=fonts.sm.render(txt,True,WHITE)
            screen.blit(s,(btn.centerx-s.get_width()//2,btn.centery-s.get_height()//2))

        # Painel inventário
        if show_inv:
            _draw_inventory_panel(screen, fonts, inv_list, sort_mode)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:     show_inv = not show_inv
                if event.key == pygame.K_o:     inventory.cycle_sort(); sort_mode=inventory.sort_mode; inv_list=inventory.get_sorted()
                if event.key == pygame.K_r:     return True
                if event.key == pygame.K_ESCAPE:return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                if btn_again.collidepoint(event.pos): return True
                if btn_menu.collidepoint(event.pos):  return False
                if inv_btn.collidepoint(event.pos):   show_inv=not show_inv

    return False


def _draw_inventory_panel(screen, fonts, inv_list, sort_mode):
    iw, ih = 460, 360
    ix = SCREEN_W//2 - iw//2; iy = SCREEN_H//2 - ih//2
    bg = pygame.Surface((iw,ih), pygame.SRCALPHA)
    bg.fill((15,15,40,240)); screen.blit(bg,(ix,iy))
    pygame.draw.rect(screen,YELLOW,(ix,iy,iw,ih),2,border_radius=8)

    t=fonts.lg.render(f"INVENTÁRIO (Heapsort por {sort_mode})",True,YELLOW)
    screen.blit(t,(ix+iw//2-t.get_width()//2,iy+10))
    hint=fonts.xs.render("O = mudar ordenação",True,GRAY)
    screen.blit(hint,(ix+iw-hint.get_width()-10,iy+ih-20))
    pygame.draw.line(screen,YELLOW,(ix+10,iy+42),(ix+iw-10,iy+42))

    cols,slot,gap=4,88,6
    for idx,item in enumerate(inv_list[:16]):
        col=idx%cols; row=idx//cols
        sx_=ix+14+col*(slot+gap); sy_=iy+52+row*(slot+gap)
        if sy_+slot>iy+ih-30: break
        sr=pygame.Rect(sx_,sy_,slot,slot)
        pygame.draw.rect(screen,DARK_GRAY,sr,border_radius=6)
        pygame.draw.rect(screen,GRAY,sr,1,border_radius=6)
        pygame.draw.circle(screen,item["color"],(sx_+slot//2,sy_+slot//2-8),16)
        bright=tuple(min(255,c+70) for c in item["color"])
        pygame.draw.circle(screen,bright,(sx_+slot//2-5,sy_+slot//2-13),5)
        ic=fonts.xxs.render(item["icon"][:2],True,WHITE)
        screen.blit(ic,(sx_+slot//2-ic.get_width()//2,sy_+slot//2-8-ic.get_height()//2))
        nm=fonts.xxs.render(item["name"][:8],True,WHITE)
        screen.blit(nm,(sx_+slot//2-nm.get_width()//2,sy_+slot-16))
        val=fonts.xxs.render(f"V:{item['value']}",True,YELLOW)
        screen.blit(val,(sx_+2,sy_+2))


# ── Loop principal do TSP Mode ───────────────────────────────────────────────

def run_tsp_mode(screen: pygame.Surface, clock: pygame.time.Clock, fonts) -> None:
    """
    Ponto de entrada do TSP Mode chamado pelo main.py.
    Loop: config → jogo → resultado → repetir ou sair.
    """
    while True:
        # ── Configuração ──────────────────────────────────────────────
        cfg = run_config_screen(screen, clock, fonts)
        if cfg is None:
            return   # volta ao menu principal

        n_pts   = cfg["n_points"]
        p_color = cfg["player_color"]

        # ── Setup ─────────────────────────────────────────────────────
        points   = _gen_points(n_pts)
        items    = [random.choice(ITEM_TYPES) for _ in points]
        cpoints  = [CollectPoint(i, px, py, items[i]) for i,(px,py) in enumerate(points)]
        inventory= TSPInventory()

        # TSP — calcula rota ótima
        tour, optimal_dist, method = solve_tsp(points)

        # Player nasce próximo ao ponto 0 da rota ótima
        start = points[tour[0]]
        player = TSPPlayer(start[0], start[1], p_color)

        collected_order = []
        show_optimal    = True    # S alterna exibição da rota ótima
        show_inv        = False
        sort_mode_lbl   = inventory.sort_mode

        # Fundo do mapa (grama simples)
        bg_surf = pygame.Surface((SCREEN_W, SCREEN_H))
        bg_surf.fill((60, 130, 55))
        # Grade decorativa
        for gy in range(0, SCREEN_H, TILE_SIZE):
            for gx in range(0, SCREEN_W, TILE_SIZE):
                pygame.draw.rect(bg_surf,(55,125,50),(gx,gy,TILE_SIZE,TILE_SIZE),1)

        running = True
        while running:
            dt = min(clock.tick(FPS) / 1000.0, 0.05)

            # ── Eventos ───────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: running=False
                    if event.key == pygame.K_s and not pygame.key.get_mods()&pygame.KMOD_SHIFT:
                        pass  # WASD handle below
                    if event.key == pygame.K_TAB:
                        show_optimal = not show_optimal
                    if event.key == pygame.K_i:
                        show_inv = not show_inv
                    if event.key == pygame.K_o and show_inv:
                        inventory.cycle_sort()
                        sort_mode_lbl = inventory.sort_mode

            # ── Movimento ─────────────────────────────────────────────
            keys = pygame.key.get_pressed()
            dx = dy = 0.0
            if keys[pygame.K_w] or keys[pygame.K_UP]:    dy-=1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy+=1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx-=1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx+=1
            player.move(dx, dy, dt)

            # ── Coleta ────────────────────────────────────────────────
            for cp in cpoints:
                cp.update(dt)
                if not cp.collected:
                    if math.hypot(player.x-cp.x, player.y-cp.y) < COLLECT_RADIUS:
                        cp.collected = True
                        collected_order.append(cp.idx)
                        inventory.add(cp.item)

            # Todos coletados → resultado
            if all(cp.collected for cp in cpoints):
                running = False

            # ── Desenho ───────────────────────────────────────────────
            screen.blit(bg_surf, (0, 0))

            # Rastro do jogador
            if len(player.trail) >= 2:
                pygame.draw.lines(screen, (150,255,150,120), False,
                                  [(int(x),int(y)) for x,y in player.trail], 2)

            # Rota ótima TSP
            if show_optimal:
                for i in range(len(tour)):
                    a = points[tour[i]]
                    b = points[tour[(i+1)%len(tour)]]
                    # Cor diferente se o segmento já foi percorrido
                    seg_done = (tour[i] in collected_order and tour[(i+1)%len(tour)] in collected_order)
                    clr = VISITED_COLOR if seg_done else OPTIMAL_COLOR
                    _draw_arrow(screen, a[0], a[1], b[0], b[1], clr, 2)
                # Números da ordem ótima
                font_s = pygame.font.SysFont("Arial", 10, bold=True)
                for rank, idx in enumerate(tour):
                    px_, py_ = points[idx]
                    lbl = font_s.render(str(rank+1), True, OPTIMAL_COLOR)
                    screen.blit(lbl, (int(px_)-16, int(py_)-28))

            # Pontos de coleta
            for cp in cpoints:
                cp.draw(screen)
                if cp.collected:
                    # Tick verde sobre pontos coletados
                    pygame.draw.circle(screen, VISITED_COLOR,
                                       (int(cp.x), int(cp.y)), POINT_RADIUS+2, 3)

            # Player
            player.draw(screen)

            # ── HUD ───────────────────────────────────────────────────
            _draw_tsp_hud(screen, fonts, player, collected_order, cpoints,
                          optimal_dist, show_optimal, sort_mode_lbl, inventory)

            # Painel inventário
            if show_inv:
                _draw_inventory_panel(screen, fonts, inventory.get_sorted(), sort_mode_lbl)

            pygame.display.flip()

        # ── Resultado ─────────────────────────────────────────────────
        play_again = run_result_screen(
            screen, clock, fonts,
            player.dist_traveled, optimal_dist, method,
            inventory, n_pts
        )
        if not play_again:
            return   # volta ao menu principal
        # Senão: reinicia o loop externo (nova partida)


def _draw_tsp_hud(screen, fonts, player, collected_order, cpoints,
                  optimal_dist, show_optimal, sort_mode, inventory):
    # Barra superior
    pygame.draw.rect(screen, (10,10,30), (0,0,SCREEN_W,56))
    pygame.draw.line(screen, GRAY, (0,56),(SCREEN_W,56))

    done  = len(collected_order)
    total = len(cpoints)

    # Progresso
    prog = fonts.md.render(f"Coletados: {done}/{total}", True, YELLOW)
    screen.blit(prog, (20, 8))

    # Distância percorrida
    dist_t = fonts.sm.render(f"Dist percorrida: {player.dist_traveled:.0f}px", True, WHITE)
    screen.blit(dist_t, (20, 34))

    # Distância ótima
    opt_t = fonts.sm.render(f"Dist ótima (TSP): {optimal_dist:.0f}px", True, OPTIMAL_COLOR)
    screen.blit(opt_t, (260, 34))

    # Eficiência atual
    if player.dist_traveled > 0:
        eff = min(100.0, optimal_dist / player.dist_traveled * 100)
        ec  = GREEN if eff>80 else ORANGE if eff>60 else RED
        et  = fonts.sm.render(f"Eficiência: {eff:.1f}%", True, ec)
        screen.blit(et, (530, 34))

    # Inventário contador
    inv_t = fonts.xs.render(f"I=inventário({inventory.count}) O=ordenar({sort_mode})", True, LIGHT_GRAY)
    screen.blit(inv_t, (SCREEN_W-inv_t.get_width()-10, 38))

    # Toggle rota
    tab_t = fonts.xs.render("TAB=rota TSP on/off", True, OPTIMAL_COLOR if show_optimal else GRAY)
    screen.blit(tab_t, (SCREEN_W-tab_t.get_width()-10, 8))

    # Barra de progresso
    bw = 220; bx = SCREEN_W//2 - bw//2; by = 10
    pygame.draw.rect(screen, DARK_GRAY, (bx,by,bw,14), border_radius=4)
    if total>0:
        pygame.draw.rect(screen, GREEN, (bx,by,int(bw*done/total),14), border_radius=4)
    pygame.draw.rect(screen, WHITE, (bx,by,bw,14), 1, border_radius=4)
