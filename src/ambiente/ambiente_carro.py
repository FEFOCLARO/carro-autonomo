# src/ambiente/ambiente_carro.py

import pygame
import numpy as np
from ..util.constantes import CORES, TAMANHO_JANELA, TAMANHO_GRID, FPS

class AmbienteCarro:
    def __init__(self, num_carros=1):
        """
        Inicializa o ambiente de simulação dos carros autônomos.
        Este ambiente cria um labirinto onde os carros devem aprender a navegar.
        
        Args:
            num_carros (int): Número de carros que participarão da simulação
        """
        # Inicialização do Pygame e configuração da janela
        pygame.init()
        self.tela = pygame.display.set_mode(TAMANHO_JANELA)
        pygame.display.set_caption("Carros Autônomos")
        
        # Configurações do ambiente
        self.LARGURA, self.ALTURA = TAMANHO_JANELA
        self.GRID = TAMANHO_GRID
        self.COLUNAS = self.LARGURA // self.GRID
        self.LINHAS = self.ALTURA // self.GRID
        
        # Define o tamanho dos elementos em relação ao grid
        self.TAMANHO_CARRO = int(self.GRID * 0.8)    # Carro ocupa 80% da célula
        self.TAMANHO_PAREDE = self.GRID              # Parede ocupa célula inteira
        self.TAMANHO_META = int(self.GRID * 0.9)     # Meta ocupa 90% da célula
        
        # Cria o labirinto e inicializa os carros
        self.labirinto = self.criar_labirinto()
        self.num_carros = num_carros
        self.carros = []
        
        # Inicializa cada carro com suas propriedades
        for i in range(num_carros):
            self.carros.append({
                'posicao': (1, 1),  # Posição inicial no canto superior esquerdo
                'cor': CORES['CARROS'][i],
                'passos': 0,
                'melhor_episodio': float('inf')
            })
        
        # Define a posição da meta no canto inferior direito
        self.pos_meta = (self.COLUNAS-2, self.LINHAS-2)
        
        # Inicializa contadores e estados
        self.episodio = 0
        self.pausado = False

    def criar_labirinto(self):
        """
        Cria o layout do labirinto com paredes e obstáculos.
        O labirinto é representado por uma matriz onde 1 representa parede e 0 representa caminho livre.
        """
        labirinto = np.zeros((self.LINHAS, self.COLUNAS))
        
        # Cria as paredes externas
        labirinto[0, :] = 1  # Parede superior
        labirinto[-1, :] = 1  # Parede inferior
        labirinto[:, 0] = 1  # Parede esquerda
        labirinto[:, -1] = 1  # Parede direita
        
        # Adiciona obstáculos internos para criar um percurso interessante
        # Ajustado para a nova resolução
        labirinto[5:12, 10] = 1    # Primeira parede vertical
        labirinto[8:15, 20] = 1    # Segunda parede vertical
        labirinto[3:10, 15] = 1    # Terceira parede vertical
        
        labirinto[7, 10:16] = 1    # Primeira parede horizontal
        labirinto[12, 15:21] = 1   # Segunda parede horizontal
        labirinto[15, 5:11] = 1    # Terceira parede horizontal
        
        return labirinto

    def reset_todos(self):
        """
        Reinicia todos os carros para a posição inicial.
        Usado no início de cada episódio de treinamento.
        """
        for carro in self.carros:
            carro['posicao'] = (1, 1)  # Volta para posição inicial
            carro['passos'] = 0        # Zera contador de passos
        
        return [self.obter_estado(i) for i in range(self.num_carros)]

    def obter_estado(self, indice_carro):
        """
        Retorna o estado atual de um carro específico.
        O estado é representado pela posição do carro no grid.
        """
        return self.carros[indice_carro]['posicao']

    def obter_acoes_validas(self, indice_carro):
        """
        Retorna lista de ações válidas para um carro específico.
        Uma ação é válida se não leva o carro a colidir com uma parede.
        """
        acoes = []
        x, y = self.carros[indice_carro]['posicao']
        
        # Verifica cada possível movimento
        movimentos = [
            ('cima', (x, y-1)),
            ('direita', (x+1, y)),
            ('baixo', (x, y+1)),
            ('esquerda', (x-1, y))
        ]
        
        for acao, (prox_x, prox_y) in movimentos:
            if (0 <= prox_x < self.COLUNAS and 
                0 <= prox_y < self.LINHAS and 
                not self.labirinto[prox_y, prox_x]):
                acoes.append(acao)
                
        return acoes

    def executar_acao(self, indice_carro, acao):
        """
        Executa uma ação para um carro específico e retorna o resultado.
        
        Returns:
            tuple: (novo_estado, recompensa, terminado)
        """
        carro = self.carros[indice_carro]
        x, y = carro['posicao']
        carro['passos'] += 1
        
        # Atualiza posição baseado na ação
        if acao == 'cima': y -= 1
        elif acao == 'direita': x += 1
        elif acao == 'baixo': y += 1
        elif acao == 'esquerda': x -= 1
        
        # Verifica colisão com parede
        if self.labirinto[y, x] == 1:
            return self.obter_estado(indice_carro), -10, True
        
        # Atualiza posição do carro
        carro['posicao'] = (x, y)
        
        # Verifica se chegou na meta
        if (x, y) == self.pos_meta:
            if carro['passos'] < carro['melhor_episodio']:
                carro['melhor_episodio'] = carro['passos']
            return self.obter_estado(indice_carro), 100, True
        
        return self.obter_estado(indice_carro), -0.1, False

    def renderizar(self):
        """
        Desenha o estado atual do ambiente na tela.
        Inclui o labirinto, os carros e as informações do episódio.
        """
        # Limpa a tela
        self.tela.fill(CORES['BRANCO'])
        
        # Desenha o labirinto
        espessura_bordas = 4 # Espessura das paredes laterais em pixels
        
        for y in range(self.LINHAS):
            for x in range(self.COLUNAS):
                if self.labirinto[y, x] == 1:
                    
                    is_borda = (x == 0 or x == self.COLUNAS-1 or
                                y == 0 or y == self.LINHAS-1)
                    if is_borda:
                        # Desenha parede lateral fina
                        pygame.draw.rect(
                            self.tela,
                            CORES['PRETO'],
                            (x * self.GRID,
                             y * self.GRID,
                             self.TAMANHO_PAREDE,
                             self.TAMANHO_PAREDE),
                            espessura_bordas #apenas o contorno
                            )
                    else:
                        # Desenha parede do labirinto normal (grossa)
                        pygame.draw.rect(
                            self.tela,
                            CORES['PRETO'],
                            (x * self.GRID,
                            y * self.GRID,
                            self.TAMANHO_PAREDE,
                            self.TAMANHO_PAREDE)
                        )
                   
        
        # Desenha a meta
        meta_x = self.pos_meta[0] * self.GRID + (self.GRID - self.TAMANHO_META) // 2
        meta_y = self.pos_meta[1] * self.GRID + (self.GRID - self.TAMANHO_META) // 2
        pygame.draw.rect(self.tela, CORES['VERDE'],
                        (meta_x, meta_y,
                         self.TAMANHO_META, 
                         self.TAMANHO_META))
        
        # Desenha os carros
        for carro in self.carros:
            x, y = carro['posicao']
            car_x = x * self.GRID + (self.GRID - self.TAMANHO_CARRO) // 2
            car_y = y * self.GRID + (self.GRID - self.TAMANHO_CARRO) // 2
            pygame.draw.rect(self.tela, carro['cor'],
                           (car_x, car_y,
                            self.TAMANHO_CARRO, 
                            self.TAMANHO_CARRO))
        
        # Mostra informações do episódio
        fonte = pygame.font.Font(None, 36)
        info = f'Episódio: {self.episodio}'
        for i, carro in enumerate(self.carros):
            info += f' | Carro {i+1}: {carro["passos"]}'
        texto = fonte.render(info, True, CORES['PRETO'])
        self.tela.blit(texto, (10, 10))
        
        # Atualiza a tela
        pygame.display.flip()