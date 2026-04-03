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
    Herda de Transacao.
    """

    def tipo(self) -> str:
        """Retorna o tipo da transação."""
        return "receita"


class Despesa(Transacao):
    """
    Representa uma saída de dinheiro.
    Herda de Transacao.
    """

    def tipo(self) -> str:
        """Retorna o tipo da transação."""
        return "despesa"
