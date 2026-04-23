"""
main.py — ponto de entrada do jogo.
Execute: python main.py

CORREÇÕES:
  1. pygame.mixer.init() envolto em try/except — em sistemas sem áudio
     lançava exceção não capturada, fechando a janela imediatamente.
  2. except agora captura Exception genérica e imprime o traceback no
     terminal, em vez de fechar silenciosamente sem mensagem de erro.
"""
import sys
import pygame


def main():
    pygame.init()

    try:
        pygame.mixer.init()
    except pygame.error:
        pass  # Sem áudio — jogo continua normalmente

    from game import Game
    try:
        Game().run()
    except KeyboardInterrupt:
        pass
    except Exception:
        import traceback
        traceback.print_exc()   # Mostra o erro real no terminal
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()