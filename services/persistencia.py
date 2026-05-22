# =============================================================================
# services/persistencia.py  —  Frente 0: fundação SQLite
# -----------------------------------------------------------------------------
# Migra o armazenamento de dados/dados.txt (separador '|') para SQLite,
# usando exclusivamente a biblioteca padrão sqlite3 (sem ORM, sem deps extras).
#
# Esta versão contém APENAS o esqueleto de infraestrutura:
#   - constante de caminho portátil
#   - helpers de conexão e execução de SQL
#   - inicialização do banco a partir do schema
#
# Frente 0 concluída: esqueleto + métodos de usuário e transação.
#
# Responsável: Joao Guilherme
# =============================================================================

import os
import sqlite3
from datetime import date

from models.transacao import Receita, Despesa, Transacao


# Caminho absoluto e portátil para db/financas.db.
# os.path.dirname(__file__) resolve para o diretório deste arquivo (services/).
# ".." sobe um nível para a raiz do projeto, depois desce em db/.
# Isso funciona independente de onde o usuário executa o script.
CAMINHO_BANCO: str = os.path.join(
    os.path.dirname(__file__), "..", "db", "financas.db"
)

# Caminho para o arquivo SQL que define as tabelas.
# Mantido como constante separada para que inicializar_banco() seja legível.
CAMINHO_SCHEMA: str = os.path.join(
    os.path.dirname(__file__), "..", "db", "schema.sql"
)


class Persistencia:
    """Camada de acesso a dados: lê e grava no banco SQLite db/financas.db."""

    # -------------------------------------------------------------------------
    # Helpers privados de infraestrutura  (convenção: prefixo _)
    # -------------------------------------------------------------------------

    @staticmethod
    def _conectar() -> sqlite3.Connection:
        """
        Abre e devolve uma conexão pronta com o banco SQLite.

        Habilita PRAGMA foreign_keys porque o SQLite desativa a integridade
        referencial por padrão — uma decisão histórica de retrocompatibilidade
        que remonta à época em que FOREIGN KEY ainda não existia no padrão.
        """
        # Cria db/financas.db se ainda não existir (mas NÃO cria a pasta db/,
        # por isso inicializar_banco() precisa garantir a pasta antes).
        conn = sqlite3.connect(CAMINHO_BANCO)

        # PRAGMA foreign_keys é uma configuração POR CONEXÃO, não persistida
        # no arquivo do banco. Toda nova conexão começa com foreign_keys = OFF,
        # então precisamos ativar aqui, antes de qualquer outra operação.
        # Sem isso, inserir transacao com usuario_id inexistente não geraria
        # erro nenhum — um bug silencioso muito difícil de rastrear depois.
        conn.execute("PRAGMA foreign_keys = ON")

        return conn

    @staticmethod
    def _executar(sql: str, params: tuple = ()) -> None:
        """
        Executa um comando de escrita: INSERT, UPDATE ou DELETE.

        O 'with conn' garante commit em sucesso e rollback em exceção.
        O 'finally' garante o fechamento da conexão — porque o context manager
        sqlite3.Connection NÃO fecha a conexão, apenas faz commit/rollback.
        """
        conn = Persistencia._conectar()
        try:
            # 'with conn' ativa o context manager da conexão sqlite3.
            # Em sucesso: chama conn.commit() automaticamente ao sair do bloco.
            # Em exceção: chama conn.rollback() e re-lança a exceção.
            # PEGADINHA: ao contrário de 'with open(arquivo)', este 'with'
            # NÃO fecha a conexão — a conexão continua viva após o bloco.
            with conn:
                conn.execute(sql, params)
        finally:
            # finally garante o fechamento mesmo que 'with conn' tenha
            # re-lançado uma exceção após o rollback. Sem isso a conexão
            # ficaria aberta em memória até o garbage collector agir.
            conn.close()

    @staticmethod
    def _consultar(sql: str, params: tuple = ()) -> list:
        """
        Executa uma consulta SELECT e devolve todas as linhas encontradas.

        SELECT não modifica dados, portanto não precisa de commit.
        A conexão ainda deve ser fechada explicitamente — mesmo padrão
        com try/finally para garantir isso em qualquer caminho de execução.
        """
        conn = Persistencia._conectar()
        try:
            # conn.execute() cria um cursor internamente e o devolve.
            # O cursor é o "ponteiro" que navega linha a linha no resultado.
            cursor = conn.execute(sql, params)

            # fetchall() traz todas as linhas para a memória de uma vez.
            # É simples e suficiente para este projeto; em tabelas muito
            # grandes, fetchmany(n) ou iteração via cursor seriam preferíveis.
            return cursor.fetchall()
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # Inicialização
    # -------------------------------------------------------------------------

    @staticmethod
    def inicializar_banco() -> None:
        """
        Lê db/schema.sql e cria as tabelas no banco (idempotente).

        Deve ser chamado uma única vez no início de main.py.
        CREATE TABLE IF NOT EXISTS no schema garante que chamar novamente
        não apaga dados já existentes.
        """
        # Garante que a pasta db/ existe antes de sqlite3.connect() tentar
        # criar o arquivo — connect() não cria subdiretórios, só o arquivo.
        os.makedirs(os.path.dirname(CAMINHO_BANCO), exist_ok=True)

        # Lê o schema completo como string — executescript() espera texto puro.
        with open(CAMINHO_SCHEMA, "r", encoding="utf-8") as arquivo_schema:
            schema_sql = arquivo_schema.read()

        conn = Persistencia._conectar()
        try:
            # executescript() aceita múltiplos comandos separados por ';'.
            # execute() só aceita um comando por vez, portanto não serviria aqui.
            # executescript() faz um commit implícito antes de rodar o script,
            # encerrando qualquer transação pendente — o commit do 'with conn'
            # seria redundante, então usamos o padrão simples try/finally.
            conn.executescript(schema_sql)
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # Usuário  —  consumido pela frente de Autenticação
    # -------------------------------------------------------------------------

    @staticmethod
    def cadastrar_usuario(email: str, senha_hash: str, tipo_perfil: str) -> int:
        """
        Insere um novo usuário no banco e devolve o id gerado automaticamente.

        Não usa _executar() porque precisamos de lastrowid — o id que o banco
        atribuiu à linha recém-inserida. _executar() descarta o cursor, então
        abrimos a conexão via _conectar() com try/finally, conforme o padrão.
        """
        sql = (
            "INSERT INTO usuario (email, senha_hash, tipo_perfil) "
            "VALUES (?, ?, ?)"
        )
        # Placeholders '?' separam o CÓDIGO SQL dos DADOS em duas etapas:
        # 1. O banco compila o SQL sem nenhum valor ainda.
        # 2. Os valores chegam depois, tratados como literais de dados — nunca
        #    como SQL a ser interpretado. Assim, um email como
        #    "x' OR '1'='1" vira um texto inofensivo, não um comando SQL.
        conn = Persistencia._conectar()
        try:
            with conn:
                cursor = conn.execute(sql, (email, senha_hash, tipo_perfil))
                # lastrowid lido DENTRO do with, antes do commit implícito,
                # porque após conn.close() o cursor não é mais confiável.
                return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def buscar_usuario_por_email(email: str) -> Usuario | None:
        """
        Devolve o objeto Usuario com aquele email, ou None se não existir.

        Usa _consultar() porque é leitura pura — sem necessidade de commit.
        """
        from models.usuario import Usuario  # Importação local para evitar dependência circular entre módulos
        sql = (
            "SELECT id, email, senha_hash, tipo_perfil "
            "FROM usuario WHERE email = ?"
        )
        linhas = Persistencia._consultar(sql, (email,))

        # Lista vazia = email não cadastrado; None é o contrato de "não achei".
        if not linhas:
            return None

        # Email tem restrição UNIQUE no schema, então há no máximo uma linha.
        linha = linhas[0]
        # Reconstrói o objeto mapeando cada coluna do SELECT para o parâmetro
        # correspondente — a ordem do SELECT deve coincidir com os índices aqui.
        return Usuario(
            id=linha[0],
            email=linha[1],
            senha_hash=linha[2],
            tipo_perfil=linha[3],
        )

    @staticmethod
    def buscar_usuario_por_id(usuario_id: int) -> Usuario | None:
        """
        Devolve o objeto Usuario com aquele id, ou None se não existir.

        Separado de buscar_por_email para que o chamador escolha a chave
        de busca sem precisar converter tipos externamente.
        """
        from models.usuario import Usuario  # Importação local para evitar dependência circular entre módulos
        sql = (
            "SELECT id, email, senha_hash, tipo_perfil "
            "FROM usuario WHERE id = ?"
        )
        linhas = Persistencia._consultar(sql, (usuario_id,))

        if not linhas:
            return None

        linha = linhas[0]
        return Usuario(
            id=linha[0],
            email=linha[1],
            senha_hash=linha[2],
            tipo_perfil=linha[3],
        )

    # -------------------------------------------------------------------------
    # Transação  —  consumido pelo Gerenciador
    # -------------------------------------------------------------------------

    @staticmethod
    def salvar_transacao(transacao: Transacao, usuario_id: int) -> int:
        """
        Insere uma transação vinculada ao usuário e devolve o id gerado.

        Acessa o objeto apenas via interface pública (tipo(), .descricao etc.)
        para respeitar o encapsulamento — nunca acessa _atributos privados.
        """
        # Compatibilidade: categoria pode ser string ou objeto com .nome,
        # exatamente como o .txt antigo tratava — comportamento preservado.
        categoria = (
            transacao.categoria.nome
            if hasattr(transacao.categoria, "nome")
            else str(transacao.categoria)
        )

        sql = (
            "INSERT INTO transacao "
            "(tipo, descricao, valor, categoria, data, usuario_id) "
            "VALUES (?, ?, ?, ?, ?, ?)"
        )
        params = (
            transacao.tipo(),            # polimorfismo: "receita" ou "despesa"
            transacao.descricao,
            transacao.valor,
            categoria,
            transacao.data.isoformat(),  # persiste como texto "AAAA-MM-DD"
            usuario_id,
        )

        conn = Persistencia._conectar()
        try:
            with conn:
                cursor = conn.execute(sql, params)
                return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def carregar_transacoes(usuario_id: int) -> list:
        """
        Carrega todas as transações do usuário como objetos Receita ou Despesa.

        Usa um mini-factory (dict tipo→classe) para decidir qual subclasse
        instanciar sem if/elif encadeados — mais fácil de extender no futuro.
        """
        sql = (
            "SELECT id, tipo, descricao, valor, categoria, data "
            "FROM transacao WHERE usuario_id = ?"
        )
        linhas = Persistencia._consultar(sql, (usuario_id,))

        # Factory: string do banco → classe Python. Centraliza o mapeamento.
        _factory = {"receita": Receita, "despesa": Despesa}

        resultado = []
        for linha in linhas:
            id_bd, tipo, descricao, valor, categoria, data_str = linha

            classe = _factory.get(tipo)
            # Tipo desconhecido: ignora silenciosamente, como o .txt antigo fazia,
            # evitando que um registro corrompido derrube toda a carga.
            if classe is None:
                continue

            # Reconstrói o objeto via construtor da subclasse.
            # date.fromisoformat() converte "2026-04-01" → date(2026, 4, 1).
            obj = classe(descricao, valor, categoria, date.fromisoformat(data_str))

            # O modelo Transacao não tem atributo 'id' (é responsabilidade do banco).
            # Atribuímos dinamicamente para que remover_transacao() possa usá-lo.
            # Python permite isso; numa versão mais madura, 'id' entraria no modelo.
            obj.id = id_bd

            resultado.append(obj)

        return resultado

    @staticmethod
    def remover_transacao(transacao_id: int, usuario_id: int) -> None:
        """
        Deleta uma transação, mas SOMENTE se ela pertencer ao usuário informado.

        O segundo filtro AND usuario_id = ? é defesa em profundidade: mesmo que
        a camada acima envie um transacao_id errado por bug ou tentativa maliciosa,
        o DELETE não afeta registros de outros usuários.
        """
        sql = "DELETE FROM transacao WHERE id = ? AND usuario_id = ?"
        # _executar() é suficiente: não precisamos de lastrowid num DELETE.
        Persistencia._executar(sql, (transacao_id, usuario_id))
