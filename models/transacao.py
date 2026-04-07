from datetime import date


class Transacao:
    """
    Classe base para qualquer movimentação financeira.

    Toda transação tem: descrição, valor, categoria e data.
    Os atributos são privados (começam com _) para proteger os dados
    e garantir que só sejam alterados de forma controlada.
    """

    def __init__(self, descricao: str, valor: float, categoria: str, data: date):
        """
        Cria uma nova transação já validando os dados recebidos.
        Se algo estiver errado, lança um ValueError explicando o problema.
        """

        # Não faz sentido ter uma transação sem saber o que é
        if not descricao or not descricao.strip():
            raise ValueError("A descrição não pode ficar em branco.")

        # Valor negativo ou zero não representa uma movimentação real
        if valor <= 0:
            raise ValueError("O valor precisa ser maior que zero.")

        # Toda transação precisa ter uma categoria pra gente conseguir filtrar depois
        if not categoria or not categoria.strip():
            raise ValueError("A categoria não pode ficar em branco.")

        # Garante que a data seja realmente um objeto date do Python
        if not isinstance(data, date):
            raise ValueError("A data precisa ser um objeto do tipo date.")

        # Salva os dados já limpos (sem espaços extras nas pontas)
        self._descricao = descricao.strip()
        self._valor = valor
        self._categoria = categoria.strip()
        self._data = data

    # Propriedades — forma de acessar os dados sem expor os atributos direto

    @property
    def descricao(self) -> str:
        return self._descricao

    @property
    def valor(self) -> float:
        return self._valor

    @property
    def categoria(self) -> str:
        return self._categoria

    @property
    def data(self) -> date:
        return self._data

    # Esse método precisa ser implementado por Receita e Despesa.
    # Aqui ele só avisa que a subclasse esqueceu de fazer isso.

    def tipo(self) -> str:
        """Retorna o tipo da transação. Cada subclasse define o seu."""
        raise NotImplementedError("Cada subclasse precisa definir o método tipo().")

    # Como a transação aparece quando a gente dá print nela

    def __str__(self) -> str:
        return (
            f"[{self.tipo()}] {self._descricao} | "
            f"R$ {self._valor:.2f} | "
            f"{self._categoria} | "
            f"{self._data.isoformat()}"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"descricao={self._descricao!r}, "
            f"valor={self._valor}, "
            f"categoria={self._categoria!r}, "
            f"data={self._data.isoformat()!r})"
        )

# Receita — representa dinheiro entrando (ex: salário, freelance)

class Receita(Transacao):
    """
    Herda tudo de Transacao e só define que o tipo é 'Receita'.
    Simples assim — a herança já faz o trabalho pesado.
    """

    def tipo(self) -> str:
        return "Receita"


# Despesa — representa dinheiro saindo (ex: aluguel, mercado)

class Despesa(Transacao):
    """
    Igual à Receita, mas identifica a transação como 'Despesa'.
    O saldo do sistema vai usar essa distinção pra calcular tudo certo.
    """

    def tipo(self) -> str:
        return "Despesa"
