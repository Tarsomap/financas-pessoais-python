import tkinter as tk
from tkinter import ttk
from datetime import date
from services import Gerenciador, Relatorio


class TelaRelatorio(tk.Frame):
    """
    Tela de relatórios e análises financeiras.

    Exibe:
    - Resumo do mês selecionado (receitas, despesas, saldo)
    - Gráfico de barras por categoria (Canvas do tkinter)
    - Categoria que mais gastou
    - Sugestões de corte de gastos
    """

    def __init__(self, parent, gerenciador: Gerenciador):
        super().__init__(parent, bg="#1e1e2e")
        self.pack(fill=tk.BOTH, expand=True)
        self.gerenciador = gerenciador

        self._construir_ui()
        self._gerar_relatorio()

    def _construir_ui(self):
        """
        TODO: Implementar com:
        1. Seletor de mês/ano (OptionMenu ou Spinbox)
        2. Button: Gerar Relatório
        3. Labels para receitas totais, despesas totais, saldo
        4. Canvas para o gráfico de barras
        5. Label para categoria que mais gastou
        6. Frame para sugestões de corte
        """
        # TODO: Implementar
        pass

    def _gerar_relatorio(self):
        """
        TODO: Ler mês/ano selecionado, chamar Relatorio.resumo_mensal(),
        atualizar Labels e redesenhar o gráfico.
        """
        # TODO: Implementar
        pass

    def _desenhar_grafico(self, dados_categorias: dict):
        """
        Desenha um gráfico de barras horizontal usando tk.Canvas.

        Args:
            dados_categorias: Dicionário {categoria: valor}.

        TODO: Implementar usando self.canvas.create_rectangle() e create_text().
        Dica:
            - Normalize as barras pelo maior valor
            - Use cores diferentes por categoria
            - Exiba o valor no final de cada barra
        """
        # TODO: Implementar
        pass
