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
# RESPONSÁVEL: Pessoa 3
# =============================================================================

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

    # ── Transações ──────────────────────────────────────────────────────────

    def adicionar_receita(self, descricao: str, valor: float, categoria: str, data: date = None) -> Receita:
        """
        Cria e adiciona uma Receita à lista de transações.

        Returns:
            O objeto Receita criado.
        """
        # TODO: Implementar
        # Dica: crie um objeto Receita e adicione em self._transacoes
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
        # Dica: valide o índice antes de remover para lançar IndexError claro
        pass

    def listar_transacoes(self, tipo: str = None, categoria: str = None, mes: int = None, ano: int = None) -> list:
        """
        Retorna transações filtradas pelos parâmetros fornecidos.
        Parâmetros não informados (None) não aplicam filtro.

        Args:
            tipo: 'receita' ou 'despesa'.
            categoria: Nome da categoria.
            mes: Número do mês (1-12).
            ano: Ano com 4 dígitos.

        Returns:
            Lista de transações que atendem a todos os filtros.
        """
        # TODO: Implementar usando list comprehension
        # Dica: comece com resultado = self._transacoes e vá filtrando
        pass

    def saldo_atual(self) -> float:
        """
        Calcula o saldo atual (total receitas - total despesas).

        Returns:
            Saldo como float.
        """
        # TODO: Implementar
        # Dica: use sum() com list comprehension para receitas e despesas
        pass

    # ── Metas ────────────────────────────────────────────────────────────────

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
        """Retorna cópia da lista de metas."""
        return self._metas.copy()

    # ── Dados brutos (usados pela Persistência) ──────────────────────────────

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
