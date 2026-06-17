# =============================================================================
# models/categoria.py
# -----------------------------------------------------------------------------
# Define a classe Categoria, que representa uma classificação para transações
# financeiras (ex.: Alimentação, Transporte, Salário).
#
# CONCEITOS APLICADOS:
#   - Encapsulamento: atributos _nome e _icone são privados, acessados
#     somente via @property (somente leitura). Isso impede que código externo
#     altere o nome de uma categoria já criada — se precisar mudar, cria outra.
#   - Classmethod (@classmethod): listar_padroes() é um método da CLASSE,
#     não de uma instância. Pode ser chamado sem criar um objeto antes:
#     Categoria.listar_padroes(). Útil para fornecer uma lista pré-definida
#     de categorias sem depender de banco de dados.
#   - Validação no construtor: impede a criação de categorias com nome vazio,
#     garantindo que todo objeto Categoria é válido desde o nascimento.
#
# RESPONSÁVEL: Pessoa 2 (João Gustavo Lima dos Santos)
# =============================================================================


class Categoria:
    """
    Representa uma categoria de transação financeira com nome e ícone.

    Cada transação (Receita ou Despesa) pode ter uma Categoria associada.
    A classe oferece um conjunto de categorias padrão via listar_padroes(),
    mas o usuário pode criar categorias personalizadas passando nome e ícone.
    """

    # Lista de tuplas (nome, ícone) com as categorias que vêm de fábrica.
    # É um atributo de CLASSE (compartilhado por todas as instâncias),
    # não de instância — por isso fica fora do __init__.
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
        Inicializa uma categoria com validação do nome.

        Parâmetros:
            nome  (str) : texto identificador da categoria (não pode ser vazio)
            icone (str) : emoji representativo; padrão "📦" se não informado

        Lança:
            ValueError se o nome for vazio ou apenas espaços em branco.
        """
        if not nome or not nome.strip():
            raise ValueError("O nome da categoria não pode ser vazio.")

        # strip() remove espaços em branco nas extremidades, evitando
        # que " Alimentação " e "Alimentação" sejam tratados como diferentes.
        self._nome = nome.strip()
        self._icone = icone

    # -------------------------------------------------------------------------
    # Propriedades — encapsulamento com acesso somente leitura
    # -------------------------------------------------------------------------

    @property
    def nome(self) -> str:
        """Nome textual da categoria (ex.: 'Alimentação')."""
        return self._nome

    @property
    def icone(self) -> str:
        """Emoji associado à categoria (ex.: '🍔')."""
        return self._icone

    # -------------------------------------------------------------------------
    # Métodos de classe e de instância
    # -------------------------------------------------------------------------

    @classmethod
    def listar_padroes(cls) -> list:
        """
        Cria e devolve uma lista de objetos Categoria a partir das padrão.

        Usa @classmethod porque não depende de nenhuma instância — é uma
        operação da classe inteira. 'cls' é a própria classe Categoria,
        permitindo que subclasses (se existirem) herdem este comportamento.

        Retorna:
            Lista de objetos Categoria com nome e ícone pré-definidos.
        """
        return [cls(nome, icone) for nome, icone in cls.CATEGORIAS_PADRAO]

    def __str__(self) -> str:
        """
        Representação legível para exibição na interface.

        Python chama __str__ automaticamente quando usamos str(obj) ou
        print(obj). Aqui montamos "🍔 Alimentação" para exibir bonito.
        """
        return f"{self._icone} {self._nome}"
