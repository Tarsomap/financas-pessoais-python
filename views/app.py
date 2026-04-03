import tkinter as tk
from tkinter import ttk
from services import Gerenciador, Persistencia
from views.tela_transacoes import TelaTransacoes
from views.tela_metas import TelaMetas
from views.tela_relatorio import TelaRelatorio


class App(tk.Tk):
    """
    Janela principal da aplicação.
    Gerencia a navegação entre as telas.
    """

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

        # Tela inicial
        self.mostrar_tela("transacoes")

        # Salvar ao fechar
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    def _carregar_dados(self):
        """Carrega os dados salvos ao iniciar."""
        transacoes, metas = Persistencia.carregar()
        self.gerenciador.carregar_transacoes(transacoes)
        self.gerenciador.carregar_metas(metas)

    def _construir_sidebar(self):
        """Cria o menu lateral com botões de navegação."""
        # TODO: Implementar sidebar com botões:
        # - 💰 Transações  → self.mostrar_tela("transacoes")
        # - 🎯 Metas       → self.mostrar_tela("metas")
        # - 📊 Relatórios  → self.mostrar_tela("relatorio")
        # Dica: use tk.Frame com bg="#181825" para o sidebar
        pass

    def _construir_area_principal(self):
        """Cria o frame central onde as telas são exibidas."""
        # TODO: Criar self.frame_principal com tk.Frame
        # Dica: use pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        pass

    def mostrar_tela(self, nome: str):
        """
        Troca a tela exibida na área principal.

        Args:
            nome: 'transacoes', 'metas' ou 'relatorio'.
        """
        # TODO: Implementar
        # Dica: destrua os widgets filhos de self.frame_principal
        # Depois instancie a tela correta passando self.gerenciador
        # TelaTransacoes(self.frame_principal, self.gerenciador)
        pass

    def _ao_fechar(self):
        """Salva os dados e fecha a aplicação."""
        Persistencia.salvar(
            self.gerenciador.get_transacoes(),
            self.gerenciador.get_metas()
        )
        self.destroy()
