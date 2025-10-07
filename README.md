# simulador-incendio
Simulador da propagação do fogo por meio de Autômatos Celulares - Cálculo Numérico

Explicação do código
O programa implementa uma simulação da propagação de incêndios florestais
utilizando a técnica de autômatos celulares, com interface gráfica desenvolvida em
Python, por meio da biblioteca Pygame. Essa simulação tem o objetivo de
representar o comportamento do fogo em uma floresta hipotética, considerando
fatores ambientais como temperatura, umidade, tipo e densidade da vegetação e a
influência do vento.

Introdução ao funcionamento geral
A base do código está na representação de uma floresta como uma grade
bidimensional (matriz), onde cada célula representa um pedaço do terreno. O
estado de cada célula muda ao longo do tempo, seguindo regras que determinam
se a célula está com vegetação, queimando, já queimada ou vazia.
Essas mudanças acontecem de forma discreta e local, ou seja, o próximo estado de
uma célula depende apenas do seu estado atual e dos estados das células vizinhas,
o que é exatamente a definição de um autômato celular.

Parâmetros iniciais e variáveis principais
Logo no início do código, são definidos os parâmetros de simulação, como o
tamanho da grade (GRADE = 320), o tamanho visual de cada célula (CELULA = 2)
e a taxa de atualização da tela (FPS = 60).
Também são definidas as cores usadas na interface, representando cada estado
das células:

● Verde: vegetação viva;
● Vermelho: célula queimando;
● Cinza: célula já queimada;
● Preto: área vazia (sem vegetação).

O programa define três tipos principais de vegetação (agrícola, arbustiva e floresta),
cada um com uma probabilidade diferente de pegar fogo e uma duração diferente
de queima. Da mesma forma, são definidos três níveis de densidade (esparsa,
normal e densa), que afetam a quantidade de células preenchidas por vegetação no
início da simulação.

Criação da floresta (função criar_grade)
A função criar_grade gera aleatoriamente a floresta inicial com base no tipo e
densidade de vegetação escolhidos.
Cada célula tem uma chance de conter vegetação viva, de acordo com a
probabilidade de preenchimento associada à densidade. As bordas da matriz são
deixadas vazias para evitar erros de propagação nas extremidades.

Estados e dinâmica da simulação
O vetor estado armazena o valor de cada célula:
● 0: vazio
● 1: célula com vegetação viva
● 2: célula queimando
● 3: célula já queimada

Além disso, a matriz tempo_queimando armazena quanto tempo cada célula ainda
permanecerá queimando, o que permite que o fogo se propague de forma gradual e
realista.

Função principal de atualização (passo)
A função passo é o núcleo do autômato. Ela atualiza o estado de cada célula
conforme as seguintes regras:

1. Células que estão queimando (estado == 2) têm seu tempo de queima
reduzido. Quando o tempo chega a zero, elas se tornam “queimadas”
(estado = 3).
2. As células vizinhas de uma célula em chamas podem pegar fogo,
dependendo de uma probabilidade calculada dinamicamente.
3. Essa probabilidade é influenciada por:
○ Temperatura ambiente (quanto maior, mais fácil o fogo se espalha);
○ Umidade do ar (quanto maior, mais difícil o fogo se espalha);
○ Temperatura do fogo (quanto mais intenso, maior a propagação);
○ Tipo de vegetação (vegetações densas e secas queimam mais rápido)
○ Direção e força do vento (que aumenta a chance de o fogo se espalhar
em uma direção específica).

O código utiliza operações com NumPy para realizar cálculos vetorizados, o que
permite atualizar milhares de células simultaneamente.

Influência do vento
O vento é representado pelas variáveis vento_dir (direção) e vento_forca
(intensidade).
A direção pode ser norte, sul, leste, oeste ou “nenhuma”, e influencia a
probabilidade de que o fogo se espalhe preferencialmente em uma direção
específica.
Por exemplo, se o vento sopra de norte para sul, as células ao sul de uma chama
têm uma chance maior de inflamar.
Esse efeito é obtido por meio de deslocamentos de matriz com a função np.roll,
que desloca o padrão das células queimando na direção do vento.

Interface gráfica e interação do usuário
A interface é construída com Pygame, exibindo a floresta à esquerda e um painel de
controle à direita. O painel mostra as variáveis atuais (tipo de vegetação,
temperatura, umidade, vento etc.) e instruções de uso.
O usuário pode interagir em tempo real com o simulador:

● Espaço: pausa ou continua a simulação;
● Clique do mouse: inicia o fogo em uma célula;
● Teclas Z, X, C: alteram o tipo de vegetação;
● Teclas 4, 5, 6: alteram a densidade;
● Teclas (8↑ / 2↓) : ajustam temperatura ambiente;
● Teclas (← / →): ajustam a umidade;
● Teclas (↑ / ↓): ajustam temperatura do fogo;
● Q/N/S/L/O: alteram a direção do vento;
● + e -: controlam a intensidade do vento;
● R: reinicia a simulação;
● P: salva uma captura da tela.
A função desenhar_rosa_dos_ventos mostra visualmente a direção e
intensidade do vento por meio de uma “rosa dos ventos” animada, facilitando a
interpretação dos resultados.

Considerações sobre desempenho
O código é relativamente eficiente por utilizar operações vetoriais e matrizes
pequenas (640x640 pixels na tela). Ainda assim, a simulação envolve muitos
cálculos por segundo, então a taxa de atualização é limitada a 60 FPS para manter
a fluidez.

Explicação da Equação de Probabilidade de Propagação do Fogo
No código, a probabilidade de propagação do fogo é calculada de forma empírica,
resultando da combinação de fatores ambientais como temperatura, umidade, tipo
de vegetação e vento. Esses fatores modificam a chance base de uma célula
vizinha pegar fogo.

A equação geral que representa essa lógica pode ser expressa como:
P_prop = P_base(v) × F_temp(T) × F_umid(U) × F_vento(D, F)

Cada tipo de vegetação possui uma probabilidade base diferente de queimar:
agrícola (0,4), arbusto (0,6) e floresta (0,8). Assim, florestas são naturalmente mais
inflamáveis.

O fator de temperatura é modelado da seguinte forma:
F_temp(T) = 1 + α × (T - T0)

em que T0 é a temperatura de referência (25 °C) e α é um coeficiente de
sensibilidade (cerca de 0,01). Isso significa que um aumento de 10 °C eleva a
probabilidade de ignição em aproximadamente 10%.

O fator de umidade é modelado como:
F_umid(U) = 1 - β × (U - U0)

onde U0 é a umidade de referência (30%) e β ≈ 0,01. Assim, um aumento de 20%
na umidade reduz a probabilidade em cerca de 20%.

O vento é tratado por meio de deslocamentos na matriz do fogo (usando np.roll), e a
força do vento ajusta a probabilidade conforme sua direção:
F_vento(D,F) =
 1 + γF, se a célula vizinha está na direção do vento;
 1, se a célula é perpendicular ao vento;
 1 - γF, se a célula está contra o vento.
onde γ ≈ 0,05 e F varia de 1 a 10.

Assim, a forma completa pode ser escrita como:
P_prop = P_base(v) × (1 + 0.01 × (T - 25)) × (1 - 0.01 × (U - 30)) × (1 + 0.05 ×
F_ajuste)
onde F_ajuste é positivo se o vento favorece a direção do fogo e negativo se é
contrário.

Por fim, o programa gera um número aleatório entre 0 e 1 (random.random()). Se
esse valor for menor que P_prop, a célula viva passa ao estado "queimando" no
próximo passo. Essa abordagem faz com que o comportamento do fogo varie
naturalmente, sem ser totalmente determinístico, tornando a simulação mais
realista.