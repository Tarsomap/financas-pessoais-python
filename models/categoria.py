# =============================================================================
# models/categoria.py
# -----------------------------------------------------------------------------
# Define a classe Categoria, que representa uma classificação para
# agrupar transações do mesmo tipo (ex: Alimentação, Transporte, Saúde).
#
# Conceitos demonstrados neste arquivo:
#   - Atributo de classe (CATEGORIAS_PADRAO): pertence à classe, não a
#     cada objeto. É compartilhado por todas as instâncias.
#   - @classmethod (listar_padroes): método que pertence à classe, não
#     a uma instância específica. Recebe 'cls' em vez de 'self'.
#     Usado aqui para criar objetos Categoria a partir da lista padrão.
#
# RESPONSÁVEL: João Gustavo
# =============================================================================

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
        Método de classe que retorna uma lista de objetos Categoria
        criados a partir de CATEGORIAS_PADRAO.

        Returns:
            Lista de objetos Categoria.
        """
        # TODO: Implementar
        # Dica: [Categoria(nome, icone) for nome, icone in cls.CATEGORIAS_PADRAO]
        pass

    def __str__(self) -> str:
        """Representação em string: 'icone nome'."""
        # TODO: Implementar
        pass
