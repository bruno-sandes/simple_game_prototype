"""
systems/inventory_manager.py
=============================
Inventário baseado em dicionário (Map/dict) que agrupa
materiais por tipo e acumula quantidades.

Estrutura de dados central:
    _stock: dict[str, int]   — { item_type: quantidade }

Ordenação ativa (refletida na UI):
    sort_by("label")   — alfabético pelo nome
    sort_by("count")   — do mais ao menos comum
    sort_by("type")    — por categoria (materiais antes de equipamentos)

Categorias (para sort_by "type"):
    material  — gem, coin, herb, ore, wood
    consumable — hp_potion, scroll
    equipment  — sword, shield, key

Uso:
    inv = InventoryManager()
    inv.add("gem", 3)
    inv.add("hp_potion")
    inv.remove("gem")        # → True
    inv.count("gem")         # → 2
    inv.sorted_display()     # → [(label, count, color, type), ...]
    inv.use_potion()         # → True se tinha poção
"""

from config import ITEM_DEFS


# ── Categoria de cada tipo ──────────────────────────────────────────
_CATEGORY: dict[str, int] = {
    # ordem numérica define prioridade no sort_by("type")
    "gem":      0,
    "coin":     0,
    "scroll":   1,
    "hp_potion":1,
    "sword":    2,
    "shield":   2,
    "key":      2,
}


class InventoryManager:
    """
    Inventário agrupado por tipo com ordenação configurável.

    Parâmetros:
        sort_mode — modo de ordenação inicial
            "label"  → A→Z pelo nome do item
            "count"  → maior quantidade primeiro
            "type"   → material < consumível < equipamento
    """

    SORT_MODES = ("label", "count", "type")

    def __init__(self, sort_mode: str = "label"):
        self._stock: dict[str, int] = {}   # estrutura principal
        self._mode = sort_mode

    # ------------------------------------------------------------------ #
    #  Manipulação do estoque                                              #
    # ------------------------------------------------------------------ #
    def add(self, item_type: str, amount: int = 1) -> None:
        """Adiciona `amount` unidades de `item_type`."""
        if item_type not in ITEM_DEFS:
            return
        self._stock[item_type] = self._stock.get(item_type, 0) + amount

    def remove(self, item_type: str, amount: int = 1) -> bool:
        """
        Remove `amount` unidades. Retorna True se bem-sucedido.
        Remove a chave do dict ao zerar.
        """
        current = self._stock.get(item_type, 0)
        if current < amount:
            return False
        new_val = current - amount
        if new_val == 0:
            del self._stock[item_type]
        else:
            self._stock[item_type] = new_val
        return True

    def count(self, item_type: str) -> int:
        """Quantidade de `item_type` no inventário."""
        return self._stock.get(item_type, 0)

    def has(self, item_type: str) -> bool:
        return self.count(item_type) > 0

    def use_potion(self) -> bool:
        """Tenta consumir 1 Poção de Vida. Retorna True se bem-sucedido."""
        return self.remove("hp_potion")

    @property
    def total(self) -> int:
        """Total de unidades no inventário."""
        return sum(self._stock.values())

    @property
    def unique_types(self) -> int:
        """Quantos tipos distintos há no inventário."""
        return len(self._stock)

    def is_empty(self) -> bool:
        return not self._stock

    # ------------------------------------------------------------------ #
    #  Ordenação                                                           #
    # ------------------------------------------------------------------ #
    def sort_by(self, mode: str) -> None:
        """Define o modo de ordenação ativo. Reflete na próxima chamada a sorted_display()."""
        if mode in self.SORT_MODES:
            self._mode = mode

    def cycle_sort(self) -> str:
        """Avança para o próximo modo de ordenação. Retorna o novo modo."""
        idx = self.SORT_MODES.index(self._mode)
        self._mode = self.SORT_MODES[(idx + 1) % len(self.SORT_MODES)]
        return self._mode

    @property
    def current_sort(self) -> str:
        return self._mode

    # ------------------------------------------------------------------ #
    #  Exibição                                                            #
    # ------------------------------------------------------------------ #
    def sorted_display(self) -> list[dict]:
        """
        Retorna lista de dicts ordenados pelo modo ativo:
            {type, label, count, color, icon, category}
        """
        rows = []
        for itype, cnt in self._stock.items():
            d = ITEM_DEFS.get(itype, {})
            rows.append({
                "type":     itype,
                "label":    d.get("label", itype),
                "count":    cnt,
                "color":    d.get("color", (180, 180, 180)),
                "icon":     d.get("icon",  "??"),
                "category": _CATEGORY.get(itype, 9),
            })

        if self._mode == "label":
            rows.sort(key=lambda r: r["label"])
        elif self._mode == "count":
            rows.sort(key=lambda r: -r["count"])
        elif self._mode == "type":
            rows.sort(key=lambda r: (r["category"], r["label"]))

        return rows

    # ── Representação textual para debug ──────────────────────────────
    def __repr__(self) -> str:
        return f"InventoryManager({dict(self._stock)}, sort='{self._mode}')"