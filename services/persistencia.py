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
# Os métodos de negócio (salvar/carregar/remover) vêm nas próximas frentes.
#
# Responsável: Joao Guilherme
# =============================================================================

import os
import sqlite3


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
