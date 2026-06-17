-- Define a ESTRUTURA do banco. Executado uma vez na inicializacao.
-- Cada bloco CREATE TABLE e uma tabela; dentro, cada linha e uma coluna.
-- IF NOT EXISTS: roda sem erro mesmo que a tabela ja exista (re-execucao segura).

-- TABELA usuario -- quem usa o sistema (cada linha = uma conta).
-- E a tabela 'mae': transacao, meta e conta apontam para ca.
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- id automatico, unico
    email TEXT NOT NULL UNIQUE,             -- obrigatorio e nao repete (login)
    senha_hash TEXT NOT NULL,               -- senha embaralhada, NUNCA pura
    -- CHECK barra valores fora do dominio: o perfil so pode ser um dos dois.
    tipo_perfil TEXT NOT NULL CHECK (tipo_perfil IN ('pessoa_fisica', 'empresa'))
);

-- TABELA transacao -- receitas e despesas (o coracao do sistema).
CREATE TABLE IF NOT EXISTS transacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL CHECK (tipo IN ('receita', 'despesa')),  -- so esses dois
    descricao TEXT NOT NULL,
    valor REAL NOT NULL CHECK (valor > 0),  -- REAL: dinheiro tem centavos; sempre positivo
    categoria TEXT NOT NULL,
    data TEXT NOT NULL,                     -- texto ISO 'AAAA-MM-DD'
    usuario_id INTEGER NOT NULL,            -- DONO desta transacao
    -- ON DELETE CASCADE: ao apagar o usuario, suas transacoes somem junto
    -- (nao deixa "orfas" no banco).
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);

-- TABELA meta -- objetivos de economia.
CREATE TABLE IF NOT EXISTS meta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    valor_alvo REAL NOT NULL CHECK (valor_alvo > 0),            -- alvo precisa ser positivo
    valor_atual REAL NOT NULL DEFAULT 0 CHECK (valor_atual >= 0),  -- comeca zerada; nunca negativa
    prazo TEXT,                             -- opcional (pode ser nulo)
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);

-- TABELA conta -- contas a pagar/receber (funcionalidade de empresa).
-- Segue de proposito o mesmo molde das anteriores: padrao = facil de aprender.
CREATE TABLE IF NOT EXISTS conta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL CHECK (tipo IN ('pagar', 'receber')),    -- so esses dois
    descricao TEXT NOT NULL,
    valor REAL NOT NULL CHECK (valor > 0),
    vencimento TEXT NOT NULL,               -- data ISO 'AAAA-MM-DD'
    -- SQLite nao tem boolean: usamos 0/1 e o CHECK garante so esses valores.
    pago INTEGER NOT NULL DEFAULT 0 CHECK (pago IN (0, 1)),
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);

-- INDICES -- aceleram o filtro mais comum do sistema: "tudo de UM usuario".
-- Toda consulta e escopada por usuario_id; o indice evita varrer a tabela toda.
CREATE INDEX IF NOT EXISTS idx_transacao_usuario ON transacao(usuario_id);
CREATE INDEX IF NOT EXISTS idx_meta_usuario ON meta(usuario_id);
CREATE INDEX IF NOT EXISTS idx_conta_usuario ON conta(usuario_id);
