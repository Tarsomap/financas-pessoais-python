# =============================================================================
# models/conta.py
# -----------------------------------------------------------------------------
# Define a classe Conta — representa uma conta a pagar ou a receber,
# funcionalidade central do perfil Empresa. Exemplos: "Aluguel do escritório
# (a pagar, R$ 2000, vence 20/06)" ou "Fatura cliente X (a receber, R$ 5000)".
#
# CONCEITOS APLICADOS:
#   - Validação no construtor: tipo deve ser 'pagar' ou 'receber', descrição
#     não pode ser vazia, valor deve ser positivo. Garante que toda Conta
#     nasce num estado válido (fail fast).
#   - Duck typing no vencimento: aceita tanto str ISO ("2026-06-20") quanto
#     date(2026, 6, 20). O método _vencimento_date() normaliza para date
#     quando precisa comparar — assim a classe funciona independente de como
#     o dado chegou (criado na mão vs. reconstruído pela Persistencia).
#   - Constante de classe (TIPOS_VALIDOS): centraliza os valores aceitos
#     para 'tipo' numa tupla imutável. Se no futuro surgir um terceiro tipo,
#     basta adicioná-lo aqui.
#   - Serialização (para_dict): converte a Conta para dicionário com
#     vencimento como texto ISO — formato padrão para persistência em SQLite.
#   - id dinâmico: assim como Transacao e Meta, o id é responsabilidade do
#     banco. A Persistencia o atribui dinamicamente (obj.id = id_bd) ao
#     carregar do banco.
#
# RESPONSÁVEL: Tarso - Frente 5 (Empresa: contas a pagar/receber)
# =============================================================================

from datetime import date


class Conta:
    """
    Conta a pagar ou a receber — funcionalidade central do perfil Empresa.

    vencimento é guardado COMO VEIO (str ISO ou date): a conversão para texto
    do banco é responsabilidade da Persistencia. O id é anexado dinamicamente
    pelo banco ao carregar, como em Transacao e Meta.
    """

    # Tupla (imutável) com os tipos aceitos. Usar tupla em vez de lista
    # porque esses valores nunca devem ser alterados em tempo de execução.
    TIPOS_VALIDOS = ("pagar", "receber")

    def __init__(self, tipo: str, descricao: str, valor: float,
                 vencimento, pago: bool = False):
        """
        Inicializa uma conta com validação dos dados de entrada.

        Parâmetros:
            tipo       (str)          : 'pagar' ou 'receber'
            descricao  (str)          : texto identificador (não pode ser vazio)
            valor      (float)        : valor em reais (> 0)
            vencimento (str ou date)  : data de vencimento (ISO ou date)
            pago       (bool)         : se a conta já foi quitada (padrão False)

        Lança:
            ValueError se tipo inválido, descrição vazia ou valor <= 0.
        """
        # Validação no construtor — defesa em profundidade, igual a Transacao/Meta.
        if tipo not in self.TIPOS_VALIDOS:
            raise ValueError("tipo deve ser 'pagar' ou 'receber'.")
        if not descricao or not descricao.strip():
            raise ValueError("A descrição da conta não pode ser vazia.")
        if valor <= 0:
            raise ValueError("O valor da conta deve ser maior que zero.")

        self.tipo = tipo
        self.descricao = descricao.strip()
        self.valor = float(valor)
        self.vencimento = vencimento     # cru: str ISO ou date
        self.pago = bool(pago)

    # -------------------------------------------------------------------------
    # Métodos de negócio
    # -------------------------------------------------------------------------

    def _vencimento_date(self) -> date:
        """
        Normaliza vencimento (str ISO ou date) para um objeto date.

        Por que um método separado? Porque esta conversão é usada em dois
        lugares (esta_vencida e para_dict) e a lógica de isinstance/fromisoformat
        ficaria duplicada sem ele.
        """
        if isinstance(self.vencimento, date):
            return self.vencimento
        return date.fromisoformat(self.vencimento)

    def esta_vencida(self, referencia: date | None = None) -> bool:
        """
        Verifica se a conta está vencida (não paga e já passou do vencimento).

        Parâmetros:
            referencia (date, opt) : data de referência para a comparação;
                                     padrão date.today() se não informada.

        Retorna:
            True se a conta NÃO está paga E o vencimento já passou.
            Contas pagas nunca são consideradas vencidas.
        """
        if self.pago:
            return False
        referencia = referencia or date.today()
        return self._vencimento_date() < referencia

    # -------------------------------------------------------------------------
    # Serialização
    # -------------------------------------------------------------------------

    def para_dict(self) -> dict:
        """
        Serializa a conta para dicionário; vencimento sai como texto ISO.

        Retorna:
            dict com chaves: tipo, descricao, valor, vencimento, pago.
        """
        return {
            "tipo": self.tipo,
            "descricao": self.descricao,
            "valor": self.valor,
            "vencimento": self._vencimento_date().isoformat(),
            "pago": self.pago,
        }
