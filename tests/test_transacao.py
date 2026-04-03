# =============================================================================
# tests/test_transacao.py
# -----------------------------------------------------------------------------
# Testes unitários para as classes Transacao, Receita e Despesa.
#
# O que são testes unitários?
#   São funções que verificam automaticamente se uma unidade de código
#   (uma função ou método) se comporta como esperado. O pytest executa
#   todas as funções que começam com 'test_' e reporta quais passaram
#   ou falharam.
#
# Como rodar:
#   pytest tests/test_transacao.py -v
#
# Estrutura de um teste:
#   1. Arrange: preparar os dados necessários
#   2. Act:     chamar o método sendo testado
#   3. Assert:  verificar se o resultado é o esperado
#
# pytest.raises(ExcecaoEsperada):
#   Verifica que um bloco de código lança a exceção correta.
#   Se a exceção não for lançada, o teste FALHA.
# =============================================================================

import pytest
from datetime import date
from models import Receita, Despesa


class TestReceita:

    def test_criar_receita_valida(self):
        """Deve criar uma Receita com os dados corretos."""
        r = Receita("Salário", 3000.0, "Salário", date(2026, 4, 1))
        assert r.descricao == "Salário"
        assert r.valor == 3000.0
        assert r.categoria == "Salário"
        assert r.data == date(2026, 4, 1)
        assert r.tipo() == "receita"

    def test_receita_valor_zero_levanta_excecao(self):
        """Valor zero deve lançar ValueError."""
        with pytest.raises(ValueError):
            Receita("Teste", 0, "Outros")

    def test_receita_valor_negativo_levanta_excecao(self):
        """Valor negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            Receita("Teste", -100, "Outros")

    def test_receita_descricao_vazia_levanta_excecao(self):
        """Descrição vazia deve lançar ValueError."""
        with pytest.raises(ValueError):
            Receita("", 100, "Outros")

    def test_receita_data_padrao_e_hoje(self):
        """Se data não for informada, deve usar a data de hoje."""
        r = Receita("Teste", 100, "Outros")
        assert r.data == date.today()

    def test_receita_para_dict(self):
        """para_dict deve retornar dicionário com as chaves corretas."""
        r = Receita("Salário", 3000.0, "Salário", date(2026, 4, 1))
        d = r.para_dict()
        assert d["descricao"] == "Salário"
        assert d["valor"] == 3000.0
        assert d["categoria"] == "Salário"


class TestDespesa:

    def test_criar_despesa_valida(self):
        """Deve criar uma Despesa com tipo correto."""
        d = Despesa("Mercado", 250.0, "Alimentação", date(2026, 4, 2))
        assert d.descricao == "Mercado"
        assert d.valor == 250.0
        assert d.tipo() == "despesa"

    def test_despesa_valor_negativo_levanta_excecao(self):
        with pytest.raises(ValueError):
            Despesa("Teste", -50, "Outros")
