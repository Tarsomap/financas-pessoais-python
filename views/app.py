# =============================================================================
# views/app.py
# -----------------------------------------------------------------------------
# Janela principal da aplicação. Ponto de entrada da interface gráfica.
#
# Herda de tk.Tk (janela raiz do tkinter) e é responsável por:
#   - Criar e configurar a janela principal
#   - Instanciar o Gerenciador compartilhado entre todas as telas
#   - Carregar dados salvos ao iniciar
#   - Construir a sidebar (menu lateral) e a área principal
#   - Controlar a navegação entre telas
#   - Salvar dados automaticamente ao fechar
#
# Conceitos demonstrados:
#   - Herança com tkinter: class App(tk.Tk)
#   - super().__init__() para inicializar a classe pai
#   - protocol() para capturar o evento de fechar a janela
#   - Composição: App contém instâncias de outras classes
#
# RESPONSÁVEL: Pessoa 6
# =============================================================================

import tkinter as tk
from tkinter import ttk
from services import Gerenciador, Persistencia
from views.tela_transacoes import TelaTransacoes
from views.tela_metas import TelaMetas
from views.tela_relatorio import TelaRelatorio


class App(tk.Tk):
    """Janela principal da aplicação."""

    def __init__(self):
        super().__init__()
        self.title("💸 Finanças Pessoais")
        self.geometry("900x600")
        self.resizable(True, True)
        self.configure(bg="#1e1e2e")

        self.gerenciador = Gerenciador()
        self._carregar_dados()
        self._construir_sidebar()
        self._construir_area_principal()
        self.mostrar_tela("transacoes")
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    def _carregar_dados(self):
        transacoes, metas = Persistencia.carregar()
        self.gerenciador.carregar_transacoes(transacoes)
        self.gerenciador.carregar_metas(metas)

    def _construir_sidebar(self):
        """
        Cria o menu lateral.
        TODO: Botões:
          - 💰 Transações  → self.mostrar_tela('transacoes')
          - 🎯 Metas       → self.mostrar_tela('metas')
          - 📊 Relatórios  → self.mostrar_tela('relatorio')
        """
        # TODO: Implementar
        pass

    def _construir_area_principal(self):
        """
        Cria o frame central onde as telas são renderizadas.
        TODO: self.frame_principal = tk.Frame(...)
        """
        # TODO: Implementar
        pass

    def mostrar_tela(self, nome: str):
        """
        Troca a tela na área principal.
        TODO: Destruir filhos de self.frame_principal e instanciar a tela correta.
        """
        # TODO: Implementar
        pass

    def _ao_fechar(self):
        Persistencia.salvar(self.gerenciador.get_transacoes(), self.gerenciador.get_metas())
        self.destroy()
