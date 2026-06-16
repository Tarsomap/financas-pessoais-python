from __future__ import annotations

import hashlib
import hmac
import secrets

from models.usuario import Usuario
from services.persistencia import Persistencia


ALGORITMO = "pbkdf2_sha256"
ITERACOES = 260_000
TAMANHO_SALT = 16


def gerar_hash(senha: str) -> str:
    """Gera um hash seguro para salvar a senha no banco."""
    if not senha:
        raise ValueError("Senha nao pode ser vazia.")

    salt = secrets.token_bytes(TAMANHO_SALT)
    senha_hash = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        ITERACOES,
    )
    return f"{ALGORITMO}${ITERACOES}${salt.hex()}${senha_hash.hex()}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Confere se a senha digitada corresponde ao hash salvo."""
    if not senha or not senha_hash:
        return False

    try:
        algoritmo, iteracoes_txt, salt_hex, hash_hex = senha_hash.split("$", 3)
        if algoritmo != ALGORITMO:
            return False

        iteracoes = int(iteracoes_txt)
        salt = bytes.fromhex(salt_hex)
        hash_salvo = bytes.fromhex(hash_hex)
    except (ValueError, TypeError):
        return False

    hash_digitado = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        iteracoes,
    )
    return hmac.compare_digest(hash_digitado, hash_salvo)


def cadastrar_usuario(
    email: str,
    senha: str,
    tipo_perfil: str = "pessoa_fisica",
) -> Usuario:
    """Cadastra um usuario novo e devolve o objeto carregado do banco."""
    email_normalizado = _normalizar_email(email)
    senha_hash = gerar_hash(senha)
    usuario_id = Persistencia.cadastrar_usuario(
        email=email_normalizado,
        senha_hash=senha_hash,
        tipo_perfil=tipo_perfil,
    )
    usuario = Persistencia.buscar_usuario_por_id(usuario_id)
    if usuario is None:
        raise RuntimeError("Usuario cadastrado nao foi encontrado no banco.")
    return usuario


def autenticar(email: str, senha: str) -> Usuario | None:
    """Valida login por email e senha. Retorna None quando falhar."""
    try:
        email_normalizado = _normalizar_email(email)
    except ValueError:
        return None

    usuario = Persistencia.buscar_usuario_por_email(email_normalizado)
    if usuario is None:
        return None

    if verificar_senha(senha, usuario.senha_hash):
        return usuario
    return None


def login(email: str, senha: str) -> Usuario | None:
    """Alias simples para deixar as rotas mais legiveis."""
    return autenticar(email, senha)


def _normalizar_email(email: str) -> str:
    if not email or not email.strip():
        raise ValueError("Email nao pode ser vazio.")
    return email.strip().lower()
