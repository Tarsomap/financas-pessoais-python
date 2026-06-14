CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    tipo_perfil TEXT NOT NULL CHECK (tipo_perfil IN ('pessoa_fisica', 'empresa'))
);

CREATE TABLE IF NOT EXISTS transacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL CHECK (tipo IN ('receita', 'despesa')),
    descricao TEXT NOT NULL,
    valor REAL NOT NULL CHECK (valor > 0),
    categoria TEXT NOT NULL,
    data TEXT NOT NULL,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS meta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    valor_alvo REAL NOT NULL CHECK (valor_alvo > 0),
    valor_atual REAL NOT NULL DEFAULT 0 CHECK (valor_atual >= 0),
    prazo TEXT,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL CHECK (tipo IN ('pagar', 'receber')),
    descricao TEXT NOT NULL,
    valor REAL NOT NULL CHECK (valor > 0),
    vencimento TEXT NOT NULL,
    pago INTEGER NOT NULL DEFAULT 0 CHECK (pago IN (0, 1)),
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_transacao_usuario ON transacao(usuario_id);
CREATE INDEX IF NOT EXISTS idx_meta_usuario ON meta(usuario_id);
CREATE INDEX IF NOT EXISTS idx_conta_usuario ON conta(usuario_id);
