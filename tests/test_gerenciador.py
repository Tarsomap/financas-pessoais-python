# =============================================================================
# tests/test_gerenciador.py
# -----------------------------------------------------------------------------
# Testes do Gerenciador na versão WEB (Contrato B): escopado por usuario_id,
# persistindo de verdade na Persistencia (banco SQLite :memory:), com remoção
# POR ID (não por posição) e isolamento entre usuários.
#
# Por que banco :memory: e não listas em memória?
#   O Gerenciador novo não guarda nada em atributos próprios — ele delega tudo
#   à Persistencia. Para testá-lo de ponta a ponta usamos a fixture banco_limpo
#   (conftest.py), que aponta a Persistencia para um SQLite em memória, isolado
#   e instantâneo. Cada teste nasce com um banco vazio.
#
# RESPONSÁVEL: Tarso (Coordenador) — adaptado à Frente 3 (Gerenciador web) na
#              integração da Frente 6 (Qualidade).
# =============================================================================

import pytest

from services.persistencia import Persistencia
from services.gerenciador import Gerenciador


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def usuario_id(banco_limpo):
    """
    Cria um usuário dono das operações e devolve seu id.

    Recebe banco_limpo (conftest) para herdar o banco :memory: já inicializado.
    Cadastra direto pela Persistencia com um hash fictício — não depende de
    services.auth (Frente 1), então funciona mesmo antes dela entrar na main.
    """
    return Persistencia.cadastrar_usuario(
        email="dono@teste.com", senha_hash="hash_ficticio", tipo_perfil="pessoa_fisica"
    )


@pytest.fixture
def gerenciador(usuario_id):
    """Gerenciador limpo, amarrado ao usuário da fixture usuario_id."""
    return Gerenciador(usuario_id)


@pytest.fixture
def gerenciador_populado(gerenciador):
    """Gerenciador com três transações já persistidas (datas como ISO str)."""
    gerenciador.adicionar_receita("Salário", 3000.0, "Salário", "2026-04-01")
    gerenciador.adicionar_despesa("Mercado", 500.0, "Alimentação", "2026-04-02")
    gerenciador.adicionar_despesa("Uber", 50.0, "Transporte", "2026-04-03")
    return gerenciador


# ---------------------------------------------------------------------------
# Transações — criação e validação
# ---------------------------------------------------------------------------

class TestAdicionarTransacoes:

    def test_adicionar_receita_retorna_id(self, gerenciador):
        """adicionar_receita persiste e devolve o id gerado pelo banco."""
        novo_id = gerenciador.adicionar_receita("Salário", 3000.0, "Salário")
        assert isinstance(novo_id, int) and novo_id > 0

    def test_adicionar_despesa_retorna_id(self, gerenciador):
        novo_id = gerenciador.adicionar_despesa("Mercado", 200.0, "Alimentação")
        assert isinstance(novo_id, int) and novo_id > 0

    def test_valor_invalido_levanta_excecao(self, gerenciador):
        """Valor <= 0 deve ser barrado antes de tocar o banco."""
        with pytest.raises(ValueError):
            gerenciador.adicionar_receita("Teste", -100.0, "Outros")

    def test_descricao_vazia_levanta_excecao(self, gerenciador):
        with pytest.raises(ValueError):
            gerenciador.adicionar_despesa("   ", 100.0, "Outros")


# ---------------------------------------------------------------------------
# Saldo
# ---------------------------------------------------------------------------

class TestSaldo:

    def test_saldo_vazio_e_zero(self, gerenciador):
        assert gerenciador.saldo_atual() == 0.0

    def test_saldo_com_receitas_e_despesas(self, gerenciador_populado):
        # 3000 - (500 + 50) = 2450
        assert gerenciador_populado.saldo_atual() == 2450.0


# ---------------------------------------------------------------------------
# Listagem e filtros
# ---------------------------------------------------------------------------

class TestListarFiltrar:

    def test_listar_todas(self, gerenciador_populado):
        assert len(gerenciador_populado.listar_transacoes()) == 3

    def test_filtrar_por_tipo_despesa(self, gerenciador_populado):
        despesas = gerenciador_populado.listar_transacoes(tipo="despesa")
        assert len(despesas) == 2
        assert all(t.tipo() == "despesa" for t in despesas)

    def test_filtrar_por_tipo_receita(self, gerenciador_populado):
        receitas = gerenciador_populado.listar_transacoes(tipo="receita")
        assert len(receitas) == 1
        assert receitas[0].tipo() == "receita"

    def test_filtrar_por_categoria(self, gerenciador_populado):
        transporte = gerenciador_populado.listar_transacoes(categoria="Transporte")
        assert len(transporte) == 1
        assert transporte[0].descricao == "Uber"

    def test_filtrar_sem_resultados(self, gerenciador_populado):
        assert gerenciador_populado.listar_transacoes(categoria="Inexistente") == []


# ---------------------------------------------------------------------------
# Remoção por id (não por posição)
# ---------------------------------------------------------------------------

class TestRemover:

    def test_remover_transacao_por_id(self, gerenciador):
        novo_id = gerenciador.adicionar_receita("Bônus", 800.0, "Salário")
        gerenciador.remover_transacao(novo_id)
        assert gerenciador.listar_transacoes() == []

    def test_remover_transacao_de_outro_usuario_nao_funciona(self, gerenciador, usuario_id):
        """
        Defesa em profundidade: o DELETE filtra WHERE id = ? AND usuario_id = ?.
        Um Gerenciador de outro usuário não apaga a transação alheia mesmo
        conhecendo o id.
        """
        id_transacao = gerenciador.adicionar_receita("Salário A", 1000.0, "Salário")

        outro_id = Persistencia.cadastrar_usuario(
            email="intruso@teste.com", senha_hash="h", tipo_perfil="empresa"
        )
        gerenciador_intruso = Gerenciador(outro_id)
        gerenciador_intruso.remover_transacao(id_transacao)  # deve ser no-op

        assert len(gerenciador.listar_transacoes()) == 1, "FALHA: intruso apagou dado alheio!"


# ---------------------------------------------------------------------------
# Metas
# ---------------------------------------------------------------------------

class TestMetas:

    def test_adicionar_meta_retorna_id(self, gerenciador):
        novo_id = gerenciador.adicionar_meta("Viagem", 1500.0)
        assert isinstance(novo_id, int) and novo_id > 0

    def test_adicionar_meta_persiste_prazo(self, gerenciador):
        """O prazo informado como ISO deve sobreviver ao round-trip no banco."""
        gerenciador.adicionar_meta("Viagem", 1500.0, "2026-12-31")
        meta = gerenciador.listar_metas()[0]
        assert meta.prazo.isoformat() == "2026-12-31"

    def test_depositar_em_meta(self, gerenciador):
        meta_id = gerenciador.adicionar_meta("Reserva", 1000.0)
        gerenciador.depositar_em_meta(meta_id, 250.0)
        assert gerenciador.listar_metas()[0].valor_atual == 250.0

    def test_depositar_valor_invalido_levanta(self, gerenciador):
        meta_id = gerenciador.adicionar_meta("Reserva", 1000.0)
        with pytest.raises(ValueError):
            gerenciador.depositar_em_meta(meta_id, -10.0)

    def test_depositar_meta_inexistente_levanta_lookup(self, gerenciador):
        with pytest.raises(LookupError):
            gerenciador.depositar_em_meta(9999, 100.0)

    def test_remover_meta_por_id(self, gerenciador):
        meta_id = gerenciador.adicionar_meta("Temporária", 500.0)
        gerenciador.remover_meta(meta_id)
        assert gerenciador.listar_metas() == []


# ---------------------------------------------------------------------------
# Isolamento entre usuários — o teste mais importante da arquitetura web
# ---------------------------------------------------------------------------

class TestIsolamento:

    def test_usuarios_nao_veem_dados_um_do_outro(self, banco_limpo):
        id_a = Persistencia.cadastrar_usuario(
            email="a@teste.com", senha_hash="h", tipo_perfil="pessoa_fisica"
        )
        id_b = Persistencia.cadastrar_usuario(
            email="b@teste.com", senha_hash="h", tipo_perfil="empresa"
        )
        g_a, g_b = Gerenciador(id_a), Gerenciador(id_b)

        g_a.adicionar_receita("Salário A", 1000.0, "Salário")

        assert len(g_a.listar_transacoes()) == 1
        assert g_b.listar_transacoes() == [], "FALHA DE ISOLAMENTO: B vê dados de A!"
        assert g_b.saldo_atual() == 0.0
