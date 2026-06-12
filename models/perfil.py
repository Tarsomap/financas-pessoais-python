# models/perfil.py
# RESPONSÁVEL: Pessoa 2 (João Gustavo Lima dos Santos) - Frente 2

from abc import ABC, abstractmethod


class Perfil(ABC):
    """Classe base dos perfis de usuário. Não pode ser instanciada direto."""

    @abstractmethod
    def categorias_disponiveis(self) -> list:
        """Categorias de transação que esse perfil pode usar."""
        pass

    @abstractmethod
    def tipo_str(self) -> str:
        """Valor salvo na coluna tipo_perfil do banco."""
        pass

    def __str__(self) -> str:
        return self.tipo_str()


class PessoaFisica(Perfil):
    """Perfil de pessoa física - finanças do dia a dia."""

    CATEGORIAS = [
        "Alimentação",
        "Transporte",
        "Saúde",
        "Educação",
        "Lazer",
        "Moradia",
        "Salário",
        "Outros",
    ]

    def categorias_disponiveis(self) -> list:
        return list(self.CATEGORIAS)

    def tipo_str(self) -> str:
        return "pessoa_fisica"


class Empresa(Perfil):
    """Perfil de empresa - foco em fluxo de caixa e contas."""

    CATEGORIAS = [
        "Vendas",
        "Serviços Prestados",
        "Fornecedores",
        "Folha de Pagamento",
        "Impostos",
        "Marketing",
        "Infraestrutura",
        "Outros",
    ]

    def categorias_disponiveis(self) -> list:
        return list(self.CATEGORIAS)

    def tipo_str(self) -> str:
        return "empresa"


def criar_perfil(tipo: str) -> Perfil:
    """Factory: recebe o texto do banco e devolve o Perfil certo."""
    if not tipo:
        raise ValueError("Tipo de perfil não pode ser vazio.")

    tipo = tipo.strip().lower()

    if tipo == "pessoa_fisica":
        return PessoaFisica()
    if tipo == "empresa":
        return Empresa()

    raise ValueError(f"Tipo de perfil desconhecido: '{tipo}'")