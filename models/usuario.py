from __future__ import annotations

from models.perfil import Perfil, criar_perfil


class Usuario:
    """Usuario autenticavel do sistema."""

    def __init__(
        self,
        id: int,
        email: str,
        senha_hash: str,
        perfil: Perfil | None = None,
        tipo_perfil: str | None = None,
    ):
        if not email or not email.strip():
            raise ValueError("Email nao pode ser vazio.")
        if not senha_hash:
            raise ValueError("Hash da senha nao pode ser vazio.")

        if perfil is None:
            if tipo_perfil is None:
                raise ValueError("Perfil do usuario deve ser informado.")
            perfil = criar_perfil(tipo_perfil)

        self.id = id
        self.email = email.strip().lower()
        self.senha_hash = senha_hash
        self.perfil = perfil

    @property
    def tipo_perfil(self) -> str:
        """Texto usado pela persistencia para representar o perfil."""
        return self.perfil.tipo_str()

    def __repr__(self) -> str:
        return (
            f"Usuario(id={self.id}, "
            f"email='{self.email}', "
            f"tipo_perfil='{self.tipo_perfil}')"
        )
