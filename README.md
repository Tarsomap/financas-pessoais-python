# 💸 Plataforma Financeira

> Sistema de gerenciamento de finanças **pessoais e empresariais** desenvolvido em Python.
> Evolução de um app de terminal (CLI) para uma **aplicação web Flask** com banco **SQLite**
> e login por usuário, onde o sistema se comporta de forma diferente conforme o perfil de
> quem está logado (**pessoa física × empresa**).
> Projeto avaliativo da disciplina de **Laboratório de Programação** — Universidade Tiradentes (UNIT).

---

## 👥 Integrantes e Frentes de Trabalho

O time de 7 pessoas se divide em **frentes** paralelas. Cada arquivo traz um cabeçalho
`RESPONSÁVEL: ...` e o trabalho entra na `main` via Pull Request (1 colega revisa).

| Frente | Responsável | Escopo | Status |
|---|---|---|---|
| 0 · Banco SQLite | Tarso Monteiro Alves Passos | `db/schema.sql`, `services/persistencia.py` | ✅ na `main` |
| 1 · Autenticação | João Guilherme Costa Carvalho | `models/usuario.py`, `services/auth.py` | ✅ na `main` |
| 2 · Perfis polimórficos | João Gustavo Lima dos Santos | `models/perfil.py` | ✅ na `main` |
| 3 · Gerenciador + Isolamento | Vinicius Prado Sobral | `services/gerenciador.py` | ✅ na `main` |
| 4 · Frontend Flask | Lívia Rodrigues Pinto · Alice Santos Silva | `app.py`, `routes/`, `templates/`, `static/` | ✅ na `main` |
| 5 · Empresa (contas / fluxo de caixa) | Tarso Monteiro Alves Passos | `models/conta.py`, fluxo de caixa em `Relatorio` | ✅ na `main` |
| 6 · Qualidade (testes) | João Guilherme Teles de Souza Lopes | `tests/` | ✅ na `main` |

---

## 📋 Descrição do Projeto

A **Plataforma Financeira** permite que o usuário controle receitas, despesas, metas de
economia e — no perfil empresa — contas a pagar/receber e fluxo de caixa. Os dados são
persistidos em um banco **SQLite** local, escopados por usuário (cada um só enxerga os
próprios dados).

O sistema é **polimórfico por perfil**: a mesma base de código atende pessoa física
(categorias do dia a dia: Alimentação, Transporte, Saúde…) e empresa (Vendas, Fornecedores,
Folha de Pagamento…, mais contas a pagar/receber e projeção de caixa).

O projeto demonstra na prática os conceitos da disciplina:

- **Modelagem orientada a objetos** — herança (`Transacao` → `Receita`/`Despesa`),
  classes abstratas (`Perfil` → `PessoaFisica`/`Empresa`) e factory (`criar_perfil`)
- **Separação de responsabilidades em camadas** (frontend → services → models → banco)
- **Padrão Repository** — só a `Persistencia` escreve SQL
- **Persistência em SQLite** com isolamento por `usuario_id`
- **Testes automatizados** com `pytest` cobrindo as regras de negócio

---

## 🗂️ Estrutura do Projeto

```text
financas-pessoais-python/
├── app.py                          # App Flask: cria a instância e registra os blueprints
├── README.md
├── CLAUDE.md                       # Guia para o agente de IA + estado do projeto
├── Plano-Tecnico-Plataforma-Financeira.md  # Documento-fonte (schema, contratos, frentes)
├── requirements.txt
├── db/
│   ├── schema.sql                  # Estrutura do banco (usuario, transacao, meta, conta)
│   └── financas.db                 # Banco SQLite (não versionado)
├── models/                         # Entidades de domínio (POO)
│   ├── __init__.py
│   ├── transacao.py                # Transacao → Receita / Despesa (herança)
│   ├── categoria.py                # Categoria com validação de nome
│   ├── meta.py                     # Meta com cálculo de progresso
│   ├── perfil.py                   # Perfil(ABC) → PessoaFisica / Empresa + criar_perfil
│   ├── conta.py                    # Conta a pagar/receber (perfil empresa)
│   └── usuario.py                  # Usuario(id, email, senha_hash, perfil)
├── services/                       # Regra de negócio
│   ├── __init__.py
│   ├── gerenciador.py              # Gerenciador(usuario_id): fachada de operações
│   ├── relatorio.py                # Relatório de transações + fluxo de caixa
│   ├── persistencia.py             # Única camada que fala com o SQLite (Repository)
│   └── auth.py                     # Cadastro, hash de senha e login
├── routes/                         # Blueprints Flask (camada de views)
│   ├── __init__.py
│   ├── dashboard.py                # Página inicial: saldo e resumo
│   ├── transacoes.py               # Listar / adicionar / remover transações
│   ├── metas.py                    # Listar / adicionar / depositar / remover metas
│   ├── auth.py                     # Login / cadastro / logout (liga ao services/auth.py)
│   └── contas.py                   # Contas a pagar/receber (liga ao Gerenciador)
├── templates/                      # HTML (Jinja2)
│   ├── base.html
│   ├── dashboard.html
│   ├── transacoes.html
│   ├── metas.html
│   ├── login.html
│   ├── cadastro.html
│   └── contas.html
├── static/
│   └── style.css
└── tests/                          # Suíte pytest (banco :memory:)
    ├── conftest.py
    ├── test_transacao.py
    ├── test_perfil.py
    ├── test_conta.py
    ├── test_gerenciador.py
    ├── test_relatorio.py
    ├── test_usuario.py
    ├── test_auth.py
    └── test_rotas.py               # (skip até app.py expor create_app)
```

> ℹ️ **Integração ainda em aberto:** `tests/test_rotas.py` espera uma fábrica `create_app` em
> `app.py` (hoje a instância é criada no nível do módulo) **e** rotas sem prefixo (`/login`,
> `/transacoes`), enquanto os blueprints usam prefixo (`/auth/login`, `/transacoes/`). Por
> isso os 11 smoke tests de rota ficam em *skip* — alinhar URLs/fábrica é tarefa conjunta das
> Frentes 4 e 6.

---

## ⚙️ Funcionalidades

### Comuns a todos os perfis
- ✅ Cadastro de **receitas** e **despesas** com descrição, valor, categoria e data
- ✅ Listagem e remoção de transações (por id) com atualização do saldo
- ✅ **Saldo atual** calculado em tempo real (receitas − despesas)
- ✅ Filtro de transações por tipo e categoria
- ✅ Cadastro de **metas de economia** com valor-alvo e prazo, depósito parcial e progresso
- ✅ **Relatório mensal**: totais por categoria, comparativo com o mês anterior e sugestões de corte
- ✅ Persistência em **SQLite** isolada por usuário

### Específicas do perfil Empresa
- ✅ **Contas a pagar / receber** com vencimento e baixa (marcar como paga)
- ✅ Detecção de contas vencidas
- ✅ **Fluxo de caixa** mensal — projeção de entradas, saídas e saldo projetado pelas contas que vencem no mês

### Autenticação e web (Frentes 1 e 4 — na `main`)
- ✅ **Cadastro e login** com senha hasheada (`services/auth.py`: `gerar_hash`, `verificar_senha`, `cadastrar_usuario`, `autenticar`, `login`)
- ✅ Model `Usuario(id, email, senha_hash, perfil)`
- ✅ **Interface web Flask completa**: `app.py` + blueprints de dashboard, transações, metas, **autenticação** (login/cadastro/logout) e **contas a pagar/receber**, com templates Jinja2 e CSS
- ✅ Menu **Contas** aparece só para o perfil **empresa**; mensagens *flash* de feedback em todas as páginas
- 🔧 Resta: fábrica `create_app` + alinhar URLs com `tests/test_rotas.py` (ver nota acima)

---

## 🚀 Como Executar

### Pré-requisitos

- Python **3.10** ou superior (o ambiente atual usa 3.14)
- `sqlite3` já vem com o Python. A **app web depende do Flask**; os **testes**, do `pytest`.

> ⚠️ O `requirements.txt` atual (gerado no Windows) está em **UTF-16** e lista só o Flask e
> suas dependências — **não inclui o `pytest`**. Até ser regenerado em UTF-8 com o pytest, vale
> instalar à mão: `./venv/bin/pip install Flask pytest`.

### Ambiente e dependências

```bash
python -m venv venv
./venv/bin/pip install -r requirements.txt
```

### Rodar os testes

```bash
# Todos
./venv/bin/python -m pytest tests/ -v

# Um arquivo / classe / teste isolado
./venv/bin/python -m pytest tests/test_gerenciador.py -v
./venv/bin/python -m pytest "tests/test_gerenciador.py::TestSaldo::test_saldo_vazio_e_zero"
```

Estado atual da suíte: **104 passed, 11 skipped**. Os 11 skips são os smoke tests de
`test_rotas`, que aguardam a fábrica `create_app` e o alinhamento de URLs (ver nota na
seção de estrutura).

### Rodar a app web

```bash
./venv/bin/pip install Flask     # se ainda não instalou
./venv/bin/python app.py         # ou: ./venv/bin/python -m flask run
```

A aplicação **sobe e funciona**: cadastro, login/logout, dashboard, transações, metas e — para
o perfil empresa — contas a pagar/receber. Acesse `http://127.0.0.1:5000/` (redireciona para
o login).

---

## 🏛️ Arquitetura em Camadas

O Flask entra no topo; a base de services/models quase não muda; só a persistência troca de
tecnologia (`.txt` → SQLite).

```
Flask (routes/ + templates/)   ← frontend   [camada NOVA — Frente 4]
Gerenciador, Relatorio         ← services   [Gerenciador escopado a usuario_id]
Usuario, Perfil, Conta...      ← models     [domínio POO]
Persistencia → SQLite          ← banco      [padrão Repository: só ela escreve SQL]
```

**Regra de camadas:** a view **não calcula nada** — chama o `Gerenciador` e exibe; o
`Gerenciador` **não escreve SQL** — delega à `Persistencia`; a `Persistencia` é a **única**
que fala com o banco. `Relatorio` é desacoplado: recebe listas prontas e calcula em cima
delas, sem saber a origem.

---

## 🧠 Conceitos Aplicados

| Conceito | Onde é usado |
|----------|-------------|
| **Herança e polimorfismo** | `Receita`/`Despesa` herdam de `Transacao`; `PessoaFisica`/`Empresa` de `Perfil` |
| **Classe abstrata (ABC)** | `Perfil(ABC)` com `@abstractmethod` `categorias_disponiveis()` e `tipo_str()` |
| **Factory** | `criar_perfil(tipo)` devolve o `Perfil` certo a partir do texto do banco |
| **Encapsulamento** | `usuario_id` privado no `Gerenciador`; a view nunca o vê |
| **Padrão Repository** | `Persistencia` concentra todo o SQL; o resto do código ignora o banco |
| **List comprehensions** | Filtros de transações/contas por tipo e categoria |
| **Tratamento de exceções** | `ValueError`/`LookupError` em validações de domínio |
| **SQLite** | `sqlite3` da biblioteca padrão; isolamento por `usuario_id` |
| **`datetime`** | Datas em texto ISO (`date.fromisoformat()` ⇄ `.isoformat()`) |
| **Testes com `pytest`** | Fixtures, `pytest.raises`, banco `:memory:` por teste |

---

## 📌 Convenções

- **Tudo em português** — tabelas, colunas, métodos, classes e variáveis (única exceção: `id`).
- **Um conceito, um nome** no projeto inteiro (ex.: sempre `usuario_id`, nunca `user_id`).
- `snake_case` para funções/variáveis/arquivos; `PascalCase` para classes; `MAIÚSCULAS` para constantes; prefixo `_` para uso interno.
- **Type hints** nas assinaturas e **docstring curta** em toda função pública.
- Datas como **texto ISO**; booleanos no banco como **`0/1`**; `id` é responsabilidade do banco (anexado dinamicamente ao carregar).
- `db/*.db` **nunca** é versionado (binário = conflito garantido); veja `.gitignore`.

> O documento-fonte do plano (schema, contratos congelados e divisão de trabalho) é
> `Plano-Tecnico-Plataforma-Financeira.md` na raiz — leia-o antes de qualquer mudança estrutural.
