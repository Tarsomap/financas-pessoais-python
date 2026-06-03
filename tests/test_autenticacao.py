import pytest

from services.autenticacao import Autenticacao
from services.persistencia import Persistencia


@pytest.fixture(autouse=True)
def banco_temporario(tmp_path, monkeypatch):
    caminho_banco = tmp_path / "financas.db"
    monkeypatch.setattr("services.persistencia.CAMINHO_BANCO", str(caminho_banco))
    Persistencia.inicializar_banco()


def test_cadastrar_usuario_salva_email_normalizado_e_hash():
    usuario = Autenticacao.cadastrar("Pessoa@Email.com", "senha-segura-123")

    assert usuario.id is not None
    assert usuario.email == "pessoa@email.com"
    assert usuario.tipo_perfil == "pessoal"
    assert usuario.senha_hash != "senha-segura-123"
    assert usuario.senha_hash.startswith("pbkdf2_sha256$")


def test_cadastrar_usuario_empresa():
    usuario = Autenticacao.cadastrar(
        "empresa@email.com",
        "senha-segura-123",
        tipo_perfil="empresa",
    )

    assert usuario.tipo_perfil == "empresa"


def test_cadastrar_email_repetido_levanta_erro():
    Autenticacao.cadastrar("pessoa@email.com", "senha-segura-123")

    with pytest.raises(ValueError):
        Autenticacao.cadastrar("PESSOA@email.com", "outra-senha-123")


def test_autenticar_credenciais_validas_retorna_usuario():
    cadastrado = Autenticacao.cadastrar("pessoa@email.com", "senha-segura-123")

    autenticado = Autenticacao.autenticar("PESSOA@email.com", "senha-segura-123")

    assert autenticado is not None
    assert autenticado.id == cadastrado.id
    assert autenticado.email == "pessoa@email.com"


def test_autenticar_senha_incorreta_retorna_none():
    Autenticacao.cadastrar("pessoa@email.com", "senha-segura-123")

    assert Autenticacao.autenticar("pessoa@email.com", "senha-errada") is None


def test_login_invalido_levanta_erro_generico():
    with pytest.raises(ValueError, match="E-mail ou senha invalidos"):
        Autenticacao.login("naoexiste@email.com", "senha-segura-123")


def test_senha_curta_levanta_erro():
    with pytest.raises(ValueError):
        Autenticacao.cadastrar("pessoa@email.com", "curta")
