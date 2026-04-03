# =============================================================================
# views/tela_transacoes.py
# -----------------------------------------------------------------------------
# Tela de gerenciamento de receitas e despesas.
# É a tela principal do sistema — a primeira exibida ao abrir o programa.
#
# Responsabilidades:
#   - Exibir o saldo atual em destaque (verde se positivo, vermelho se negativo)
#   - Formulário para adicionar nova receita ou despesa
#   - Lista de todas as transações cadastradas
#   - Filtros por tipo (receita/despesa) e categoria
#   - Botão para remover a transação selecionada
#
# Como essa tela se comunica com a lógica de negócio:
#   Ela recebe uma instância do Gerenciador no __init__ e chama
#   seus métodos (adicionar_receita, adicionar_despesa, etc.).
#   A tela NUNCA cria objetos Transacao diretamente — isso é papel do Gerenciador.
#
# Conceitos demonstrados neste arquivo:
#   - Herança com tkinter (class TelaTransacoes(tk.Frame))
#   - try/except para capturar erros de validação e exibir com messagebox
#   - StringVar e DoubleVar: variáveis reativas do tkinter
#   - ttk.Treeview para exibir dados em formato de tabela
#   - OptionMenu para listas de seleção
#
# RESPONSÁVEL: Pessoa 6
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from services import Gerenciador
from models import Categoria


class TelaTransacoes(tk.Frame):
    """Tela de gerenciamento de receitas e despesas."""

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
        TODO: Implementar com os widgets:

        1. Frame superior: título + saldo atual
           - Label grande mostrando o saldo
           - Verde (#a6e3a1) se positivo, vermelho (#f38ba8) se negativo

        2. Frame formulário:
           - Entry: descrição
           - Entry: valor (aceitar número)
           - OptionMenu: categoria (usar self.categorias)
           - OptionMenu: tipo ('Receita' / 'Despesa')
           - Entry: data no formato AAAA-MM-DD
           - Button: 'Adicionar' → chama self._adicionar_transacao()

        3. Frame filtros:
           - OptionMenu: filtrar por tipo
           - OptionMenu: filtrar por categoria
           - Button: 'Filtrar' → chama self._aplicar_filtro()
           - Button: 'Limpar filtro' → chama self._atualizar_lista()

        4. ttk.Treeview: colunas Tipo | Descrição | Valor | Categoria | Data

        5. Button: 'Remover selecionado' → chama self._remover_transacao()
        """
        # TODO: Implementar
        pass

    def _adicionar_transacao(self):
        """
        Lê os campos do formulário e chama o método correto do Gerenciador.
        TODO: Implementar com try/except.
        - Se tipo == 'Receita': self.gerenciador.adicionar_receita(...)
        - Se tipo == 'Despesa': self.gerenciador.adicionar_despesa(...)
        - Em caso de ValueError: messagebox.showerror(...)
        - Ao final: limpar campos e chamar self._atualizar_lista()
        """
        # TODO: Implementar
        pass

    def _remover_transacao(self):
        """
        Remove a transação selecionada na Treeview.
        TODO: Pegar o índice selecionado, chamar self.gerenciador.remover_transacao(indice)
        e chamar self._atualizar_lista().
        """
        # TODO: Implementar
        pass

    def _atualizar_lista(self):
        """
        Recarrega a Treeview e o Label do saldo.
        TODO: Limpar a Treeview e repopular com self.gerenciador.listar_transacoes().
        Atualizar também o texto e cor do Label de saldo.
        """
        # TODO: Implementar
        pass

    def _aplicar_filtro(self):
        """
        Filtra a lista conforme os OptionMenus.
        TODO: Chamar self.gerenciador.listar_transacoes(tipo=..., categoria=...)
        e repopular a Treeview com o resultado.
        """
        # TODO: Implementar
        pass
