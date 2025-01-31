# src/agentes/carro_genetico.py

import random
from dataclasses import dataclass
from ..util.constantes import PARAMS_GENETICOS as PG

@dataclass
class Genes:
    velocidade: float
    sensor_perigo: float

class CarroGenetico:
    def __init__(self, indice):
        self.genes = self._inicializar_genes()
        self.indice = indice
        self.chegou_meta = False
        self.tempo_chegada = float('inf') # Infinito até chegar meta
        self.melhor_distancia = float('inf') # Para rastrear quão perto chegou
        self.fitness = 0
        
    def _inicializar_genes(self):
        
        # Nascimento com valores moderados, partindo do mínimo 
        return Genes(
            velocidade=random.uniform(PG['VELOCIDADE_MIN'], PG['VELOCIDADE_MAX']),
            sensor_perigo=random.uniform(PG['SENSOR_MIN'], PG['SENSOR_MAX'])
        )
    
    @staticmethod
    def mutacao(genes_pai1, genes_pai2):
        """
        Realiza o cruzamento genético entre dois carros.
        Permite que as mutações ultrapassem os limites iniciais,
        possibilitando evolução para valores mais altos.
        """
        # Crossover com média ponderada
        nova_velocidade = (genes_pai1.velocidade + genes_pai2.velocidade) / 2
        novo_sensor = (genes_pai1.sensor_perigo + genes_pai2.sensor_perigo) / 2
        
        # Adiciona mutação aleatória
        if random.random() < PG['TAXA_MUTACAO']:
            nova_velocidade *= random.uniform(0.8, 1.5)
        if random.random() < PG['TAXA_MUTACAO']:
            novo_sensor *= random.uniform(0.8, 1.5)
        
        # Mantém os valores dentro dos limites
        nova_velocidade = max(PG['VELOCIDADE_MIN'], 
                            min(PG['VELOCIDADE_MAX'], nova_velocidade))
        novo_sensor = max(PG['SENSOR_MIN'], 
                         min(PG['SENSOR_MAX'], novo_sensor))
        
        return Genes(velocidade=nova_velocidade, sensor_perigo=novo_sensor)