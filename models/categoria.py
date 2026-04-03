class Categoria:
    """
    Representa uma categoria de transação.

    Atributos:
        _nome (str): Nome da categoria.
        _icone (str): Emoji representando a categoria.
    """

    CATEGORIAS_PADRAO = [
        ("Alimentação", "🍔"),
        ("Transporte", "🚗"),
        ("Saúde", "💊"),
        ("Educação", "📚"),
        ("Lazer", "🎮"),
        ("Moradia", "🏠"),
        ("Salário", "💼"),
        ("Outros", "📦"),
    ]

    def __init__(self, nome: str, icone: str = "📦"):
        """
        Inicializa uma Categoria.

        Args:
            nome: Nome da categoria.
            icone: Emoji da categoria.

        Raises:
            ValueError: Se o nome estiver vazio.
        """
        # TODO: Implementar validações e atribuições
        pass

    @property
    def nome(self) -> str:
        """Retorna o nome da categoria."""
        # TODO: Implementar
        pass

    @property
    def icone(self) -> str:
        """Retorna o ícone da categoria."""
        # TODO: Implementar
        pass

    @classmethod
    def listar_padroes(cls) -> list:
        """
        Retorna lista de objetos Categoria com as categorias padrão.

        Returns:
            Lista de objetos Categoria.
        """
        # TODO: Implementar usando CATEGORIAS_PADRAO
        pass

    def __str__(self) -> str:
        """Representação em string: 'icone nome'."""
        # TODO: Implementar
        pass
