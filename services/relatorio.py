# =============================================================================
# services/relatorio.py
# -----------------------------------------------------------------------------
# Gera relatórios financeiros a partir de listas de transações e contas.
#
# O Relatorio é DESACOPLADO do banco: ele recebe listas prontas (transações
# e, opcionalmente, contas) e calcula em cima delas, sem saber a origem dos
# dados. Quem fornece as listas é o Gerenciador. Essa separação permite
# testar o Relatorio isoladamente, sem banco.
#
# CONCEITOS APLICADOS:
#   - Desacoplamento: o Relatorio não importa Persistencia nem sabe de banco.
#     Recebe dados puros e devolve resultados puros — fácil de testar e de
#     reutilizar (se amanhã os dados vierem de uma API, nada muda aqui).
#   - isinstance() para polimorfismo: diferencia Receita de Despesa sem
#     if/elif sobre strings — usa a hierarquia de herança das classes.
#   - List comprehension com filtro: [t for t in lista if condição] é o
#     padrão Pythônico para filtrar coleções sem loop explícito.
#   - dict.get() com default: totais.get(nome, 0) retorna 0 se a chave
#     não existir, evitando KeyError e substituindo a necessidade de
#     verificar antes com 'if nome in totais'.
#   - Método estático (_vencimento): lógica sem estado que pertence
#     logicamente à classe mas não precisa de self nem cls.
#
# RESPONSÁVEL: Pessoa 4
# =============================================================================

from datetime import date

from models.transacao import Receita, Despesa


class Relatorio:
    """
    Gerador de relatórios financeiros mensais.

    Recebe no construtor as listas de transações e contas do usuário
    (fornecidas pelo Gerenciador) e oferece métodos para calcular:
        - Total de receitas e despesas por mês
        - Saldo mensal (receitas − despesas)
        - Fluxo de caixa projetado (contas a pagar/receber)
        - Gastos por categoria
        - Comparativo com o mês anterior
        - Sugestões de corte de gastos
    """

    def __init__(self, transacoes: list, contas: list | None = None):
        """
        Inicializa o relatório com os dados do usuário.

        Parâmetros:
            transacoes (list)      : lista de objetos Receita/Despesa
            contas     (list, opt) : lista de objetos Conta (para fluxo de caixa)
        """
        # Guarda a lista de transações recebida do Gerenciador.
        self._transacoes = transacoes
        # Contas a pagar/receber (opcional): usadas só no fluxo de caixa.
        # Default [] mantém compatível quem instancia só com transações.
        self._contas = contas or []

    # -------------------------------------------------------------------------
    # Helpers privados
    # -------------------------------------------------------------------------

    def _do_mes(self, ano: int, mes: int) -> list:
        """
        Filtra apenas as transações do mês/ano pedido.

        Parâmetros:
            ano (int) : ano de referência (ex.: 2026)
            mes (int) : mês de referência (1–12)

        Retorna:
            Lista filtrada de transações daquele mês.
        """
        return [t for t in self._transacoes if t.data.year == ano and t.data.month == mes]

    # -------------------------------------------------------------------------
    # Totais do mês
    # -------------------------------------------------------------------------

    def total_receitas_mes(self, ano: int, mes: int) -> float:
        """
        Soma todas as receitas do mês.

        Usa isinstance(t, Receita) para filtrar — polimorfismo via herança.
        O tipo real do objeto é verificado em tempo de execução.
        """
        return sum(t.valor for t in self._do_mes(ano, mes) if isinstance(t, Receita))

    def total_despesas_mes(self, ano: int, mes: int) -> float:
        """
        Soma todas as despesas do mês.

        Mesmo padrão de total_receitas_mes, filtrando por Despesa.
        """
        return sum(t.valor for t in self._do_mes(ano, mes) if isinstance(t, Despesa))

    def saldo_mes(self, ano: int, mes: int) -> float:
        """
        Calcula o saldo do mês: receitas − despesas (pode ser negativo).

        Um saldo negativo indica que o usuário gastou mais do que recebeu
        naquele mês — informação importante para o dashboard.
        """
        return self.total_receitas_mes(ano, mes) - self.total_despesas_mes(ano, mes)

    # -------------------------------------------------------------------------
    # Fluxo de caixa (contas a pagar/receber) — funcionalidade Empresa
    # -------------------------------------------------------------------------

    @staticmethod
    def _vencimento(conta) -> date:
        """
        Normaliza o vencimento de uma Conta (str ISO ou date) para date.

        Conta guarda o vencimento CRU: str ISO (criada na mão) ou date
        (reconstruída pela Persistencia). Normaliza para date para poder
        comparar ano/mês corretamente.
        """
        v = conta.vencimento
        return v if isinstance(v, date) else date.fromisoformat(v)

    def fluxo_de_caixa(self, ano: int, mes: int) -> dict:
        """
        Projeção de caixa do mês pelas contas a pagar/receber.

        Diferente do saldo (que é realizado — baseado em transações já
        lançadas), o fluxo de caixa olha o FUTURO: o que ainda vai entrar
        (contas a receber) e sair (contas a pagar) pelas datas de vencimento.
        Por isso usa as contas, não as transações.

        Parâmetros:
            ano (int) : ano de referência
            mes (int) : mês de referência

        Retorna:
            dict com 'entradas', 'saidas' e 'saldo_projetado' (entradas − saidas).
        """
        # Filtra contas que vencem no mês/ano pedido
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

    # -------------------------------------------------------------------------
    # Gastos por categoria
    # -------------------------------------------------------------------------

    def gastos_por_categoria(self, ano: int, mes: int) -> dict:
        """
        Totaliza as despesas do mês agrupadas por categoria.

        Útil para o usuário visualizar onde está gastando mais (ex.:
        "Alimentação: R$ 800, Transporte: R$ 400").

        Parâmetros:
            ano (int) : ano de referência
            mes (int) : mês de referência

        Retorna:
            dict[str, float] — chave é o nome da categoria, valor é o total.
        """
        totais = {}
        for t in self._do_mes(ano, mes):
            if isinstance(t, Despesa):
                # categoria pode ser objeto Categoria (com .nome) ou string.
                # hasattr verifica isso em tempo de execução para suportar os dois casos:
                # - testes criam Despesa com objeto Categoria → usa .nome
                # - views criam Despesa com string direta    → usa str()
                nome = t.categoria.nome if hasattr(t.categoria, "nome") else str(t.categoria)
                # dict.get(chave, 0): retorna o valor existente ou 0 se a chave
                # ainda não existir — evita KeyError sem precisar de if/else.
                totais[nome] = totais.get(nome, 0) + t.valor
        return totais

    # -------------------------------------------------------------------------
    # Comparativo com o mês anterior
    # -------------------------------------------------------------------------

    def comparativo_mensal(self, ano: int, mes: int) -> dict:
        """
        Compara receitas e despesas do mês atual com o mês anterior.

        Calcula a variação absoluta (positivo = aumentou, negativo = diminuiu).
        Útil para o usuário perceber tendências: "gastei R$ 200 a mais este mês".

        Parâmetros:
            ano (int) : ano de referência
            mes (int) : mês de referência

        Retorna:
            dict com receita_atual, receita_anterior, variacao_receita,
            despesa_atual, despesa_anterior, variacao_despesa.
        """
        # Trata a virada de ano: janeiro (mes=1) → dezembro do ano anterior
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

    # -------------------------------------------------------------------------
    # Sugestões de corte
    # -------------------------------------------------------------------------

    def sugestoes_corte(self, ano: int, mes: int, limite: float = 30.0) -> list:
        """
        Sugere categorias onde o usuário poderia cortar gastos.

        O critério: se uma categoria representa mais de 'limite'% do total
        de despesas do mês, sugere cortar 20% daquele gasto. O default de 30%
        significa "qualquer categoria que sozinha representa quase um terço
        dos gastos merece atenção".

        Parâmetros:
            ano    (int)   : ano de referência
            mes    (int)   : mês de referência
            limite (float) : percentual mínimo para gerar sugestão (padrão 30%)

        Retorna:
            Lista de dicts com categoria, gasto, percentual e economia_sugerida,
            ordenada do maior gasto para o menor.
        """
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
