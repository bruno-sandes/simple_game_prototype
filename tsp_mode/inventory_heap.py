"""
tsp_mode/inventory_heap.py
===========================
Inventário baseado em Min-Heap com Heapsort.

SEGUNDO PROBLEMA COMPUTACIONAL:
  Heapsort aplicado ao inventário do TSP Mode.
  O jogador coleta itens com peso, valor e raridade distintos.
  O inventário pode ser ordenado por qualquer um desses critérios.

ESTRUTURAS:
  - Heap: lista Python usada como árvore binária completa
    filho_esq(i) = 2i+1  |  filho_dir(i) = 2i+2  |  pai(i) = (i-1)//2
  - Item: dict {name, weight, value, rarity, icon, color}

COMPLEXIDADE:
  heapsort: O(n log n) tempo, O(1) espaço adicional
  insert:   O(log n)
  pop_min:  O(log n)
"""

from typing import List, Dict, Any


# ── Definição dos itens coletáveis no TSP Mode ──────────────────────────────

ITEM_TYPES = [
    {"name": "Gema Azul",    "weight": 1, "value": 10, "rarity": 3, "icon": "GE", "color": (80,  200, 255)},
    {"name": "Moeda",        "weight": 1, "value":  5, "rarity": 1, "icon": "$$", "color": (255, 220,   0)},
    {"name": "Pocao",        "weight": 2, "value":  8, "rarity": 2, "icon": "HP", "color": (255,  80,  80)},
    {"name": "Pergaminho",   "weight": 1, "value": 12, "rarity": 3, "icon": "SC", "color": (220, 180, 120)},
    {"name": "Espada",       "weight": 3, "value": 20, "rarity": 4, "icon": "SW", "color": (200, 210, 255)},
    {"name": "Escudo",       "weight": 3, "value": 15, "rarity": 4, "icon": "SH", "color": (255, 200,  80)},
    {"name": "Chave Magica", "weight": 1, "value": 25, "rarity": 5, "icon": "KY", "color": (255, 255,  50)},
]

SORT_KEYS = {
    "valor":    lambda item: item["value"],
    "peso":     lambda item: item["weight"],
    "raridade": lambda item: item["rarity"],
    "nome":     lambda item: item["name"],
}


# ── Heapsort ────────────────────────────────────────────────────────────────

def _heapify_down(arr: List, n: int, i: int, key_fn) -> None:
    """
    Ajusta o heap para baixo a partir do índice i (max-heap pelo key_fn).
    Usado internamente pelo heapsort.
    """
    largest = i
    left    = 2 * i + 1
    right   = 2 * i + 2

    if left < n and key_fn(arr[left]) > key_fn(arr[largest]):
        largest = left
    if right < n and key_fn(arr[right]) > key_fn(arr[largest]):
        largest = right

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        _heapify_down(arr, n, largest, key_fn)


def heapsort(items: List[Dict], sort_by: str = "valor") -> List[Dict]:
    """
    Ordena uma lista de itens usando Heapsort.
    sort_by: 'valor' | 'peso' | 'raridade' | 'nome'

    Retorna nova lista ordenada em ordem DECRESCENTE do critério escolhido
    (maior valor primeiro, maior raridade primeiro, etc.).
    """
    arr    = list(items)   # cópia para não modificar o original
    n      = len(arr)
    key_fn = SORT_KEYS.get(sort_by, SORT_KEYS["valor"])

    # Fase 1 — Build Max-Heap: heapify de baixo para cima
    for i in range(n // 2 - 1, -1, -1):
        _heapify_down(arr, n, i, key_fn)

    # Fase 2 — Extração: move raiz (max) para o final, reduz heap
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        _heapify_down(arr, i, 0, key_fn)

    arr.reverse()   # decrescente (maior primeiro)
    return arr


# ── Min-Heap para fila de prioridade (estrutura auxiliar) ───────────────────

class MinHeap:
    """
    Min-Heap genérico para uso interno (ex.: nearest-neighbor no TSP).
    Armazena tuplas (prioridade, dado).
    """

    def __init__(self):
        self._data: List = []

    def push(self, priority: float, item: Any) -> None:
        self._data.append((priority, item))
        self._sift_up(len(self._data) - 1)

    def pop(self) -> Any:
        if not self._data:
            return None
        self._data[0], self._data[-1] = self._data[-1], self._data[0]
        item = self._data.pop()
        if self._data:
            self._sift_down(0)
        return item[1]

    def __len__(self):
        return len(self._data)

    def _sift_up(self, i: int) -> None:
        while i > 0:
            parent = (i - 1) // 2
            if self._data[i][0] < self._data[parent][0]:
                self._data[i], self._data[parent] = self._data[parent], self._data[i]
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        n = len(self._data)
        while True:
            smallest = i
            l, r     = 2*i+1, 2*i+2
            if l < n and self._data[l][0] < self._data[smallest][0]:
                smallest = l
            if r < n and self._data[r][0] < self._data[smallest][0]:
                smallest = r
            if smallest == i:
                break
            self._data[i], self._data[smallest] = self._data[smallest], self._data[i]
            i = smallest


# ── Inventário do TSP Mode ───────────────────────────────────────────────────

class TSPInventory:
    """
    Inventário do TSP Mode.
    Itens são adicionados conforme coletados.
    Ordenação via Heapsort por critério configurável.
    """

    SORT_MODES = ["valor", "peso", "raridade", "nome"]

    def __init__(self):
        self._items:     List[Dict] = []
        self._sort_mode: str        = "valor"
        self._sorted:    List[Dict] = []
        self._dirty:     bool       = False

    def add(self, item: Dict) -> None:
        self._items.append(dict(item))   # cópia do item
        self._dirty = True

    def get_sorted(self) -> List[Dict]:
        """Retorna lista ordenada por Heapsort. Re-ordena só se houve mudança."""
        if self._dirty:
            self._sorted = heapsort(self._items, self._sort_mode)
            self._dirty  = False
        return self._sorted

    def cycle_sort(self) -> str:
        idx              = self.SORT_MODES.index(self._sort_mode)
        self._sort_mode  = self.SORT_MODES[(idx + 1) % len(self.SORT_MODES)]
        self._dirty      = True
        return self._sort_mode

    @property
    def sort_mode(self) -> str:
        return self._sort_mode

    @property
    def count(self) -> int:
        return len(self._items)

    @property
    def total_value(self) -> int:
        return sum(i["value"] for i in self._items)

    @property
    def total_weight(self) -> int:
        return sum(i["weight"] for i in self._items)
