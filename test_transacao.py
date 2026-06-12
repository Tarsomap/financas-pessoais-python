"""
test_transacao.py — Testa os models de transação e persistência (adaptado ao usuario_id).

EDITADO: remoção agora usa id (não posição), e todas as operações
recebem usuario_id explicitamente.
"""

import pytest
from models.transacao import Transacao, Receita, Despesa
from services.persistencia import Persistencia
from services.auth import gerar_hash


class TestModelTransacao:

    def test_receita_tem_tipo_correto(self):
        r = Receita(descricao="Salário", valor=3000.0, categoria="salario")
        assert r.tipo == "receita"

    def test_despesa_tem_tipo_correto(self):
        d = Despesa(descricao="Aluguel", valor=1200.0, categoria="moradia")
        assert d.tipo == "despesa"

    def test_atributos_preservados(self):
        r = Receita(descricao="Freelance", valor=500.0, categoria="servicos", data="2024-06-01")
        assert r.descricao == "Freelance"
        assert r.valor == 500.0
        assert r.categoria == "servicos"
        assert r.data == "2024-06-01"

    def test_receita_e_subclasse_de_transacao(self):
        assert issubclass(Receita, Transacao)

    def test_despesa_e_subclasse_de_transacao(self):
        assert issubclass(Despesa, Transacao)


class TestTransacaoPersistencia:

    def test_salvar_e_carregar_receita(self, banco_limpo):
        id_u = Persistencia.cadastrar_usuario("t@t.com", gerar_hash("s"), "pessoa_fisica")
        r = Receita(descricao="Salário", valor=3000.0, categoria="salario", data="2024-06-01")

        Persistencia.salvar_transacao(r, id_u)
        transacoes = Persistencia.carregar_transacoes(id_u)

        assert len(transacoes) == 1
        assert isinstance(transacoes[0], Receita)
        assert transacoes[0].valor == 3000.0

    def test_salvar_e_carregar_despesa(self, banco_limpo):
        id_u = Persistencia.cadastrar_usuario("u@u.com", gerar_hash("s"), "pessoa_fisica")
        d = Despesa(descricao="Aluguel", valor=1200.0, categoria="moradia", data="2024-06-01")

        Persistencia.salvar_transacao(d, id_u)
        transacoes = Persistencia.carregar_transacoes(id_u)

        assert isinstance(transacoes[0], Despesa)

    def test_remover_transacao_por_id(self, banco_limpo):
        """CONTRATO NOVO: remover por id (PRIMARY KEY), não por índice."""
        id_u = Persistencia.cadastrar_usuario("v@v.com", gerar_hash("s"), "pessoa_fisica")
        r = Receita(descricao="Bônus", valor=800.0, categoria="bonus", data="2024-06-01")

        id_transacao = Persistencia.salvar_transacao(r, id_u)
        Persistencia.remover_transacao(id_transacao, id_u)

        assert len(Persistencia.carregar_transacoes(id_u)) == 0

    def test_isolamento_transacoes(self, dois_usuarios):
        """Transações de A não aparecem para B."""
        id_a = dois_usuarios["id_a"]
        id_b = dois_usuarios["id_b"]

        r = Receita(descricao="Receita de A", valor=1000.0, categoria="salario", data="2024-06-01")
        Persistencia.salvar_transacao(r, id_a)

        transacoes_b = Persistencia.carregar_transacoes(id_b)
        assert len(transacoes_b) == 0
