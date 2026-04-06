# models/transacao.py
# RESPONSÁVEL: Pessoa 2

from datetime import date


class Transacao:
    def __init__(self, descricao: str, valor: float, categoria, data: date = None):
        if not descricao or not descricao.strip():
            raise ValueError("A descrição não pode ser vazia.")
        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")

        self._descricao = descricao.strip()
        self._valor = float(valor)
        self._categoria = categoria
        self._data = data if data is not None else date.today()

    @property
    def descricao(self) -> str:
        return self._descricao

    @property
    def valor(self) -> float:
        return self._valor

    @property
    def categoria(self):
        return self._categoria

    @property
    def data(self) -> date:
        return self._data

    def para_dict(self) -> dict:
        return {
            "tipo":      self.tipo(),
            "descricao": self._descricao,
            "valor":     self._valor,
            "categoria": self._categoria.nome,
            "data":      self._data.isoformat(),
        }

    def __str__(self) -> str:
        return (f"[{self.tipo().upper()}] {self._descricao} | "
                f"R$ {self._valor:.2f} | {self._categoria} | {self._data}")


class Receita(Transacao):
    def tipo(self) -> str:
        return "receita"


class Despesa(Transacao):
    def tipo(self) -> str:
        return "despesa"