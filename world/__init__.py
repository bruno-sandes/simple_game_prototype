"""
world/
======
Pacote de elementos do mundo de jogo.

    from world import World, Item, Particle
"""

from world.tilemap  import World
from world.item     import Item
from world.particle import Particle

__all__ = ["World", "Item", "Particle"]