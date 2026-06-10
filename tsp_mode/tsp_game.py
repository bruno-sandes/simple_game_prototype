"""
tsp_mode/tsp_game.py
====================
Loop principal do modo TSP - Adaptado para os Requisitos Acadêmicos.
Inclui: TSP (GPS), Inventário (Heapsort) e Capacidade Limitada (Mochila).
"""

import pygame
import math
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import (SCREEN_W, SCREEN_H, FPS, WHITE, BLACK, YELLOW, RED, GREEN,
                    GRAY, LIGHT_GRAY, ORANGE)
from tsp_mode.tsp_algorithm  import solve_tsp
from tsp_mode.inventory_heap import TSPInventory

# --- Configurações de Mecânica e Balanceamento ---
POINT_RADIUS   = 14
COLLECT_RADIUS = 25
BASE_SPEED     = 220.0
MAX_WEIGHT     = 60  # REQUISITO 2.4: Capacidade Limitada da Mochila!

# Gerador local de itens para evitar problemas de importação
TIPOS_DE_CARGA = [
    {"name": "Cristal de Dados", "weight": 5,  "value": 50, "color": (50, 200, 255)}, # Leve e Valioso
    {"name": "Kit Médico",       "weight": 10, "value": 30, "color": (50, 255, 50)},
    {"name": "Minério Comum",    "weight": 15, "value": 15, "color": (180, 180, 180)},
    {"name": "Sucata Pesada",    "weight": 25, "value": 5,  "color": (139, 69, 19)},  # Armadilha de Peso!
    {"name": "Motor Quebrado",   "weight": 35, "value": 10, "color": (200, 50, 50)},  # Armadilha de Peso!
]

class TSPPlayer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dist_traveled = 0.0

def gerar_pontos_espacados(num_points, min_dist=70):
    pontos = []
    while len(pontos) < num_points:
        px = random.randint(80, SCREEN_W - 320)
        py = random.randint(120, SCREEN_H - 80)
        muito_perto = any(math.hypot(px - pt[0], py - pt[1]) < min_dist for pt in pontos)
        if not muito_perto:
            pontos.append((px, py))
    return pontos

def run_tsp_mode(screen, clock, fonts):
    # 1. Setup do Mapa e Itens
    num_points = 10
    cpoints = gerar_pontos_espacados(num_points)
    base_position = cpoints[0] # Ponto 0 é sempre a Base
    
    # Atribui uma carga aleatória para cada ponto no mapa (A base recebe None)
    itens_no_mapa = [None] + [random.choice(TIPOS_DE_CARGA) for _ in range(num_points - 1)]
    
    player = TSPPlayer(base_position[0], base_position[1])
    inventory = TSPInventory()
    
    collected_mask = [False] * len(cpoints)
    collected_mask[0] = True # Base conta como visitada para não coletar logo no início
    
    # REQUISITO 2.1: Calcula a Rota Ótima (TSP) UMA ÚNICA VEZ para evitar o crash
    optimal_tour, optimal_dist, method_used = solve_tsp(cpoints)
    
    show_lines = True
    game_state = "PLAYING"
    score = 0
    message_log = ["OBJETIVO: Siga o GPS, pegue as cargas e volte à base!"]

    while True:
        dt = clock.tick(FPS) / 1000.0
        peso_total = inventory.total_weight
        
        # --- PROCESSAMENTO DE EVENTOS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 
                if game_state in ("WIN", "GAMEOVER") and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return
                if game_state == "PLAYING":
                    if event.key == pygame.K_TAB:
                        show_lines = not show_lines
                    # REQUISITO 2.4: Operações da Estrutura de Dados (Heapsort e Remoção)
                    if event.key == pygame.K_o:
                        current_sort = inventory.cycle_sort()
                        message_log.append(f"Mochila ordenada por: {current_sort.upper()}")
                    if event.key == pygame.K_e:
                        dropped = inventory.consume_top_item()
                        if dropped:
                            message_log.append(f"Descartou: {dropped['name']} (-{dropped['weight']}kg)")

        # --- LÓGICA DO JOGO ---
        if game_state == "PLAYING":
            
            # MECÂNICA DE CAPACIDADE: Se passar do limite, a nave não anda!
            if peso_total > MAX_WEIGHT:
                current_speed = 0.0
            else:
                current_speed = BASE_SPEED
            
            keys = pygame.key.get_pressed()
            dx = keys[pygame.K_d] - keys[pygame.K_a]
            dy = keys[pygame.K_s] - keys[pygame.K_w]
            
            if dx != 0 and dy != 0:
                dx *= 0.7071
                dy *= 0.7071

            old_x, old_y = player.x, player.y
            player.x += dx * current_speed * dt
            player.y += dy * current_speed * dt
            
            if current_speed > 0 and (dx != 0 or dy != 0):
                player.dist_traveled += math.hypot(player.x - old_x, player.y - old_y)

            # REQUISITO 2.3: Lógica de Coleta
            all_collected = all(collected_mask[1:])
            
            for i, pt in enumerate(cpoints):
                if i == 0 and not all_collected:
                    continue # Só pode voltar à base no final
                    
                if not collected_mask[i]:
                    if math.hypot(player.x - pt[0], player.y - pt[1]) < COLLECT_RADIUS:
                        collected_mask[i] = True
                        item_coletado = itens_no_mapa[i]
                        inventory.add(item_coletado)
                        message_log.append(f"Coletou: {item_coletado['name']}")

            # Condição de Vitória
            if all_collected and math.hypot(player.x - base_position[0], player.y - base_position[1]) < COLLECT_RADIUS:
                if peso_total <= MAX_WEIGHT:
                    game_state = "WIN"
                    valor_inventario = sum(item["value"] for item in inventory._items)
                    score = int(min(100, (optimal_dist / max(1, player.dist_traveled)) * 100)) * 10 + valor_inventario
                else:
                    message_log.append("AVISO: Descarte peso antes de atracar na base!")

        # --- RENDERIZAÇÃO E MAPA ---
        screen.fill((18, 18, 24))
        
        # Grid visual
        for x in range(0, SCREEN_W - 280, 40): pygame.draw.line(screen, (30, 30, 42), (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, 40): pygame.draw.line(screen, (30, 30, 42), (0, y), (SCREEN_W - 280, y))

        # Desenhar Rota TSP (Apenas ligando os pontos que o jogador AINDA não pegou)
        if show_lines and game_state == "PLAYING":
            pontos_restantes = [cpoints[idx] for idx in optimal_tour if not collected_mask[idx]]
            # Garante que a linha sempre termine na base
            if not all(collected_mask[1:]):
                pontos_restantes.append(base_position)
            
            if len(pontos_restantes) > 0:
                # Desenha uma linha guia saindo do jogador até o próximo ponto ótimo
                pygame.draw.line(screen, (40, 100, 160), (player.x, player.y), pontos_restantes[0], 2)
                if len(pontos_restantes) > 1:
                    pygame.draw.lines(screen, (40, 100, 160), False, pontos_restantes, 2)

        # Desenhar Pontos e Nomes dos Itens
        for i, pt in enumerate(cpoints):
            if i == 0:
                pygame.draw.rect(screen, GREEN if all(collected_mask[1:]) else ORANGE, (pt[0]-14, pt[1]-14, 28, 28))
                screen.blit(fonts.sm.render("BASE", True, WHITE), (pt[0]-15, pt[1]+15))
            elif not collected_mask[i]:
                cor_item = itens_no_mapa[i]["color"]
                pygame.draw.circle(screen, cor_item, pt, POINT_RADIUS)
                # Mostra o peso do item no chão para o jogador planejar
                peso_txt = fonts.sm.render(f"{itens_no_mapa[i]['weight']}kg", True, WHITE)
                screen.blit(peso_txt, (pt[0]-10, pt[1]+15))

        # Jogador
        pygame.draw.circle(screen, (0, 255, 150), (int(player.x), int(player.y)), 10)

        # --- HUD: PAINEL LATERAL INFORMATIVO ---
        panel_x = SCREEN_W - 280
        pygame.draw.rect(screen, (15, 15, 20), (panel_x, 0, 280, SCREEN_H))
        pygame.draw.line(screen, (60, 60, 80), (panel_x, 0), (panel_x, SCREEN_H), 3)

        screen.blit(fonts.md.render("TSP COMPUTAÇÃO", True, YELLOW), (panel_x + 20, 20))
        
        # Alerta de Sobrecarga (Capacidade Limitada)
        if peso_total > MAX_WEIGHT:
            alerta = fonts.md.render("SOBRECARGA!", True, RED)
            screen.blit(alerta, (panel_x + 20, 60))
            screen.blit(fonts.sm.render("Velocidade: 0 (Travado)", True, RED), (panel_x + 20, 90))
        else:
            screen.blit(fonts.sm.render(f"Velocidade: {current_speed:.0f}", True, GREEN), (panel_x + 20, 70))

        # Barra de Peso da Mochila
        screen.blit(fonts.sm.render(f"Mochila: {peso_total} / {MAX_WEIGHT} kg", True, WHITE), (panel_x + 20, 120))
        pygame.draw.rect(screen, (40, 10, 10), (panel_x + 20, 140, 240, 15))
        bar_width = int(240 * (min(peso_total, MAX_WEIGHT) / MAX_WEIGHT))
        pygame.draw.rect(screen, RED if peso_total > MAX_WEIGHT else GREEN, (panel_x + 20, 140, bar_width, 15))

        # Inventário e Heapsort
        screen.blit(fonts.sm.render(f"Itens Coletados: {inventory.count}", True, YELLOW), (panel_x + 20, 180))
        screen.blit(fonts.xs.render(f"Filtro Heapsort: {inventory.sort_mode}", True, LIGHT_GRAY), (panel_x + 20, 200))
        
        # Lista dos itens no inventário
        for idx, item in enumerate(inventory.get_sorted()[:5]): # Mostra os 5 do topo
            texto_item = f"- {item['name']} ({item['weight']}kg)"
            screen.blit(fonts.xs.render(texto_item, True, item['color']), (panel_x + 20, 230 + (idx * 25)))

        # Tutoriais de Tecla (Requisito para usabilidade do professor)
        pygame.draw.rect(screen, (25, 25, 35), (panel_x + 10, SCREEN_H - 160, 260, 140), 0, 5)
        screen.blit(fonts.xs.render("CONTROLES:", True, YELLOW), (panel_x + 20, SCREEN_H - 150))
        screen.blit(fonts.xs.render("[WASD] Mover a nave", True, WHITE), (panel_x + 20, SCREEN_H - 125))
        screen.blit(fonts.xs.render("[TAB] Ocultar GPS Azul", True, WHITE), (panel_x + 20, SCREEN_H - 100))
        screen.blit(fonts.xs.render("[O] Heapsort (Mudar Filtro)", True, WHITE), (panel_x + 20, SCREEN_H - 75))
        screen.blit(fonts.xs.render("[E] DESCARTAR ITEM DO TOPO", True, ORANGE), (panel_x + 20, SCREEN_H - 50))

        # Log de Mensagens
        if message_log:
            screen.blit(fonts.xs.render(message_log[-1], True, YELLOW), (20, SCREEN_H - 35))

        # Telas Finais
        if game_state == "WIN":
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((10, 40, 20, 220))
            screen.blit(overlay, (0, 0))
            t1 = fonts.xl.render("MISSÃO CONCLUÍDA!", True, GREEN)
            t2 = fonts.md.render(f"Pontuação Total: {score} pts", True, WHITE)
            screen.blit(t1, (SCREEN_W // 2 - t1.get_width() // 2, SCREEN_H // 2 - 50))
            screen.blit(t2, (SCREEN_W // 2 - t2.get_width() // 2, SCREEN_H // 2 + 20))

        pygame.display.flip()