"""
config.py
=========
Todas as constantes globais do jogo:
  - Dimensões de tela e mapa
  - Cores
  - Estados do jogo
  - Configurações de gameplay

Importe daqui em qualquer módulo. Não importa nada do projeto.
"""

# ─── Tela ─────────────────────────────────────────────────────
SCREEN_W: int = 1024
SCREEN_H: int = 768
FPS: int = 60
TITLE: str = "⚔ RPG Adventure"

# ─── Mapa ─────────────────────────────────────────────────────
TILE_SIZE: int  = 40
MAP_W: int      = 50          # tiles horizontais
MAP_H: int      = 50          # tiles verticais

# ─── Gameplay ─────────────────────────────────────────────────
PLAYER_SPEED: int        = 160
PLAYER_MAX_HP: int       = 100
PLAYER_SKILL_CD: int     = 55   # frames
PLAYER_INVINCIBLE: int   = 70   # frames após tomar dano
PROJECTILE_SPEED: int    = 320
PROJECTILE_DAMAGE: int   = 30
PROJECTILE_LIFE: int     = 140  # frames
MONSTER_AGGRO_RANGE: int = 380
MONSTER_ATTACK_CD: int   = 90
MONSTER_RESPAWN_COUNT: int = 5
NPC_INTERACT_RANGE: int  = 90
ITEM_COLLECT_RADIUS: int = 14
CAMERA_LERP: float       = 8.0  # suavidade da câmera

# ─── Cores ────────────────────────────────────────────────────
WHITE       = (255, 255, 255)
BLACK       = (0,   0,   0)
RED         = (220, 50,  50)
GREEN       = (60,  200, 60)
BLUE        = (70,  130, 210)
YELLOW      = (255, 220, 0)
ORANGE      = (255, 160, 30)
GRAY        = (150, 150, 150)
DARK_GRAY   = (40,  40,  50)
LIGHT_GRAY  = (200, 200, 200)
BROWN       = (140, 90,  45)
DARK_GREEN  = (40,  110, 40)
TEAL        = (50,  180, 180)
PURPLE      = (160, 60,  200)
LIGHT_BLUE  = (100, 190, 255)

# ─── Paleta de cores do jogador (customização) ────────────────
PLAYER_COLORS = [
    (70,  130, 210),  # Azul
    (210, 70,  70),   # Vermelho
    (70,  200, 80),   # Verde
    (200, 200, 70),   # Amarelo
    (180, 70,  200),  # Roxo
    (70,  200, 200),  # Ciano
    (220, 130, 50),   # Laranja
    (50,  180, 180),  # Turquesa
]

# ─── Estados do jogo ──────────────────────────────────────────
STATE_CUSTOMIZE = "customize"
STATE_PLAYING   = "playing"
STATE_DIALOGUE  = "dialogue"
STATE_INVENTORY = "inventory"
STATE_GAMEOVER  = "gameover"

# ─── Tipos de monstro ─────────────────────────────────────────
MONSTER_DEFS = {
    "slime":  {"color": (60,  200, 80),  "hp": 50,  "speed": 65,  "dmg": 8,  "xp": 20, "size": 20},
    "goblin": {"color": (200, 100, 50),  "hp": 70,  "speed": 90,  "dmg": 12, "xp": 30, "size": 22},
    "ghost":  {"color": (160, 160, 230), "hp": 40,  "speed": 110, "dmg": 15, "xp": 35, "size": 18},
    "orc":    {"color": (80,  140, 80),  "hp": 120, "speed": 55,  "dmg": 20, "xp": 50, "size": 26},
}

# ─── Tipos de item ────────────────────────────────────────────
ITEM_DEFS = {
    "hp_potion": {"color": (255, 80,  80),  "label": "Poção de Vida", "icon": "HP"},
    "gem":       {"color": (80,  200, 255), "label": "Gema",          "icon": "GE"},
    "sword":     {"color": (200, 210, 255), "label": "Espada",        "icon": "SW"},
    "shield":    {"color": (255, 200, 80),  "label": "Escudo",        "icon": "SH"},
    "key":       {"color": (255, 255, 100), "label": "Chave Mágica",  "icon": "KY"},
    "coin":      {"color": (255, 220, 0),   "label": "Moeda",         "icon": "$$"},
    "scroll":    {"color": (220, 180, 120), "label": "Pergaminho",    "icon": "SC"},
}

# ─── Tiles do mapa ────────────────────────────────────────────
TILE_GRASS = 0
TILE_WATER = 1
TILE_TREE  = 2
TILE_STONE = 3

TILE_COLORS = {
    TILE_GRASS: (75,  155, 75),
    TILE_WATER: (45,  95,  200),
    TILE_TREE:  (40,  115, 40),
    TILE_STONE: (130, 120, 110),
}