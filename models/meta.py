# models/meta.py
# RESPONSÁVEL: Pessoa 3 (Vinicius Prado Sobral)

# CORREÇÃO: importado date para suportar prazo como objeto date
# (os testes passam date(2026, 12, 31) e a persistência usa date.fromisoformat)
from datetime import date


class Meta:
    def __init__(self, nome: str, valor_alvo: float, prazo="Sem prazo"):
        # CORREÇÃO: prazo aceita tanto str quanto date (era prazo: str = "Sem prazo")
        if not nome or not nome.strip():
            raise ValueError("O nome da meta não pode ser vazio.")
        if valor_alvo <= 0:
            raise ValueError("O valor-alvo da meta deve ser maior que zero.")
        self.nome = nome.strip()
        self.valor_alvo = valor_alvo
        self.valor_atual = 0.0
        self.prazo = prazo

    def depositar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("O valor depositado deve ser maior que zero.")
        self.valor_atual = min(self.valor_atual + valor, self.valor_alvo)

    def progresso_percentual(self) -> float:
        return (self.valor_atual / self.valor_alvo) * 100

    def valor_restante(self) -> float:
        return self.valor_alvo - self.valor_atual

    def concluida(self) -> bool:
        return self.valor_atual >= self.valor_alvo

    def __repr__(self) -> str:
        status = "Concluída" if self.concluida() else f"{self.progresso_percentual():.1f}%"
        return (
            f"Meta(nome='{self.nome}', "
            f"alvo=R${self.valor_alvo:.2f}, "
            f"atual=R${self.valor_atual:.2f}, "
            f"prazo='{self.prazo}', "
            f"status='{status}')"
        )

    def to_dict(self) -> dict:
        # CORREÇÃO: prazo pode ser date ou str; isoformat() só existe em objetos date
        prazo_str = self.prazo.isoformat() if hasattr(self.prazo, "isoformat") else str(self.prazo)
        return {
            "nome":        self.nome,
            "valor_alvo":  self.valor_alvo,
            "valor_atual": self.valor_atual,
            "prazo":       prazo_str,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Meta":
        # CORREÇÃO: tenta converter prazo para date; mantém string se não for possível
        prazo_raw = dados.get("prazo", "Sem prazo")
        try:
            prazo = date.fromisoformat(prazo_raw)
        except (ValueError, AttributeError, TypeError):
            prazo = prazo_raw

        meta = cls(
            nome=dados["nome"],
            valor_alvo=float(dados["valor_alvo"]),
            prazo=prazo,
        )
        meta.valor_atual = float(dados.get("valor_atual", 0.0))
        return meta