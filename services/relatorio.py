# services/relatorio.py
# RESPONSÁVEL: Pessoa 4

from datetime import date

from models.transacao import Receita, Despesa


class Relatorio:
    def __init__(self, transacoes: list, contas: list | None = None):
        # Guarda a lista de transações recebida do Gerenciador.
        self._transacoes = transacoes
        # Contas a pagar/receber (opcional): usadas só no fluxo de caixa.
        # Default [] mantém compatível quem instancia só com transações.
        self._contas = contas or []

    def _do_mes(self, ano: int, mes: int) -> list:
        # Filtra apenas as transações do mês/ano pedido
        return [t for t in self._transacoes if t.data.year == ano and t.data.month == mes]

    # --- Totais do mês ---

    def total_receitas_mes(self, ano: int, mes: int) -> float:
        # Soma só as Receitas do mês
        return sum(t.valor for t in self._do_mes(ano, mes) if isinstance(t, Receita))

    def total_despesas_mes(self, ano: int, mes: int) -> float:
        # Soma só as Despesas do mês
        return sum(t.valor for t in self._do_mes(ano, mes) if isinstance(t, Despesa))

    def saldo_mes(self, ano: int, mes: int) -> float:
        # Saldo = receitas - despesas (pode ser negativo)
        return self.total_receitas_mes(ano, mes) - self.total_despesas_mes(ano, mes)

    # --- Fluxo de caixa (contas a pagar/receber) ---

    @staticmethod
    def _vencimento(conta) -> date:
        # Conta guarda o vencimento CRU: str ISO (criada na mão) ou date
        # (reconstruída pela Persistencia). Normaliza para date e poder comparar.
        v = conta.vencimento
        return v if isinstance(v, date) else date.fromisoformat(v)

    def fluxo_de_caixa(self, ano: int, mes: int) -> dict:
        """
        Projeção de caixa do mês pelas contas a pagar/receber que VENCEM nele.

        Diferente do saldo (que é realizado): o fluxo de caixa olha o futuro —
        o que ainda vai entrar (a receber) e sair (a pagar) pelas datas de
        vencimento. Por isso usa as contas, não as transações.

        Returns:
            dict com 'entradas', 'saidas' e 'saldo_projetado' (entradas − saidas).
        """
        do_mes = [
            c for c in self._contas
            if self._vencimento(c).year == ano and self._vencimento(c).month == mes
        ]
        entradas = sum(c.valor for c in do_mes if c.tipo == "receber")
        saidas   = sum(c.valor for c in do_mes if c.tipo == "pagar")
        return {
            "entradas":        round(float(entradas), 2),
            "saidas":          round(float(saidas), 2),
            "saldo_projetado": round(float(entradas - saidas), 2),
        }

    # --- Gastos por categoria ---

    def gastos_por_categoria(self, ano: int, mes: int) -> dict:
        totais = {}
        for t in self._do_mes(ano, mes):
            if isinstance(t, Despesa):
                # CORREÇÃO: categoria pode ser objeto Categoria (com .nome) ou string.
                # hasattr verifica isso em tempo de execução para suportar os dois casos:
                # - testes criam Despesa com objeto Categoria → usa .nome
                # - views criam Despesa com string direta    → usa str()
                nome = t.categoria.nome if hasattr(t.categoria, "nome") else str(t.categoria)
                # Acumula o valor; se a chave não existe, começa do zero
                totais[nome] = totais.get(nome, 0) + t.valor
        return totais

    # --- Comparativo com o mês anterior ---

    def comparativo_mensal(self, ano: int, mes: int) -> dict:
        # Trata a virada de ano: janeiro → dezembro do ano anterior
        if mes == 1:
            ano_ant, mes_ant = ano - 1, 12
        else:
            ano_ant, mes_ant = ano, mes - 1

        rec_atual  = self.total_receitas_mes(ano, mes)
        rec_ant    = self.total_receitas_mes(ano_ant, mes_ant)
        desp_atual = self.total_despesas_mes(ano, mes)
        desp_ant   = self.total_despesas_mes(ano_ant, mes_ant)

        return {
            "receita_atual":     rec_atual,
            "receita_anterior":  rec_ant,
            "variacao_receita":  round(rec_atual  - rec_ant,  2),  # positivo = ganhou mais
            "despesa_atual":     desp_atual,
            "despesa_anterior":  desp_ant,
            "variacao_despesa":  round(desp_atual - desp_ant, 2),  # positivo = gastou mais
        }

    # --- Sugestões de corte ---

    def sugestoes_corte(self, ano: int, mes: int, limite: float = 30.0) -> list:
        gastos = self.gastos_por_categoria(ano, mes)
        total  = sum(gastos.values())
        if total == 0:
            return []

        sugestoes = []
        for categoria, gasto in gastos.items():
            pct = gasto / total * 100
            # Sinaliza categorias que passaram o limite do total de despesas
            if pct >= limite:
                sugestoes.append({
                    "categoria":         categoria,
                    "gasto":             round(gasto, 2),
                    "percentual":        round(pct, 2),
                    "economia_sugerida": round(gasto * 0.20, 2),  # sugere cortar 20%
                })

        # Ordena da categoria mais pesada para a mais leve
        return sorted(sugestoes, key=lambda x: x["gasto"], reverse=True)