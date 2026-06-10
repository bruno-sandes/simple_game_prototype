"""
tsp_mode/tsp_algorithm.py
=========================
Implementação do Travelling Salesman Problem (TSP).

ESTRATÉGIA:
  n <= 15  →  Held-Karp (programação dinâmica, solução EXATA)
               Complexidade: O(n² · 2ⁿ) tempo, O(n · 2ⁿ) espaço
  n >  15  →  Nearest-Neighbor (construção) + 2-opt (melhoria)
               Complexidade: O(n²) construção, O(n²) por iteração 2-opt

ESTRUTURAS DE DADOS:
  - Matriz de distâncias: lista 2D n×n (float)
  - Estado do Held-Karp: dict {(bitmask, cidade): custo}
  - Tour: lista de índices [0..n-1]
"""

import math
import time
from typing import List, Tuple


# ── Utilitário ─────────────────────────────────────────────────────────────

def _euclidean(p1: Tuple[float,float], p2: Tuple[float,float]) -> float:
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1])

def _build_dist_matrix(points: List[Tuple[float,float]]) -> List[List[float]]:
    n = len(points)
    return [[_euclidean(points[i], points[j]) for j in range(n)] for i in range(n)]

def _tour_length(tour: List[int], dist: List[List[float]]) -> float:
    return sum(dist[tour[i]][tour[(i+1) % len(tour)]] for i in range(len(tour)))


# ── Held-Karp (exato, n ≤ 15) ──────────────────────────────────────────────

def held_karp(points: List[Tuple[float,float]]) -> Tuple[List[int], float]:
    """
    Retorna (tour_ótimo, custo_total).
    tour_ótimo: lista de índices na ordem de visita, começando em 0.

    Programação Dinâmica sobre subconjuntos (bitmask DP):
      dp[(S, i)] = menor custo para visitar exatamente as cidades em S,
                   terminando na cidade i, partindo de 0.
    """
    n = len(points)
    dist = _build_dist_matrix(points)

    # dp[(mask, i)] = custo mínimo
    INF = float('inf')
    dp      = [[INF] * n for _ in range(1 << n)]
    parent  = [[-1]  * n for _ in range(1 << n)]

    dp[1][0] = 0.0   # começa na cidade 0; mask=0b1 (só cidade 0 visitada)

    for S in range(1, 1 << n):
        if not (S & 1):          # toda rota válida inclui cidade 0
            continue
        for i in range(n):
            if not (S >> i & 1): # i não está em S
                continue
            if dp[S][i] == INF:
                continue
            # Tenta ir para cada cidade j ainda não visitada
            for j in range(n):
                if S >> j & 1:
                    continue
                nS   = S | (1 << j)
                cost = dp[S][i] + dist[i][j]
                if cost < dp[nS][j]:
                    dp[nS][j]     = cost
                    parent[nS][j] = i

    # Encontra a última cidade que minimiza o retorno a 0
    full     = (1 << n) - 1
    min_cost = INF
    last     = 0

    for i in range(1, n):
        c = dp[full][i] + dist[i][0]
        if c < min_cost:
            min_cost = c
            last     = i

    # Reconstrói o tour pelo caminho reverso dos pais
    tour = []
    S    = full
    cur  = last
    while cur != -1:
        tour.append(cur)
        prev = parent[S][cur]
        S    = S ^ (1 << cur)
        cur  = prev
    tour.reverse()

    return tour, min_cost


# ── Nearest Neighbor (construção inicial para 2-opt) ───────────────────────

def _nearest_neighbor(dist: List[List[float]]) -> List[int]:
    n       = len(dist)
    visited = [False] * n
    tour    = [0]
    visited[0] = True

    for _ in range(n - 1):
        cur     = tour[-1]
        nearest = -1
        best    = float('inf')
        for j in range(n):
            if not visited[j] and dist[cur][j] < best:
                best    = dist[cur][j]
                nearest = j
        tour.append(nearest)
        visited[nearest] = True

    return tour


# ── 2-opt (melhoria local) ──────────────────────────────────────────────────

def two_opt(tour: List[int], dist: List[List[float]],
            max_iter: int = 1000) -> List[int]:
    """
    Melhora um tour existente usando 2-opt:
    a cada iteração, tenta reverter um segmento do tour para
    reduzir a distância total.
    Termina quando nenhuma melhoria é encontrada ou max_iter é atingido.
    """
    n       = len(tour)
    improved = True
    iters    = 0

    while improved and iters < max_iter:
        improved = False
        iters   += 1
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                # Custo das arestas que serão trocadas
                a, b = tour[i-1], tour[i]
                c, d = tour[j],   tour[(j+1) % n]
                delta = (dist[a][c] + dist[b][d]) - (dist[a][b] + dist[c][d])
                if delta < -1e-10:   # melhoria real
                    tour[i:j+1] = tour[i:j+1][::-1]
                    improved     = True

    return tour


# ── API pública ─────────────────────────────────────────────────────────────

def solve_tsp(points: List[Tuple[float,float]]) -> Tuple[List[int], float, str]:
    """
    Resolve o TSP para a lista de pontos.

    Retorna:
        (tour, custo_total, método_usado)
        tour: lista de índices na ordem ótima/heurística
        método: 'Held-Karp (exato)' ou '2-opt (heurística)'
    """
    n = len(points)
    if n <= 1:
        return list(range(n)), 0.0, "trivial"

    dist = _build_dist_matrix(points)

    if n <= 15:
        tour, cost = held_karp(points)
        method     = "Held-Karp (exato)"
    else:
        tour       = _nearest_neighbor(dist)
        tour       = two_opt(tour, dist)
        cost       = _tour_length(tour, dist)
        method     = "2-opt (heurística)"

    return tour, cost, method


def route_distance(visited_order: List[int],
                   points: List[Tuple[float,float]]) -> float:
    """Calcula a distância total de uma rota percorrida pelo jogador."""
    if len(visited_order) < 2:
        return 0.0
    dist = _build_dist_matrix(points)
    return _tour_length(visited_order, dist)
