
# Categorias que já vêm prontas no sistema — o usuário pode escolher uma dessas
CATEGORIAS_PADRAO = [
    "Alimentação",
    "Moradia",
    "Transporte",
    "Saúde",
    "Educação",
    "Lazer",
    "Vestuário",
    "Salário",
    "Investimento",
    "Outros",
]


class Categoria:
    """
    Representa uma categoria usada pra classificar as transações.

    O nome é armazenado de forma privada e sempre capitalizado
    (primeira letra maiúscula) pra manter um padrão visual.
    """

    # Limite máximo de caracteres que um nome de categoria pode ter
    TAMANHO_MAXIMO = 50

    def __init__(self, nome: str):
        """
        Cria uma categoria validando o nome recebido.
        Se o nome for inválido, lança um ValueError com uma mensagem clara.
        """
        self._nome = self._validar_nome(nome)
    
    # Validação do nome — centralizada aqui pra não repetir em vários lugares
   
    @staticmethod
    def _validar_nome(nome: str) -> str:
        """
        Checa se o nome é válido e já devolve ele normalizado.
        Usamos @staticmethod porque essa função não depende de nenhum
        atributo do objeto — ela só processa o texto recebido.
        """

        if not isinstance(nome, str):
            raise ValueError("O nome da categoria precisa ser um texto.")

        nome = nome.strip()  # remove espaços desnecessários nas pontas

        if not nome:
            raise ValueError("O nome da categoria não pode ficar em branco.")

        if len(nome) > Categoria.TAMANHO_MAXIMO:
            raise ValueError(
                f"Nome muito longo. O máximo é {Categoria.TAMANHO_MAXIMO} caracteres."
            )

        # Só letras e espaços são aceitos — números e símbolos não fazem sentido aqui
        if not all(c.isalpha() or c.isspace() for c in nome):
            raise ValueError(
                "O nome da categoria só pode ter letras e espaços."
            )

        # capitalize() deixa a primeira letra maiúscula e o resto minúsculo
        return nome.capitalize()

    # Propriedade — acesso controlado ao nome

    @property
    def nome(self) -> str:
        """Retorna o nome da categoria."""
        return self._nome

    # Métodos especiais — deixam a classe mais útil no dia a dia do código

    def __eq__(self, other: object) -> bool:
        """
        Compara duas categorias pelo nome, ignorando maiúsculas/minúsculas.
        Assim 'alimentação' e 'Alimentação' são consideradas iguais.
        """
        if isinstance(other, Categoria):
            return self._nome.lower() == other._nome.lower()
        return False

    def __hash__(self) -> int:
        """
        Necessário porque sobrescrevemos __eq__.
        Permite usar Categoria como chave em dicionários — o relatorio.py vai precisar disso.
        """
        return hash(self._nome.lower())

    def __str__(self) -> str:
        """Quando der print na categoria, mostra só o nome."""
        return self._nome

    def __repr__(self) -> str:
        return f"Categoria(nome={self._nome!r})"

    # Método utilitário — gera a lista de categorias padrão já prontas

    @classmethod
    def listar_categorias_padrao(cls) -> list["Categoria"]:
        """
        Retorna os objetos Categoria das categorias padrão do sistema.
        Útil pra popular dropdowns na interface sem precisar criar na mão.
        """
        return [cls(nome) for nome in CATEGORIAS_PADRAO]
