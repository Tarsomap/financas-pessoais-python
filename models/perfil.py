# =============================================================================
# models/perfil.py
# -----------------------------------------------------------------------------
# Define os perfis de usuário usando herança e polimorfismo.
#
# O sistema atende dois públicos diferentes: pessoa física (finanças do
# dia a dia) e empresa (foco em fluxo de caixa e contas a pagar/receber).
# Em vez de usar if/elif para verificar o tipo em cada canto do código,
# criamos uma hierarquia de classes: Perfil (abstrata) → PessoaFisica / Empresa.
# Cada subclasse define suas próprias categorias e seu identificador de tipo.
#
# CONCEITOS APLICADOS:
#   - Classe abstrata (ABC): Perfil não pode ser instanciada diretamente.
#     Obriga as subclasses a implementar categorias_disponiveis() e tipo_str().
#     ABC vem do módulo abc (Abstract Base Class) da biblioteca padrão.
#   - @abstractmethod: decora métodos que DEVEM ser sobrescritos. Se uma
#     subclasse esquecer de implementar, Python levanta TypeError na
#     instanciação — o erro aparece cedo, não em produção.
#   - Herança: PessoaFisica e Empresa herdam de Perfil, reaproveitando
#     __str__ e o contrato da interface sem duplicar código.
#   - Polimorfismo: código que recebe um Perfil pode chamar tipo_str() ou
#     categorias_disponiveis() sem saber se é PessoaFisica ou Empresa —
#     cada subclasse responde de forma diferente ao mesmo método.
#   - Factory function (criar_perfil): recebe uma string do banco de dados
#     ("pessoa_fisica" ou "empresa") e devolve o objeto Perfil correto.
#     Centraliza a criação num único ponto — se amanhã surgir um terceiro
#     perfil, só este lugar precisa mudar.
#
# RESPONSÁVEL: Pessoa 2 (João Gustavo Lima dos Santos) - Frente 2
# =============================================================================

from abc import ABC, abstractmethod


class Perfil(ABC):
    """
    Classe base abstrata dos perfis de usuário.

    Não pode ser instanciada diretamente — use PessoaFisica() ou Empresa().
    Define o contrato (interface) que todas as subclasses devem seguir:
    cada perfil precisa informar quais categorias de transação estão
    disponíveis e qual é seu identificador textual para o banco.
    """

    @abstractmethod
    def categorias_disponiveis(self) -> list[str]:
        """
        Lista de categorias de transação que este perfil pode usar.

        Cada perfil tem categorias diferentes: pessoa física usa Alimentação,
        Transporte etc.; empresa usa Vendas, Fornecedores etc.

        Retorna:
            Lista de strings com os nomes das categorias.
        """
        pass

    @abstractmethod
    def tipo_str(self) -> str:
        """
        Identificador textual do perfil, salvo na coluna tipo_perfil do banco.

        Retorna:
            'pessoa_fisica' ou 'empresa' — texto usado pela Persistencia.
        """
        pass

    def __str__(self) -> str:
        """Representação legível: delega para tipo_str() (polimorfismo)."""
        return self.tipo_str()


class PessoaFisica(Perfil):
    """
    Perfil de pessoa física — finanças do dia a dia.

    Categorias voltadas para gastos pessoais: alimentação, transporte,
    saúde, educação, lazer, moradia, salário e outros.
    """

    # Categorias são atributo de CLASSE: compartilhadas entre todas as
    # instâncias de PessoaFisica. Não faz sentido cada instância ter sua
    # própria cópia — o perfil é o mesmo para todo PF.
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

    def categorias_disponiveis(self) -> list[str]:
        """Devolve cópia da lista (list()) para que o chamador não altere o original."""
        return list(self.CATEGORIAS)

    def tipo_str(self) -> str:
        """Retorna 'pessoa_fisica' — valor salvo no banco de dados."""
        return "pessoa_fisica"


class Empresa(Perfil):
    """
    Perfil de empresa — foco em fluxo de caixa e contas a pagar/receber.

    Categorias voltadas para operações empresariais: vendas, serviços,
    fornecedores, folha de pagamento, impostos, marketing e infraestrutura.
    """

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

    def categorias_disponiveis(self) -> list[str]:
        """Devolve cópia da lista (list()) para que o chamador não altere o original."""
        return list(self.CATEGORIAS)

    def tipo_str(self) -> str:
        """Retorna 'empresa' — valor salvo no banco de dados."""
        return "empresa"


def criar_perfil(tipo: str) -> Perfil:
    """
    Factory function: recebe o texto do banco e devolve o Perfil certo.

    Por que uma factory em vez de instanciar direto?
        Quando a Persistencia carrega um usuário do banco, ela só tem uma
        string ("pessoa_fisica" ou "empresa"). A factory traduz essa string
        no objeto correto, isolando a lógica de "qual classe instanciar"
        num único ponto. Sem ela, esse if/elif ficaria espalhado em todo
        lugar que precisa reconstruir um Perfil.

    Parâmetros:
        tipo (str) : 'pessoa_fisica' ou 'empresa'

    Retorna:
        Instância de PessoaFisica ou Empresa.

    Lança:
        ValueError se o tipo for vazio ou desconhecido.
    """
    if not tipo:
        raise ValueError("Tipo de perfil não pode ser vazio.")

    # strip().lower() normaliza: " Pessoa_Fisica " → "pessoa_fisica".
    # Protege contra espaços acidentais e variações de caixa.
    tipo = tipo.strip().lower()

    if tipo == "pessoa_fisica":
        return PessoaFisica()
    if tipo == "empresa":
        return Empresa()

    raise ValueError(f"Tipo de perfil desconhecido: '{tipo}'")
