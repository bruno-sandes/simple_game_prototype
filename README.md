# RPGame Lite

Jogo 2D desenvolvido em Python + Pygame com algoritmos computacionais integrados.

## Como executar

```bash
pip install pygame
Execute o jogo pelo arquivo principal:
python main.py
```

## Modos de jogo

### 1 — RPG Dungeon (Modo Principal)
RPG de exploração com sistema de inventário, mobs, boss e sistema de andares.
- WASD para mover
- Clique direito para atacar
- E para interagir com NPCs / usar porta
- I para inventário · F para poção · ESC para pausar

# 2 - TSP Puzzle

## Como jogar:

```bash
No menu principal, selecione o modo TSP Puzzle.
Gênero do jogo
O projeto é um jogo de puzzle/estratégia com movimentação em mapa 2D. O jogador precisa planejar a rota de coleta, administrar energia e escolher uma estratégia de organização do inventário.
O jogo não é do gênero survivor.
Objetivo do modo TSP Puzzle
O objetivo é coletar todos os itens espalhados pelo mapa e retornar para a base.
Durante a partida, o jogador não vê a rota ideal. Ele precisa analisar os pesos, valores e raridades dos itens para tentar formular uma boa rota. Ao final, o jogo revela a rota ideal calculada pelo TSP, permitindo comparar a estratégia do jogador com a solução algorítmica.
Modos de jogo
Modo Normal
No modo normal, o jogador move a nave com WASD.
Modo Difícil
No modo difícil, o jogador move a nave clicando no mapa. Enquanto a nave está em movimento, não é possível alterar a estratégia do Heapsort. Isso obriga o jogador a escolher a estratégia antes de se deslocar, tornando o planejamento mais importante.
Controles
WASD: mover no modo normal
Clique no mapa: definir destino no modo difícil
O: alternar estratégia do Heapsort
I: abrir inventário na tela final
ESC: sair do modo TSP
Algoritmos implementados
Travelling Salesman Problem (TSP)
O TSP é usado para calcular a rota ideal entre a base e todos os pontos de coleta. A rota ideal considera a menor distância total para visitar todos os itens e retornar à base.
Para mapas pequenos, o projeto usa uma abordagem exata baseada em programação dinâmica, conhecida como Held-Karp. Para quantidades maiores de pontos, o sistema pode usar heurística com vizinho mais próximo e melhoria por 2-opt.
A rota ideal não é exibida durante a partida. Ela aparece apenas ao final, para comparar o caminho feito pelo jogador com a solução calculada pelo algoritmo.
Inventário
O inventário armazena todos os itens coletados pelo jogador. Cada item possui:
peso;
valor;
raridade;
nome;
cor visual.
O inventário permite adicionar itens, consultar o peso total, consultar o valor total e listar os itens coletados. Ao final da partida, o jogador pode abrir o inventário para revisar tudo que foi coletado.
Heapsort
O Heapsort é o segundo problema computacional integrado ao gameplay. Ele não é apenas visual: a estratégia de ordenação escolhida afeta a partida.
A tecla O alterna entre três estratégias:
Peso: reduz o gasto de energia causado pela carga pesada.
Valor: aumenta a pontuação recebida por itens valiosos, mas aumenta o gasto de energia.
Raridade: aumenta o bônus de itens raros quando a rota é eficiente, mas é a estratégia mais arriscada em energia.
No modo difícil, o Heapsort não pode ser alterado enquanto a nave está em movimento. Assim, o jogador precisa escolher a estratégia antes de executar o deslocamento.
Sistema de energia
O jogo não usa tempo como condição principal de derrota. Em vez disso, usa energia.
A energia diminui apenas quando o jogador se move. Isso permite que o jogador pare e pense na rota sem ser punido. Porém, movimentos mal planejados gastam energia e podem causar derrota.
O peso carregado aumenta o gasto de energia e reduz a velocidade da nave. Por isso, coletar itens pesados cedo pode ser perigoso, mas usar a estratégia de Heapsort por peso ajuda a compensar esse problema.
Pontuação
A pontuação final considera:
eficiência da rota do jogador em comparação com a rota ideal do TSP;
energia restante;
valor dos itens coletados;
raridade dos itens;
bônus pela ordem de coleta;
estratégia ativa do Heapsort.
O jogo também mostra uma pontuação máxima estimada ao final. Essa estimativa considera uma rota ideal, energia preservada e bônus estratégicos possíveis. Ela serve como referência para o jogador tentar melhorar em novas partidas.
Justificativa algorítmica
O TSP foi escolhido porque representa diretamente o problema central do modo: encontrar uma boa ordem para visitar vários pontos e retornar à base. Como o jogador precisa coletar todos os itens, o problema de rota é parte natural da jogabilidade.
O inventário foi escolhido para cumprir a necessidade de armazenar os itens coletados e permitir consulta posterior. Ele também fornece dados importantes para energia, pontuação e tela final.
O Heapsort foi escolhido como segundo problema computacional porque a ordenação dos itens pode ser transformada em decisão estratégica. Em vez de ser apenas uma lista ordenada, a escolha do critério de ordenação altera o comportamento do jogo.
Corretude do TSP
O algoritmo recebe uma lista de coordenadas dos pontos do mapa, incluindo a base. Ele calcula uma rota que passa por todos os pontos e retorna ao início.
Para poucos pontos, a solução exata Held-Karp garante a menor rota possível dentro do conjunto informado. Ao final da partida, essa rota é desenhada com setas, permitindo visualizar a comparação entre o caminho ideal e o caminho feito pelo jogador.
Funcionalidade da coleta e inventário
A coleta acontece quando o jogador se aproxima de um ponto do mapa. O item é removido visualmente do mapa e adicionado ao inventário.
O inventário mantém os dados de cada item coletado e permite exibir peso, valor e raridade na tela final.
Integração real do segundo problema computacional
O Heapsort influencia diretamente a jogabilidade. O jogador escolhe entre organizar a carga por peso, valor ou raridade. Essa escolha altera gasto de energia, risco e pontuação.
No modo difícil, a escolha se torna ainda mais importante porque não pode ser alterada durante a locomoção. Isso impede que o jogador mude a estratégia a qualquer momento e torna o planejamento parte central do desafio.
Jogabilidade e clareza
O jogador deve observar os itens no mapa, analisar peso, valor e raridade, escolher uma estratégia de Heapsort e então decidir a rota de coleta.
A rota ideal não aparece no início para que o jogador tente resolver o problema por conta própria. Ao final, o jogo revela o caminho calculado pelo TSP, funcionando como feedback sobre a qualidade da rota escolhida.
```
