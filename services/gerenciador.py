from __future__ import annotations

from typing import List, Optional
from models.meta import Meta


class Gerenciador:

    def __init__(self):
        self._transacoes: list = []
        self._metas: List[Meta] = []


    # TRANSAÇÕES

    def adicionar_transacao(self, transacao) -> None:
        if transacao is None:
            raise TypeError("A transação não pode ser None.")
        self._transacoes.append(transacao)

    def remover_transacao(self, transacao) -> bool:
        try:
            self._transacoes.remove(transacao)
            return True
        except ValueError:
            return False

    def listar_transacoes(self) -> list:
        return list(self._transacoes)

    def filtrar_por_tipo(self, tipo: str) -> list:
        tipo_lower = tipo.strip().lower()
        return [
            t for t in self._transacoes
            if hasattr(t, "tipo") and t.tipo.lower() == tipo_lower
        ]

    def filtrar_por_categoria(self, categoria) -> list:
        if isinstance(categoria, str):
            return [
                t for t in self._transacoes
                if hasattr(t, "categoria") and str(t.categoria).lower() == categoria.lower()
            ]
        return [
            t for t in self._transacoes
            if hasattr(t, "categoria") and t.categoria == categoria
        ]

    def filtrar_por_periodo(self, data_inicio: str, data_fim: str) -> list:
        from datetime import datetime

        fmt = "%d/%m/%Y"
        try:
            inicio = datetime.strptime(data_inicio, fmt)
            fim = datetime.strptime(data_fim, fmt)
        except ValueError as e:
            raise ValueError(f"Formato de data inválido. Use DD/MM/AAAA. Detalhe: {e}")

        resultado = []
        for t in self._transacoes:
            if not hasattr(t, "data"):
                continue
            try:
                data_t = datetime.strptime(t.data, fmt)
                if inicio <= data_t <= fim:
                    resultado.append(t)
            except ValueError:
                pass

        return resultado


    # METAS

    def adicionar_meta(self, meta: Meta) -> None:
        if not isinstance(meta, Meta):
            raise TypeError("Apenas instâncias de Meta são aceitas.")

        nomes_existentes = [m.nome.lower() for m in self._metas]
        if meta.nome.lower() in nomes_existentes:
            raise ValueError(f"Já existe uma meta com o nome '{meta.nome}'.")

        self._metas.append(meta)

    def remover_meta(self, nome: str) -> bool:
        for i, meta in enumerate(self._metas):
            if meta.nome.lower() == nome.strip().lower():
                self._metas.pop(i)
                return True
        return False

    def buscar_meta(self, nome: str) -> Optional[Meta]:
        for meta in self._metas:
            if meta.nome.lower() == nome.strip().lower():
                return meta
        return None

    def depositar_em_meta(self, nome: str, valor: float) -> None:
        meta = self.buscar_meta(nome)
        if meta is None:
            raise ValueError(f"Meta '{nome}' não encontrada.")
        meta.depositar(valor)

    def listar_metas(self) -> List[Meta]:
        return list(self._metas)

    def metas_concluidas(self) -> List[Meta]:
        return [m for m in self._metas if m.concluida()]

    def metas_pendentes(self) -> List[Meta]:
        return [m for m in self._metas if not m.concluida()]


    # RESUMO E PERSISTÊNCIA

    def resumo(self) -> dict:
        return {
            "total_transacoes": len(self._transacoes),
            "total_metas": len(self._metas),
            "metas_concluidas": len(self.metas_concluidas()),
            "metas_pendentes": len(self.metas_pendentes()),
        }

    def metas_para_salvar(self) -> List[dict]:
        return [m.to_dict() for m in self._metas]

    def carregar_metas(self, lista_dicts: List[dict]) -> None:
        self._metas = [Meta.from_dict(d) for d in lista_dicts]
