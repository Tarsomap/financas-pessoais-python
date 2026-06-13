"""
test_usuario.py — Testa o model Usuario e o cadastro/busca via Persistencia (Frente 1).

Conceitos cobertos:
    - Construção correta do objeto Usuario
    - Busca por email e por id devolve o objeto certo
    - Email duplicado é rejeitado pelo banco
    - Usuário inexistente devolve None (não estoura exceção)
"""

import pytest

# Depende das Frentes 1 (auth + usuario) e 2 (perfil). Enquanto não
# estiverem na main, este arquivo é PULADO inteiro — não quebra a suíte.
pytest.importorskip("services.auth")
pytest.importorskip("models.usuario")
pytest.importorskip("models.perfil")

from models.usuario import Usuario
from models.perfil import PessoaFisica, Empresa
from services.persistencia import Persistencia
from services.auth import gerar_hash


class TestModelUsuario:
    """Testa o model Usuario isoladamente, sem banco."""

    def test_atributos_basicos(self):
        """
        O construtor deve expor id, email, senha_hash e perfil.
        Usamos um PessoaFisica() real para testar a composição.
        """
        perfil = PessoaFisica()
        u = Usuario(id=1, email="a@b.com", senha_hash="hash123", perfil=perfil)

        assert u.id == 1
        assert u.email == "a@b.com"
        assert u.senha_hash == "hash123"
        assert u.perfil is perfil

    def test_perfil_acessivel_via_usuario(self):
        """A composição Usuario→Perfil deve funcionar: u.perfil.tipo_str()."""
        u = Usuario(id=1, email="x@x.com", senha_hash="h", perfil=Empresa())
        assert u.perfil.tipo_str() == "empresa"


class TestCadastroEBusca:
    """Testa fluxo completo de cadastro e recuperação do banco."""

    def test_cadastrar_usuario_retorna_id_inteiro(self, banco_limpo):
        """
        banco_limpo é uma fixture do conftest.py — o pytest injeta
        automaticamente antes de rodar este teste.
        """
        id_criado = Persistencia.cadastrar_usuario(
            email="novo@teste.com",
            senha_hash=gerar_hash("senha"),
            tipo_perfil="pessoa_fisica"
        )
        assert isinstance(id_criado, int)
        assert id_criado > 0

    def test_buscar_por_email_existente(self, banco_limpo):
        Persistencia.cadastrar_usuario("alice@teste.com", gerar_hash("123"), "pessoa_fisica")
        usuario = Persistencia.buscar_usuario_por_email("alice@teste.com")

        assert usuario is not None
        assert usuario.email == "alice@teste.com"
        assert isinstance(usuario.perfil, PessoaFisica)

    def test_buscar_por_email_inexistente_retorna_none(self, banco_limpo):
        """Não deve estourar exceção — simplesmente retorna None."""
        usuario = Persistencia.buscar_usuario_por_email("naoexiste@teste.com")
        assert usuario is None

    def test_buscar_por_id_existente(self, banco_limpo):
        id_criado = Persistencia.cadastrar_usuario("bob@teste.com", gerar_hash("abc"), "empresa")
        usuario = Persistencia.buscar_usuario_por_id(id_criado)

        assert usuario is not None
        assert usuario.id == id_criado
        assert isinstance(usuario.perfil, Empresa)

    def test_buscar_por_id_inexistente_retorna_none(self, banco_limpo):
        usuario = Persistencia.buscar_usuario_por_id(99999)
        assert usuario is None

    def test_email_duplicado_deve_falhar(self, banco_limpo):
        """
        A coluna email tem UNIQUE no schema — o banco deve rejeitar o segundo cadastro.
        sqlite3 lança uma exceção de integridade nesses casos.
        """
        import sqlite3
        Persistencia.cadastrar_usuario("dup@teste.com", gerar_hash("a"), "pessoa_fisica")
        with pytest.raises(sqlite3.IntegrityError):
            Persistencia.cadastrar_usuario("dup@teste.com", gerar_hash("b"), "empresa")

    def test_tipo_perfil_persistido_corretamente(self, banco_limpo):
        """
        O texto salvo no banco deve gerar o objeto Python certo ao carregar.
        Isso garante que a factory funciona no ciclo completo salvar→carregar.
        """
        Persistencia.cadastrar_usuario("emp@teste.com", gerar_hash("x"), "empresa")
        usuario = Persistencia.buscar_usuario_por_email("emp@teste.com")
        assert isinstance(usuario.perfil, Empresa)
