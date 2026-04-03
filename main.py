# =============================================================================
# main.py
# -----------------------------------------------------------------------------
# Ponto de entrada da aplicação.
# Este arquivo é o primeiro a ser executado quando o programa inicia.
# Ele importa a classe App (janela principal) e chama o método mainloop(),
# que é o loop de eventos do tkinter — mantém a janela aberta esperando
# interações do usuário até que ela seja fechada.
#
# RESPONSÁVEL: Pessoa 1 (Coordenador)
# =============================================================================

from views.app import App


def main():
    """Ponto de entrada da aplicação."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
