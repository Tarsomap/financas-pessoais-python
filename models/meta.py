from datetime import date


class Meta:
    """
    Representa uma meta de economia.

    Atributos:
        _descricao (str): O que se deseja alcançar.
        _valor_alvo (float): Valor a ser economizado.
        _valor_atual (float): Quanto já foi economizado.
        _prazo (date): Data limite para a meta.
    """

    def __init__(self, descricao: str, valor_alvo: float, prazo: date):
        """
        Inicializa uma Meta.

        Args:
            descricao: Descrição da meta.
            valor_alvo: Valor total a atingir (deve ser > 0).
            prazo: Data limite.

        Raises:
            ValueError: Se o valor_alvo for <= 0.
            ValueError: Se o prazo for uma data no passado.
        """
        # TODO: Implementar validações e atribuições
        # Dica: self._valor_atual começa em 0.0
        pass

    @property
    def descricao(self) -> str:
        # TODO: Implementar
        pass

    @property
    def valor_alvo(self) -> float:
        # TODO: Implementar
        pass

    @property
    def valor_atual(self) -> float:
        # TODO: Implementar
        pass

    @property
    def prazo(self) -> date:
        # TODO: Implementar
        pass

    def depositar(self, valor: float) -> None:
        """
        Adiciona valor ao progresso da meta.

        Args:
            valor: Valor a depositar (deve ser > 0).

        Raises:
            ValueError: Se o valor for <= 0.
        """
        # TODO: Implementar
        # Dica: não deixar ultrapassar o valor_alvo
        pass

    def percentual_concluido(self) -> float:
        """
        Calcula o percentual de conclusão da meta.

        Returns:
            Valor entre 0.0 e 100.0.
        """
        # TODO: Implementar
        pass

    def esta_concluida(self) -> bool:
        """
        Verifica se a meta foi atingida.

        Returns:
            True se valor_atual >= valor_alvo.
        """
        # TODO: Implementar
        pass

    def esta_atrasada(self) -> bool:
        """
        Verifica se a meta está atrasada (prazo passou e não foi concluída).

        Returns:
            True se prazo < hoje e não está concluída.
        """
        # TODO: Implementar
        pass

    def status(self) -> str:
        """
        Retorna o status da meta como string.

        Returns:
            'concluída', 'atrasada' ou 'em andamento'.
        """
        # TODO: Implementar usando esta_concluida() e esta_atrasada()
        pass

    def para_dict(self) -> dict:
        """Converte a meta para dicionário (usado na persistência)."""
        # TODO: Implementar
        pass

    def __str__(self) -> str:
        """Representação em string da meta."""
        # TODO: Implementar
        pass
