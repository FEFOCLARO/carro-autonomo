# src/interface/menu_inicial.py
import pygame
from ..util.constantes import CORES, TAMANHO_JANELA

class MenuInicial:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode(TAMANHO_JANELA)
        pygame.display.set_caption("Configuração da Simulação")
        self.fonte = pygame.font.Font(None, 36)
        self.fonte_titulo = pygame.font.Font(None, 48)
        self.fonte_subtitulo = pygame.font.Font(None, 28)
        self.num_carros = 1

    def mostrar(self):
        """Mostra o menu inicial centralizado"""
        rodando = True
        while rodando:
            self.tela.fill(CORES['BRANCO'])
            
            # Título centralizado
            titulo = self.fonte_titulo.render("Simulação de Carros Autônomos", True, CORES['PRETO'])
            titulo_rect = titulo.get_rect(center=(TAMANHO_JANELA[0]//2, 100))
            self.tela.blit(titulo, titulo_rect)
            
            # Subtítulo em itálico
            subtitulo = self.fonte_subtitulo.render(
                "Um projeto de Aprendizado por Reforço, por Fernando Claro", 
                True, CORES['PRETO'])
            subtitulo_rect = subtitulo.get_rect(center=(TAMANHO_JANELA[0]//2, 150))
            self.tela.blit(subtitulo, subtitulo_rect)
            
            # Seletor de número de carros
            texto_carros = self.fonte.render(f"Número de Carros: {self.num_carros}", True, CORES['PRETO'])
            texto_rect = texto_carros.get_rect(center=(TAMANHO_JANELA[0]//2, 300))
            self.tela.blit(texto_carros, texto_rect)
            
            # Botões de - e +
            botao_menos = pygame.Rect(texto_rect.left - 80, 285, 40, 40)
            botao_mais = pygame.Rect(texto_rect.right + 40, 285, 40, 40)
            
            pygame.draw.rect(self.tela, CORES['CINZA'], botao_menos)
            pygame.draw.rect(self.tela, CORES['CINZA'], botao_mais)
            
            menos = self.fonte.render("-", True, CORES['PRETO'])
            mais = self.fonte.render("+", True, CORES['PRETO'])
            
            self.tela.blit(menos, menos.get_rect(center=botao_menos.center))
            self.tela.blit(mais, mais.get_rect(center=botao_mais.center))
            
            # Botão Iniciar
            botao_iniciar = pygame.Rect(TAMANHO_JANELA[0]//2 - 100, 400, 200, 50)
            pygame.draw.rect(self.tela, CORES['VERDE_CLARO'], botao_iniciar)
            
            texto_iniciar = self.fonte.render("Iniciar", True, CORES['PRETO'])
            self.tela.blit(texto_iniciar, 
                          texto_iniciar.get_rect(center=botao_iniciar.center))
            
            pygame.display.flip()
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return 0
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if botao_menos.collidepoint(mouse_pos):
                        self.num_carros = max(1, self.num_carros - 1)
                    elif botao_mais.collidepoint(mouse_pos):
                        self.num_carros = min(6, self.num_carros + 1)
                    elif botao_iniciar.collidepoint(mouse_pos):
                        return self.num_carros