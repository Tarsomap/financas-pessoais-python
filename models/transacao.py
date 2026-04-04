# =============================================================================
# models/transacao.py
# -----------------------------------------------------------------------------
# Define as classes que representam transações financeiras.
#
# Estrutura de herança utilizada:
#   Transacao (classe base / pai)
#   ├── Receita  (entrada de dinheiro, ex: salário, freelance)
#   └── Despesa  (saída de dinheiro, ex: mercado, aluguel)
#
# Por que usar herança aqui?
# Receita e Despesa compartilham os mesmos atributos (descrição, valor,
# categoria, data) e as mesmas validações. A diferença está apenas no
# tipo ('receita' ou 'despesa'). Com herança, evitamos repetição de código
# e demonstramos polimorfismo: o método tipo() retorna valores diferentes
# dependendo de qual subclasse está sendo usada.
#
# RESPONSÁVEL: João Gustavo
# =============================================================================

from datetime import date


class Transacao:
    """
    Classe base que representa uma transação financeira.

    Atributos:
        _descricao (str): Descrição da transação.
        _valor (float): Valor da transação (deve ser positivo).
        _categoria (str): Categoria da transação.
        _data (date): Data da transação.
    """

    def __init__(self, descricao: str, valor: float, categoria: str, data: date = None):
        """
        Inicializa uma Transacao.

        Args:
            descricao: Texto descrevendo a transação.
            valor: Valor monetário (deve ser > 0).
            categoria: Categoria da transação.
            data: Data da transação. Se None, usa a data de hoje.

        Raises:
            ValueError: Se o valor for menor ou igual a zero.
            ValueError: Se a descrição estiver vazia.
        """
        # TODO: Implementar validações e atribuições
        pass

    @property
    def descricao(self) -> str:
        """Retorna a descrição da transação."""
        # TODO: Implementar
        pass

    @property
    def valor(self) -> float:
        """Retorna o valor da transação."""
        # TODO: Implementar
        pass

    @property
    def categoria(self) -> str:
        """Retorna a categoria da transação."""
        # TODO: Implementar
        pass

    @property
    def data(self) -> date:
        """Retorna a data da transação."""
        # TODO: Implementar
        pass

    def para_dict(self) -> dict:
        """
        Converte a transação para dicionário (usado na persistência).

        Returns:
            Dicionário com os dados da transação.
        """
        # TODO: Implementar
        pass

    def __str__(self) -> str:
        """Representação em string da transação."""
        # TODO: Implementar
        pass


class Receita(Transacao):
    """
    Representa uma entrada de dinheiro.
    Herda todos os atributos e validações de Transacao.
    Sobrescreve apenas o método tipo().
    """

    def tipo(self) -> str:
        """Retorna o tipo da transação como string."""
        return "receita"


class Despesa(Transacao):
    """
    Representa uma saída de dinheiro.
    Herda todos os atributos e validações de Transacao.
    Sobrescreve apenas o método tipo().
    """

    def tipo(self) -> str:
        """Retorna o tipo da transação como string."""
        return "despesa"
