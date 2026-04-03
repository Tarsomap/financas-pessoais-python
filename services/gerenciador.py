from datetime import date
from models import Transacao, Receita, Despesa, Meta


class Gerenciador:
    """
    Gerencia todas as transações e metas do sistema.
    É a classe central de lógica de negócio.

    Atributos:
        _transacoes (list): Lista de todas as transações.
        _metas (list): Lista de todas as metas.
    """

    def __init__(self):
        """Inicializa o gerenciador com listas vazias."""
        self._transacoes = []
        self._metas = []

    # ── Transações ─────────────────────────────────────────────────────

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

        Args:
            indice: Posição na lista (começa em 0).

        Returns:
            A transação removida.

        Raises:
            IndexError: Se o índice for inválido.
        """
        # TODO: Implementar
        pass

    def listar_transacoes(self, tipo: str = None, categoria: str = None, mes: int = None, ano: int = None) -> list:
        """
        Retorna transações filtradas pelos parâmetros fornecidos.

        Args:
            tipo: 'receita' ou 'despesa'. None retorna todos.
            categoria: Filtra por categoria. None retorna todos.
            mes: Filtra por mês (1-12). None retorna todos.
            ano: Filtra por ano. None retorna todos.

        Returns:
            Lista de transações que atendem aos filtros.
        """
        # TODO: Implementar usando list comprehension
        # Dica: use t.tipo() para verificar o tipo
        pass

    def saldo_atual(self) -> float:
        """
        Calcula o saldo atual (total receitas - total despesas).

        Returns:
            Saldo como float.
        """
        # TODO: Implementar
        pass

    # ── Metas ───────────────────────────────────────────────────────────

    def adicionar_meta(self, descricao: str, valor_alvo: float, prazo: date) -> Meta:
        """
        Cria e adiciona uma Meta.

        Returns:
            O objeto Meta criado.
        """
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
        """Retorna todas as metas."""
        return self._metas.copy()

    # ── Dados brutos (usados pela Persistência) ─────────────────────────

    def get_transacoes(self) -> list:
        """Retorna a lista interna de transações."""
        return self._transacoes

    def get_metas(self) -> list:
        """Retorna a lista interna de metas."""
        return self._metas

    def carregar_transacoes(self, transacoes: list) -> None:
        """Substitui a lista de transações (usado ao carregar do arquivo)."""
        self._transacoes = transacoes

    def carregar_metas(self, metas: list) -> None:
        """Substitui a lista de metas (usado ao carregar do arquivo)."""
        self._metas = metas
