"""
main.py — Menu principal com seleção de modo de jogo.

MODOS:
  1. RPG Dungeon  — jogo principal (já existente)
  2. TSP Puzzle   — coleta com rota ótima (Held-Karp / 2-opt + Heapsort)
"""
import sys
import pygame


def _draw_menu(screen, fonts, selected):
    from config import SCREEN_W, SCREEN_H, YELLOW, WHITE, GRAY, DARK_GRAY, LIGHT_GRAY, BLACK, GREEN, ORANGE

    screen.fill((12, 12, 28))

    # Estrelas de fundo
    import random
    rng = random.Random(99)
    for _ in range(80):
        pygame.draw.circle(screen,
            (rng.randint(50,110), 55, 100),
            (rng.randint(0,SCREEN_W), rng.randint(0,SCREEN_H)),
            rng.choice([1,1,2]))

    # Título
    t = fonts.xl.render("+ RPGame Lite +", True, YELLOW)
    screen.blit(t, (SCREEN_W//2 - t.get_width()//2, 70))

    sub = fonts.sm.render("Selecione o modo de jogo", True, GRAY)
    screen.blit(sub, (SCREEN_W//2 - sub.get_width()//2, 125))

    pygame.draw.line(screen, (60,60,100),
                     (SCREEN_W//2-300, 152), (SCREEN_W//2+300, 152), 1)

    modes = [
        {
            "title":  "RPG DUNGEON",
            "desc":   "Explore masmorras, enfrente mobs e bosses.",
            "alg":    "Algoritmos: Inventário (Dict), Pathfinder A*, Heapsort",
            "color":  (70, 130, 210),
            "tag":    "MODO PRINCIPAL",
        },
        {
            "title":  "TSP PUZZLE — Rota Ótima",
            "desc":   "Colete todos os itens pelo caminho mais curto!",
            "alg":    "Algoritmos: Held-Karp (n≤15) | 2-opt (n>15) | Heapsort",
            "color":  (80, 200, 80),
            "tag":    "ALGORITMOS COMPUTACIONAIS",
        },
    ]

    btn_rects = []
    for i, mode in enumerate(modes):
        by  = 185 + i * 165
        br  = pygame.Rect(SCREEN_W//2 - 320, by, 640, 145)
        btn_rects.append(br)

        # Fundo do card
        bg_clr = (30,45,80) if i==selected else (20,20,40)
        bd_clr = mode["color"] if i==selected else (50,50,70)
        pygame.draw.rect(screen, bg_clr, br, border_radius=12)
        pygame.draw.rect(screen, bd_clr, br, 2 if i!=selected else 3, border_radius=12)

        # Tag
        tag = fonts.xs.render(mode["tag"], True, mode["color"])
        screen.blit(tag, (br.x+16, br.y+10))

        # Título do modo
        mt = fonts.lg.render(mode["title"], True,
                              mode["color"] if i==selected else WHITE)
        screen.blit(mt, (br.x+16, br.y+28))

        # Descrição
        ds = fonts.sm.render(mode["desc"], True, LIGHT_GRAY)
        screen.blit(ds, (br.x+16, br.y+68))

        # Algoritmos
        al = fonts.xs.render(mode["alg"], True, (160,160,160))
        screen.blit(al, (br.x+16, br.y+96))

        # Seta de seleção
        if i == selected:
            arrow = fonts.lg.render("▶", True, mode["color"])
            screen.blit(arrow, (br.right-44, br.centery-arrow.get_height()//2))

    # Dica
    hint = fonts.xs.render(
        "↑↓ ou mouse para escolher  |  ENTER ou clique para iniciar  |  ESC para sair",
        True, GRAY)
    screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 36))

    return btn_rects


def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        pass

    from config import SCREEN_W, SCREEN_H, FPS
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
    pygame.display.set_caption("+ RPGame Lite +")
    clock  = pygame.time.Clock()

    from ui.fonts import init_fonts
    init_fonts()                  # 1º Inicializa as fontes lá no arquivo original
    from ui.fonts import fonts    # 2º AGORA SIM importa a variável que já está preenchida

    selected = 0
    running  = True

    while running:
        btn_rects = _draw_menu(screen, fonts, selected)
        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % 2
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % 2
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    _launch(selected, screen, clock, fonts)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, br in enumerate(btn_rects):
                    if br.collidepoint(event.pos):
                        selected = i
                        _launch(selected, screen, clock, fonts)


def _launch(mode_idx, screen, clock, fonts):
    if mode_idx == 0:
        # ── Modo RPG (jogo principal) ──────────────────────────────────
        try:
            from game import Game
            game = Game()
            # Reaproveita a janela já aberta
            game.screen = screen
            game.clock  = clock
            game.run()
        except Exception:
            import traceback; traceback.print_exc()
    else:
        # ── Modo TSP ───────────────────────────────────────────────────
        try:
            from tsp_mode.tsp_game import run_tsp_mode
            run_tsp_mode(screen, clock, fonts)
        except Exception:
            import traceback; traceback.print_exc()


if __name__ == "__main__":
    main()
