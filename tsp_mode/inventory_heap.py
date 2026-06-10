"""
tsp_mode/inventory_heap.py
==========================
Inventario do modo TSP com ordenacao por Heapsort.

Uso no jogo:
- Guarda os itens coletados.
- Permite consultar peso total, quantidade e itens ordenados.
- Tecla O no jogo alterna o criterio do Heapsort: peso, valor ou raridade.

Observacao:
O jogador nao descarta itens neste modo, porque o objetivo e coletar todos
os pontos e voltar para a base antes do tempo acabar.
"""

from typing import Dict, List, Optional


def heapsort(arr: List[Dict], key: str) -> List[Dict]:
    """
    Ordena uma lista de dicionarios usando Heapsort.
    Retorna em ordem decrescente pelo campo informado.
    Exemplo: maior peso primeiro, maior valor primeiro, maior raridade primeiro.
    """
    n = len(arr)

    def heapify(a: List[Dict], heap_size: int, root: int) -> None:
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2

        if left < heap_size and a[left].get(key, 0) > a[largest].get(key, 0):
            largest = left

        if right < heap_size and a[right].get(key, 0) > a[largest].get(key, 0):
            largest = right

        if largest != root:
            a[root], a[largest] = a[largest], a[root]
            heapify(a, heap_size, largest)

    result = list(arr)

    for i in range(n // 2 - 1, -1, -1):
        heapify(result, n, i)

    for i in range(n - 1, 0, -1):
        result[i], result[0] = result[0], result[i]
        heapify(result, i, 0)

    return result[::-1]


class TSPInventory:
    SORT_MODES = ["weight", "value", "rarity"]

    SORT_LABELS = {
        "weight": "peso",
        "value": "valor",
        "rarity": "raridade",
    }

    def __init__(self):
        self._items: List[Dict] = []
        self._sort_mode: str = "weight"
        self._sorted: List[Dict] = []
        self._dirty: bool = True

    def add(self, item: Optional[Dict]) -> None:
        if item is None:
            return

        self._items.append(dict(item))
        self._dirty = True

    def remove_by_name(self, item_name: str) -> Optional[Dict]:
        """
        Operacao de remover do inventario, mantida para cumprir o requisito
        de estrutura de dados. Nao e usada como mecanica principal do jogo.
        """
        for item in self._items:
            if item.get("name") == item_name:
                self._items.remove(item)
                self._dirty = True
                return item

        return None

    def get_sorted(self) -> List[Dict]:
        if self._dirty:
            self._sorted = heapsort(self._items, self._sort_mode)
            self._dirty = False

        return self._sorted

    def cycle_sort(self) -> str:
        idx = self.SORT_MODES.index(self._sort_mode)
        self._sort_mode = self.SORT_MODES[(idx + 1) % len(self.SORT_MODES)]
        self._dirty = True
        return self._sort_mode

    @property
    def total_weight(self) -> int:
        return sum(item.get("weight", 0) for item in self._items)

    @property
    def total_value(self) -> int:
        return sum(item.get("value", 0) for item in self._items)

    @property
    def count(self) -> int:
        return len(self._items)

    @property
    def sort_mode(self) -> str:
        return self._sort_mode

    @property
    def sort_label(self) -> str:
        return self.SORT_LABELS.get(self._sort_mode, self._sort_mode)

    @property
    def items(self) -> List[Dict]:
        return list(self._items)