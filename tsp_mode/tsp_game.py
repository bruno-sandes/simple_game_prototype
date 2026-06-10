import math
import os
import random
import sys

import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import SCREEN_W, SCREEN_H, FPS, WHITE, YELLOW, RED, GREEN, LIGHT_GRAY, ORANGE
from tsp_mode.inventory_heap import TSPInventory
from tsp_mode.tsp_algorithm import solve_tsp
from tsp_mode.tsp_config import (
    PANEL_W,
    MAP_RIGHT,
    POINT_RADIUS,
    COLLECT_RADIUS,
    BASE_SPEED,
    MIN_SPEED,
    MAX_ENERGY,
    MAX_EFFICIENCY_RATIO,
    NORMAL_ENERGY_MULT,
    HARD_ENERGY_MULT,
)
from tsp_mode.tsp_items import gerar_itens_planejados


class TSPPlayer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dist_traveled = 0.0


def gerar_pontos_espacados(num_points):
    base = (MAP_RIGHT // 2, SCREEN_H // 2)

    anchors = [
        (145, 145),
        (MAP_RIGHT - 165, 155),
        (155, SCREEN_H - 175),
        (MAP_RIGHT - 175, SCREEN_H - 170),
        (MAP_RIGHT // 2 - 210, 210),
        (MAP_RIGHT // 2 + 195, SCREEN_H - 230),
        (MAP_RIGHT // 2 + 115, 190),
        (MAP_RIGHT // 2 - 135, SCREEN_H - 215),
        (MAP_RIGHT // 2 + 25, SCREEN_H // 2 - 175),
    ]

    random.shuffle(anchors)
    pontos = [base]

    for ax, ay in anchors[:num_points - 1]:
        px = max(155, min(MAP_RIGHT - 155, ax + random.randint(-30, 30)))
        py = max(155, min(SCREEN_H - 165, ay + random.randint(-30, 30)))
        pontos.append((px, py))

    return pontos


def draw_text(screen, font, text, color, x, y):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))
    return y + surface.get_height() + 6


def draw_wrapped_text(screen, font, text, color, x, y, max_width):
    words = text.split(" ")
    line = ""

    for word in words:
        test = word if not line else line + " " + word
        if font.size(test)[0] <= max_width:
            line = test
        else:
            if line:
                surface = font.render(line, True, color)
                screen.blit(surface, (x, y))
                y += surface.get_height() + 5
            line = word

    if line:
        surface = font.render(line, True, color)
        screen.blit(surface, (x, y))
        y += surface.get_height() + 5

    return y


def get_logistic_effect(inventory):
    if inventory.sort_mode == "weight":
        return {
            "name": "Peso",
            "desc": "seguro: reduz gasto por carga pesada",
            "weight_factor": 0.48,
            "base_cost_mult": 1.00,
            "value_mult": 0.90,
            "rarity_mult": 1.00,
            "order_key": "weight",
        }

    if inventory.sort_mode == "value":
        return {
            "name": "Valor",
            "desc": "arriscado: mais pontos por valor, mais gasto",
            "weight_factor": 0.95,
            "base_cost_mult": 1.18,
            "value_mult": 1.75,
            "rarity_mult": 1.00,
            "order_key": "value",
        }

    return {
        "name": "Raridade",
        "desc": "muito arriscado: bonus alto se a rota for boa",
        "weight_factor": 1.05,
        "base_cost_mult": 1.25,
        "value_mult": 1.00,
        "rarity_mult": 2.20,
        "order_key": "rarity",
    }


def calcular_velocidade(inventory):
    effect = get_logistic_effect(inventory)
    effective_weight = inventory.total_weight * effect["weight_factor"]
    speed = BASE_SPEED - effective_weight * 0.62
    return max(MIN_SPEED, speed)


def calcular_gasto_energia(distance, inventory, hard_mode):
    effect = get_logistic_effect(inventory)
    effective_weight = inventory.total_weight * effect["weight_factor"]
    mode_mult = HARD_ENERGY_MULT if hard_mode else NORMAL_ENERGY_MULT

    base_cost = distance * 0.020 * effect["base_cost_mult"]
    weight_cost = distance * effective_weight * 0.00032

    return (base_cost + weight_cost) * mode_mult


def calcular_bonus_ordem(item, remaining_items, inventory):
    effect = get_logistic_effect(inventory)
    key = effect["order_key"]

    candidates = [it for it in remaining_items if it is not None]
    if not candidates:
        return 0, ""

    best = max(it[key] for it in candidates)

    if item[key] != best:
        return 0, ""

    if key == "weight":
        return 90, "Bonus: pegou carga pesada no modo Peso."
    if key == "value":
        return 170, "Bonus: pegou item valioso no modo Valor."
    return 220, "Bonus: pegou item raro no modo Raridade."


def calcular_bonus_raridade(optimal_dist, dist_traveled, inventory):
    effect = get_logistic_effect(inventory)
    ratio = dist_traveled / max(1, optimal_dist)
    rarity_sum = sum(item.get("rarity", 0) for item in inventory.items)

    if ratio <= 1.20:
        return int(rarity_sum * 95 * effect["rarity_mult"])
    if ratio <= 1.50:
        return int(rarity_sum * 48 * effect["rarity_mult"])
    return int(rarity_sum * 10 * effect["rarity_mult"])


def calcular_pontuacao(optimal_dist, dist_traveled, energy, inventory, order_bonus):
    effect = get_logistic_effect(inventory)
    ratio = dist_traveled / max(1, optimal_dist)

    route_score = int(max(0, 1100 * (1 - ((ratio - 1) / (MAX_EFFICIENCY_RATIO - 1)))))
    energy_score = int(max(0, energy) * 14)
    value_score = int(inventory.total_value * 120 * effect["value_mult"])
    rarity_score = calcular_bonus_raridade(optimal_dist, dist_traveled, inventory)

    return route_score + energy_score + value_score + rarity_score + order_bonus


def estimar_pontuacao_maxima(itens_no_mapa):
    total_value = sum(item["value"] for item in itens_no_mapa if item)
    total_rarity = sum(item["rarity"] for item in itens_no_mapa if item)

    return 1100 + 1400 + int(total_value * 120 * 1.75) + int(total_rarity * 95 * 2.20) + 1200


def eficiencia_percentual(optimal_dist, dist_traveled):
    if dist_traveled <= 0:
        return 0
    return max(0, min(100, int((optimal_dist / dist_traveled) * 100)))


def draw_arrow(screen, start, end, color):
    pygame.draw.line(screen, color, start, end, 4)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])

    left = (end[0] - 15 * math.cos(angle - math.pi / 6), end[1] - 15 * math.sin(angle - math.pi / 6))
    right = (end[0] - 15 * math.cos(angle + math.pi / 6), end[1] - 15 * math.sin(angle + math.pi / 6))

    pygame.draw.polygon(screen, color, [end, left, right])


def desenhar_rota_ideal_final(screen, fonts, cpoints, optimal_tour):
    route = [cpoints[idx] for idx in optimal_tour] + [cpoints[0]]

    for i in range(len(route) - 1):
        start = route[i]
        end = route[i + 1]
        mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)

        draw_arrow(screen, start, mid, (255, 215, 60))
        pygame.draw.line(screen, (255, 215, 60), mid, end, 4)

        step = fonts.sm.render(str(i + 1), True, (20, 20, 20))
        pygame.draw.circle(screen, (255, 215, 60), (int(start[0]), int(start[1])), 12)
        screen.blit(step, (start[0] - step.get_width() // 2, start[1] - step.get_height() // 2))

    label = fonts.md.render("Rota ideal calculada pelo TSP", True, (255, 215, 60))
    screen.blit(label, (20, 20))


def desenhar_base(screen, fonts, pt, all_collected):
    color = GREEN if all_collected else ORANGE

    pygame.draw.circle(screen, WHITE, pt, 34, 2)
    pygame.draw.polygon(
        screen,
        color,
        [(pt[0], pt[1] - 30), (pt[0] + 30, pt[1]), (pt[0], pt[1] + 30), (pt[0] - 30, pt[1])],
    )
    pygame.draw.polygon(
        screen,
        WHITE,
        [(pt[0], pt[1] - 30), (pt[0] + 30, pt[1]), (pt[0], pt[1] + 30), (pt[0] - 30, pt[1])],
        2,
    )

    label = fonts.md.render("BASE", True, WHITE)
    screen.blit(label, (pt[0] - label.get_width() // 2, pt[1] + 38))


def desenhar_player(screen, fonts, player, target_pos):
    pos = (int(player.x), int(player.y))

    ship = [
        (pos[0], pos[1] - 18),
        (pos[0] + 12, pos[1] + 14),
        (pos[0], pos[1] + 7),
        (pos[0] - 12, pos[1] + 14),
    ]

    pygame.draw.polygon(screen, (0, 240, 255), ship)
    pygame.draw.polygon(screen, WHITE, ship, 2)
    pygame.draw.circle(screen, (0, 240, 255), pos, 18, 1)

    if target_pos:
        pygame.draw.circle(screen, (0, 240, 255), (int(target_pos[0]), int(target_pos[1])), 8, 2)

    label = fonts.sm.render("VOCE", True, WHITE)
    screen.blit(label, (pos[0] - label.get_width() // 2, pos[1] + 20))


def desenhar_item(screen, fonts, pt, item):
    pygame.draw.circle(screen, item["color"], pt, POINT_RADIUS)
    pygame.draw.circle(screen, WHITE, pt, POINT_RADIUS, 2)

    weight = fonts.md.render(f"{item['weight']}kg", True, WHITE)
    screen.blit(weight, (pt[0] - weight.get_width() // 2, pt[1] - weight.get_height() // 2))

    name = fonts.sm.render(item["name"], True, item["color"])
    screen.blit(name, (pt[0] - name.get_width() // 2, pt[1] - 58))

    value_text = fonts.sm.render(f"Valor: {'*' * item['value']}", True, WHITE)
    rarity_text = fonts.sm.render(f"Raro:  {'*' * item['rarity']}", True, YELLOW)

    box_w = max(value_text.get_width(), rarity_text.get_width()) + 16
    box_h = value_text.get_height() + rarity_text.get_height() + 12
    box_x = pt[0] - box_w // 2
    box_y = pt[1] + 32

    pygame.draw.rect(screen, (8, 8, 14), (box_x, box_y, box_w, box_h))
    pygame.draw.rect(screen, item["color"], (box_x, box_y, box_w, box_h), 2)
    screen.blit(value_text, (box_x + 8, box_y + 5))
    screen.blit(rarity_text, (box_x + 8, box_y + 5 + value_text.get_height()))


def desenhar_mapa(screen, fonts, cpoints, itens_no_mapa, collected_mask, player, target_pos):
    screen.fill((18, 18, 24))

    for x in range(0, MAP_RIGHT, 40):
        pygame.draw.line(screen, (30, 30, 42), (x, 0), (x, SCREEN_H))
    for y in range(0, SCREEN_H, 40):
        pygame.draw.line(screen, (30, 30, 42), (0, y), (MAP_RIGHT, y))

    all_collected = all(collected_mask[1:])

    for i, pt in enumerate(cpoints):
        if i == 0:
            desenhar_base(screen, fonts, pt, all_collected)
        elif not collected_mask[i]:
            desenhar_item(screen, fonts, pt, itens_no_mapa[i])

    desenhar_player(screen, fonts, player, target_pos)


def desenhar_hud(screen, fonts, inventory, energy, speed, optimal_dist, player, num_items,
                order_bonus, hard_mode, moving, itens_no_mapa, collected_mask):
    panel_x = MAP_RIGHT
    inner_x = panel_x + 20
    text_w = PANEL_W - 40

    pygame.draw.rect(screen, (15, 15, 20), (panel_x, 0, PANEL_W, SCREEN_H))
    pygame.draw.line(screen, (60, 60, 80), (panel_x, 0), (panel_x, SCREEN_H), 3)

    y = 18
    y = draw_text(screen, fonts.lg, "TSP PUZZLE", YELLOW, inner_x, y)
    y = draw_text(screen, fonts.md, "DIFICIL: clique no mapa" if hard_mode else "NORMAL: WASD", WHITE, inner_x, y)

    y = draw_wrapped_text(screen, fonts.sm, "Colete tudo e volte para a BASE. A rota ideal aparece so no final.", LIGHT_GRAY, inner_x, y, text_w)

    y += 8
    y = draw_text(screen, fonts.md, f"Energia: {energy:.0f}/100", WHITE, inner_x, y)
    pygame.draw.rect(screen, (45, 15, 15), (inner_x, y + 2, text_w, 18))
    pygame.draw.rect(screen, GREEN if energy > 35 else RED, (inner_x, y + 2, int(text_w * max(0, energy / MAX_ENERGY)), 18))
    y += 32

    y = draw_text(screen, fonts.sm, f"Eficiencia: {eficiencia_percentual(optimal_dist, player.dist_traveled)}%", GREEN, inner_x, y)
    y = draw_text(screen, fonts.sm, f"Distancia ideal: {optimal_dist:.0f}", WHITE, inner_x, y)
    y = draw_text(screen, fonts.sm, f"Sua distancia: {player.dist_traveled:.0f}", WHITE, inner_x, y)
    y = draw_text(screen, fonts.sm, f"Velocidade: {speed:.0f}", WHITE, inner_x, y)
    y = draw_text(screen, fonts.sm, f"Peso carregado: {inventory.total_weight}kg", WHITE, inner_x, y)

    y += 8
    effect = get_logistic_effect(inventory)
    y = draw_text(screen, fonts.md, "HEAPSORT", YELLOW, inner_x, y)
    y = draw_wrapped_text(screen, fonts.sm, f"[O] Estrategia: {effect['name']}", WHITE, inner_x, y, text_w)
    y = draw_wrapped_text(screen, fonts.sm, effect["desc"] + ".", LIGHT_GRAY, inner_x, y, text_w)

    if hard_mode and moving:
        y = draw_wrapped_text(screen, fonts.sm, "Em movimento: troca bloqueada.", RED, inner_x, y, text_w)

    y += 8
    y = draw_text(screen, fonts.md, f"Itens: {inventory.count}/{num_items}", YELLOW, inner_x, y)
    y = draw_text(screen, fonts.sm, f"Bonus ordem: {order_bonus}", WHITE, inner_x, y)

    y += 6
    y = draw_text(screen, fonts.md, "ITENS NO MAPA", YELLOW, inner_x, y)
    shown = 0
    for i, item in enumerate(itens_no_mapa):
        if item and not collected_mask[i]:
            text = f"{item['name']}: {item['weight']}kg | valor {'*' * item['value']} | raro {'*' * item['rarity']}"
            y = draw_wrapped_text(screen, fonts.sm, text, item["color"], inner_x, y, text_w)
            shown += 1
        if shown >= 4:
            break

    y += 8
    y = draw_text(screen, fonts.md, "CONTROLES", YELLOW, inner_x, y)
    y = draw_text(screen, fonts.sm, "Clique: destino" if hard_mode else "WASD: mover", WHITE, inner_x, y)
    y = draw_text(screen, fonts.sm, "O: mudar Heapsort", WHITE, inner_x, y)
    y = draw_text(screen, fonts.sm, "ESC: sair", WHITE, inner_x, y)


def desenhar_briefing(screen, fonts):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((8, 12, 18, 238))
    screen.blit(overlay, (0, 0))

    title = fonts.xl.render("TSP PUZZLE", True, YELLOW)
    screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 55))

    lines = [
        ("Escolha o modo:", YELLOW),
        ("N - Normal: movimento por WASD.", WHITE),
        ("H - Dificil: clique no mapa e maior gasto de energia.", WHITE),
        ("No dificil, nao da para mudar Heapsort durante movimento.", RED),
        ("", WHITE),
        ("Valor e Raridade usam estrelas: mais estrelas = maior prioridade.", WHITE),
        ("Peso economiza energia. Valor e Raridade pontuam mais, mas gastam mais.", WHITE),
        ("ENTER inicia no Normal. H inicia no Dificil.", GREEN),
    ]

    y = 145
    for text, color in lines:
        if text == "":
            y += 18
            continue
        surface = fonts.md.render(text, True, color)
        screen.blit(surface, (SCREEN_W // 2 - surface.get_width() // 2, y))
        y += 40


def desenhar_inventario_final(screen, fonts, inventory):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((5, 8, 12, 238))
    screen.blit(overlay, (0, 0))

    title = fonts.xl.render("INVENTARIO COLETADO", True, YELLOW)
    screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 55))

    x = SCREEN_W // 2 - 300
    y = 130

    for item in inventory.items:
        line = f"{item['name']} | Peso: {item['weight']}kg | Valor: {'*' * item['value']} | Raridade: {'*' * item['rarity']}"
        y = draw_text(screen, fonts.md, line, item["color"], x, y)

    footer = fonts.md.render("Pressione I para voltar ao resultado", True, WHITE)
    screen.blit(footer, (SCREEN_W // 2 - footer.get_width() // 2, SCREEN_H - 70))


def run_tsp_mode(screen, clock, fonts):
    num_points = 10

    cpoints = gerar_pontos_espacados(num_points)
    base_position = cpoints[0]
    itens_no_mapa = gerar_itens_planejados(num_points - 1)

    player = TSPPlayer(base_position[0], base_position[1])
    inventory = TSPInventory()

    collected_mask = [False] * len(cpoints)
    collected_mask[0] = True

    optimal_tour, optimal_dist, method_used = solve_tsp(cpoints)
    max_score_estimate = estimar_pontuacao_maxima(itens_no_mapa)

    energy = MAX_ENERGY
    order_bonus = 0
    hard_mode = False
    target_pos = None
    show_inventory = False

    game_state = "BRIEFING"
    score = 0
    final_message = ""
    message_log = "Escolha Normal ou Dificil."

    while True:
        dt = clock.tick(FPS) / 1000.0
        speed = calcular_velocidade(inventory)
        moving = target_pos is not None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                if game_state == "BRIEFING":
                    if event.key == pygame.K_h:
                        hard_mode = True
                        game_state = "PLAYING"
                        message_log = "Modo Dificil: clique no mapa. Heapsort bloqueado durante movimento."
                    elif event.key in (pygame.K_n, pygame.K_RETURN, pygame.K_SPACE):
                        hard_mode = False
                        game_state = "PLAYING"
                        message_log = "Modo Normal: use WASD."

                elif game_state in ("WIN", "GAMEOVER"):
                    if event.key == pygame.K_i:
                        show_inventory = not show_inventory
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return

                elif game_state == "PLAYING" and event.key == pygame.K_o:
                    if hard_mode and moving:
                        message_log = "Nao pode mudar Heapsort durante movimento no modo dificil."
                    else:
                        inventory.cycle_sort()
                        effect = get_logistic_effect(inventory)
                        message_log = f"Heapsort: {effect['name']} - {effect['desc']}."

            if game_state == "PLAYING" and hard_mode and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if event.pos[0] < MAP_RIGHT:
                    target_pos = event.pos

        if game_state == "PLAYING":
            old_x, old_y = player.x, player.y
            dx = 0
            dy = 0

            if hard_mode:
                if target_pos:
                    vx = target_pos[0] - player.x
                    vy = target_pos[1] - player.y
                    dist = math.hypot(vx, vy)

                    if dist < 6:
                        target_pos = None
                    else:
                        dx = vx / dist
                        dy = vy / dist
            else:
                keys = pygame.key.get_pressed()
                dx = keys[pygame.K_d] - keys[pygame.K_a]
                dy = keys[pygame.K_s] - keys[pygame.K_w]
                if dx != 0 and dy != 0:
                    dx *= 0.7071
                    dy *= 0.7071

            player.x += dx * speed * dt
            player.y += dy * speed * dt
            player.x = max(10, min(MAP_RIGHT - 10, player.x))
            player.y = max(10, min(SCREEN_H - 10, player.y))

            moved_distance = math.hypot(player.x - old_x, player.y - old_y)

            if moved_distance > 0:
                player.dist_traveled += moved_distance
                energy -= calcular_gasto_energia(moved_distance, inventory, hard_mode)

            if energy <= 0:
                energy = 0
                game_state = "GAMEOVER"
                final_message = "ENERGIA ESGOTADA!"

            for i, pt in enumerate(cpoints):
                if i == 0 or collected_mask[i]:
                    continue

                if math.hypot(player.x - pt[0], player.y - pt[1]) < COLLECT_RADIUS:
                    remaining_items = [itens_no_mapa[j] for j in range(1, len(cpoints)) if not collected_mask[j]]
                    item = itens_no_mapa[i]
                    bonus, bonus_msg = calcular_bonus_ordem(item, remaining_items, inventory)

                    collected_mask[i] = True
                    inventory.add(item)
                    order_bonus += bonus

                    message_log = f"Coletou {item['name']}: {item['weight']}kg, valor {'*' * item['value']}, raridade {'*' * item['rarity']}."
                    if bonus_msg:
                        message_log += " " + bonus_msg

            if all(collected_mask[1:]):
                dist_base = math.hypot(player.x - base_position[0], player.y - base_position[1])

                if dist_base < COLLECT_RADIUS:
                    if player.dist_traveled / max(1, optimal_dist) <= MAX_EFFICIENCY_RATIO:
                        game_state = "WIN"
                        score = calcular_pontuacao(optimal_dist, player.dist_traveled, energy, inventory, order_bonus)
                        final_message = "MISSAO CONCLUIDA!"
                    else:
                        game_state = "GAMEOVER"
                        final_message = "ROTA MUITO INEFICIENTE!"

        desenhar_mapa(screen, fonts, cpoints, itens_no_mapa, collected_mask, player, target_pos)

        if game_state in ("WIN", "GAMEOVER"):
            desenhar_rota_ideal_final(screen, fonts, cpoints, optimal_tour)

        desenhar_hud(
            screen, fonts, inventory, energy, speed, optimal_dist, player,
            num_points - 1, order_bonus, hard_mode, moving, itens_no_mapa, collected_mask
        )

        if message_log:
            pygame.draw.rect(screen, (12, 12, 18), (8, SCREEN_H - 58, MAP_RIGHT - 16, 50))
            draw_wrapped_text(screen, fonts.sm, message_log, YELLOW, 18, SCREEN_H - 48, MAP_RIGHT - 36)

        if game_state == "BRIEFING":
            desenhar_briefing(screen, fonts)

        if game_state in ("WIN", "GAMEOVER"):
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((10, 40, 20, 185) if game_state == "WIN" else (45, 10, 10, 185))
            screen.blit(overlay, (0, 0))
            desenhar_rota_ideal_final(screen, fonts, cpoints, optimal_tour)

            title_color = GREEN if game_state == "WIN" else RED
            t1 = fonts.xl.render(final_message, True, title_color)
            screen.blit(t1, (SCREEN_W // 2 - t1.get_width() // 2, SCREEN_H // 2 - 125))

            efficiency = eficiencia_percentual(optimal_dist, player.dist_traveled)
            lines = [
                f"Pontuacao: {score} pts",
                f"Pontuacao maxima estimada: {max_score_estimate} pts",
                f"Eficiencia da rota: {efficiency}%",
                f"Sua distancia: {player.dist_traveled:.0f} | Ideal TSP: {optimal_dist:.0f}",
                f"Energia restante: {energy:.0f} | Bonus ordem: {order_bonus}",
                "Pressione I para abrir o inventario",
            ]

            y = SCREEN_H // 2 - 50
            for line in lines:
                surface = fonts.md.render(line, True, WHITE)
                screen.blit(surface, (SCREEN_W // 2 - surface.get_width() // 2, y))
                y += 34

            footer = fonts.sm.render("ENTER/ESPACO para voltar ao menu", True, WHITE)
            screen.blit(footer, (SCREEN_W // 2 - footer.get_width() // 2, SCREEN_H // 2 + 165))

            if show_inventory:
                desenhar_inventario_final(screen, fonts, inventory)

        pygame.display.flip()