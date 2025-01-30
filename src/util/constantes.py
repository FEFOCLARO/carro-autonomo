# src/util/constantes.py

# Configurações da janela
TAMANHO_JANELA = (1280, 720)
TAMANHO_GRID = 40
FPS = 60

# Definição de cores em RGB
CORES = {
    'BRANCO': (255, 255, 255),
    'PRETO': (0, 0, 0),
    'VERDE': (0, 255, 0),
    'CINZA': (200, 200, 200),
    'VERDE_CLARO': (150, 255, 150),
    # Cores distintas para cada carro
    'CARROS': [
        (0, 0, 255),      # Azul
        (255, 165, 0),    # Laranja
        (138, 43, 226),   # Roxo
        (0, 255, 127),    # Verde água
        (255, 20, 147),   # Rosa
        (0, 191, 255)     # Azul claro
    ]
}

# Parâmetros de aprendizagem
PARAMS_APRENDIZAGEM = {
    'TAXA_APRENDIZAGEM_BASE': 0.1,    # Taxa base de aprendizagem
    'INCREMENTO_TAXA': 0.02,          # Incremento para cada carro adicional
    'FATOR_DESCONTO': 0.95,           # Quanto importam as recompensas futuras
    'EPSILON_INICIAL': 1.0,           # Taxa inicial de exploração
    'EPSILON_MINIMO': 0.01,           # Taxa mínima de exploração
    'EPSILON_DECAY': 0.995            # Taxa de decaimento da exploração
}