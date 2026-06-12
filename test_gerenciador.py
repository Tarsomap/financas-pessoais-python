"""
test_gerenciador.py — Testa o Gerenciador adaptado ao usuario_id (Frente 3).

EDITADO para refletir o novo contrato: Gerenciador(usuario_id) no construtor
e remoção por id (não por posição na lista).

Conceitos cobertos:
    - Gerenciador amarra as operações a um usuario_id específico
    - Saldo calculado corretamente a partir do banco
    - ISOLAMENTO ENTRE USUÁRIOS — o teste mais importante desta suíte
"""

import pytest
from services.gerenciador import Gerenciador
from services.persistencia import Persistencia
from services.auth import gerar_hash


class TestGerenciadorTransacoes:

    def test_adicionar_receita_e_listar(self, banco_limpo):
        id_u = Persistencia.cadastrar_usuario("a@a.com", gerar_hash("s"), "pessoa_fisica")
        g = Gerenciador(id_u)

        g.adicionar_receita("Salário", 3000.0, "salario")
        transacoes = g.listar_transacoes()

        assert len(transacoes) == 1
        assert transacoes[0].descricao == "Salário"
        assert transacoes[0].valor == 3000.0

    def test_adicionar_despesa_e_listar(self, banco_limpo):
        id_u = Persistencia.cadastrar_usuario("b@b.com", gerar_hash("s"), "pessoa_fisica")
        g = Gerenciador(id_u)

        g.adicionar_despesa("Aluguel", 1200.0, "moradia")
        transacoes = g.listar_transacoes()

        assert len(transacoes) == 1
        assert transacoes[0].tipo == "despesa"

    def test_saldo_atual_soma_corretamente(self, banco_limpo):
        """saldo = receitas - despesas."""
        id_u = Persistencia.cadastrar_usuario("c@c.com", gerar_hash("s"), "pessoa_fisica")
        g = Gerenciador(id_u)

        g.adicionar_receita("Salário", 3000.0, "salario")
        g.adicionar_despesa("Aluguel", 1000.0, "moradia")
        g.adicionar_despesa("Mercado", 500.0, "alimentacao")

        assert g.saldo_atual() == pytest.approx(1500.0)

    def test_remover_transacao_por_id(self, banco_limpo):
        """
        CONTRATO NOVO: remoção por id (PRIMARY KEY), não por posição.
        Isso é robusto a filtros e paginação — se a lista for reordenada,
        o id continua apontando para a linha certa.
        """
        id_u = Persistencia.cadastrar_usuario("d@d.com", gerar_hash("s"), "pessoa_fisica")
        g = Gerenciador(id_u)

        id_transacao = g.adicionar_receita("Freelance", 500.0, "servicos")
        g.remover_transacao(id_transacao)

        assert len(g.listar_transacoes()) == 0

    def test_filtrar_transacoes_por_tipo(self, banco_limpo):
        id_u = Persistencia.cadastrar_usuario("e@e.com", gerar_hash("s"), "pessoa_fisica")
        g = Gerenciador(id_u)

        g.adicionar_receita("Salário", 3000.0, "salario")
        g.adicionar_despesa("Conta de luz", 150.0, "servicos")

        receitas = g.listar_transacoes(tipo="receita")
        despesas = g.listar_transacoes(tipo="despesa")

        assert len(receitas) == 1
        assert len(despesas) == 1


class TestIsolamentoEntreUsuarios:
    """
    ================================================================
    O TESTE MAIS IMPORTANTE DA SUÍTE INTEIRA.
    ================================================================

    Por que testar isolamento é crítico?
        É a regra de segurança mais fundamental do sistema multiusuário.
        Se o isolamento furar, o usuário A pode ver as transações do
        usuário B — vazamento de dados financeiros sigilosos.

        Um sistema que funciona mas não isola é PIOR do que um que não
        funciona — porque o dano é silencioso.

    Como o isolamento é garantido?
        Cada método da Persistencia tem WHERE usuario_id = ?.
        O Gerenciador guarda o usuario_id internamente e nunca deixa
        a view passá-lo diretamente.
    """

    def test_usuario_a_nao_ve_transacoes_do_usuario_b(self, dois_usuarios):
        """
        Cenário:
            - Usuário A lança uma receita
            - Usuário B lista suas transações
            - B não deve ver absolutamente nada de A
        """
        id_a = dois_usuarios["id_a"]
        id_b = dois_usuarios["id_b"]

        gerenciador_a = Gerenciador(id_a)
        gerenciador_b = Gerenciador(id_b)

        # A lança uma transação
        gerenciador_a.adicionar_receita("Salário sigiloso de A", 9999.0, "salario")

        # B não deve ver nada
        transacoes_b = gerenciador_b.listar_transacoes()
        assert len(transacoes_b) == 0, (
            "FALHA DE ISOLAMENTO: o usuário B está vendo transações do usuário A! "
            "Isso é um vazamento de dados."
        )

    def test_saldo_de_b_nao_inclui_transacoes_de_a(self, dois_usuarios):
        """
        O saldo de B deve ser 0, não afetado pelas transações de A.
        """
        id_a = dois_usuarios["id_a"]
        id_b = dois_usuarios["id_b"]

        Gerenciador(id_a).adicionar_receita("Bônus de A", 50000.0, "bonus")

        saldo_b = Gerenciador(id_b).saldo_atual()
        assert saldo_b == pytest.approx(0.0), (
            f"FALHA DE ISOLAMENTO: saldo de B é {saldo_b}, deveria ser 0.0"
        )

    def test_cada_usuario_ve_apenas_seus_proprios_dados(self, dois_usuarios):
        """
        Teste completo: A e B lançam transações diferentes.
        Cada um lista e vê SOMENTE as suas.
        """
        id_a = dois_usuarios["id_a"]
        id_b = dois_usuarios["id_b"]

        g_a = Gerenciador(id_a)
        g_b = Gerenciador(id_b)

        g_a.adicionar_receita("Receita de A", 1000.0, "salario")
        g_a.adicionar_despesa("Despesa de A", 200.0, "outros")

        g_b.adicionar_receita("Receita de B", 5000.0, "servicos")

        transacoes_a = g_a.listar_transacoes()
        transacoes_b = g_b.listar_transacoes()

        # A só vê suas 2 transações
        assert len(transacoes_a) == 2
        # B só vê sua 1 transação
        assert len(transacoes_b) == 1

        # Nenhuma transação de B aparece para A
        descricoes_a = [t.descricao for t in transacoes_a]
        assert "Receita de B" not in descricoes_a

        # Nenhuma transação de A aparece para B
        descricoes_b = [t.descricao for t in transacoes_b]
        assert "Receita de A" not in descricoes_b
        assert "Despesa de A" not in descricoes_b


class TestGerenciadorMetas:

    def test_adicionar_e_listar_meta(self, banco_limpo):
        id_u = Persistencia.cadastrar_usuario("m@m.com", gerar_hash("s"), "pessoa_fisica")
        g = Gerenciador(id_u)

        g.adicionar_meta("Viagem", 5000.0, prazo="2024-12-31")
        metas = g.listar_metas()

        assert len(metas) == 1
        assert metas[0].nome == "Viagem"

    def test_depositar_em_meta(self, banco_limpo):
        id_u = Persistencia.cadastrar_usuario("n@n.com", gerar_hash("s"), "pessoa_fisica")
        g = Gerenciador(id_u)

        id_meta = g.adicionar_meta("Reserva", 1000.0)
        g.depositar_em_meta(id_meta, 300.0)
        g.depositar_em_meta(id_meta, 200.0)

        metas = g.listar_metas()
        assert metas[0].valor_atual == pytest.approx(500.0)
