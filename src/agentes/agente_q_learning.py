# src/agentes/agente_q_learning.py

from collections import defaultdict
import random
from ..util.constantes import PARAMS_APRENDIZAGEM as PA

class AgenteQLearning:
    """
    Implementa um agente de aprendizagem por reforço usando Q-Learning.
    Cada agente mantém sua própria tabela Q e parâmetros de aprendizagem.
    """
    def __init__(self, indice_carro=0):
        # Tabela Q armazena os valores estado-ação
        self.tabela_q = defaultdict(lambda: defaultdict(float))
        
        # Parâmetros de aprendizagem personalizados para cada carro
        self.taxa_aprendizagem = PA['TAXA_APRENDIZAGEM_BASE'] + (indice_carro * PA['INCREMENTO_TAXA'])
        self.gamma = PA['FATOR_DESCONTO']
        self.epsilon = PA['EPSILON_INICIAL']
        
        # Identificação do agente
        self.indice = indice_carro

    def escolher_acao(self, estado, acoes_validas):
        """
        Seleciona uma ação usando a política epsilon-greedy.
        Equilibra exploração (ações aleatórias) e exploração (melhores ações conhecidas).
        """
        if random.random() < self.epsilon:
            # Exploração: escolhe ação aleatória
            return random.choice(acoes_validas)
        else:
            # Exploração: escolhe ação com maior valor Q
            return max(acoes_validas, 
                      key=lambda a: self.tabela_q[estado][a])

    def aprender(self, estado, acao, recompensa, proximo_estado, proximas_acoes):
        """
        Atualiza a tabela Q com base na experiência adquirida.
        Usa a equação de Bellman para atualizar os valores Q.
        """
        # Encontra o maior valor Q possível no próximo estado
        proximo_max = max([self.tabela_q[proximo_estado][a] 
                          for a in proximas_acoes], default=0)
        
        # Atualiza o valor Q usando a equação de Bellman
        q_atual = self.tabela_q[estado][acao]
        novo_q = q_atual + self.taxa_aprendizagem * (
            recompensa + self.gamma * proximo_max - q_atual)
        self.tabela_q[estado][acao] = novo_q
        
        # Reduz gradualmente a taxa de exploração
        self.epsilon = max(PA['EPSILON_MINIMO'], 
                          self.epsilon * PA['EPSILON_DECAY'])