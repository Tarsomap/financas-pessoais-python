"""
test_relatorio.py — Testa o Relatorio adaptado ao usuario_id (Frente 5).

EDITADO: Relatorio recebe um Gerenciador (já escopado ao usuario_id),
não uma lista avulsa. O fluxo_de_caixa é o método novo da Frente 5.
"""

import pytest
from services.gerenciador import Gerenciador
from services.relatorio import Relatorio
from services.persistencia import Persistencia
from services.auth import gerar_hash


@pytest.fixture
def gerenciador_com_dados(banco_limpo):
    """
    Fixture local: cria um gerenciador com transações prontas.
    Fixtures locais (neste arquivo) só ficam disponíveis aqui.
    Fixtures globais (conftest.py) ficam disponíveis em todos os arquivos.
    """
    id_u = Persistencia.cadastrar_usuario("rel@rel.com", gerar_hash("s"), "pessoa_fisica")
    g = Gerenciador(id_u)
    g.adicionar_receita("Salário", 3000.0, "salario")
    g.adicionar_receita("Freelance", 500.0, "servicos")
    g.adicionar_despesa("Aluguel", 1200.0, "moradia")
    g.adicionar_despesa("Mercado", 400.0, "alimentacao")
    return g


class TestResumo:

    def test_resumo_calcula_receitas(self, gerenciador_com_dados):
        rel = Relatorio(gerenciador_com_dados)
        resumo = rel.resumo()
        assert resumo["receitas"] == pytest.approx(3500.0)

    def test_resumo_calcula_despesas(self, gerenciador_com_dados):
        rel = Relatorio(gerenciador_com_dados)
        resumo = rel.resumo()
        assert resumo["despesas"] == pytest.approx(1600.0)

    def test_resumo_calcula_saldo(self, gerenciador_com_dados):
        rel = Relatorio(gerenciador_com_dados)
        resumo = rel.resumo()
        assert resumo["saldo"] == pytest.approx(1900.0)  # 3500 - 1600

    def test_resumo_sem_transacoes(self, banco_limpo):
        """Relatorio com gerenciador vazio deve devolver zeros, não explodir."""
        id_u = Persistencia.cadastrar_usuario("vazio@rel.com", gerar_hash("s"), "pessoa_fisica")
        g = Gerenciador(id_u)
        rel = Relatorio(g)
        resumo = rel.resumo()

        assert resumo["receitas"] == pytest.approx(0.0)
        assert resumo["despesas"] == pytest.approx(0.0)
        assert resumo["saldo"] == pytest.approx(0.0)


class TestFluxoDeCaixa:
    """Testa o método novo adicionado pela Frente 5."""

    def test_fluxo_de_caixa_calcula_entradas_e_saidas(self, banco_limpo):
        id_u = Persistencia.cadastrar_usuario("fc@fc.com", gerar_hash("s"), "empresa")
        g = Gerenciador(id_u)

        # Contas com vencimento em junho de 2024
        g.adicionar_conta("receber", "Cliente X", 5000.0, "2024-06-10")
        g.adicionar_conta("receber", "Cliente Y", 3000.0, "2024-06-20")
        g.adicionar_conta("pagar",   "Fornecedor", 2000.0, "2024-06-15")

        rel = Relatorio(g)
        fluxo = rel.fluxo_de_caixa(2024, 6)

        assert fluxo["entradas"] == pytest.approx(8000.0)
        assert fluxo["saidas"] == pytest.approx(2000.0)
        assert fluxo["saldo_projetado"] == pytest.approx(6000.0)

    def test_fluxo_de_caixa_ignora_outro_mes(self, banco_limpo):
        """Contas de julho não devem aparecer no fluxo de junho."""
        id_u = Persistencia.cadastrar_usuario("mes@mes.com", gerar_hash("s"), "empresa")
        g = Gerenciador(id_u)

        g.adicionar_conta("receber", "Junho", 1000.0, "2024-06-01")
        g.adicionar_conta("receber", "Julho", 9999.0, "2024-07-01")

        rel = Relatorio(g)
        fluxo = rel.fluxo_de_caixa(2024, 6)

        assert fluxo["entradas"] == pytest.approx(1000.0)
