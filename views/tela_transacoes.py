# =============================================================================
# views/tela_transacoes.py
# -----------------------------------------------------------------------------
# Tela de gerenciamento de receitas e despesas.
# É a tela principal do sistema, exibida ao abrir o programa.
#
# Exibe:
#   - Saldo atual em destaque (verde se positivo, vermelho se negativo)
#   - Formulário para adicionar receita ou despesa
#   - Tabela (Treeview) com todas as transações
#   - Filtros por tipo e categoria
#   - Botão para remover a transação selecionada
#
# Conceitos demonstrados:
#   - Herança: class TelaTransacoes(tk.Frame)
#   - try/except para capturar ValueError e exibir com messagebox
#   - StringVar: variável reativa do tkinter ligada a widgets
#   - ttk.Treeview: tabela com colunas e linhas
#   - OptionMenu: lista de seleção suspensa
#
# RESPONSÁVEL: Lívia Unit Rodrigues
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
        TODO: Implementar widgets:
        1. Label saldo (verde/vermelho)
        2. Formulário: Entry descrição, Entry valor, OptionMenu categoria,
           OptionMenu tipo (Receita/Despesa), Entry data, Button Adicionar
        3. Filtros: OptionMenu tipo, OptionMenu categoria, Button Filtrar
        4. ttk.Treeview: colunas Tipo | Descrição | Valor | Categoria | Data
        5. Button Remover selecionado
        """
        # TODO: Implementar
        pass

    def _adicionar_transacao(self):
        """
        TODO: Ler campos, chamar gerenciador.adicionar_receita() ou
        adicionar_despesa(). Usar try/except para ValueError.
        """
        # TODO: Implementar
        pass

    def _remover_transacao(self):
        """TODO: Pegar índice selecionado na Treeview e chamar remover_transacao()."""
        # TODO: Implementar
        pass

    def _atualizar_lista(self):
        """TODO: Limpar Treeview, repopular e atualizar Label do saldo."""
        # TODO: Implementar
        pass

    def _aplicar_filtro(self):
        """TODO: Chamar listar_transacoes(tipo=..., categoria=...) e repopular Treeview."""
        # TODO: Implementar
        pass
