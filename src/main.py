# src/main.py

import pygame
from src.interface.menu_inicial import MenuInicial
from src.interface.menu_pausa import MenuPausa
from src.ambiente.ambiente_carro import AmbienteCarro
from src.agentes.agente_q_learning import AgenteQLearning
from src.util.constantes import FPS

def main():
    """
    Função principal que coordena toda a simulação.
    Gerencia o fluxo entre menus e a simulação dos carros autônomos.
    """
    # Inicialização do Pygame
    pygame.init()
    
    # Criação e exibição do menu inicial
    menu = MenuInicial()
    num_carros = menu.mostrar()
    if num_carros == 0:  # Se o usuário fechou a janela
        pygame.quit()
        return

    # Criação do ambiente e dos agentes
    ambiente = AmbienteCarro(num_carros=num_carros)
    agentes = [AgenteQLearning(i) for i in range(num_carros)]
    menu_pausa = MenuPausa(ambiente)
    
    # Configuração do relógio para controle de FPS
    clock = pygame.time.Clock()
    
    # Loop principal do programa
    rodando = True
    while rodando:
        try:
            # Tratamento de eventos globais
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
                        elif opcao == 3:  # Sair
                            rodando = False
                            break

            if not rodando:
                break

            # Início de um novo episódio
            estados = ambiente.reset_todos()
            terminado = False
            ambiente.episodio += 1
            
            # Loop do episódio
            while not terminado and rodando:
                # Atualização de cada carro
                for i, (estado, agente) in enumerate(zip(estados, agentes)):
                    # Obtém ações válidas e escolhe uma
                    acoes_validas = ambiente.obter_acoes_validas(i)
                    acao = agente.escolher_acao(estado, acoes_validas)
                    
                    # Executa a ação e observa o resultado
                    proximo_estado, recompensa, fim = ambiente.executar_acao(i, acao)
                    
                    # Agente aprende com a experiência
                    proximas_acoes = ambiente.obter_acoes_validas(i)
                    agente.aprender(estado, acao, recompensa, 
                                  proximo_estado, proximas_acoes)
                    
                    estados[i] = proximo_estado
                    terminado = terminado or fim
                
                # Renderização do estado atual
                ambiente.renderizar()
                
                # Controle de FPS
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
            print(f"Erro durante a execução: {e}")
            break

    # Limpeza e encerramento
    pygame.quit()

if __name__ == "__main__":
    main()