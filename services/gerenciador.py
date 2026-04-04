# =============================================================================
# services/gerenciador.py
# -----------------------------------------------------------------------------
# Classe central de lógica de negócio da aplicação.
# O Gerenciador é o único ponto de contato entre a interface gráfica
# (views) e os dados (models). Nenhuma tela deve criar ou modificar
# objetos Transacao ou Meta diretamente — tudo passa pelo Gerenciador.
#
# Responsabilidades:
#   - Criar e armazenar Receitas e Despesas
#   - Criar e armazenar Metas
#   - Remover transações e metas
#   - Filtrar transações por tipo, categoria, mês e ano
#   - Calcular o saldo atual
#
# Conceitos demonstrados neste arquivo:
#   - Encapsulamento: as listas _transacoes e _metas são privadas
#   - List comprehension: usada nos métodos de filtro
#   - Tratamento de exceções: IndexError ao remover índice inválido
#
# RESPONSÁVEL: Vinicius
# =============================================================================

from datetime import date
from models import Transacao, Receita, Despesa, Meta


class Gerenciador:
    """
    Gerencia todas as transações e metas do sistema.
    É a classe central de lógica de negócio.
    """

    def __init__(self):
        """Inicializa o gerenciador com listas vazias."""
        self._transacoes = []
        self._metas = []

    def adicionar_receita(self, descricao: str, valor: float, categoria: str, data: date = None) -> Receita:
        """
        Cria e adiciona uma Receita à lista de transações.

        Returns:
            O objeto Receita criado.
        """
        # TODO: Implementar
        pass

    def adicionar_despesa(self, descricao: str, valor: float, categoria: str, data: date = None) -> Despesa:
        """
        Cria e adiciona uma Despesa à lista de transações.

        Returns:
            O objeto Despesa criado.
        """
        # TODO: Implementar
        pass

    def remover_transacao(self, indice: int) -> Transacao:
        """
        Remove uma transação pelo índice.

        Raises:
            IndexError: Se o índice for inválido.
        """
        # TODO: Implementar
        pass

    def listar_transacoes(self, tipo: str = None, categoria: str = None, mes: int = None, ano: int = None) -> list:
        """
        Retorna transações filtradas pelos parâmetros fornecidos.
        Parâmetros não informados (None) não aplicam filtro.
        """
        # TODO: Implementar usando list comprehension
        pass

    def saldo_atual(self) -> float:
        """
        Calcula o saldo atual (total receitas - total despesas).
        """
        # TODO: Implementar
        pass

    def adicionar_meta(self, descricao: str, valor_alvo: float, prazo: date) -> Meta:
        """Cria e adiciona uma Meta."""
        # TODO: Implementar
        pass

    def remover_meta(self, indice: int) -> Meta:
        """
        Remove uma meta pelo índice.

        Raises:
            IndexError: Se o índice for inválido.
        """
        # TODO: Implementar
        pass

    def listar_metas(self) -> list:
        """Retorna cópia da lista de metas."""
        return self._metas.copy()

    def get_transacoes(self) -> list:
        return self._transacoes

    def get_metas(self) -> list:
        return self._metas

    def carregar_transacoes(self, transacoes: list) -> None:
        self._transacoes = transacoes

    def carregar_metas(self, metas: list) -> None:
        self._metas = metas
