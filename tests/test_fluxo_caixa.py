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
