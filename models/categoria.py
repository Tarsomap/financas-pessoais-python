# models/categoria.py
# RESPONSÁVEL: Pessoa 2

class Categoria:
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
        if not nome or not nome.strip():
            raise ValueError("O nome da categoria não pode ser vazio.")
        self._nome = nome.strip()
        self._icone = icone

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def icone(self) -> str:
        return self._icone

    @classmethod
    def listar_padroes(cls) -> list:
        return [cls(nome, icone) for nome, icone in cls.CATEGORIAS_PADRAO]

    def __str__(self) -> str:
        return f"{self._icone} {self._nome}"