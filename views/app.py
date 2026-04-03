# =============================================================================
# views/app.py
# -----------------------------------------------------------------------------
# Janela principal da aplicação. É o ponto de entrada da interface gráfica.
#
# Esta classe herda de tk.Tk, que é a janela raiz do tkinter.
# Ela é responsável por:
#   - Criar e configurar a janela principal
#   - Instanciar o Gerenciador (compartilhado entre todas as telas)
#   - Carregar os dados salvos ao iniciar
#   - Construir a sidebar (menu lateral) e a área principal
#   - Controlar a navegação entre telas (trocar o conteúdo da área principal)
#   - Salvar os dados automaticamente ao fechar a janela
#
# Padrão de navegação utilizado:
#   Ao clicar em um botão da sidebar, a área principal é limpa e a
#   nova tela é instanciada dentro dela. Isso evita múltiplas janelas.
#
# Conceitos demonstrados neste arquivo:
#   - Herança com tkinter (class App(tk.Tk))
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

        # Instância central compartilhada entre todas as telas
        self.gerenciador = Gerenciador()
        self._carregar_dados()

        self._construir_sidebar()
        self._construir_area_principal()

        # Tela inicial ao abrir
        self.mostrar_tela("transacoes")

        # Garante que os dados são salvos ao fechar a janela
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    def _carregar_dados(self):
        """Carrega os dados salvos ao iniciar."""
        transacoes, metas = Persistencia.carregar()
        self.gerenciador.carregar_transacoes(transacoes)
        self.gerenciador.carregar_metas(metas)

    def _construir_sidebar(self):
        """
        Cria o menu lateral com botões de navegação.
        TODO: Implementar sidebar com botões:
          - 💰 Transações  → self.mostrar_tela("transacoes")
          - 🎯 Metas       → self.mostrar_tela("metas")
          - 📊 Relatórios  → self.mostrar_tela("relatorio")
        Dica: use tk.Frame com bg="#181825" para o sidebar
        """
        # TODO: Implementar
        pass

    def _construir_area_principal(self):
        """
        Cria o frame central onde as telas são renderizadas.
        TODO: Criar self.frame_principal com tk.Frame
        Dica: use pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        """
        # TODO: Implementar
        pass

    def mostrar_tela(self, nome: str):
        """
        Troca a tela exibida na área principal.

        Args:
            nome: 'transacoes', 'metas' ou 'relatorio'.
        """
        # TODO: Implementar
        # Dica: destrua os widgets filhos de self.frame_principal com winfo_children()
        # Depois instancie a tela correta passando self.frame_principal e self.gerenciador
        pass

    def _ao_fechar(self):
        """Salva os dados e fecha a aplicação."""
        Persistencia.salvar(
            self.gerenciador.get_transacoes(),
            self.gerenciador.get_metas()
        )
        self.destroy()
