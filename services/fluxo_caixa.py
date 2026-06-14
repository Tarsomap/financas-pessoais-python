# services/fluxo_caixa.py
# RESPONSÁVEL: Tarso - Frente 5 (fluxo de caixa)

from datetime import date


class FluxoCaixa:
    """
    Indicadores de contas a pagar/receber de um usuário.

    Desacoplado da origem: recebe uma lista de Conta e calcula em cima dela,
    no mesmo espírito do Relatorio. O perfil, quando informado, adapta os
    indicadores — pessoa física não tem recebíveis, então não há saldo
    projetado "completo". Sem perfil, assume o comportamento de empresa.
    """

    def __init__(self, contas: list, perfil=None):
        self._contas = list(contas)
        self._perfil = perfil

    def _pendentes(self, tipo: str) -> list:
        """Contas não pagas de um tipo ('pagar'/'receber')."""
        return [c for c in self._contas if c.tipo == tipo and not c.pago]

    def total_a_pagar(self) -> float:
        return round(sum(c.valor for c in self._pendentes("pagar")), 2)

    def total_a_receber(self) -> float:
        return round(sum(c.valor for c in self._pendentes("receber")), 2)

    def mostra_recebiveis(self) -> bool:
        """Pessoa física não tem 'receber'; sem perfil, assume empresa."""
        return self._perfil is None or "receber" in self._perfil.tipos_conta()

    def saldo_projetado(self) -> float:
        """Empresa: receber − pagar. Pessoa física (sem recebíveis): −pagar."""
        if self.mostra_recebiveis():
            return round(self.total_a_receber() - self.total_a_pagar(), 2)
        return round(-self.total_a_pagar(), 2)

    def contas_vencidas(self, referencia: date | None = None) -> list:
        return [c for c in self._contas if c.esta_vencida(referencia)]

    def contas_a_vencer(self, referencia: date | None = None) -> list:
        return [
            c for c in self._contas
            if not c.pago and not c.esta_vencida(referencia)
        ]

    def total_vencido(self, referencia: date | None = None) -> float:
        return round(sum(c.valor for c in self.contas_vencidas(referencia)), 2)
