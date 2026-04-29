"""
config.py
<<<<<<< Updated upstream
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
=======

MUDANCAS:
  LANTERN_DEFAULT_RADIUS: 190 -> 110  (torna upgrade essencial)
  orc dmg: 30 -> 22, charge dano 1.5x em vez de 2x (menos one-shot)
  slime/goblin speed up para andar 1 já desafiar
  MOB_SPAWN_MIN_DIST / MAX_DIST definidos aqui para fácil ajuste
  BOSS_UNLOCK_LEVEL: nível mínimo para acessar a sala do boss
  STATE_PAUSE adicionado
  scroll/sword/shield efeitos definidos via ITEM_EFFECTS
"""

# ─── Tela
SCREEN_W: int = 1024
SCREEN_H: int = 768
FPS: int      = 60
TITLE: str    = "+ RPGame Lite +"

# ─── Mapa
TILE_SIZE: int = 40
MAP_W: int     = 80
MAP_H: int     = 80

# ─── Tiles
>>>>>>> Stashed changes
TILE_GRASS = 0
TILE_WATER = 1
TILE_TREE  = 2
TILE_STONE = 3
TILE_FLOOR = 4
TILE_DOOR  = 5

TILE_COLORS = {
    TILE_GRASS: (75,  155, 75),
    TILE_WATER: (45,  95,  200),
    TILE_TREE:  (40,  115, 40),
    TILE_STONE: (100, 90,  80),
    TILE_FLOOR: (180, 160, 120),
    TILE_DOOR:  (220, 180,  50),
}

# ─── Gameplay
PLAYER_SPEED: int       = 160
PLAYER_MAX_HP: int      = 100
PLAYER_SKILL_CD: int    = 55
PLAYER_INVINCIBLE: int  = 70
SKILL_SPEED: int        = 340
SKILL_DAMAGE: int       = 30
SKILL_LIFE: int         = 160
MOB_AGGRO_RANGE: int    = 420      # raio de perseguição
MOB_ATTACK_CD: int      = 80
MOB_RESPAWN_COUNT: int  = 3
NPC_INTERACT_RANGE: int = 90
ITEM_COLLECT_RADIUS: int= 14
CAMERA_LERP: float      = 8.0

# Spawn: distância mínima/máxima do centro da zona segura em pixels
# Zona segura tem ~480px de raio (paredes). Mobs nascem FORA e
# dentro do aggro_range para que ataquem imediatamente.
MOB_SPAWN_MIN_DIST: int = 500   # logo fora das paredes
MOB_SPAWN_MAX_DIST: int = 800   # dentro do alcance do aggro estendido

# ─── Lanterna  (raio menor = upgrade faz diferença)
LANTERN_DEFAULT_RADIUS: int = 110   # era 190 — agora realmente limita a visão
LANTERN_DARKNESS_ALPHA: int = 248   # quase total escuridão

# ─── Sistema de andares
FLOOR_MOB_BASE: int   = 7
FLOOR_MOB_STEP: int   = 4
FLOOR_DMG_MULT: float = 0.30

# ─── Boss
BOSS_UNLOCK_LEVEL: int = 3   # nível mínimo para acessar sala do boss
BOSS_HP_BASE: int      = 400
BOSS_DMG_BASE: int     = 25
BOSS_SPEED_BASE: int   = 85

# ─── Loja
SHOP_PRICE_SPEED    = 3
SHOP_PRICE_FIRERATE = 3
SHOP_PRICE_DAMAGE   = 4
SHOP_PRICE_LANTERN  = 3   # lanterna mais barata pois é essencial
SHOP_PRICE_POTION   = 2

# ─── Cores
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
RED        = (220, 50,  50)
GREEN      = (60,  200, 60)
BLUE       = (70,  130, 210)
YELLOW     = (255, 220, 0)
ORANGE     = (255, 160, 30)
GRAY       = (150, 150, 150)
DARK_GRAY  = (40,  40,  50)
LIGHT_GRAY = (200, 200, 200)
BROWN      = (140, 90,  45)
DARK_GREEN = (40,  110, 40)
TEAL       = (50,  180, 180)
PURPLE     = (160, 60,  200)
LIGHT_BLUE = (100, 190, 255)

PLAYER_COLORS = [
    (70,  130, 210), (210, 70,  70),  (70,  200, 80),
    (200, 200, 70),  (180, 70,  200), (70,  200, 200),
    (220, 130, 50),  (50,  180, 180), (255, 255, 255),
    (150, 150, 150),
]

# ─── Estados
STATE_CUSTOMIZE = "customize"
STATE_PLAYING   = "playing"
STATE_DIALOGUE  = "dialogue"
STATE_INVENTORY = "inventory"
STATE_GAMEOVER  = "gameover"
STATE_PAUSE     = "pause"      # NOVO: menu de pausa (ESC em jogo)

# ─── Mobs
MOB_DEFS = {
    # slime: fácil, drop comum de moedas
    "slime":  {"color": (60,  200, 80),  "hp": 55,  "speed": 80,  "dmg": 8,  "xp": 15, "size": 20},
    # goblin: glass cannon — rápido, alto dano, pouco HP, esquiva 20%
    "goblin": {"color": (200, 100, 50),  "hp": 50,  "speed": 140, "dmg": 16, "xp": 25, "size": 21},
    # ghost: atravessa paredes, rápido, intangível 1.5s ao nascer
    "ghost":  {"color": (160, 160, 230), "hp": 40,  "speed": 170, "dmg": 12, "xp": 30, "size": 18},
    # orc: tanque — lento, HP alto, charge 1.5x dano (não more one-shot)
    "orc":    {"color": (80,  140, 80),  "hp": 180, "speed": 55,  "dmg": 22, "xp": 50, "size": 28},
}

MOB_DROPS = {
    # coin: 70% | gem(xp): 20% | nothing: 10%
    "slime":  [("coin", 70), ("gem", 20), ("nothing", 10)],
    # coin: 50% | gem: 15% | scroll: 20% | nothing: 15%
    "goblin": [("coin", 50), ("gem", 15), ("scroll", 20), ("nothing", 15)],
    # gem: 60% | scroll: 25% | coin: 10% | nothing: 5%
    "ghost":  [("gem",  60), ("scroll", 25), ("coin", 10), ("nothing", 5)],
    # coin: 55% | key_chance: 30% | hp_potion: 5% | nothing: 10%
    "orc":    [("coin", 55), ("key_chance", 30), ("hp_potion", 5), ("nothing", 10)],
}

# ─── Itens
ITEM_DEFS = {
    "hp_potion": {"color": (255, 80,  80),  "label": "Pocao de Vida",  "icon": "HP"},
    "gem":       {"color": (80,  200, 255), "label": "Gema",           "icon": "GE"},
    "sword":     {"color": (200, 210, 255), "label": "Espada",         "icon": "SW"},
    "shield":    {"color": (255, 200, 80),  "label": "Escudo",         "icon": "SH"},
    "key":       {"color": (255, 255, 50),  "label": "Chave do Andar", "icon": "KY"},
    "coin":      {"color": (255, 220, 0),   "label": "Moeda",          "icon": "$$"},
    "scroll":    {"color": (220, 180, 120), "label": "Pergaminho",     "icon": "SC"},
}

# Efeitos imediatos ao coletar (aplicados em game.py _on_collect_item)
# sword: +15 dano skill  | shield: +30 HP max  | scroll: +25 XP
ITEM_EFFECTS = {
    "sword":  {"skill_damage": +15, "msg": "Espada! +15 dano de magia permanente!"},
    "shield": {"max_hp": +30,       "msg": "Escudo! +30 HP maximo permanente!"},
    "scroll": {"xp": +25,           "msg": "Pergaminho! +25 XP!"},
}

GEM_XP_VALUE   = 40    # XP por gema coletada