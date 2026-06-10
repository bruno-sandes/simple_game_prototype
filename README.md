# RPGame Lite

Jogo 2D desenvolvido em Python + Pygame com algoritmos computacionais integrados.

## Como executar

```bash
pip install pygame
python main.py
```

## Modos de jogo

### 1 — RPG Dungeon (Modo Principal)
RPG de exploração com sistema de inventário, mobs, boss e sistema de andares.
- WASD para mover
- Clique direito para atacar
- E para interagir com NPCs / usar porta
- I para inventário · F para poção · ESC para pausar

### 2 — TSP Puzzle (Modo Acadêmico)
Puzzle de coleta onde o jogador tenta percorrer o menor caminho possível
visitando todos os pontos de coleta do mapa.
- TAB alterna visualização da rota ótima
- I abre inventário · O muda ordenação (Heapsort)
- WASD para mover

---

## Algoritmos implementados

### Requisito 2.1 — TSP (Travelling Salesman Problem)
**Arquivo:** `tsp_mode/tsp_algorithm.py`

| n pontos | Algoritmo | Complexidade |
|---|---|---|
| n ≤ 15 | Held-Karp (Programação Dinâmica com bitmask) | O(n² · 2ⁿ) |
| n > 15 | Nearest-Neighbor + 2-opt | O(n²) |

A rota ótima é desenhada visualmente no mapa com setas e números.
O jogador vê sua eficiência em tempo real comparado ao ótimo calculado.

### Requisito 2.2 — Sistema de Inventário
**Arquivo:** `tsp_mode/inventory_heap.py` e `systems/inventory_manager.py`

- Inventário do TSP Mode usa estrutura de dados **Heap (Min-Heap)**
- Operações: adicionar O(log n), ordenar O(n log n)
- Inventário do RPG Mode usa **dicionário (dict)** com chave por tipo de item

### Requisito 2.3 — Coleta de Itens
Mecânica central em ambos os modos:
- RPG: coleta automática por contato com raio de coleta
- TSP: coleta ao aproximar do ponto de coleta (raio 22px)

### Segundo Problema Computacional — Heapsort
**Arquivo:** `tsp_mode/inventory_heap.py`

```
Algoritmo: Heapsort
Complexidade: O(n log n) tempo, O(1) espaço adicional
Aplicação: ordenação do inventário por valor, peso, raridade ou nome
```

Fase 1 (Build Heap): transforma o array em max-heap em O(n).
Fase 2 (Extração): remove raiz repetidamente, ordenando em O(n log n).

---

## Estrutura de pastas

```
simple_game_prototype/
├── main.py                   # Ponto de entrada + menu de seleção de modo
├── game.py                   # Loop principal do RPG
├── config.py                 # Constantes globais
│
├── tsp_mode/                 # Modo TSP (algoritmos acadêmicos)
│   ├── __init__.py
│   ├── tsp_algorithm.py      # Held-Karp + 2-opt
│   ├── inventory_heap.py     # Heapsort + MinHeap
│   └── tsp_game.py           # Loop do jogo TSP
│
├── entities/                 # Personagens do RPG
├── world/                    # Mapa e itens
├── systems/                  # Colisão, inventário (dict)
├── ui/                       # Interface gráfica
└── screens/                  # Telas e animações
```

---

## Justificativa das escolhas algorítmicas

**Por que Held-Karp para n ≤ 15?**
Held-Karp garante a solução ótima em O(n²·2ⁿ). Para n=15: ~7 milhões de operações, executável em < 1s. Acima disso, 2ⁿ cresce inviável.

**Por que 2-opt para n > 15?**
2-opt é uma meta-heurística local que melhora iterativamente um tour inicial (nearest-neighbor), obtendo soluções próximas do ótimo em O(n²) por iteração — adequado para gameplay em tempo real.

**Por que Heapsort no inventário?**
Heapsort garante O(n log n) no pior caso (diferente do quicksort que pode degradar para O(n²)) e usa espaço O(1) adicional. Ideal para inventários com muitos itens e reordenações frequentes.

---

## Issues sugeridas para o repositório

```
[algoritmo] Implementar Held-Karp para TSP exato (n ≤ 15)
[algoritmo] Implementar heurística 2-opt para TSP (n > 15)
[inventário] Implementar Heapsort para ordenação do inventário
[gameplay]  Criar modo TSP Puzzle com visualização de rota
[mapa]      Geração de pontos de coleta aleatórios no TSP Mode
[bug]       Corrigir ghost invadindo zona segura
[documentação] Adicionar README com algoritmos e instruções
```
