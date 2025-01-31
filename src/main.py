# src/main.py

import pygame
from src.interface.menu_inicial import MenuInicial
from src.interface.menu_pausa import MenuPausa
from src.ambiente.ambiente_carro import AmbienteCarro
from src.agentes.agente_q_learning import AgenteQLearning
from src.agentes.carro_genetico import CarroGenetico
from src.util.constantes import FPS

def main():
    """
    Função principal que coordena toda a simulação dos carros autônomos.
    Integra aspectos de aprendizado por reforço (Q-Learning) com evolução genética.
    Os carros aprendem tanto por experiência individual quanto por herança genética.
    """
    # Inicialização do ambiente Pygame
    pygame.init()
    
    # Apresenta o menu inicial e obtém o número de carros desejado
    menu = MenuInicial()
    num_carros = menu.mostrar()
    if num_carros == 0:  # Se o usuário fechou a janela
        pygame.quit()
        return

    # Inicialização do ambiente e dos agentes
    ambiente = AmbienteCarro(num_carros=num_carros)
    agentes = [AgenteQLearning(i) for i in range(num_carros)]
    menu_pausa = MenuPausa(ambiente)
    
    # Configuração do relógio para controle de FPS
    clock = pygame.time.Clock()
    
    # Loop principal do programa
    rodando = True
    while rodando:
        try:
            # Tratamento de eventos globais (fechamento de janela, tecla ESC)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                    break
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        menu_pausa.pausado = True
                        opcao = menu_pausa.mostrar()
                        
                        # Tratamento das opções do menu de pausa
                        if opcao == 1:  # Reiniciar
                            ambiente = AmbienteCarro(num_carros=num_carros)
                            agentes = [AgenteQLearning(i) for i in range(num_carros)]
                        elif opcao == 3:  # Sair
                            rodando = False
                            break

            if not rodando:
                break

            # Início de um novo episódio
            estados = ambiente.reset_todos()
            terminado = False
            ambiente.episodio += 1
            
            # Variáveis para controle da evolução genética
            carros_chegaram = 0
            carros_completaram = []
            vencedores = []
            
            # Loop do episódio - continua até que dois carros cheguem à meta
            # ou até que todos os carros sejam eliminados
            while not terminado and rodando:
                # Atualização de cada carro no ambiente
                for i, (estado, agente) in enumerate(zip(estados, agentes)):
                    # Obtém ações válidas e escolhe uma usando Q-Learning
                    acoes_validas = ambiente.obter_acoes_validas(i)
                    acao = agente.escolher_acao(estado, acoes_validas)
                    
                    # Executa a ação e observa o resultado
                    proximo_estado, recompensa, fim = ambiente.executar_acao(i, acao)
                    
                    # Verifica se o carro chegou à meta
                    if proximo_estado == ambiente.pos_meta:
                        carro_genetico = ambiente.carros_geneticos[i]
                        if not carro_genetico.chegou_meta:
                            # Registra o sucesso do carro
                            carro_genetico.chegou_meta = True
                            carro_genetico.tempo_chegada = ambiente.carros[i]['passos']
                            carros_completaram.append(carro_genetico)
                            print(f"\nCarro {i+1} chegou à meta em {carro_genetico.tempo_chegada} passo!")
                    
                    # Verifica se dois carros chegaram (condição de evolução genética)
                    if len(carros_completaram) >= 2:
                        ambiente.registrar_geracao() # Registra dados da geração
                        
                        # Registra a geração atual
                        ambiente.registrar_geracao
                        
                        # Ordena os vencedores pelo tempo de chegada
                        vencedores = sorted(carros_completaram,
                                            key =lambda x: x.tempo_chegada)[:2]
                        
                        # Realiza a evolução genética
                        novos_genes = CarroGenetico.mutacao(
                            vencedores[0].genes,  # Genes do primeiro colocado
                            vencedores[1].genes   # Genes do segundo colocado
                        )
                        
                        # Mostra os novos genes que serão aplicados e os resultados da evolução
                        print("\nDois carros completaram o percurso!")
                        print(f"Primeiro: {vencedores[0].tempo_chegada} passos")
                        print(f"Segundo: {vencedores[0].tempo_chegada} passos")
                        print("\nNovos genes para a próxima geração:")
                        print(f" Velocidade: {novos_genes.velocidade:.2f}")
                        print(f" Sensor: {novos_genes.sensor_perigo:.2f}")
                        print(f"{'='*50}\n")
                        
                        # Aplica os novos genes melhorados a todos os carros
                        # para a próxima geração
                        for carro in ambiente.carros_geneticos:
                            carro.genes = novos_genes
                        
                        terminado = True
                        break
                    
                    # O agente aprende com a experiência usando Q-Learning
                    proximas_acoes = ambiente.obter_acoes_validas(i)
                    agente.aprender(estado, acao, recompensa, 
                                  proximo_estado, proximas_acoes)
                    
                    estados[i] = proximo_estado
                    terminado = terminado or fim
                
                # Renderização do estado atual do ambiente
                ambiente.renderizar()
                
                # Controle de FPS para manter a simulação em velocidade adequada
                clock.tick(FPS)
                
                # Verificação de eventos durante o episódio
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        rodando = False
                        break
                    elif evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_ESCAPE:
                            menu_pausa.pausado = True
                            opcao = menu_pausa.mostrar()
                            
                            if opcao == 1:  # Reiniciar
                                ambiente = AmbienteCarro(num_carros=num_carros)
                                agentes = [AgenteQLearning(i) for i in range(num_carros)]
                                terminado = True
                            elif opcao == 3:  # Sair
                                rodando = False
                                break

        except Exception as e:
            # Tratamento de erros para evitar crashes
            print(f"Erro durante a execução: {e}")
            break

    # Limpeza e encerramento do Pygame
    pygame.quit()

if __name__ == "__main__":
    main()