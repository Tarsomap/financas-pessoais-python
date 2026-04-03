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
        """Deve somar apenas as receitas."""
        assert Relatorio.total_receitas(transacoes_abril) == 3500.0

    def test_total_despesas(self, transacoes_abril):
        """Deve somar apenas as despesas."""
        assert Relatorio.total_despesas(transacoes_abril) == 930.0

    def test_saldo(self, transacoes_abril):
        """Saldo deve ser receitas - despesas."""
        assert Relatorio.saldo(transacoes_abril) == 2570.0

    def test_lista_vazia_retorna_zero(self):
        """Com lista vazia, todos os totais devem ser 0."""
        assert Relatorio.total_receitas([]) == 0.0
        assert Relatorio.total_despesas([]) == 0.0
        assert Relatorio.saldo([]) == 0.0


class TestCategorias:

    def test_gastos_por_categoria(self, transacoes_abril):
        """Deve agrupar despesas por categoria corretamente."""
        gastos = Relatorio.gastos_por_categoria(transacoes_abril)
        assert gastos["Alimentação"] == 750.0
        assert gastos["Transporte"] == 80.0
        assert gastos["Saúde"] == 100.0
        assert "Salário" not in gastos  # Receita não deve entrar

    def test_categoria_mais_gasta(self, transacoes_abril):
        """Deve retornar a categoria com maior gasto."""
        assert Relatorio.categoria_mais_gasta(transacoes_abril) == "Alimentação"

    def test_categoria_mais_gasta_sem_despesas(self):
        """Sem despesas, deve retornar 'Nenhuma'."""
        receitas = [Receita("Salário", 1000.0, "Salário")]
        assert Relatorio.categoria_mais_gasta(receitas) == "Nenhuma"


class TestResumoMensal:

    def test_resumo_mensal_abril(self, transacoes_abril):
        """Resumo de abril deve bater com os valores da fixture."""
        resumo = Relatorio.resumo_mensal(transacoes_abril, mes=4, ano=2026)
        assert resumo["receitas"] == 3500.0
        assert resumo["despesas"] == 930.0
        assert resumo["saldo"] == 2570.0
        assert "por_categoria" in resumo

    def test_resumo_mes_sem_transacoes(self, transacoes_abril):
        """Mês sem transações deve retornar zeros."""
        resumo = Relatorio.resumo_mensal(transacoes_abril, mes=1, ano=2026)
        assert resumo["receitas"] == 0.0
        assert resumo["despesas"] == 0.0


class TestSugestaoCorte:

    def test_sugestao_identifica_categoria_alta(self, transacoes_abril):
        """
        Alimentação representa ~80% das despesas (750/930).
        Deve aparecer na sugestão com limite de 30%.
        """
        sugestoes = Relatorio.sugestao_corte(transacoes_abril, limite_percentual=30.0)
        assert any("Alimentação" in s for s in sugestoes)

    def test_sugestao_vazia_sem_despesas(self):
        """Sem despesas, não deve haver sugestões."""
        receitas = [Receita("Salário", 1000.0, "Salário")]
        assert Relatorio.sugestao_corte(receitas) == []
