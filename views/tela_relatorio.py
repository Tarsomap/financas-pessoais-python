# =============================================================================
# views/tela_relatorio.py
# -----------------------------------------------------------------------------
# Tela de relatórios e análises financeiras.
#
# Exibe:
#   - Seletor de mês/ano
#   - Resumo: total receitas, despesas e saldo
#   - Gráfico de barras horizontal desenhado com tk.Canvas
#   - Categoria que mais gastou
#   - Sugestões automáticas de corte de gastos
#
# Como o gráfico funciona:
#   O tkinter não tem gráfico nativo, mas o Canvas permite desenhar
#   formas geométricas. Cada barra é um create_rectangle() com largura
#   proporcional ao valor da categoria:
#     largura = (valor / valor_maximo) * largura_disponivel
#
# Conceitos demonstrados:
#   - tk.Canvas com create_rectangle() e create_text()
#   - Chamada a @staticmethod da classe Relatorio
#   - f-strings com :.2f para formatar valores monetários
#
# RESPONSÁVEL: Alice
# =============================================================================

import tkinter as tk
from tkinter import ttk
from datetime import date
from services import Gerenciador, Relatorio

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
        TODO:
        1. Frame controles: Spinbox mês, Spinbox ano, Button Gerar Relatório
        2. Frame resumo: Labels receitas (verde), despesas (vermelho), saldo, categoria top
        3. self.canvas = tk.Canvas(...) para o gráfico
        4. Frame sugestões: Labels com Relatorio.sugestao_corte()
        """
        # TODO: Implementar
        pass

    def _gerar_relatorio(self):
        """
        TODO: Ler mês/ano, chamar Relatorio.resumo_mensal(),
        atualizar Labels e chamar _desenhar_grafico().
        """
        # TODO: Implementar
        pass

    def _desenhar_grafico(self, dados_categorias: dict):
        """
        Desenha barras horizontais no Canvas.
        TODO: Para cada categoria com índice i:
            y_topo    = 20 + i * 40
            y_base    = y_topo + 25
            x_direita = 150 + (valor / valor_max) * 300
            canvas.create_rectangle(150, y_topo, x_direita, y_base, fill=cor)
            canvas.create_text(145, meio_y, text=categoria, anchor='e')
            canvas.create_text(x_direita+5, meio_y, text=f'R$ {valor:.2f}', anchor='w')
        """
        # TODO: Implementar
        pass
