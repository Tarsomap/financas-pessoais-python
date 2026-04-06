# services/relatorio.py
# RESPONSÁVEL: Pessoa 4

from models.transacao import Receita, Despesa


class Relatorio:
    def __init__(self, transacoes: list):
        # Guarda a lista de transações recebida do Gerenciador
        self._transacoes = transacoes

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

    # --- Gastos por categoria ---

    def gastos_por_categoria(self, ano: int, mes: int) -> dict:
        totais = {}
        for t in self._do_mes(ano, mes):
            if isinstance(t, Despesa):
                nome = t.categoria.nome
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
            "receita_atual":    rec_atual,
            "receita_anterior": rec_ant,
            "variacao_receita": round(rec_atual - rec_ant, 2),   # positivo = ganhou mais
            "despesa_atual":    desp_atual,
            "despesa_anterior": desp_ant,
            "variacao_despesa": round(desp_atual - desp_ant, 2), # positivo = gastou mais
        }

    # --- Sugestões de corte ---

    def sugestoes_corte(self, ano: int, mes: int, limite: float = 30.0) -> list:
        gastos = self.gastos_por_categoria(ano, mes)
        total = sum(gastos.values())

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
                    "economia_sugerida": round(gasto * 0.20, 2), # sugere cortar 20%
                })

        # Ordena da categoria mais pesada para a mais leve
        return sorted(sugestoes, key=lambda x: x["gasto"], reverse=True)