"""
tsp_mode/inventory_heap.py
===========================
Inventário baseado em Min-Heap com Heapsort.
O Heapsort agora tem utilidade real: ordenar itens pesados para o topo
para que o jogador possa descartá-los e recuperar velocidade de movimento!
"""

from typing import List, Dict

# tsp_mode/inventory_heap.py

ITEM_TYPES = [
    {"name": "Gema Azul",    "weight": 5,  "value": 50, "rarity": 3, "icon": "GE", "color": (80,  200, 255)},
    {"name": "Moeda",        "weight": 1,  "value": 10, "rarity": 1, "icon": "$$", "color": (255, 220, 0)},
    {"name": "Sucata",       "weight": 20, "value": 5,  "rarity": 1, "icon": "SC", "color": (150, 150, 150)},
    {"name": "Componente",   "weight": 10, "value": 20, "rarity": 2, "icon": "CP", "color": (50,  255, 50)},
    {"name": "Motor Pesado", "weight": 35, "value": 30, "rarity": 4, "icon": "MT", "color": (200, 50,  50)},
]

def heapsort(arr: List[Dict], key: str) -> List[Dict]:
    """Ordena uma lista de dicionários usando Heapsort."""
    n = len(arr)
    # Criamos uma cópia para ordenar
    data = list(arr)
    
    # Função para manter a propriedade de Max-Heap
    def heapify(n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        # Usa .get(key, 0) para evitar KeyError caso o item esteja incompleto
        if l < n and data[l].get(key, 0) > data[largest].get(key, 0):
            largest = l
        if r < n and data[r].get(key, 0) > data[largest].get(key, 0):
            largest = r
        if largest != i:
            data[i], data[largest] = data[largest], data[i]
            heapify(n, largest)

    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)
    for i in range(n - 1, 0, -1):
        data[i], data[0] = data[0], data[i]
        heapify(i, 0)
    return data # Retorna a lista ordenada (Ascendente)

class TSPInventory:
    def __init__(self):
        self._items = []
        self._sort_mode = "weight" # Sempre por peso

    def add(self, item):
        self._items.append(dict(item))
    
    def get_sorted(self):
        # Sempre ordena pelo critério definido (weight) antes de retornar
        return heapsort(self._items, self._sort_mode)

    @property
    def total_weight(self):
        return sum(item.get("weight", 0) for item in self._items)
    
    @property
    def count(self):
        return len(self._items)

    def consume_top_item(self):
        """Remove o item mais pesado (último da lista ascendente do heapsort)"""
        if not self._items: return None
        sorted_list = self.get_sorted()
        heaviest = sorted_list[-1]
        self._items.remove(heaviest)
        return heaviest

    def cycle_sort(self):
        # Apenas para o requisito, mas o foco é sempre weight
        self._sort_mode = "value" if self._sort_mode == "weight" else "weight"
        return self._sort_mode

'''# Implementação clássica do Heapsort (Min-Heap)
def heapsort(arr: List[Dict], key: str) -> List[Dict]:
    n = len(arr)
    # Função auxiliar para manter a propriedade max-heap (para ordem decrescente)
    def heapify(a, n, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and a[left][key] > a[largest][key]:
            largest = left
        if right < n and a[right][key] > a[largest][key]:
            largest = right
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            heapify(a, n, largest)

    # Cópia para não alterar o original
    result = list(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(result, n, i)
    for i in range(n - 1, 0, -1):
        result[i], result[0] = result[0], result[i]
        heapify(result, i, 0)
    
    # Invertendo para ter o MAIOR valor no topo (ex: o mais pesado primeiro)
    return result[::-1]


# ── Inventário do TSP Mode ───────────────────────────────────────────────────
class TSPInventory:
    SORT_MODES = ["peso", "valor", "raridade"] # 'peso' agora é o mais importante

    def __init__(self):
        self._items:     List[Dict] = []
        self._sort_mode: str        = "peso"
        self._sorted:    List[Dict] = []
        self._dirty:     bool       = False

    def add(self, item: Dict) -> None:
        self._items.append(dict(item))
        self._dirty = True

    def get_sorted(self) -> List[Dict]:
        if self._dirty:
            self._sorted = heapsort(self._items, self._sort_mode)
            self._dirty  = False
        return self._sorted

    def cycle_sort(self) -> str:
        idx              = self.SORT_MODES.index(self._sort_mode)
        self._sort_mode  = self.SORT_MODES[(idx + 1) % len(self.SORT_MODES)]
        self._dirty      = True
        return self._sort_mode
    
    # NOVA FUNÇÃO: Calcula o peso total para afetar a velocidade
    @property
    def total_weight(self) -> int:
        return sum(item["weight"] for item in self._items)

    # NOVA FUNÇÃO: Consome (descarta) o item que estiver no topo do Heapsort
    def consume_top_item(self) -> dict:
        if not self._items: return None
        if self._dirty:
            self.get_sorted()
        if self._sorted:
            item_to_remove = self._sorted.pop(0)
            self._items.remove(item_to_remove)
            self._dirty = True
            return item_to_remove
        return None

    @property
    def count(self) -> int: return len(self._items)
    @property
    def sort_mode(self) -> str: return self._sort_mode'''