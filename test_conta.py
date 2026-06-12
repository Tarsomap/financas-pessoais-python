"""
test_conta.py — Testa o model Conta e as operações de contas a pagar/receber (Frente 5).

Conceitos cobertos:
    - Construção correta do model Conta
    - Salvar, listar e marcar como paga via Persistencia
    - Isolamento: contas do usuário A não aparecem para o usuário B
    - Remoção por id + usuario_id (defesa em profundidade)
"""

import pytest
from models.conta import Conta
from services.persistencia import Persistencia
from services.gerenciador import Gerenciador
from services.auth import gerar_hash


class TestModelConta:
    """Testa o model Conta isoladamente, sem banco."""

    def test_atributos_basicos(self):
        c = Conta(tipo="pagar", descricao="Aluguel", valor=1500.0, vencimento="2024-06-01")
        assert c.tipo == "pagar"
        assert c.descricao == "Aluguel"
        assert c.valor == 1500.0
        assert c.vencimento == "2024-06-01"
        assert c.pago is False  # padrão

    def test_conta_receber(self):
        c = Conta(tipo="receber", descricao="Nota fiscal", valor=3000.0, vencimento="2024-06-15")
        assert c.tipo == "receber"

    def test_pago_padrao_e_false(self):
        """Toda conta nasce não paga — o padrão deve ser False."""
        c = Conta(tipo="pagar", descricao="X", valor=100.0, vencimento="2024-01-01")
        assert c.pago is False


class TestContaPersistencia:

    def test_salvar_e_listar_conta(self, banco_limpo):
        id_usuario = Persistencia.cadastrar_usuario("u@u.com", gerar_hash("s"), "empresa")
        c = Conta(tipo="pagar", descricao="Fornecedor", valor=500.0, vencimento="2024-07-01")

        Persistencia.salvar_conta(c, id_usuario)
        contas = Persistencia.carregar_contas(id_usuario)

        assert len(contas) == 1
        assert contas[0].descricao == "Fornecedor"
        assert contas[0].tipo == "pagar"
        assert contas[0].pago is False

    def test_marcar_conta_como_paga(self, banco_limpo):
        """
        pago é armazenado como 0/1 no SQLite (sem tipo boolean).
        Após marcar_conta_paga, deve ser carregado como True.
        """
        id_usuario = Persistencia.cadastrar_usuario("emp@emp.com", gerar_hash("s"), "empresa")
        c = Conta(tipo="pagar", descricao="Conta de luz", valor=200.0, vencimento="2024-06-10")
        id_conta = Persistencia.salvar_conta(c, id_usuario)

        Persistencia.marcar_conta_paga(id_conta, id_usuario)
        contas = Persistencia.carregar_contas(id_usuario)

        assert contas[0].pago is True

    def test_remover_conta(self, banco_limpo):
        id_usuario = Persistencia.cadastrar_usuario("x@x.com", gerar_hash("s"), "empresa")
        c = Conta(tipo="receber", descricao="Cliente", valor=1000.0, vencimento="2024-08-01")
        id_conta = Persistencia.salvar_conta(c, id_usuario)

        Persistencia.remover_conta(id_conta, id_usuario)
        contas = Persistencia.carregar_contas(id_usuario)

        assert len(contas) == 0

    def test_isolamento_contas_entre_usuarios(self, dois_usuarios):
        """
        ISOLAMENTO: o usuário B não pode ver as contas do usuário A,
        mesmo que ambos estejam no sistema.

        Por que isso é crítico?
            Uma empresa não pode ver as contas a pagar de outra.
            Esse teste verifica que o WHERE usuario_id = ? está correto.
        """
        id_a = dois_usuarios["id_a"]
        id_b = dois_usuarios["id_b"]

        # Usuário A cria uma conta
        c = Conta(tipo="pagar", descricao="Conta secreta de A", valor=9999.0, vencimento="2024-12-01")
        Persistencia.salvar_conta(c, id_a)

        # Usuário B NÃO deve ver a conta de A
        contas_b = Persistencia.carregar_contas(id_b)
        assert len(contas_b) == 0, "FALHA DE ISOLAMENTO: B está vendo contas de A!"

    def test_remover_conta_de_outro_usuario_nao_funciona(self, dois_usuarios):
        """
        Defesa em profundidade: mesmo conhecendo o id da conta de A,
        o usuário B não consegue apagá-la (WHERE id=? AND usuario_id=?).
        """
        id_a = dois_usuarios["id_a"]
        id_b = dois_usuarios["id_b"]

        c = Conta(tipo="pagar", descricao="Conta de A", valor=500.0, vencimento="2024-06-01")
        id_conta = Persistencia.salvar_conta(c, id_a)

        # B tenta apagar a conta de A usando o id correto
        Persistencia.remover_conta(id_conta, id_b)  # deve ser no-op

        # A conta de A deve continuar existindo
        contas_a = Persistencia.carregar_contas(id_a)
        assert len(contas_a) == 1, "FALHA: B conseguiu apagar conta de A!"


class TestContaViaGerenciador:

    def test_gerenciador_adicionar_e_listar_conta(self, banco_limpo):
        id_usuario = Persistencia.cadastrar_usuario("ger@ger.com", gerar_hash("s"), "empresa")
        g = Gerenciador(id_usuario)

        g.adicionar_conta("pagar", "Aluguel", 2000.0, "2024-06-01")
        contas = g.listar_contas()

        assert len(contas) == 1
        assert contas[0].descricao == "Aluguel"

    def test_gerenciador_filtrar_por_tipo(self, banco_limpo):
        id_usuario = Persistencia.cadastrar_usuario("fil@fil.com", gerar_hash("s"), "empresa")
        g = Gerenciador(id_usuario)

        g.adicionar_conta("pagar", "Fornecedor", 300.0, "2024-06-01")
        g.adicionar_conta("receber", "Cliente", 500.0, "2024-06-15")

        assert len(g.listar_contas(tipo="pagar")) == 1
        assert len(g.listar_contas(tipo="receber")) == 1
        assert len(g.listar_contas()) == 2
