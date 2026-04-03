# =============================================================================
# views/tela_metas.py
# -----------------------------------------------------------------------------
# Tela de gerenciamento de metas de economia.
#
# Responsabilidades:
#   - Formulário para criar uma nova meta (descrição, valor alvo, prazo)
#   - Exibir lista de metas com barra de progresso visual (ttk.Progressbar)
#   - Mostrar status de cada meta: em andamento / concluída / atrasada
#   - Botão para depositar valor em uma meta específica
#   - Botão para remover uma meta
#
# Conceitos demonstrados neste arquivo:
#   - ttk.Progressbar para barra de progresso
#   - tk.Toplevel para abrir uma janela secundária (popup de depósito)
#   - Criação dinâmica de widgets em loop (um card por meta)
#   - lambda com argumento para passar o índice correto a cada botão:
#     command=lambda i=indice: self._depositar(i)
#     (sem o i=indice, todos os botões usariam o último valor de 'indice')
#
# RESPONSÁVEL: Pessoa 7
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from services import Gerenciador


class TelaMetas(tk.Frame):
    """Tela de gerenciamento de metas de economia."""

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
           - Entry: valor alvo (R$)
           - Entry: prazo (AAAA-MM-DD)
           - Button: 'Criar Meta' → chama self._criar_meta()

        2. Frame scrollável para a lista de metas:
           - Para cada meta, criar um 'card' com:
             * Label: descrição e prazo
             * ttk.Progressbar: percentual concluído
             * Label: 'R$ X,XX / R$ Y,YY'
             * Label: status (colorido conforme o status)
             * Button: 'Depositar' → self._depositar(indice)
             * Button: 'Remover'   → self._remover_meta(indice)
        """
        # TODO: Implementar
        pass

    def _criar_meta(self):
        """
        Lê os campos e chama self.gerenciador.adicionar_meta().
        TODO: Tratar ValueError com messagebox.showerror().
        Converter a string de prazo com date.fromisoformat().
        """
        # TODO: Implementar
        pass

    def _depositar(self, indice: int):
        """
        Abre uma janela secundária (tk.Toplevel) para o usuário
        informar o valor do depósito.
        TODO: Ao confirmar, chamar meta.depositar(valor) e
        self._atualizar_lista().
        """
        # TODO: Implementar
        pass

    def _remover_meta(self, indice: int):
        """
        Remove a meta pelo índice.
        TODO: Chamar self.gerenciador.remover_meta(indice)
        e self._atualizar_lista().
        """
        # TODO: Implementar
        pass

    def _atualizar_lista(self):
        """
        Recria todos os cards de metas na tela.
        TODO: Destruir os cards existentes e recriar a partir de
        self.gerenciador.listar_metas().
        """
        # TODO: Implementar
        pass
