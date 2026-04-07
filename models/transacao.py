# =============================================================================
# models/transacao.py
# -----------------------------------------------------------------------------
# Define as classes de modelo para transações financeiras.
#
# CONCEITOS APLICADOS:
#   - Herança: Receita e Despesa herdam de Transacao (evita repetição de código)
#   - Polimorfismo: o método tipo() é sobrescrito em cada subclasse,
#     retornando "receita" ou "despesa" conforme o objeto real
#   - Encapsulamento: atributos com prefixo _ são privados;
#     acessados externamente apenas pelas @property
#   - Tratamento de exceções: ValueError com mensagem clara para dados inválidos
#   - datetime.date: data padrão calculada com date.today() na ausência de valor
#
# RESPONSÁVEL: Pessoa 2 (João Gustavo Lima dos Santos)
# =============================================================================

from datetime import date


class Transacao:
    """
    Classe base abstrata para transações financeiras.
    Não deve ser instanciada diretamente — use Receita ou Despesa.

    Receita e Despesa herdam todos os atributos e métodos desta classe,
    sobrescrevendo apenas o método tipo() — isso é polimorfismo.
    """

    def __init__(self, descricao: str, valor: float, categoria, data: date = None):
        """
        Inicializa uma transação com validação dos dados de entrada.

        Parâmetros:
            descricao (str)        : texto identificador (não pode ser vazio)
            valor     (float)      : valor positivo em reais (> 0)
            categoria (str ou obj) : categoria da transação;
                                     aceita string ou objeto com atributo .nome
            data      (date, opt)  : data da transação;
                                     se None, usa date.today() como padrão

        Lança:
            ValueError se descrição for vazia ou se valor for zero/negativo.
        """
        if not descricao or not descricao.strip():
            raise ValueError("A descrição não pode ser vazia.")
        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")

        self._descricao = descricao.strip()
        self._valor = float(valor)
        self._categoria = categoria
        # Se data não for informada, assume a data de hoje (datetime.date.today())
        self._data = data if data is not None else date.today()

    # -------------------------------------------------------------------------
    # Propriedades — encapsulamento com acesso somente leitura
    # -------------------------------------------------------------------------

    @property
    def descricao(self) -> str:
        """Texto identificador da transação."""
        return self._descricao

    @property
    def valor(self) -> float:
        """Valor monetário da transação."""
        return self._valor

    @property
    def categoria(self):
        """Categoria da transação (string ou objeto Categoria)."""
        return self._categoria

    @property
    def data(self) -> date:
        """Data em que a transação foi registrada."""
        return self._data

    # -------------------------------------------------------------------------
    # Métodos
    # -------------------------------------------------------------------------

    def tipo(self) -> str:
        """
        Retorna o tipo da transação ("receita" ou "despesa").
        Deve ser sobrescrito pelas subclasses — é o ponto de polimorfismo.

        Lança:
            NotImplementedError se chamado diretamente na classe base.
        """
        raise NotImplementedError("Subclasses devem implementar tipo().")

    def para_dict(self) -> dict:
        """
        Serializa a transação para um dicionário com chaves padronizadas.
        Utilizado pela camada de persistência para salvar os dados em arquivo.

        Aceita categoria tanto como string quanto como objeto com .nome,
        garantindo compatibilidade independente de como foi instanciada.

        Retorna:
            dict com chaves: tipo, descricao, valor, categoria, data
        """
        # hasattr verifica se o objeto tem o atributo 'nome' antes de acessá-lo,
        # evitando AttributeError quando categoria é uma string simples
        if hasattr(self._categoria, "nome"):
            nome_categoria = self._categoria.nome
        else:
            nome_categoria = str(self._categoria)

        return {
            "tipo":      self.tipo(),
            "descricao": self._descricao,
            "valor":     self._valor,
            "categoria": nome_categoria,
            "data":      self._data.isoformat(),
        }

    def __str__(self) -> str:
        """Representação legível para exibição na interface gráfica."""
        return (
            f"[{self.tipo().upper()}] {self._descricao} | "
            f"R$ {self._valor:.2f} | {self._categoria} | {self._data}"
        )


class Receita(Transacao):
    """
    Representa uma entrada de dinheiro (salário, freelance, bônus, etc.).
    Herda tudo de Transacao e sobrescreve apenas tipo().
    """

    def tipo(self) -> str:
        """Retorna 'receita' — identifica esta transação como entrada financeira."""
        return "receita"


class Despesa(Transacao):
    """
    Representa uma saída de dinheiro (aluguel, mercado, transporte, etc.).
    Herda tudo de Transacao e sobrescreve apenas tipo().
    """

    def tipo(self) -> str:
        """Retorna 'despesa' — identifica esta transação como saída financeira."""
        return "despesa"