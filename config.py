"""config.py — constantes globais do jogo."""
import math

# Tela
SCREEN_W, SCREEN_H = 1024, 768
FPS   = 60
TITLE = "+ RPGame Lite +"

# Mapa (60x60 — equilibrado entre espaço e densidade)
TILE_SIZE = 40
MAP_W     = 60
MAP_H     = 60

# Tiles
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

# Gameplay
PLAYER_SPEED      = 185   # era 170 — ligeiramente mais rápido
PLAYER_MAX_HP     = 100
PLAYER_SKILL_CD   = 50
PLAYER_INVINCIBLE = 70
SKILL_SPEED       = 320
SKILL_DAMAGE      = 30
SKILL_LIFE        = 90
SKILL_RADIUS      = 5
SKILL_MAX_RANGE   = 340
MOB_AGGRO_RANGE   = 420
MOB_ATTACK_CD     = 80
MOB_RESPAWN_COUNT = 4
NPC_INTERACT_RANGE= 90
ITEM_COLLECT_RADIUS=14
CAMERA_LERP       = 8.0

# Spawn — distâncias em pixels a partir do centro da zona segura
# Zona segura ~240px de raio. Spawn começa 300px fora.
MOB_SPAWN_MIN_DIST = 300
MOB_SPAWN_MAX_DIST = 750

# Lanterna — raio pequeno para tornar upgrade essencial
LANTERN_DEFAULT_RADIUS = 90    # era 110 — mais escuro no início
LANTERN_DARKNESS_ALPHA = 252   # praticamente total (0=nada, 255=total)

# XP e progressão de nível
# xp_next começa em 150 e cresce ×1.6 por nível:
# Nv1→2: 150 XP  (~5 slimes)
# Nv2→3: 240 XP  (~5 goblins)
# Nv3→4: 384 XP
# Nv4→5: 614 XP
XP_NEXT_BASE  = 150
XP_NEXT_MULT  = 1.6

# Cap de upgrades total no mercador (para evitar farming infinito)
MAX_TOTAL_UPGRADES = 12  # máximo de compras na loja em toda a run

# Andares
FLOOR_MOB_BASE  = 10
FLOOR_MOB_STEP  = 5
FLOOR_DMG_MULT  = 0.30

# Boss
BOSS_UNLOCK_LEVEL = 2   # nível mínimo para invocar boss via Sábio
BOSS_HP_BASE      = 350
BOSS_DMG_BASE     = 22
BOSS_SPEED_BASE   = 80

# Loja
SHOP_PRICE_SPEED       = 2
SHOP_PRICE_FIRERATE    = 2
SHOP_PRICE_DAMAGE      = 3
SHOP_PRICE_LANTERN     = 2
SHOP_PRICE_SKILL_RANGE = 2
SHOP_PRICE_POTION      = 2

# Cores
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
    (70,  130, 210),(210, 70,  70),(70,  200, 80),
    (200, 200, 70),(180, 70,  200),(70,  200, 200),
    (220, 130, 50),(50,  180, 180),(255, 255, 255),(150, 150, 150),
]

# Estados
STATE_CUSTOMIZE = "customize"
STATE_PLAYING   = "playing"
STATE_DIALOGUE  = "dialogue"
STATE_INVENTORY = "inventory"
STATE_GAMEOVER  = "gameover"
STATE_PAUSE     = "pause"

# Mobs
MOB_DEFS = {
    # slime: básico, drop moedas
    "slime":  {"color":(60,200,80),  "hp":60,  "speed":80,  "dmg":8,  "xp":30,  "size":20},
    # goblin: rápido, glass-cannon, esquiva 20%
    "goblin": {"color":(200,100,50), "hp":55,  "speed":145, "dmg":15, "xp":50,  "size":21},
    # ghost: rápido, atravessa ÁRVORES mas não PEDRA
    "ghost":  {"color":(160,160,230),"hp":45,  "speed":175, "dmg":12, "xp":60,  "size":18},
    # orc: tanque, charge 1.5x — só aparece nível 2+
    "orc":    {"color":(80,140,80),  "hp":180, "speed":58,  "dmg":22, "xp":100, "size":28},
}

MOB_DROPS = {
    # Slime: muitas moedas, gemn ocasional
    "slime":  [("coin",70),("coin",0),("gem",20),("hp_potion",5),("nothing",5)],
    # Goblin: moedas + scrolls (XP)
    "goblin": [("coin",60),("gem",12),("scroll",18),("hp_potion",8),("nothing",2)],
    # Ghost: gemas e scrolls
    "ghost":  [("gem",55),("scroll",25),("coin",12),("hp_potion",6),("nothing",2)],
    # Orc: moedas + chave + poção (drop mais valioso)
    "orc":    [("coin",45),("key_chance",30),("hp_potion",18),("gem",5),("nothing",2)],
}

ITEM_DEFS = {
    "hp_potion":{"color":(255,80,80),  "label":"Pocao de Vida",  "icon":"HP"},
    "gem":      {"color":(80,200,255), "label":"Gema",           "icon":"GE"},
    "sword":    {"color":(200,210,255),"label":"Espada",         "icon":"SW"},
    "shield":   {"color":(255,200,80), "label":"Escudo",         "icon":"SH"},
    "key":      {"color":(255,255,50), "label":"Chave do Andar", "icon":"KY"},
    "coin":     {"color":(255,220,0),  "label":"Moeda",          "icon":"$$"},
    "scroll":   {"color":(220,180,120),"label":"Pergaminho",     "icon":"SC"},
}

ITEM_EFFECTS = {
    "sword":  {"skill_damage":+15, "msg":"Espada! +15 dano de magia permanente!"},
    "shield": {"max_hp":+30,       "msg":"Escudo! +30 HP maximo permanente!"},
    "scroll": {"xp":+40,           "msg":"Pergaminho! +40 XP!"},
}

GEM_XP_VALUE = 50
