import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from services import Gerenciador


class TelaMetas(tk.Frame):
    """
    Tela de gerenciamento de metas de economia.

    Exibe:
    - Formulário para criar nova meta
    - Lista de metas com barra de progresso visual
    - Status de cada meta (em andamento / concluída / atrasada)
    - Botão para depositar valor em uma meta
    """

    def __init__(self, parent, gerenciador: Gerenciador):
        super().__init__(parent, bg="#1e1e2e")
        self.pack(fill=tk.BOTH, expand=True)
        self.gerenciador = gerenciador

        self._construir_ui()
        self._atualizar_lista()

    def _construir_ui(self):
        """
        TODO: Implementar com:
        1. Frame formulário:
           - Entry: descrição da meta
           - Entry: valor alvo
           - Entry: prazo (AAAA-MM-DD)
           - Button: Criar Meta
        2. Frame lista de metas:
           - Para cada meta: mostrar descrição, progresso (ttk.Progressbar), status, valor atual/alvo
           - Button: Depositar (abre janela simples pedindo valor)
           - Button: Remover
        """
        # TODO: Implementar
        pass

    def _criar_meta(self):
        """
        TODO: Ler campos e chamar self.gerenciador.adicionar_meta().
        Tratar ValueError com messagebox.showerror().
        """
        # TODO: Implementar
        pass

    def _depositar(self, indice: int):
        """
        TODO: Abrir um Toplevel (janela secundária) pedindo o valor do depósito.
        Chamar meta.depositar(valor) e atualizar a lista.
        """
        # TODO: Implementar
        pass

    def _remover_meta(self, indice: int):
        """
        TODO: Chamar self.gerenciador.remover_meta(indice) e atualizar lista.
        """
        # TODO: Implementar
        pass

    def _atualizar_lista(self):
        """
        TODO: Limpar e recriar os cards de metas na tela.
        Dica: use um Frame scrollável (Canvas + Scrollbar) se houver muitas metas.
        """
        # TODO: Implementar
        pass
