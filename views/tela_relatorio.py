# =============================================================================
# views/tela_relatorio.py
# -----------------------------------------------------------------------------
# Tela de relatórios e análises financeiras.
#
# Responsabilidades:
#   - Seletor de mês/ano para filtrar o período
#   - Exibir resumo: total de receitas, despesas e saldo do mês
#   - Gráfico de barras horizontal desenhado com tk.Canvas
#   - Mostrar a categoria que mais gastou no mês
#   - Listar sugestões automáticas de corte de gastos
#
# Como o gráfico funciona:
#   O tkinter não tem um componente de gráfico nativo, mas o Canvas
#   permite desenhar formas geométricas. Usamos create_rectangle() para
#   as barras e create_text() para os rótulos.
#   A largura de cada barra é proporcional ao valor da categoria:
#     largura_barra = (valor / valor_maximo) * largura_maxima_disponivel
#
# Conceitos demonstrados neste arquivo:
#   - tk.Canvas com create_rectangle() e create_text()
#   - Chamada a métodos estáticos da classe Relatorio
#   - StringVar com OptionMenu para seleção de mês/ano
#   - Formatação de strings com f-strings e :.2f para valores monetários
#
# RESPONSÁVEL: Pessoa 7
# =============================================================================

import tkinter as tk
from tkinter import ttk
from datetime import date
from services import Gerenciador, Relatorio

# Cores para as barras do gráfico (uma por categoria)
CORES_GRAFICO = ["#89b4fa", "#a6e3a1", "#fab387", "#f38ba8",
                 "#cba6f7", "#f9e2af", "#94e2d5", "#eba0ac"]


class TelaRelatorio(tk.Frame):
    """Tela de relatórios e análises financeiras."""

    def __init__(self, parent, gerenciador: Gerenciador):
        super().__init__(parent, bg="#1e1e2e")
        self.pack(fill=tk.BOTH, expand=True)
        self.gerenciador = gerenciador

        self._construir_ui()
        self._gerar_relatorio()

    def _construir_ui(self):
        """
        TODO: Implementar com:
        1. Frame de controles:
           - OptionMenu ou Spinbox para mês (1-12)
           - Spinbox para ano
           - Button: 'Gerar Relatório' → chama self._gerar_relatorio()

        2. Frame de resumo:
           - Label: total de receitas (verde)
           - Label: total de despesas (vermelho)
           - Label: saldo (verde/vermelho)
           - Label: categoria que mais gastou

        3. Canvas para o gráfico de barras:
           - self.canvas = tk.Canvas(...)

        4. Frame de sugestões:
           - Label título
           - Labels para cada sugestão retornada por Relatorio.sugestao_corte()
        """
        # TODO: Implementar
        pass

    def _gerar_relatorio(self):
        """
        Lê mês/ano selecionado, chama Relatorio.resumo_mensal() e
        atualiza todos os elementos da tela.
        TODO: Implementar atualizando Labels e chamando self._desenhar_grafico().
        """
        # TODO: Implementar
        pass

    def _desenhar_grafico(self, dados_categorias: dict):
        """
        Desenha um gráfico de barras horizontal no Canvas.

        Args:
            dados_categorias: Dicionário {categoria: valor}.

        TODO: Implementar com create_rectangle() e create_text().
        Dica:
            canvas_largura = self.canvas.winfo_width() ou use um valor fixo (ex: 500)
            Para cada categoria com índice i:
                y_topo    = 20 + i * 40
                y_base    = y_topo + 25
                x_direita = 150 + (valor / valor_maximo) * 300
                self.canvas.create_rectangle(150, y_topo, x_direita, y_base, fill=CORES_GRAFICO[i % len(CORES_GRAFICO)])
                self.canvas.create_text(145, (y_topo+y_base)//2, text=categoria, anchor='e')
                self.canvas.create_text(x_direita+5, (y_topo+y_base)//2, text=f'R$ {valor:.2f}', anchor='w')
        """
        # TODO: Implementar
        pass
