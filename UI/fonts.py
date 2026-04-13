"""
ui/fonts.py
===========
Gerenciamento centralizado de fontes.

Todas as fontes do jogo são criadas UMA única vez aqui e
reutilizadas via o singleton FontManager, evitando
recriação de Surface a cada frame.

Uso:
    from ui.fonts import fonts
    surface.blit(fonts.md.render("texto", True, WHITE), (x, y))
"""

import pygame


class FontManager:
    """
    Atributos públicos (todos SysFont "Arial"):
        xl  — 36px bold   (títulos de tela)
        lg  — 26px bold   (subtítulos)
        md  — 20px        (diálogos, menus)
        sm  — 14px        (HUD, labels)
        xs  — 11px        (dicas, rótulos pequenos)
        xxs —  9px        (ícones de itens, minimap)
    """

    def __init__(self):
        self.xl  = pygame.font.SysFont("Arial", 36, bold=True)
        self.lg  = pygame.font.SysFont("Arial", 26, bold=True)
        self.md  = pygame.font.SysFont("Arial", 20)
        self.sm  = pygame.font.SysFont("Arial", 14)
        self.xs  = pygame.font.SysFont("Arial", 11)
        self.xxs = pygame.font.SysFont("Arial",  9, bold=True)


# Instância global — importada pelos módulos de UI
fonts: FontManager | None = None


def init_fonts() -> FontManager:
    """
    Deve ser chamado UMA vez após pygame.init().
    Retorna e armazena o singleton global.
    """
    global fonts
    fonts = FontManager()
    return fonts