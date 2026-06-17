# =============================================================================
# models/usuario.py
# -----------------------------------------------------------------------------
# Define o modelo Usuario — a entidade que representa uma pessoa cadastrada
# no sistema. Cada usuário tem email, senha (hash) e um perfil (PessoaFisica
# ou Empresa) que determina quais funcionalidades e categorias ele pode usar.
#
# CONCEITOS APLICADOS:
#   - Composição: Usuario TEM UM Perfil (não herda dele). Isso permite trocar
#     o perfil sem mudar a classe do usuário — princípio "favor composition
#     over inheritance" do Design Orientado a Objetos.
#   - Factory delegada: quando o construtor recebe tipo_perfil (string do
#     banco) em vez de um objeto Perfil pronto, ele chama criar_perfil()
#     para instanciar o perfil correto. Assim a Persistencia não precisa
#     saber sobre PessoaFisica/Empresa — só passa a string e o model resolve.
#   - Validação no construtor: email e senha_hash não podem ser vazios;
#     pelo menos perfil OU tipo_perfil deve ser informado. Erros são
#     levantados cedo (fail fast) para evitar objetos em estado inválido.
#   - Normalização: email é convertido para minúsculas e sem espaços
#     laterais, garantindo que "Fulano@Email.COM" e "fulano@email.com"
#     sejam tratados como o mesmo usuário.
#   - Annotations futuras (from __future__ import annotations): permite
#     usar Perfil | None como type hint sem causar NameError na importação.
#     Sem esse import, Python tentaria avaliar o tipo na hora da definição
#     da classe, antes de Perfil estar importado — com ele, type hints
#     são tratados como strings e avaliados apenas quando necessário.
#
# RESPONSÁVEL: João Guilherme Costa ("Jigui") - Frente 1
# =============================================================================

from __future__ import annotations

from models.perfil import Perfil, criar_perfil


class Usuario:
    """
    Usuário autenticável do sistema.

    Armazena as credenciais (email + hash da senha) e o perfil que define
    quais funcionalidades estão disponíveis. O id vem do banco (PRIMARY KEY
    autoincrement) e é passado no construtor ao carregar — nunca gerado aqui.

    Uso típico:
        # Pelo service de autenticação (services/auth.py):
        usuario = autenticar('fulano@email.com', 'senha123')
        # Pela Persistencia ao carregar do banco:
        usuario = Usuario(id=1, email='fulano@email.com',
                          senha_hash='pbkdf2...', tipo_perfil='pessoa_fisica')
    """

    def __init__(
        self,
        id: int,
        email: str,
        senha_hash: str,
        perfil: Perfil | None = None,
        tipo_perfil: str | None = None,
    ):
        """
        Inicializa um usuário com validação dos dados obrigatórios.

        Aceita perfil (objeto) OU tipo_perfil (string) — pelo menos um deve
        ser informado. Quando só tipo_perfil é passado (caso da Persistencia),
        criar_perfil() converte a string no objeto Perfil correto.

        Parâmetros:
            id          (int)          : identificador único vindo do banco
            email       (str)          : endereço de e-mail (será normalizado)
            senha_hash  (str)          : hash da senha (nunca a senha em texto)
            perfil      (Perfil, opt)  : objeto Perfil já instanciado
            tipo_perfil (str, opt)     : string do banco ('pessoa_fisica'/'empresa')

        Lança:
            ValueError se email ou senha_hash forem vazios, ou se nenhum perfil
            for informado (nem objeto nem string).
        """
        if not email or not email.strip():
            raise ValueError("Email nao pode ser vazio.")
        if not senha_hash:
            raise ValueError("Hash da senha nao pode ser vazio.")

        # Se não recebeu objeto Perfil, precisa receber a string para criá-lo.
        # Esse duplo caminho existe para flexibilidade: o service de auth monta
        # o Perfil antes; a Persistencia passa só a string do banco.
        if perfil is None:
            if tipo_perfil is None:
                raise ValueError("Perfil do usuario deve ser informado.")
            perfil = criar_perfil(tipo_perfil)

        self.id = id
        # strip().lower() normaliza o email: "  Fulano@Email.COM  " → "fulano@email.com"
        # Sem isso, o mesmo usuário poderia ter cadastros "diferentes" por variação de caixa.
        self.email = email.strip().lower()
        # Armazena o HASH, nunca a senha em texto — princípio básico de segurança.
        # A verificação é feita em services/auth.py com comparação de hash.
        self.senha_hash = senha_hash
        self.perfil = perfil

    # -------------------------------------------------------------------------
    # Propriedades
    # -------------------------------------------------------------------------

    @property
    def tipo_perfil(self) -> str:
        """
        Texto do perfil usado pela Persistencia para salvar no banco.

        Delega para perfil.tipo_str() (polimorfismo): se o perfil for
        PessoaFisica, retorna 'pessoa_fisica'; se for Empresa, 'empresa'.
        A view também usa isso para decidir o que mostrar (ex.: menu de
        Contas aparece só para perfil empresa).
        """
        return self.perfil.tipo_str()

    # -------------------------------------------------------------------------
    # Representação
    # -------------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Representação técnica para debug — mostra id, email e tipo de perfil.

        Não inclui senha_hash por segurança: evita que o hash apareça
        acidentalmente em logs ou no terminal interativo.
        """
        return (
            f"Usuario(id={self.id}, "
            f"email='{self.email}', "
            f"tipo_perfil='{self.tipo_perfil}')"
        )
