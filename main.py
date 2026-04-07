# =============================================================================
# main.py
# -----------------------------------------------------------------------------
# Ponto de entrada da aplicacao de Financas Pessoais.
#
# Responsabilidades deste arquivo:
#   1. Criar o Gerenciador (servico central do sistema)
#   2. Carregar os dados salvos via Persistencia.carregar()
#   3. Iniciar o menu interativo (views/menu.py)
#   4. Salvar os dados ao encerrar via Persistencia.salvar()
#
# O padrao "if __name__ == '__main__'" garante que main() so seja chamada
# quando o arquivo for executado diretamente (python main.py), e nao quando
# for importado por outro modulo (como nos testes automaticos com pytest).
#
# RESPONSAVEL: Tarso Monteiro Alves Passos (Coordenador)
# =============================================================================

from services import Gerenciador
from services.persistencia import Persistencia
from views.menu import iniciar


def main():
    """
    Inicializa o sistema, carrega os dados e abre o menu principal.
    Ao retornar do menu (usuario escolheu sair), salva os dados no disco.
    """
    # 1. Cria o gerenciador (listas de transacoes e metas ainda vazias)
    gerenciador = Gerenciador()

    # 2. Carrega os dados persistidos de execucoes anteriores.
    #    Persistencia.carregar() retorna (lista_transacoes, lista_metas)
    transacoes, metas = Persistencia.carregar()
    gerenciador.carregar_transacoes(transacoes)
    gerenciador.carregar_metas(metas)

    # 3. Abre o menu interativo no terminal.
    #    A funcao iniciar() fica em loop ate o usuario escolher sair.
    iniciar(gerenciador)

    # 4. Salva os dados antes de encerrar o programa.
    Persistencia.salvar(
        gerenciador.get_transacoes(),
        gerenciador.get_metas()
    )


if __name__ == "__main__":
    # Ponto de entrada real do programa
    main()
