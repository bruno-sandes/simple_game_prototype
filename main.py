"""
main.py — ponto de entrada do jogo.
Execute: python main.py
"""
import sys
import pygame


def main():
    pygame.init()
    pygame.mixer.init()

    from game import Game
    try:
        Game().run()
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
