"""main.py — ponto de entrada.
CORRECAO: pygame.SCALED resolve a janela ultrapassando a escala do monitor.
"""
import sys, pygame

def main():
    pygame.init()
    try: pygame.mixer.init()
    except pygame.error: pass
    from game import Game
    try:
        Game().run()
    except KeyboardInterrupt: pass
    except Exception:
        import traceback; traceback.print_exc()
    finally:
        pygame.quit(); sys.exit(0)

if __name__ == "__main__":
    main()
