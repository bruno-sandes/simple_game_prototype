"""systems/inventory_manager.py — inventário baseado em dict."""
from config import ITEM_DEFS

_CATEGORY = {"gem":0,"coin":0,"scroll":1,"hp_potion":1,"sword":2,"shield":2,"key":2}

class InventoryManager:
    SORT_MODES = ("label","count","type")

    def __init__(self, sort_mode="label"):
        self._stock = {}
        self._mode  = sort_mode

    def add(self, item_type, amount=1):
        if item_type not in ITEM_DEFS: return
        self._stock[item_type] = self._stock.get(item_type,0) + amount

    def remove(self, item_type, amount=1):
        cur = self._stock.get(item_type,0)
        if cur<amount: return False
        new = cur-amount
        if new==0: del self._stock[item_type]
        else: self._stock[item_type]=new
        return True

    def count(self, item_type): return self._stock.get(item_type,0)
    def has(self, item_type):   return self.count(item_type)>0

    def use_potion(self):
        return self.remove("hp_potion")

    @property
    def total(self): return sum(self._stock.values())
    @property
    def unique_types(self): return len(self._stock)
    def is_empty(self): return not self._stock

    def sort_by(self, mode):
        if mode in self.SORT_MODES: self._mode=mode

    def cycle_sort(self):
        i = self.SORT_MODES.index(self._mode)
        self._mode = self.SORT_MODES[(i+1)%len(self.SORT_MODES)]
        return self._mode

    @property
    def current_sort(self): return self._mode

    def sorted_display(self):
        rows=[]
        for itype,cnt in self._stock.items():
            d=ITEM_DEFS.get(itype,{})
            rows.append({"type":itype,"label":d.get("label",itype),"count":cnt,
                         "color":d.get("color",(180,180,180)),"icon":d.get("icon","??"),
                         "category":_CATEGORY.get(itype,9)})
        if self._mode=="label":  rows.sort(key=lambda r:r["label"])
        elif self._mode=="count": rows.sort(key=lambda r:-r["count"])
        elif self._mode=="type":  rows.sort(key=lambda r:(r["category"],r["label"]))
        return rows

    def __iter__(self): return iter(self._stock.items())
