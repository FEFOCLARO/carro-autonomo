# src/interface/menu_pausa.py
import pygame
from ..util.constantes import CORES, TAMANHO_JANELA

class MenuPausa:
    def __init__(self, ambiente):
        self.ambiente = ambiente
        self.fonte = pygame.font.Font(None, 36)
        self.pausado = False
        
        # Configuração do botão de pausa
        self.botao_pausa = pygame.Rect(TAMANHO_JANELA[0] - 50, 10, 40, 40)

    def desenhar_botao_pausa(self):
        """Desenha o botão de pausa na interface principal"""
        pygame.draw.rect(self.ambiente.tela, CORES['CINZA'], self.botao_pausa)
        # Desenha o ícone de pausa (duas barras verticais)
        pygame.draw.rect(self.ambiente.tela, CORES['PRETO'], 
                        (self.botao_pausa.x + 10, self.botao_pausa.y + 8, 6, 24))
        pygame.draw.rect(self.ambiente.tela, CORES['PRETO'], 
                        (self.botao_pausa.x + 24, self.botao_pausa.y + 8, 6, 24))

    def mostrar(self):
        """Mostra o menu de pausa centralizado"""
        # Cria overlay semi-transparente
        overlay = pygame.Surface(TAMANHO_JANELA)
        overlay.set_alpha(128)
        overlay.fill(CORES['BRANCO'])
        self.ambiente.tela.blit(overlay, (0, 0))

        opcoes = ["Continuar", "Reiniciar", "Estatísticas", "Sair"]
        largura_opcao = 200
        altura_opcao = 50
        espacamento = 20
        
        # Calcula posição inicial para centralizar o menu
        pos_y_inicial = (TAMANHO_JANELA[1] - (len(opcoes) * (altura_opcao + espacamento))) // 2
        
        # Desenha as opções
        for i, opcao in enumerate(opcoes):
            pos_y = pos_y_inicial + i * (altura_opcao + espacamento)
            pos_x = (TAMANHO_JANELA[0] - largura_opcao) // 2
            
            # Retângulo do botão
            rect = pygame.Rect(pos_x, pos_y, largura_opcao, altura_opcao)
            pygame.draw.rect(self.ambiente.tela, CORES['CINZA'], rect)
            
            # Texto centralizado no botão
            texto = self.fonte.render(opcao, True, CORES['PRETO'])
            texto_rect = texto.get_rect(center=rect.center)
            self.ambiente.tela.blit(texto, texto_rect)
        
        pygame.display.flip()
        
        # Loop de eventos do menu de pausa
        while self.pausado:
            for evento in pygame.event.get():
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    self.pausado = False
                    return 0
                    
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Verifica clique em cada opção
                    for i in range(len(opcoes)):
                        pos_y = pos_y_inicial + i * (altura_opcao + espacamento)
                        rect = pygame.Rect((TAMANHO_JANELA[0] - largura_opcao) // 2,
                                         pos_y, largura_opcao, altura_opcao)
                        if rect.collidepoint(mouse_pos):
                            return i