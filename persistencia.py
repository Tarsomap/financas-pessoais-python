import sqlite3
from models.transacao import Receita, Despesa
from models.meta import Meta
from models.conta import Conta
from models.usuario import Usuario
from models.perfil import criar_perfil


class Persistencia:
    """
    Isola o resto do sistema do SQLite (padrão Repository).
    Ninguém além daqui escreve SQL.

    Por que _conn_memoria?
        sqlite3.connect(':memory:') abre um banco NOVO e VAZIO a cada chamada.
        Para os testes, precisamos de uma única conexão compartilhada que
        sobreviva entre os métodos. Então guardamos essa conexão como atributo
        de classe e a reutilizamos enquanto o banco for :memory:.
    """

    _caminho_banco: str = "db/financas.db"
    _conn_memoria: sqlite3.Connection | None = None

    @classmethod
    def configurar_banco(cls, caminho: str) -> None:
        """Troca o banco em uso. Chamado pela fixture banco_limpo nos testes."""
        cls._caminho_banco = caminho
        if caminho == ":memory:":
            # Cria (ou recria) a conexão em memória
            cls._conn_memoria = sqlite3.connect(":memory:", check_same_thread=False)
            cls._conn_memoria.execute("PRAGMA foreign_keys = ON")
        else:
            # Banco em arquivo: cada operação abre e fecha a própria conexão
            if cls._conn_memoria is not None:
                cls._conn_memoria.close()
            cls._conn_memoria = None

    @classmethod
    def _conectar(cls) -> sqlite3.Connection:
        """Devolve a conexão ativa. Para :memory: é sempre a mesma."""
        if cls._conn_memoria is not None:
            return cls._conn_memoria
        conn = sqlite3.connect(cls._caminho_banco)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @classmethod
    def _executar(cls, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Executa um comando DML (INSERT/UPDATE/DELETE) e commita."""
        conn = cls._conectar()
        cur = conn.execute(sql, params)
        conn.commit()
        return cur

    @classmethod
    def _consultar(cls, sql: str, params: tuple = ()):
        """Executa um SELECT e devolve todas as linhas."""
        conn = cls._conectar()
        return conn.execute(sql, params).fetchall()

    # ------------------------------------------------------------------
    # Inicialização
    # ------------------------------------------------------------------

    @classmethod
    def inicializar_banco(cls) -> None:
        """Cria as tabelas se ainda não existirem."""
        conn = cls._conectar()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS usuario (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                email       TEXT NOT NULL UNIQUE,
                senha_hash  TEXT NOT NULL,
                tipo_perfil TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS transacao (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo        TEXT NOT NULL,
                descricao   TEXT NOT NULL,
                valor       REAL NOT NULL,
                categoria   TEXT NOT NULL,
                data        TEXT NOT NULL,
                usuario_id  INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuario(id)
            );
            CREATE TABLE IF NOT EXISTS meta (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nome        TEXT NOT NULL,
                valor_alvo  REAL NOT NULL,
                valor_atual REAL NOT NULL DEFAULT 0,
                prazo       TEXT,
                usuario_id  INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuario(id)
            );
            CREATE TABLE IF NOT EXISTS conta (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo        TEXT NOT NULL,
                descricao   TEXT NOT NULL,
                valor       REAL NOT NULL,
                vencimento  TEXT NOT NULL,
                pago        INTEGER NOT NULL DEFAULT 0,
                usuario_id  INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuario(id)
            );
        """)
        conn.commit()

    # ------------------------------------------------------------------
    # Usuário
    # ------------------------------------------------------------------

    @classmethod
    def cadastrar_usuario(cls, email: str, senha_hash: str, tipo_perfil: str) -> int:
        cur = cls._executar(
            "INSERT INTO usuario (email, senha_hash, tipo_perfil) VALUES (?, ?, ?)",
            (email, senha_hash, tipo_perfil)
        )
        return cur.lastrowid

    @classmethod
    def buscar_usuario_por_email(cls, email: str):
        rows = cls._consultar("SELECT * FROM usuario WHERE email = ?", (email,))
        if not rows:
            return None
        r = rows[0]
        return Usuario(id=r[0], email=r[1], senha_hash=r[2], perfil=criar_perfil(r[3]))

    @classmethod
    def buscar_usuario_por_id(cls, usuario_id: int):
        rows = cls._consultar("SELECT * FROM usuario WHERE id = ?", (usuario_id,))
        if not rows:
            return None
        r = rows[0]
        return Usuario(id=r[0], email=r[1], senha_hash=r[2], perfil=criar_perfil(r[3]))

    # ------------------------------------------------------------------
    # Transações
    # ------------------------------------------------------------------

    @classmethod
    def salvar_transacao(cls, transacao, usuario_id: int) -> int:
        cur = cls._executar(
            "INSERT INTO transacao (tipo, descricao, valor, categoria, data, usuario_id) VALUES (?, ?, ?, ?, ?, ?)",
            (transacao.tipo, transacao.descricao, transacao.valor,
             transacao.categoria, transacao.data or "2024-01-01", usuario_id)
        )
        return cur.lastrowid

    @classmethod
    def carregar_transacoes(cls, usuario_id: int) -> list:
        rows = cls._consultar("SELECT * FROM transacao WHERE usuario_id = ?", (usuario_id,))
        resultado = []
        for r in rows:
            cls_t = Receita if r[1] == "receita" else Despesa
            t = cls_t(descricao=r[2], valor=r[3], categoria=r[4], data=r[5], id=r[0], usuario_id=r[6])
            resultado.append(t)
        return resultado

    @classmethod
    def remover_transacao(cls, transacao_id: int, usuario_id: int) -> None:
        cls._executar(
            "DELETE FROM transacao WHERE id = ? AND usuario_id = ?",
            (transacao_id, usuario_id)
        )

    # ------------------------------------------------------------------
    # Metas
    # ------------------------------------------------------------------

    @classmethod
    def salvar_meta(cls, meta, usuario_id: int) -> int:
        cur = cls._executar(
            "INSERT INTO meta (nome, valor_alvo, valor_atual, prazo, usuario_id) VALUES (?, ?, ?, ?, ?)",
            (meta.nome, meta.valor_alvo, meta.valor_atual, meta.prazo, usuario_id)
        )
        return cur.lastrowid

    @classmethod
    def carregar_metas(cls, usuario_id: int) -> list:
        rows = cls._consultar("SELECT * FROM meta WHERE usuario_id = ?", (usuario_id,))
        return [
            Meta(nome=r[1], valor_alvo=r[2], valor_atual=r[3], prazo=r[4], id=r[0], usuario_id=r[5])
            for r in rows
        ]

    @classmethod
    def atualizar_meta(cls, meta, usuario_id: int) -> None:
        cls._executar(
            "UPDATE meta SET valor_atual = ? WHERE id = ? AND usuario_id = ?",
            (meta.valor_atual, meta.id, usuario_id)
        )

    @classmethod
    def remover_meta(cls, meta_id: int, usuario_id: int) -> None:
        cls._executar(
            "DELETE FROM meta WHERE id = ? AND usuario_id = ?",
            (meta_id, usuario_id)
        )

    # ------------------------------------------------------------------
    # Contas a pagar/receber
    # ------------------------------------------------------------------

    @classmethod
    def salvar_conta(cls, conta, usuario_id: int) -> int:
        cur = cls._executar(
            "INSERT INTO conta (tipo, descricao, valor, vencimento, pago, usuario_id) VALUES (?, ?, ?, ?, ?, ?)",
            (conta.tipo, conta.descricao, conta.valor, conta.vencimento, int(conta.pago), usuario_id)
        )
        return cur.lastrowid

    @classmethod
    def carregar_contas(cls, usuario_id: int) -> list:
        rows = cls._consultar("SELECT * FROM conta WHERE usuario_id = ?", (usuario_id,))
        return [
            Conta(tipo=r[1], descricao=r[2], valor=r[3], vencimento=r[4],
                  pago=bool(r[5]), id=r[0], usuario_id=r[6])
            for r in rows
        ]

    @classmethod
    def marcar_conta_paga(cls, conta_id: int, usuario_id: int) -> None:
        cls._executar(
            "UPDATE conta SET pago = 1 WHERE id = ? AND usuario_id = ?",
            (conta_id, usuario_id)
        )

    @classmethod
    def remover_conta(cls, conta_id: int, usuario_id: int) -> None:
        cls._executar(
            "DELETE FROM conta WHERE id = ? AND usuario_id = ?",
            (conta_id, usuario_id)
        )
