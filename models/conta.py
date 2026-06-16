# models/conta.py
# RESPONSÁVEL: Tarso - Frente 5 (Empresa: contas a pagar/receber)

from datetime import date


class Conta:
    """
    Conta a pagar ou a receber — funcionalidade central do perfil Empresa.

    vencimento é guardado COMO VEIO (str ISO ou date): a conversão para texto
    do banco é responsabilidade da Persistencia. O id é anexado dinamicamente
    pelo banco ao carregar, como em Transacao e Meta.
    """

    TIPOS_VALIDOS = ("pagar", "receber")

    def __init__(self, tipo: str, descricao: str, valor: float,
                 vencimento, pago: bool = False):
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

    def _vencimento_date(self) -> date:
        """Normaliza vencimento (str ISO ou date) para um date, para comparar."""
        if isinstance(self.vencimento, date):
            return self.vencimento
        return date.fromisoformat(self.vencimento)

    def esta_vencida(self, referencia: date | None = None) -> bool:
        """True se a conta NÃO está paga e já passou do vencimento (default hoje)."""
        if self.pago:
            return False
        referencia = referencia or date.today()
        return self._vencimento_date() < referencia

    def para_dict(self) -> dict:
        """Serializa a conta; vencimento sai como texto ISO."""
        return {
            "tipo": self.tipo,
            "descricao": self.descricao,
            "valor": self.valor,
            "vencimento": self._vencimento_date().isoformat(),
            "pago": self.pago,
        }
