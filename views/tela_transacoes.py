import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from services import Gerenciador
from models import Categoria


class TelaTransacoes(tk.Frame):
    """
    Tela de gerenciamento de receitas e despesas.

    Exibe:
    - Formulário para adicionar nova transação
    - Saldo atual em destaque
    - Lista de transações com opção de remoção
    - Filtros por tipo e categoria
    """

    def __init__(self, parent, gerenciador: Gerenciador):
        super().__init__(parent, bg="#1e1e2e")
        self.pack(fill=tk.BOTH, expand=True)
        self.gerenciador = gerenciador
        self.categorias = [c.nome for c in Categoria.listar_padroes()]

        self._construir_ui()
        self._atualizar_lista()

    def _construir_ui(self):
        """
        Constrói todos os elementos visuais da tela.
        TODO: Implementar com os widgets abaixo:

        1. Frame superior: título + saldo atual (Label grande, verde se positivo, vermelho se negativo)
        2. Frame formulário:
           - Entry: descrição
           - Entry: valor
           - OptionMenu: categoria (usar self.categorias)
           - OptionMenu: tipo (Receita / Despesa)
           - Entry ou DateEntry: data (pode usar string 'AAAA-MM-DD')
           - Button: Adicionar
        3. Frame filtros:
           - OptionMenu: filtrar por tipo
           - OptionMenu: filtrar por categoria
           - Button: Aplicar Filtro
        4. Listbox ou Treeview: exibir transações
        5. Button: Remover selecionado
        """
        # TODO: Implementar
        pass

    def _adicionar_transacao(self):
        """
        Lê os campos do formulário e chama o gerenciador.
        TODO: Implementar com try/except para tratar erros de validação.
        Após adicionar, limpar campos e chamar self._atualizar_lista().
        """
        # TODO: Implementar
        pass

    def _remover_transacao(self):
        """
        Remove a transação selecionada na lista.
        TODO: Implementar pegando o índice selecionado no Listbox/Treeview.
        """
        # TODO: Implementar
        pass

    def _atualizar_lista(self):
        """
        Recarrega a lista de transações na tela.
        TODO: Implementar limpando e repopulando o Listbox/Treeview.
        Também atualizar o Label do saldo.
        """
        # TODO: Implementar
        pass

    def _aplicar_filtro(self):
        """
        Filtra a lista conforme os OptionMenus de filtro.
        TODO: Chamar self.gerenciador.listar_transacoes() com os parâmetros.
        """
        # TODO: Implementar
        pass
