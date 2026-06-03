from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Usuario:
    """Representa uma conta autenticavel do sistema."""

    PERFIS_VALIDOS: ClassVar[set[str]] = {"pessoal", "empresa"}

    id: int | None
    email: str
    senha_hash: str
    tipo_perfil: str = "pessoal"

    def __post_init__(self) -> None:
        email = self.email.strip().lower()
        tipo_perfil = self.tipo_perfil.strip().lower()

        if self.id is not None and self.id <= 0:
            raise ValueError("O id do usuario deve ser positivo.")
        if not email or "@" not in email:
            raise ValueError("E-mail invalido.")
        if not self.senha_hash:
            raise ValueError("Hash da senha nao pode ser vazio.")
        if tipo_perfil not in self.PERFIS_VALIDOS:
            perfis = ", ".join(sorted(self.PERFIS_VALIDOS))
            raise ValueError(f"Tipo de perfil invalido. Use: {perfis}.")

        object.__setattr__(self, "email", email)
        object.__setattr__(self, "tipo_perfil", tipo_perfil)
