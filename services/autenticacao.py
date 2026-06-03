from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3

from models.usuario import Usuario
from services.persistencia import Persistencia


class Autenticacao:
    """
    Servico de cadastro e login.

    Mantem regras de autenticacao fora da camada SQLite. Assim a interface
    futura, seja CLI, API ou web, chama este servico sem conhecer detalhes de
    hash, salt ou formato das tabelas.
    """

    _ALGORITMO = "pbkdf2_sha256"
    _ITERACOES = 120_000
    _TAMANHO_SALT = 16
    _TAMANHO_CHAVE = 32
    _TAMANHO_MINIMO_SENHA = 8

    @staticmethod
    def cadastrar(email: str, senha: str, tipo_perfil: str = "pessoal") -> Usuario:
        """
        Cria um usuario e retorna o objeto salvo no banco.

        Levanta ValueError quando os dados forem invalidos ou o e-mail ja
        estiver cadastrado.
        """
        Persistencia.inicializar_banco()

        email_normalizado = Autenticacao._normalizar_email(email)
        Autenticacao._validar_senha(senha)

        if Persistencia.buscar_usuario_por_email(email_normalizado) is not None:
            raise ValueError("E-mail ja cadastrado.")

        usuario_sem_id = Usuario(
            id=None,
            email=email_normalizado,
            senha_hash=Autenticacao._gerar_hash_senha(senha),
            tipo_perfil=tipo_perfil,
        )

        try:
            usuario_id = Persistencia.cadastrar_usuario(
                usuario_sem_id.email,
                usuario_sem_id.senha_hash,
                usuario_sem_id.tipo_perfil,
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("E-mail ja cadastrado.") from exc

        return Usuario(
            id=usuario_id,
            email=usuario_sem_id.email,
            senha_hash=usuario_sem_id.senha_hash,
            tipo_perfil=usuario_sem_id.tipo_perfil,
        )

    @staticmethod
    def autenticar(email: str, senha: str) -> Usuario | None:
        """
        Valida credenciais.

        Retorna Usuario quando o login for valido, ou None para e-mail/senha
        incorretos. A mensagem unica evita revelar qual parte falhou.
        """
        Persistencia.inicializar_banco()

        email_normalizado = Autenticacao._normalizar_email(email)
        usuario = Persistencia.buscar_usuario_por_email(email_normalizado)
        if usuario is None:
            return None
        if not Autenticacao._verificar_senha(senha, usuario.senha_hash):
            return None
        return usuario

    @staticmethod
    def login(email: str, senha: str) -> Usuario:
        """Variante que levanta ValueError quando as credenciais falham."""
        usuario = Autenticacao.autenticar(email, senha)
        if usuario is None:
            raise ValueError("E-mail ou senha invalidos.")
        return usuario

    @staticmethod
    def _normalizar_email(email: str) -> str:
        if not isinstance(email, str):
            raise ValueError("E-mail invalido.")
        email_normalizado = email.strip().lower()
        if not email_normalizado or "@" not in email_normalizado:
            raise ValueError("E-mail invalido.")
        return email_normalizado

    @staticmethod
    def _validar_senha(senha: str) -> None:
        if not isinstance(senha, str) or len(senha) < Autenticacao._TAMANHO_MINIMO_SENHA:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")

    @staticmethod
    def _gerar_hash_senha(senha: str) -> str:
        salt = secrets.token_bytes(Autenticacao._TAMANHO_SALT)
        chave = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            salt,
            Autenticacao._ITERACOES,
            dklen=Autenticacao._TAMANHO_CHAVE,
        )
        return (
            f"{Autenticacao._ALGORITMO}$"
            f"{Autenticacao._ITERACOES}$"
            f"{salt.hex()}$"
            f"{chave.hex()}"
        )

    @staticmethod
    def _verificar_senha(senha: str, senha_hash: str) -> bool:
        if not isinstance(senha, str):
            return False

        try:
            algoritmo, iteracoes, salt_hex, chave_hex = senha_hash.split("$")
            if algoritmo != Autenticacao._ALGORITMO:
                return False

            chave_calculada = hashlib.pbkdf2_hmac(
                "sha256",
                senha.encode("utf-8"),
                bytes.fromhex(salt_hex),
                int(iteracoes),
                dklen=len(bytes.fromhex(chave_hex)),
            )
        except (ValueError, TypeError):
            return False

        return hmac.compare_digest(chave_calculada.hex(), chave_hex)
