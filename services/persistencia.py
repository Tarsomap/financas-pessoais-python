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
from __future__ import annotations

import os
import sqlite3
from datetime import date

from models.transacao import Receita, Despesa, Transacao
from models.meta import Meta


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

    # -------------------------------------------------------------------------
    # Meta  —  consumido pelo Gerenciador
    # -------------------------------------------------------------------------

    @staticmethod
    def salvar_meta(meta: Meta, usuario_id: int) -> int:
        """
        Insere uma nova meta no banco e devolve o id gerado.

        É INSERT (não UPDATE) porque a meta ainda não tem id — está sendo
        criada agora. UPDATE pressupõe que a linha já existe; atualizar_meta()
        cuida desse caso.
        """
        # prazo pode ser date (tem .isoformat()), str "Sem prazo", ou None.
        # Unificamos "Sem prazo" e None como NULL no banco: é mais semântico
        # que gravar um texto arbitrário e facilita WHERE prazo IS NOT NULL
        # no futuro.
        if hasattr(meta.prazo, "isoformat"):
            prazo_bd = meta.prazo.isoformat()  # date(2026, 12, 31) → "2026-12-31"
        else:
            prazo_bd = None                    # "Sem prazo" ou None → NULL SQLite

        sql = (
            "INSERT INTO meta (nome, valor_alvo, valor_atual, prazo, usuario_id) "
            "VALUES (?, ?, ?, ?, ?)"
        )
        conn = Persistencia._conectar()
        try:
            with conn:
                cursor = conn.execute(
                    sql,
                    (meta.nome, meta.valor_alvo, meta.valor_atual, prazo_bd, usuario_id),
                )
                return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def carregar_metas(usuario_id: int) -> list:
        """
        Carrega todas as metas do usuário e devolve objetos Meta reconstituídos.

        Restaura valor_atual por atribuição direta, não por depositar() —
        mesma decisão de Meta.from_dict, que é a fonte canônica de restauração.
        """
        sql = (
            "SELECT id, nome, valor_alvo, valor_atual, prazo "
            "FROM meta WHERE usuario_id = ?"
        )
        linhas = Persistencia._consultar(sql, (usuario_id,))

        resultado = []
        for linha in linhas:
            id_bd, nome, valor_alvo, valor_atual, prazo_str = linha

            # Reverte a lógica de salvar_meta: NULL → padrão do modelo ("Sem prazo");
            # string ISO → date; qualquer outro texto → mantém como string.
            if prazo_str is None:
                prazo = "Sem prazo"
            else:
                try:
                    prazo = date.fromisoformat(prazo_str)
                except (ValueError, TypeError):
                    prazo = prazo_str  # texto não-ISO: preserva para não perder dado

            meta = Meta(nome, valor_alvo, prazo)

            # Meta.__init__ sempre zera valor_atual. Restauramos com atribuição
            # direta porque depositar() é semântica de "acrescentar incremento",
            # não de "restaurar estado salvo" — e poderia colidir com a validação
            # de valor <= 0 se o banco devolver 0.0.
            meta.valor_atual = float(valor_atual)

            # id gerado pelo banco; o modelo não o tem nativamente.
            meta.id = id_bd

            resultado.append(meta)

        return resultado

    @staticmethod
    def atualizar_meta(meta: Meta, usuario_id: int) -> None:
        """
        Atualiza o valor_atual de uma meta já existente no banco.

        Por que UPDATE separado de salvar_meta (INSERT)?
        INSERT cria uma NOVA linha — se a meta já existe, geraria uma cópia
        duplicada com um segundo id. UPDATE localiza a linha pelo id existente
        e modifica só o campo que mudou, sem criar outra linha. São operações
        SQL com semânticas opostas: criar vs. modificar.
        meta.id deve existir (vindo de carregar_metas); se não existir, o
        UPDATE afeta zero linhas sem erro — o chamador deve garantir isso.
        """
        sql = "UPDATE meta SET valor_atual = ? WHERE id = ? AND usuario_id = ?"
        # _executar() é suficiente: UPDATE não precisa de lastrowid.
        Persistencia._executar(sql, (meta.valor_atual, meta.id, usuario_id))

    @staticmethod
    def remover_meta(meta_id: int, usuario_id: int) -> None:
        """
        Remove uma meta pelo id, somente se pertencer ao usuário informado.

        AND usuario_id = ? é a mesma defesa em profundidade de remover_transacao:
        impede deleção cruzada mesmo que a camada superior envie um id errado.
        """
        sql = "DELETE FROM meta WHERE id = ? AND usuario_id = ?"
        Persistencia._executar(sql, (meta_id, usuario_id))

    # -------------------------------------------------------------------------
    # Conta  —  consumido pela frente de Empresa (Frente 5)
    # models/conta.py ainda não existe; import adiado dentro de carregar_contas.
    # -------------------------------------------------------------------------

    @staticmethod
    def salvar_conta(conta, usuario_id: int) -> int:
        """
        Insere uma conta a pagar/receber e devolve o id gerado.

        'conta' não tem type hint: models/conta.py só existirá na Frente 5.
        O import de Conta fica adiado em carregar_contas, que é quem precisa
        instanciar — aqui apenas lemos atributos, sem importar a classe.
        """
        # vencimento pode ser date ou string; garantimos texto ISO no banco
        # para que carregar_contas possa sempre usar date.fromisoformat().
        vencimento_bd = (
            conta.vencimento.isoformat()
            if hasattr(conta.vencimento, "isoformat")
            else str(conta.vencimento)
        )
        # SQLite não tem tipo booleano nativo — usa 0/1 como inteiro.
        # int(True) == 1, int(False) == 0; a conversão explícita documenta
        # a intenção e evita surpresa caso pago seja None no futuro.
        pago_bd = 1 if conta.pago else 0

        sql = (
            "INSERT INTO conta (tipo, descricao, valor, vencimento, pago, usuario_id) "
            "VALUES (?, ?, ?, ?, ?, ?)"
        )
        conn = Persistencia._conectar()
        try:
            with conn:
                cursor = conn.execute(
                    sql,
                    (conta.tipo, conta.descricao, conta.valor, vencimento_bd, pago_bd, usuario_id),
                )
                return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def carregar_contas(usuario_id: int) -> list:
        """
        Carrega todas as contas do usuário e devolve objetos Conta.

        Import adiado: 'from models.conta import Conta' fica dentro do método
        para não causar ImportError enquanto models/conta.py não existir.
        O resto da Persistencia continua funcionando normalmente — só este
        método falha se chamado antes da Frente 5 estar implementada.
        """
        # Import executado apenas na chamada deste método, não na importação
        # do módulo. Isso isola a dependência da Frente 5 neste único ponto.
        from models.conta import Conta

        sql = (
            "SELECT id, tipo, descricao, valor, vencimento, pago "
            "FROM conta WHERE usuario_id = ?"
        )
        linhas = Persistencia._consultar(sql, (usuario_id,))

        resultado = []
        for linha in linhas:
            id_bd, tipo, descricao, valor, vencimento_str, pago_int = linha

            vencimento = date.fromisoformat(vencimento_str)

            # pago vem do banco como 0 ou 1 (inteiro). bool() converte:
            # bool(0) → False, bool(1) → True. Necessário porque Conta espera
            # bool no parâmetro pago= e comparações como pago == True
            # falhariam se o valor fosse o inteiro 1 sem conversão.
            pago = bool(pago_int)

            obj = Conta(tipo, descricao, valor, vencimento, pago=pago)
            obj.id = id_bd

            resultado.append(obj)

        return resultado

    @staticmethod
    def marcar_conta_paga(conta_id: int, usuario_id: int) -> None:
        """
        Marca uma conta como paga (pago = 1).

        Por que pago = 1 fixo, em vez de receber o valor por parâmetro?
        Esta operação representa uma ação de negócio com semântica clara:
        "pagar uma conta". Aceitar um parâmetro criaria o risco de chamar
        marcar_conta_paga(id, uid, pago=0) por engano, revertendo o pagamento.
        Se a lógica inversa for necessária no futuro, um método dedicado
        'estornar_conta()' deixa a intenção explícita no próprio nome.
        """
        sql = "UPDATE conta SET pago = 1 WHERE id = ? AND usuario_id = ?"
        Persistencia._executar(sql, (conta_id, usuario_id))

    @staticmethod
    def remover_conta(conta_id: int, usuario_id: int) -> None:
        """
        Remove uma conta, somente se pertencer ao usuário informado.

        Defesa em profundidade: AND usuario_id = ? impede deleção cruzada
        mesmo que a camada superior envie um conta_id de outro usuário.
        """
        sql = "DELETE FROM conta WHERE id = ? AND usuario_id = ?"
        Persistencia._executar(sql, (conta_id, usuario_id))
