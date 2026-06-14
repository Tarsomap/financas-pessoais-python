# tests/test_fluxo_caixa.py
# RESPONSÁVEL: Tarso - Frente 5 (fluxo de caixa e diferenciação por perfil)

import pytest
from datetime import date

pytest.importorskip("models.conta")

from models.perfil import PessoaFisica, Empresa


class TestPerfilTiposConta:
    def test_empresa_tem_pagar_e_receber(self):
        assert Empresa().tipos_conta() == ("pagar", "receber")

    def test_pessoa_fisica_so_pagar(self):
        assert PessoaFisica().tipos_conta() == ("pagar",)

    def test_permite_tipo_conta(self):
        assert Empresa().permite_tipo_conta("receber") is True
        assert PessoaFisica().permite_tipo_conta("receber") is False
        assert PessoaFisica().permite_tipo_conta("pagar") is True


from models.conta import Conta
from services.fluxo_caixa import FluxoCaixa


def _conta(tipo, valor, vencimento="2026-06-01", pago=False):
    return Conta(tipo=tipo, descricao="x", valor=valor, vencimento=vencimento, pago=pago)


class TestTotais:
    def test_total_a_pagar_soma_pendentes(self):
        contas = [_conta("pagar", 100), _conta("pagar", 50), _conta("receber", 999)]
        assert FluxoCaixa(contas).total_a_pagar() == 150.0

    def test_total_a_receber_soma_pendentes(self):
        contas = [_conta("receber", 300), _conta("receber", 200), _conta("pagar", 999)]
        assert FluxoCaixa(contas).total_a_receber() == 500.0

    def test_pagas_nao_contam(self):
        contas = [_conta("pagar", 100, pago=True), _conta("pagar", 40)]
        assert FluxoCaixa(contas).total_a_pagar() == 40.0


class TestVencimento:
    HOJE = date(2026, 6, 15)

    def test_contas_vencidas_e_total(self):
        contas = [_conta("pagar", 100, vencimento="2026-06-01"),   # vencida
                  _conta("pagar", 50, vencimento="2026-06-30")]    # a vencer
        fc = FluxoCaixa(contas)
        assert len(fc.contas_vencidas(self.HOJE)) == 1
        assert fc.total_vencido(self.HOJE) == 100.0

    def test_contas_a_vencer(self):
        contas = [_conta("pagar", 100, vencimento="2026-06-01"),
                  _conta("pagar", 50, vencimento="2026-06-30")]
        assert len(FluxoCaixa(contas).contas_a_vencer(self.HOJE)) == 1

    def test_paga_nunca_e_vencida(self):
        contas = [_conta("pagar", 100, vencimento="2026-06-01", pago=True)]
        assert FluxoCaixa(contas).contas_vencidas(self.HOJE) == []


class TestDiferenciacaoPerfil:
    def test_empresa_mostra_recebiveis_e_saldo_completo(self):
        contas = [_conta("receber", 1000), _conta("pagar", 400)]
        fc = FluxoCaixa(contas, Empresa())
        assert fc.mostra_recebiveis() is True
        assert fc.saldo_projetado() == 600.0

    def test_pessoa_fisica_sem_recebiveis(self):
        contas = [_conta("pagar", 400)]
        fc = FluxoCaixa(contas, PessoaFisica())
        assert fc.mostra_recebiveis() is False
        assert fc.saldo_projetado() == -400.0

    def test_sem_perfil_assume_empresa(self):
        contas = [_conta("receber", 1000), _conta("pagar", 400)]
        fc = FluxoCaixa(contas)
        assert fc.mostra_recebiveis() is True
        assert fc.saldo_projetado() == 600.0


class TestGerenciadorFluxo:
    def test_fluxo_de_caixa_via_gerenciador(self, banco_limpo):
        from services.persistencia import Persistencia
        from services.gerenciador import Gerenciador

        uid = Persistencia.cadastrar_usuario("e@e.com", "hash_ficticio", "empresa")
        g = Gerenciador(uid)
        g.adicionar_conta("pagar", "Fornecedor", 300.0, "2026-06-01")
        g.adicionar_conta("receber", "Cliente", 500.0, "2026-06-10")

        fc = g.fluxo_de_caixa(Empresa())
        assert fc.total_a_pagar() == 300.0
        assert fc.total_a_receber() == 500.0
        assert fc.saldo_projetado() == 200.0
