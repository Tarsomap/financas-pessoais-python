import pytest
from datetime import date
from services import Gerenciador


@pytest.fixture
def gerenciador():
    """Fixture que retorna um Gerenciador limpo para cada teste."""
    return Gerenciador()


@pytest.fixture
def gerenciador_populado(gerenciador):
    """Fixture com transações já adicionadas."""
    gerenciador.adicionar_receita("Salário", 3000.0, "Salário", date(2026, 4, 1))
    gerenciador.adicionar_despesa("Mercado", 500.0, "Alimentação", date(2026, 4, 2))
    gerenciador.adicionar_despesa("Uber", 50.0, "Transporte", date(2026, 4, 3))
    return gerenciador


class TestAdicionarTransacoes:

    def test_adicionar_receita(self, gerenciador):
        """Deve adicionar receita e retornar objeto correto."""
        r = gerenciador.adicionar_receita("Salário", 3000.0, "Salário")
        assert r.valor == 3000.0
        assert len(gerenciador.listar_transacoes()) == 1

    def test_adicionar_despesa(self, gerenciador):
        """Deve adicionar despesa corretamente."""
        d = gerenciador.adicionar_despesa("Mercado", 200.0, "Alimentação")
        assert d.tipo() == "despesa"
        assert len(gerenciador.listar_transacoes()) == 1

    def test_adicionar_valor_invalido_levanta_excecao(self, gerenciador):
        """Valor inválido deve propagar a exceção do model."""
        with pytest.raises(ValueError):
            gerenciador.adicionar_receita("Teste", -100, "Outros")


class TestRemoverTransacao:

    def test_remover_transacao_valida(self, gerenciador_populado):
        """Deve remover a transação pelo índice."""
        antes = len(gerenciador_populado.listar_transacoes())
        gerenciador_populado.remover_transacao(0)
        assert len(gerenciador_populado.listar_transacoes()) == antes - 1

    def test_remover_indice_invalido_levanta_excecao(self, gerenciador_populado):
        """Índice fora do range deve lançar IndexError."""
        with pytest.raises(IndexError):
            gerenciador_populado.remover_transacao(999)


class TestSaldo:

    def test_saldo_com_receitas_e_despesas(self, gerenciador_populado):
        """Saldo deve ser receitas - despesas."""
        # 3000 - 500 - 50 = 2450
        assert gerenciador_populado.saldo_atual() == 2450.0

    def test_saldo_vazio_e_zero(self, gerenciador):
        """Saldo sem transações deve ser 0."""
        assert gerenciador.saldo_atual() == 0.0


class TestFiltros:

    def test_filtrar_por_tipo_despesa(self, gerenciador_populado):
        """Deve retornar apenas despesas."""
        despesas = gerenciador_populado.listar_transacoes(tipo="despesa")
        assert len(despesas) == 2
        assert all(t.tipo() == "despesa" for t in despesas)

    def test_filtrar_por_categoria(self, gerenciador_populado):
        """Deve retornar apenas transações da categoria informada."""
        alimentacao = gerenciador_populado.listar_transacoes(categoria="Alimentação")
        assert len(alimentacao) == 1
        assert alimentacao[0].descricao == "Mercado"

    def test_filtrar_sem_resultados(self, gerenciador_populado):
        """Filtro que não encontra nada deve retornar lista vazia."""
        resultado = gerenciador_populado.listar_transacoes(categoria="Saúde")
        assert resultado == []


class TestMetas:

    def test_adicionar_meta(self, gerenciador):
        """Deve adicionar meta corretamente."""
        m = gerenciador.adicionar_meta("Viagem", 2000.0, date(2026, 12, 31))
        assert m.valor_alvo == 2000.0
        assert len(gerenciador.listar_metas()) == 1

    def test_remover_meta(self, gerenciador):
        """Deve remover meta pelo índice."""
        gerenciador.adicionar_meta("Viagem", 2000.0, date(2026, 12, 31))
        gerenciador.remover_meta(0)
        assert len(gerenciador.listar_metas()) == 0
