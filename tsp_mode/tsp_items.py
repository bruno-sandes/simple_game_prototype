ITEM_TYPES = [
    {"name": "Cristal", "weight": 5, "value": 5, "rarity": 5, "color": (50, 200, 255)},
    {"name": "Kit Medico", "weight": 10, "value": 4, "rarity": 3, "color": (50, 255, 50)},
    {"name": "Minerio", "weight": 15, "value": 2, "rarity": 1, "color": (190, 190, 190)},
    {"name": "Sucata", "weight": 25, "value": 1, "rarity": 1, "color": (170, 95, 35)},
    {"name": "Motor", "weight": 35, "value": 2, "rarity": 2, "color": (220, 55, 55)},
]


def gerar_itens_planejados(num_items):
    pool = [
        ITEM_TYPES[4],
        ITEM_TYPES[4],
        ITEM_TYPES[3],
        ITEM_TYPES[3],
        ITEM_TYPES[2],
        ITEM_TYPES[2],
        ITEM_TYPES[1],
        ITEM_TYPES[0],
        ITEM_TYPES[0],
    ]

    return [None] + [dict(item) for item in pool[:num_items]]