# =============================================================================
# views/tela_metas.py
# -----------------------------------------------------------------------------
# Tela de gerenciamento de metas de economia.
#
# Exibe:
#   - Formulário para criar nova meta
#   - Cards de metas com barra de progresso (ttk.Progressbar)
#   - Status colorido: em andamento / concluída / atrasada
#   - Botão Depositar (abre janela popup tk.Toplevel)
#   - Botão Remover
#
# Conceitos demonstrados:
#   - ttk.Progressbar para visualizar progresso
#   - tk.Toplevel para janela secundária (popup)
#   - Criação dinâmica de widgets em loop
#   - lambda com argumento fixo para evitar closure incorreta:
#     command=lambda i=indice: self._depositar(i)
#     (sem o i=indice, todos os botões usariam o último valor do loop)
#
# RESPONSÁVEL: Alice
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
        TODO:
        1. Frame formulário: Entry descrição, Entry valor alvo,
           Entry prazo (AAAA-MM-DD), Button Criar Meta
        2. Frame scrollável com cards de metas:
           - Label descrição + prazo
           - ttk.Progressbar com percentual_concluido()
           - Label 'R$ atual / R$ alvo'
           - Label status (colorido)
           - Button Depositar, Button Remover
        """
        # TODO: Implementar
        pass

    def _criar_meta(self):
        """
        TODO: Ler campos, converter prazo com date.fromisoformat(),
        chamar gerenciador.adicionar_meta(). Tratar ValueError.
        """
        # TODO: Implementar
        pass

    def _depositar(self, indice: int):
        """
        TODO: Abrir tk.Toplevel pedindo valor do depósito.
        Chamar meta.depositar(valor) e _atualizar_lista().
        """
        # TODO: Implementar
        pass

    def _remover_meta(self, indice: int):
        """TODO: Chamar gerenciador.remover_meta(indice) e _atualizar_lista()."""
        # TODO: Implementar
        pass

    def _atualizar_lista(self):
        """TODO: Destruir cards existentes e recriar a partir de listar_metas()."""
        # TODO: Implementar
        pass
