# =============================================================================
# tests/test_relatorio.py
# -----------------------------------------------------------------------------
# Testes unitários para a classe Relatorio.
#
# Por que Relatorio é fácil de testar?
#   Todos os métodos são @staticmethod e recebem dados como parâmetro.
#   Não há estado interno nem dependências externas. Dado o mesmo
#   input, sempre retornam o mesmo output (funções puras).
#
# Valores esperados da fixture transacoes_abril:
#   Receitas: 3000 + 500 = 3500
#   Despesas: 600 + 150 + 80 + 100 = 930
#   Saldo: 3500 - 930 = 2570
#   Categoria top: Alimentação (750 de 930 = ~80%)
#
# RESPONSÁVEL: Pessoa 4
# =============================================================================

import pytest
from datetime import date
from models import Receita, Despesa
from services import Relatorio


@pytest.fixture
def transacoes_abril():
    """Lista fixa de transações de abril/2026 para os testes."""
    return [
        Receita("Salário", 3000.0, "Salário", date(2026, 4, 1)),
        Receita("Freelance", 500.0, "Salário", date(2026, 4, 10)),
        Despesa("Mercado", 600.0, "Alimentação", date(2026, 4, 2)),
        Despesa("Restaurante", 150.0, "Alimentação", date(2026, 4, 5)),
        Despesa("Uber", 80.0, "Transporte", date(2026, 4, 3)),
        Despesa("Academia", 100.0, "Saúde", date(2026, 4, 4)),
    ]


class TestTotais:

    def test_total_receitas(self, transacoes_abril):
        assert Relatorio.total_receitas(transacoes_abril) == 3500.0

    def test_total_despesas(self, transacoes_abril):
        assert Relatorio.total_despesas(transacoes_abril) == 930.0

    def test_saldo(self, transacoes_abril):
        assert Relatorio.saldo(transacoes_abril) == 2570.0

    def test_lista_vazia_retorna_zero(self):
        assert Relatorio.total_receitas([]) == 0.0
        assert Relatorio.total_despesas([]) == 0.0
        assert Relatorio.saldo([]) == 0.0


class TestCategorias:

    def test_gastos_por_categoria(self, transacoes_abril):
        gastos = Relatorio.gastos_por_categoria(transacoes_abril)
        assert gastos["Alimentação"] == 750.0
        assert gastos["Transporte"] == 80.0
        assert gastos["Saúde"] == 100.0
        assert "Salário" not in gastos

    def test_categoria_mais_gasta(self, transacoes_abril):
        assert Relatorio.categoria_mais_gasta(transacoes_abril) == "Alimentação"

    def test_categoria_mais_gasta_sem_despesas(self):
        receitas = [Receita("Salário", 1000.0, "Salário")]
        assert Relatorio.categoria_mais_gasta(receitas) == "Nenhuma"


class TestResumoMensal:

    def test_resumo_mensal_abril(self, transacoes_abril):
        resumo = Relatorio.resumo_mensal(transacoes_abril, mes=4, ano=2026)
        assert resumo["receitas"] == 3500.0
        assert resumo["despesas"] == 930.0
        assert resumo["saldo"] == 2570.0
        assert "por_categoria" in resumo

    def test_resumo_mes_sem_transacoes(self, transacoes_abril):
        resumo = Relatorio.resumo_mensal(transacoes_abril, mes=1, ano=2026)
        assert resumo["receitas"] == 0.0
        assert resumo["despesas"] == 0.0


class TestSugestaoCorte:

    def test_sugestao_identifica_categoria_alta(self, transacoes_abril):
        sugestoes = Relatorio.sugestao_corte(transacoes_abril, limite_percentual=30.0)
        assert any("Alimentação" in s for s in sugestoes)

    def test_sugestao_vazia_sem_despesas(self):
        receitas = [Receita("Salário", 1000.0, "Salário")]
        assert Relatorio.sugestao_corte(receitas) == []
