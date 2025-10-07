import numpy as np
import pygame
import sys

# --- PARÂMETROS GERAIS ---
GRADE_SIZE = 320
CELL_SIZE = 2
LARGURA = GRADE_SIZE * CELL_SIZE
ALTURA = GRADE_SIZE * CELL_SIZE
FPS = 60

# --- INICIALIZAÇÃO DO PYGAME ---
pygame.init()
tela = pygame.display.set_mode((LARGURA + 300, ALTURA))
pygame.display.set_caption("Incêndio Florestal - Modelo com Tipos, Densidade e Vento")
fonte = pygame.font.SysFont("Arial", 16)
fonte_pequena = pygame.font.SysFont("Arial", 14, bold=True)
relogio = pygame.time.Clock()

# --- CORES ---
COR_FUNDO = (10, 10, 10)
COR_VAZIO = (0, 0, 0)
COR_QUEIMANDO = (255, 40, 0)
COR_QUEIMADA = (100, 100, 100)
COR_UI_FUNDO = (30, 30, 30)
COR_TEXTO = (220, 220, 220)

# --- CONFIGURAÇÕES DA SIMULAÇÃO ---

# Tipos de vegetação
TIPO_VEGETACAO = {
    "Z": {"nome": "Agrícola", "prob": 1.3, "duracao": 3, "cor": (150, 220, 100)},
    "X": {"nome": "Arbustos", "prob": 1.0, "duracao": 5, "cor": (34, 160, 34)},
    "C": {"nome": "Floresta", "prob": 0.7, "duracao": 8, "cor": (0, 100, 0)},
}

# Densidade de vegetação
DENSIDADE = {
    4: {"nome": "Esparsa", "prob_preenchimento": 0.6},
    5: {"nome": "Normal", "prob_preenchimento": 0.8},
    6: {"nome": "Densa", "prob_preenchimento": 0.95},
}

# Parâmetros iniciais
tipo_vegetacao = "C"  # Floresta
densidade_vegetacao = 6  # Densa

# Parâmetros controláveis
temperatura_amb = 25  # °C (0..50)
umidade = 30  # % (0..100)
temp_fogo = 800  # °C (250..1500)
pausado = False

# Vento
vento_dir = "Nenhum"
vento_forca = 0  # km/h (0..160)

# Matrizes de estado
tempo_queimando = np.zeros((GRADE_SIZE, GRADE_SIZE), dtype=np.int16)
deslocamentos = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
direcoes = {
    "N": (-1, 0),
    "S": (1, 0),
    "O": (0, -1),
    "L": (0, 1),
}

# --- FUNÇÕES ---

def criar_grade(tipo, densidade):
    prob = DENSIDADE[densidade]["prob_preenchimento"]
    g = (np.random.rand(GRADE_SIZE, GRADE_SIZE) < prob).astype(np.uint8)
    g[0, :] = 0
    g[-1, :] = 0
    g[:, 0] = 0
    g[:, -1] = 0
    return g

estado = np.where(criar_grade(tipo_vegetacao, densidade_vegetacao) == 1, 1, 0)

def passo(estado, temperatura_amb, umidade, temp_fogo, vento_dir, vento_forca, tipo):
    novo_estado = estado.copy()
    queimando = (estado == 2)
    
    # Reduz o tempo de queima e apaga o fogo que terminou
    tempo_queimando[queimando] -= 1
    acabou = queimando & (tempo_queimando <= 0)
    novo_estado[acabou] = 3  # Estado 'queimada'
    
    # Verifica vizinhos queimando
    vizinho_queimando = np.zeros_like(queimando, dtype=bool)
    for dx, dy in deslocamentos:
        vizinho_queimando |= np.roll(np.roll(queimando, dx, axis=0), dy, axis=1)
        
    # Calcula a probabilidade base de inflamar
    t = np.clip((temperatura_amb - 0) / 50.0, 0.0, 1.0)
    h = np.clip(umidade / 100.0, 0.0, 1.0)
    intensidade = np.clip((temp_fogo - 250) / (1500 - 250), 0.0, 1.0)
    prob_base = 0.02 + 0.8 * t * (1 - h) * (0.5 + intensidade)
    
    # Ajusta a probabilidade pelo tipo de vegetação
    ajuste_tipo = TIPO_VEGETACAO[tipo]["prob"]
    prob = np.full((GRADE_SIZE, GRADE_SIZE), prob_base * ajuste_tipo)

    # Efeito do vento
    if vento_dir in direcoes and vento_forca > 0:
        dx, dy = direcoes[vento_dir]
        favorecido = np.roll(np.roll(queimando, dx, axis=0), dy, axis=1)
        bonus = 0.5 * (vento_forca / 160.0)
        prob[favorecido] = np.clip(prob[favorecido] + bonus, 0, 1)

    # Aplica a probabilidade e inflama novas células
    rng = np.random.rand(GRADE_SIZE, GRADE_SIZE)
    inflamar = (estado == 1) & vizinho_queimando & (rng < prob)
    novo_estado[inflamar] = 2
    tempo_queimando[inflamar] = TIPO_VEGETACAO[tipo]["duracao"]
    
    return novo_estado

def desenhar_rosa_dos_ventos(tela, vento_dir, vento_forca):
    centro_x, centro_y = LARGURA - 550, 70
    raio_maior = 35
    raio_interno = 5
    cor_clara = (200, 200, 200)
    cor_escura = (0, 0, 0)
    cor_destaque = (255, 215, 0)

    def desenhar_ponta(cor1, cor2, ponta, lado1, lado2, centro):
        pygame.draw.polygon(tela, cor1, [ponta, centro, lado1])
        pygame.draw.polygon(tela, cor2, [ponta, centro, lado2])

    # Pontos cardeais
    ponta_n = (centro_x, centro_y - raio_maior)
    lado1_n = (centro_x - raio_interno, centro_y)
    lado2_n = (centro_x + raio_interno, centro_y)
    desenhar_ponta(cor_clara, cor_escura, ponta_n, lado1_n, lado2_n, (centro_x, centro_y))

    ponta_s = (centro_x, centro_y + raio_maior)
    lado1_s = (centro_x + raio_interno, centro_y)
    lado2_s = (centro_x - raio_interno, centro_y)
    desenhar_ponta(cor_clara, cor_escura, ponta_s, lado1_s, lado2_s, (centro_x, centro_y))

    ponta_l = (centro_x + raio_maior, centro_y)
    lado1_l = (centro_x, centro_y - raio_interno)
    lado2_l = (centro_x, centro_y + raio_interno)
    desenhar_ponta(cor_clara, cor_escura, ponta_l, lado1_l, lado2_l, (centro_x, centro_y))
    
    ponta_o = (centro_x - raio_maior, centro_y)
    lado1_o = (centro_x, centro_y + raio_interno)
    lado2_o = (centro_x, centro_y - raio_interno)
    desenhar_ponta(cor_clara, cor_escura, ponta_o, lado1_o, lado2_o, (centro_x, centro_y))

    # Destaque da direção ativa
    if vento_dir == "N":
        desenhar_ponta(cor_destaque, cor_destaque, ponta_n, lado1_n, lado2_n, (centro_x, centro_y))
    elif vento_dir == "S":
        desenhar_ponta(cor_destaque, cor_destaque, ponta_s, lado1_s, lado2_s, (centro_x, centro_y))
    elif vento_dir == "L":
        desenhar_ponta(cor_destaque, cor_destaque, ponta_l, lado1_l, lado2_l, (centro_x, centro_y))
    elif vento_dir == "O":
        desenhar_ponta(cor_destaque, cor_destaque, ponta_o, lado1_o, lado2_o, (centro_x, centro_y))

    # Letras
    tela.blit(fonte_pequena.render("N", True, COR_TEXTO), (centro_x - 5, centro_y - raio_maior - 20))
    tela.blit(fonte_pequena.render("S", True, COR_TEXTO), (centro_x - 5, centro_y + raio_maior + 10))
    tela.blit(fonte_pequena.render("L", True, COR_TEXTO), (centro_x + raio_maior + 10, centro_y - 7))
    tela.blit(fonte_pequena.render("O", True, COR_TEXTO), (centro_x - raio_maior - 20, centro_y - 7))

    # Velocidade do vento
    if vento_dir != "Nenhum" and vento_forca > 0:
        txt = fonte_pequena.render(f"{vento_forca} km/h", True, cor_destaque)
        rect_txt = txt.get_rect(center=(centro_x, centro_y + raio_maior + 30))
        tela.blit(txt, rect_txt)

def desenhar(estado, tipo, densidade):
    # Desenha a grade da simulação
    for y in range(GRADE_SIZE):
        for x in range(GRADE_SIZE):
            st = estado[y, x]
            if st == 0: cor = COR_VAZIO
            elif st == 1: cor = TIPO_VEGETACAO[tipo]["cor"]
            elif st == 2: cor = COR_QUEIMANDO
            else: cor = COR_QUEIMADA
            retangulo = (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(tela, cor, retangulo)
            
    # Desenha a interface do usuário (UI)
    ui_x = LARGURA
    pygame.draw.rect(tela, COR_UI_FUNDO, (ui_x, 0, 300, ALTURA))
    
    prob_atual = round(0.02 + 0.8 * (temperatura_amb / 50) * (1 - umidade / 100) * (0.5 + ((temp_fogo - 250) / (1500 - 250))) * TIPO_VEGETACAO[tipo]["prob"], 3)
    
    linhas = [
        f"Tipo: {TIPO_VEGETACAO[tipo]['nome']} (Z/X/C)",
        f"Densidade: {DENSIDADE[densidade]['nome']} (4/5/6)",
        f"Temp. ambiente: {temperatura_amb}°C (Num 8/2)",
        f"Umidade: {umidade}% (←/→)",
        f"Temp. do fogo: {temp_fogo}°C (↑/↓) [250-1500]",
        f"Prob. base: {prob_atual}",
        f"Vento: {vento_dir}, {vento_forca} km/h (N/S/L/O, +/-)",
        "-----------------------------------------",
        "Espaço: pausar/continuar",
        "Clique: inflamar célula",
        "R: reiniciar grade",
        "P: salvar captura de tela",
        "Esc: sair",
    ]
    
    y = 10
    for ln in linhas:
        superficie = fonte.render(ln, True, COR_TEXTO)
        tela.blit(superficie, (ui_x + 10, y))
        y += 22
        
    desenhar_rosa_dos_ventos(tela, vento_dir, vento_forca)

def inflamar_no_mouse(mx, my, tipo):
    gx = mx // CELL_SIZE
    gy = my // CELL_SIZE
    if 0 <= gx < GRADE_SIZE and 0 <= gy < GRADE_SIZE:
        if estado[gy, gx] == 1: # Só inflama se houver vegetação
            estado[gy, gx] = 2
            tempo_queimando[gy, gx] = TIPO_VEGETACAO[tipo]["duracao"]

# --- LOOP PRINCIPAL ---
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif evento.key == pygame.K_SPACE:
                pausado = not pausado
            elif evento.key == pygame.K_r:
                estado = np.where(criar_grade(tipo_vegetacao, densidade_vegetacao) == 1, 1, 0)
                tempo_queimando.fill(0)
            elif evento.key == pygame.K_p:
                pygame.image.save(tela, "captura_floresta.png")
            
            # --- Controles da Simulação ---
            # Temperatura do fogo
            elif evento.key == pygame.K_UP: temp_fogo = min(1500, temp_fogo + 50)
            elif evento.key == pygame.K_DOWN: temp_fogo = max(250, temp_fogo - 50)
            # Umidade
            elif evento.key == pygame.K_RIGHT: umidade = min(100, umidade + 1)
            elif evento.key == pygame.K_LEFT: umidade = max(0, umidade - 1)
            # Temperatura ambiente
            elif evento.key in (pygame.K_8, pygame.K_KP8): temperatura_amb = min(50, temperatura_amb + 1)
            elif evento.key in (pygame.K_2, pygame.K_KP2): temperatura_amb = max(0, temperatura_amb - 1)
            # Direção do Vento
            elif evento.key == pygame.K_q: vento_dir = "Nenhum"
            elif evento.key == pygame.K_n: vento_dir = "N"
            elif evento.key == pygame.K_s: vento_dir = "S"
            elif evento.key == pygame.K_l: vento_dir = "L"
            elif evento.key == pygame.K_o: vento_dir = "O"
            # Força do Vento
            elif evento.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS): vento_forca = min(160, vento_forca + 5)
            elif evento.key in (pygame.K_MINUS, pygame.K_KP_MINUS): vento_forca = max(0, vento_forca - 5)
            # Tipo de Vegetação
            elif evento.key == pygame.K_z: tipo_vegetacao = "Z"; estado = np.where(criar_grade(tipo_vegetacao, densidade_vegetacao) == 1, 1, 0); tempo_queimando.fill(0)
            elif evento.key == pygame.K_x: tipo_vegetacao = "X"; estado = np.where(criar_grade(tipo_vegetacao, densidade_vegetacao) == 1, 1, 0); tempo_queimando.fill(0)
            elif evento.key == pygame.K_c: tipo_vegetacao = "C"; estado = np.where(criar_grade(tipo_vegetacao, densidade_vegetacao) == 1, 1, 0); tempo_queimando.fill(0)
            # Densidade
            elif evento.key == pygame.K_4: densidade_vegetacao = 4; estado = np.where(criar_grade(tipo_vegetacao, densidade_vegetacao) == 1, 1, 0); tempo_queimando.fill(0)
            elif evento.key == pygame.K_5: densidade_vegetacao = 5; estado = np.where(criar_grade(tipo_vegetacao, densidade_vegetacao) == 1, 1, 0); tempo_queimando.fill(0)
            elif evento.key == pygame.K_6: densidade_vegetacao = 6; estado = np.where(criar_grade(tipo_vegetacao, densidade_vegetacao) == 1, 1, 0); tempo_queimando.fill(0)

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            mx, my = evento.pos
            if mx < LARGURA: # Permite clicar apenas na grade
                inflamar_no_mouse(mx, my, tipo_vegetacao)

    if not pausado:
        estado = passo(estado, temperatura_amb, umidade, temp_fogo, vento_dir, vento_forca, tipo_vegetacao)
    
    tela.fill(COR_FUNDO)
    desenhar(estado, tipo_vegetacao, densidade_vegetacao)
    pygame.display.flip()
    relogio.tick(FPS)
