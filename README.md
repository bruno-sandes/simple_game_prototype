# simple_game_prototype
in development


# RPGame Lite

RPG 2D em Pygame. Execute: `python main.py`

## Requisitos
```
pip install -r requirements.txt
```

## Controles
| Tecla | Ação |
|---|---|
| WASD | Mover |
| Clique Direito / Shift+Click | Lançar magia |
| E | Interagir com NPC / abrir porta |
| F | Usar poção |
| I | Inventário |
| O | Ordenar inventário |
| 1–6 | Escolher opção no diálogo |
| ESC | Pausar (em jogo) / Fechar diálogo |

## Objetivo
Fale com o **Sábio Aldren** para invocar o **Boss** de cada andar.
Derrote-o para obter a **Chave do Andar** e passe pela **Porta** para avançar.
Use moedas no **Mercador Zek** para melhorar seus atributos.

## Estrutura
```
simple_game_prototype/
├── main.py          # Entrada
├── game.py          # Loop principal
├── config.py        # Constantes
├── entities/        # Player, Mob, Boss, NPC, Skill, Sprite
├── world/           # Tilemap, Item, Particle, Lanterna
├── systems/         # Colisão, Inventário
├── ui/              # HUD, Diálogo, Inventário, Mapa, Fontes
└── screens/         # Customização, Pausa, Animação, Movimento
```
