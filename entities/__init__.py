"""
<<<<<<< Updated upstream
entities/
=========
Pacote de entidades do jogo.

Exporta as classes principais para facilitar imports externos:
    from entities import Player, Monster, NPC, Projectile
"""

from entities.base import AnimatedSprite
from entities.projectile import Projectile
from entities.player import Player
from entities.monster import Monster
from entities.npc import NPC

__all__ = ["AnimatedSprite", "Projectile", "Player", "Monster", "NPC"]
=======
entities/__init__.py
"""
from entities.sprite import AnimatedSprite
from entities.skill  import Skill
from entities.player import Player
from entities.mob    import Mob
from entities.npc    import (
    NPC, DialogueNode, DialogueTree,
    make_sage, make_merchant,
)

__all__ = [
    "AnimatedSprite", "Skill", "Player", "Mob",
    "NPC", "DialogueNode", "DialogueTree",
    "make_sage", "make_merchant",
]
>>>>>>> Stashed changes
