# src/ambiente/ambiente_carro.py

import pygame
import numpy as np
import random
from ..util.constantes import CORES, TAMANHO_JANELA, TAMANHO_GRID, FPS
from ..agentes.carro_genetico import CarroGenetico

class AmbienteCarro:
    def __init__(self, num_carros=5):
        """
        Inicializa o ambiente de simulação dos carros autônomos.
        Este ambiente cria um labirinto onde os carros devem aprender a navegar.
        
        Args:
            num_carros (int): Número de carros que participarão da simulação (Padrão: 5)
        """
        # Inicialização do Pygame e configuração da janela
        pygame.init()
        self.tela = pygame.display.set_mode(TAMANHO_JANELA)
        pygame.display.set_caption("Carros Autônomos - Versão Genética")
        
        # Configurações do ambiente
        self.LARGURA, self.ALTURA = TAMANHO_JANELA
        self.GRID = TAMANHO_GRID
        self.COLUNAS = self.LARGURA // self.GRID
        self.LINHAS = self.ALTURA // self.GRID
        
        # Define o tamanho dos elementos em relação ao grid
        self.TAMANHO_CARRO = int(self.GRID * 1.0)    # Carro ocupa 100% da célula
        self.TAMANHO_PAREDE = self.GRID              # Parede ocupa célula inteira
        self.TAMANHO_META = int(self.GRID * 2.0)     # Meta ocupa 150% da célula
        
        # Define a posição da meta no canto inferior direito antes de criar as armadilhas
        self.pos_meta = (self.COLUNAS-2, self.LINHAS-2)
        
        # Cria o labirinto e inicializa os carros
        self.labirinto = self.criar_labirinto()
        self.num_carros = num_carros
        self.carros = []
        self.carros_geneticos = [CarroGenetico(i) for i in range(num_carros)]
        self.armadilhas = self.criar_armadilhas(3)
        
        
        
        
        # Inicializa cada carro com suas propriedades
        for i in range(num_carros):
            self.carros.append({
                'posicao': (1, 1),  # Posição inicial no canto superior esquerdo
                'cor': CORES['CARROS'][i],
                'passos': 0,
                'melhor_episodio': float('inf'),
                'velocidade_atual': self.carros_geneticos[i].genes.velocidade
            })
        
        
        
        # Inicializa contadores e estados
        self.episodio = 0
        self.pausado = False
    
    def criar_armadilhas(self, num_armadilhas):
        """
        Cria armadilhas em posições aleatórias válidas no labirinto
        Args:
            num_armadilhas (int): Quantidade de armadilhas a serem criadas
            
        Returns:
            list: Lista de tuplas (x, y) com as posições das armadilhas
        """
        armadilhas = []
        
        # Mantém registro de posições que não podem ter armadilhas
        
        posicoes_ocupadas = {(1, 1), self.pos_meta}
        
        while len(armadilhas) < num_armadilhas:
            
            # Gera posição aleatória
            
            x = random.randint(1, self.COLUNAS-2)
            y = random.randint(1, self.LINHAS-2)
            
            # Verifica validade da posição
            
            if ((x, y) not in posicoes_ocupadas and
                self.labirinto[y, x] == 0): # 0 = caminho livre
                armadilhas.append((x, y))
                posicoes_ocupadas.add((x, y))
            
        return armadilhas
    
    def verificar_colisao_armadilha(self, posicao):
        """
        Verifica se uma posição colide com alguma armadilha.
        
        Args:
            posicao (tuple): Tupla (x, y) com a posição a ser verificada
            
        Returns:
            bool: True se colidiu com armadilha, False caso contrário
        """
        return posicao in self.armadilhas 
    
    def executar_acao(self, indice_carro, acao):
        """
        Executa uma ação para um carro específico e retorna o resultado.
        Agora considera os genes de velocidade e sensor de perigo.
        
        Returns:
            tuple: (novo_estado, recompensa, terminado)
        """
        carro = self.carros[indice_carro]
        carro_genetico = self.carros_geneticos[indice_carro]
        x, y = carro['posicao']
        
        # Aplica a velocidade genética ao movimento
        
        velocidade = carro_genetico.genes.velocidade * 0.1
        carro['passos'] += 1
        
        # Calcula nova posição baseado na ação e velocidade
        
        novo_x, novo_y = x, y
        if acao == 'cima':
            novo_y = y - velocidade
        elif acao == 'direita':
            novo_x = x + velocidade
        elif acao == 'baixo':
            novo_y = y + velocidade
        elif acao == 'esquerda':
            novo_x = x - velocidade
        
        # Arredonda para a posição do grid mais próxima
        novo_x = round(novo_x)
        novo_y = round(novo_y)
        
        # Verifica colisões com paredes
        if self.labirinto[novo_y, novo_x] == 1:
            return (x, y), -10, True
        
        # Verifica colisões com armadilhas
        if self.verificar_colisao_armadilha((novo_x, novo_y)):
            # Usa o sensor de perigo para tentar evitar a armadilha
            if random.random() < carro_genetico.genes.sensor_perigo/3.0:
                return (x, y), -5, False  # Evitou a armadilha
            return (x, y), -20, True  # Não evitou a armadilha
        
        # Atualiza posição do carro
        carro['posicao'] = (novo_x, novo_y)
        
        # Verifica se chegou na meta
        if (novo_x, novo_y) == self.pos_meta:
            if not carro_genetico.chegou_meta:
                carro_genetico.chegou_meta = True
                carro_genetico.tempo_chegada = carro['passos']
            return (novo_x, novo_y), 100, True
        return (novo_x, novo_y), -0.1, False
            
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
    def registrar_geracao(self):
        """
    Registra informações sobre a geração atual, incluindo:
    - Atributos de todos os carros
    - Carros que chegaram à meta
    - Tempo/passos de cada carro
        """
        print(f"\n{'='*50}")
        print(f"Geração {self.episodio}")
        print(f"{'='*50}")
        
        # Imprime informações de todos os carros
        print("\nCarros da geração:")
        for i, (carro, carro_genetico) in enumerate(zip(self.carros, self.carros_geneticos)):
            print(f"\nCarro {i+1}:")
            print(f" Velocidade: {carro_genetico.genes.velocidade:.2f}")
            print(f" Sensor: {carro_genetico.genes.velocidade:.2f}")
            print(f" Passos: {carro['passos']}")
            print(f" Chegou à meta: {'Sim' if carro_genetico.chegou_meta else 'Não'}")
            if carro_genetico.chegou_meta:
                print(f" Tempo até meta: {carro_genetico.tempo_chegada}")
                
                
        # Identifica os vencedores (carros que chegaram à meta)
        vencedores = [carro for carro in self.carros_geneticos if carro.chegou_meta]
        if len(vencedores) >= 2:
            print("\nVencedores que gerarão a próxima geração:")
            for i, v in enumerate(sorted(vencedores, key=lambda x: x.tempo_chegada)[:2]):
                print(f"\nVencedor {i+1}:")
                print(f"  Velocidade: {v.genes.velocidade:.2f}")
                print(f"  Sensor: {v.genes.sensor_perigo:.2f}")
                print(f"  Tempo até meta: {v.tempo_chegada}")

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
        Inclui armadilhas e informações genéticas.
        """
        # Limpa a tela
        self.tela.fill(CORES['BRANCO'])
        
        # Desenha o labirinto
        for y in range(self.LINHAS):
            for x in range(self.COLUNAS):
                if self.labirinto[y, x] == 1:
                    pygame.draw.rect(
                        self.tela,
                        CORES['PRETO'],
                        (x * self.GRID,
                         y * self.GRID,
                         self.TAMANHO_PAREDE,
                         self.TAMANHO_PAREDE)
                    )
        
        # Desenha as armadilhas
        for x, y in self.armadilhas:
            arm_x = x * self.GRID + (self.GRID - self.TAMANHO_CARRO) // 2
            arm_y = y * self.GRID + (self.GRID - self.TAMANHO_CARRO) // 2
            pygame.draw.rect(
                self.tela,
                CORES['VERMELHO'],
                (arm_x, arm_y,
                 self.TAMANHO_CARRO,
                 self.TAMANHO_CARRO)
            )
        
        # Desenha a meta
        meta_x = self.pos_meta[0] * self.GRID + (self.GRID - self.TAMANHO_META) // 2
        meta_y = self.pos_meta[1] * self.GRID + (self.GRID - self.TAMANHO_META) // 2
        pygame.draw.rect(
            self.tela,
            CORES['VERDE'],
            (meta_x, meta_y,
             self.TAMANHO_META, 
             self.TAMANHO_META)
        )
        
        # Desenha os carros com informações genéticas
        fonte = pygame.font.Font(None, 20)
        for i, (carro, carro_genetico) in enumerate(zip(self.carros, self.carros_geneticos)):
            x, y = carro['posicao']
            car_x = x * self.GRID + (self.GRID - self.TAMANHO_CARRO) // 2
            car_y = y * self.GRID + (self.GRID - self.TAMANHO_CARRO) // 2
            
            # Desenha o carro
            pygame.draw.rect(
                self.tela,
                carro['cor'],
                (car_x, car_y,
                 self.TAMANHO_CARRO, 
                 self.TAMANHO_CARRO)
            )
            
            # Mostra atributos genéticos sobre o carro
            info = f"V:{carro_genetico.genes.velocidade:.1f} S:{carro_genetico.genes.sensor_perigo:.1f}"
            texto = fonte.render(info, True, CORES['PRETO'])
            self.tela.blit(texto, (car_x - 10, car_y - 15))
        
        # Mostra informações do episódio
        fonte = pygame.font.Font(None, 36)
        info = f'Episódio: {self.episodio}'
        for i, carro in enumerate(self.carros):
            info += f' | Carro {i+1}: {carro["passos"]}'
        texto = fonte.render(info, True, CORES['PRETO'])
        self.tela.blit(texto, (50, 50))
        
        

            
        # Atualiza a tela
        pygame.display.flip()