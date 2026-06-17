# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O projeto e seu momento atual

**Plataforma Financeira** — finanças pessoais **e** empresariais. É a evolução de um app de
terminal (CLI) para uma **aplicação web Flask** com banco **SQLite** e login por usuário, onde
o sistema se comporta de forma diferente conforme o perfil de quem está logado (pessoa
física × empresa). Projeto avaliativo de Laboratório de Programação (UNIT).
Stack: Python · Flask · SQLite · POO. Entrega-alvo: **18/06**.

O documento-fonte do plano é `Plano-Tecnico-Plataforma-Financeira.md` na raiz — **leia-o
antes de qualquer mudança estrutural**. Ele congela schema, contratos e a divisão de
trabalho.

Trabalho em grupo de 7 pessoas, dividido em **frentes** paralelas (ver tabela). Cada arquivo
traz cabeçalho "RESPONSÁVEL: ...". Mantenha o estilo de comentários didáticos e extensos:
eles explicam o *porquê* e fazem parte da nota do trabalho.

### Onde o código realmente está agora (importante)

A migração está **quase completa**. **Todas as 7 frentes já estão integradas na `main`**
(Frentes 0–6). A suíte roda **104 passed, 1 skipped** — o único skip é `test_rotas`, que
aguarda uma fábrica `create_app` em `app.py`.

- ✅ **Frente 0** (banco): `db/schema.sql` + `services/persistencia.py` (SQLite, API por
  `usuario_id`).
- ✅ **Frente 2** (perfis): `models/perfil.py` — `Perfil(ABC)` → `PessoaFisica`/`Empresa`,
  factory `criar_perfil`.
- ✅ **Frente 3** (gerenciador): `services/gerenciador.py` **já é a versão web** —
  `Gerenciador(usuario_id)`, remoção por id, isolamento entre usuários.
- ✅ **Frente 6** (qualidade): suíte em `tests/` reorganizada e escopada a `usuario_id`,
  rodando contra banco `:memory:` via `Persistencia.configurar_banco`.
- ✅ **Frente 5** (empresa): `models/conta.py` (`Conta` a pagar/receber) e o fluxo de caixa
  em `Relatorio.fluxo_de_caixa(ano, mes)` — que recebe as contas e projeta entradas/saídas
  do mês. (Não há `services/fluxo_caixa.py` nem `Perfil.tipos_conta()`: o fluxo de caixa
  vive no `Relatorio`, não numa classe separada.)
- ✅ **Frente 1** (autenticação): `models/usuario.py` (`Usuario(id, email, senha_hash, perfil)`)
  e `services/auth.py` (`gerar_hash`, `verificar_senha`, `cadastrar_usuario`, `autenticar`,
  `login`). `persistencia.py` mantém o **import adiado** de `Usuario` (evita ciclo).
- ✅ **Frente 4** (frontend Flask): `app.py` cria a instância e registra blueprints;
  `routes/` (`dashboard`, `transacoes`, `metas`), `templates/` (Jinja2) e `static/style.css`.
- ⚠️ **Pontas soltas conhecidas:** `app.py` importa/registra `routes.auth` e `routes.contas`,
  mas `routes/auth.py` e `routes/contas.py` **ainda não existem** → `python app.py` falha no
  import até criarem esses blueprints. E `tests/test_rotas.py` espera `create_app` em `app.py`
  (hoje a instância é criada no nível do módulo), por isso esse teste fica em *skip*.
- ℹ️ O CLI antigo (`main.py` + `views/menu.py`) já foi **aposentado** e removido do repo;
  a interface é o `app.py` (Flask).

## Comandos

```bash
# Testes (todos) — venv em venv/ (Python 3.14; o plano pede 3.10+)
./venv/bin/python -m pytest tests/ -v

# Um arquivo / classe / teste isolado
./venv/bin/python -m pytest tests/test_gerenciador.py -v
./venv/bin/python -m pytest "tests/test_gerenciador.py::TestSaldo::test_saldo_vazio_e_zero"

# Rodar a app web (app.py já existe; hoje falha no import até criarem
# routes/auth.py e routes/contas.py, que app.py registra)
./venv/bin/python app.py        # ou: ./venv/bin/python -m flask run
```

O núcleo é só biblioteca padrão; a versão web adiciona **Flask** (e `werkzeug.security`, que
vem junto com o Flask). `sqlite3` é biblioteca padrão. Não introduza outras dependências
externas sem decisão do grupo.

## Arquitetura alvo (camadas)

O Flask entra no topo; a base de services/models quase não muda; só a persistência troca
de tecnologia (`.txt` → SQLite).

```
Flask (routes/ + templates/)   ← frontend   [camada NOVA]
Gerenciador, Relatorio         ← services   [Gerenciador passa a ser escopado a usuario_id]
Usuario, Perfil, Transacao...  ← models     [Usuario, Perfil e Conta já na `main`]
Persistencia → SQLite          ← banco      [padrão Repository: só ela escreve SQL]
```

Regra de camadas (não viole): a **view não calcula nada** — chama o `Gerenciador` e exibe;
o `Gerenciador` **não escreve SQL** — delega à `Persistencia`; a `Persistencia` é a **única**
que fala com o banco. `Relatorio` é desacoplado: recebe listas prontas (transações e,
opcionalmente, contas para o fluxo de caixa) e calcula em cima delas, sem saber a origem.

## Contratos congelados (programe contra eles)

Estas assinaturas são as fronteiras entre frentes — **não as altere sem combinar com o
grupo**. Quem é dono da frente implementa; as outras frentes apenas chamam.

- **Persistencia** (Contrato A — já implementado): métodos `@staticmethod`, todos
  escopados por `usuario_id`. `inicializar_banco()`;
  `cadastrar_usuario` / `buscar_usuario_por_email` / `buscar_usuario_por_id`;
  `salvar` / `carregar` / `remover_transacao`;
  `salvar` / `carregar` / `atualizar` / `remover_meta`;
  `salvar` / `carregar` / `marcar_conta_paga` / `remover_conta`. DELETE/UPDATE filtram
  sempre `WHERE id = ? AND usuario_id = ?` (defesa em profundidade).
- **Gerenciador** (Contrato B — implementado na Frente 3): `Gerenciador(usuario_id)` no
  construtor; métodos de transação/meta/conta (incluindo `adicionar_conta`,
  `marcar_conta_paga`, `listar_contas`, `remover_conta` da Frente 5); **remoção por id, não
  por posição**; a view nunca vê o `usuario_id` (fica encapsulado e é repassado à
  Persistencia). O **fluxo de caixa** não fica aqui: é `Relatorio.fluxo_de_caixa(ano, mes)`,
  que recebe a lista de contas e projeta entradas/saídas do mês.
- **Models novos** (Contrato C): `Usuario(id, email, senha_hash, perfil)` (Frente 1 — na
  `main`); `Perfil(ABC)` → `PessoaFisica()` / `Empresa()` (Frente 2 — implementado),
  expondo `categorias_disponiveis()` e `tipo_str()`, com factory `criar_perfil(tipo)`;
  `Conta(tipo, descricao, valor, vencimento, pago=False)` com `tipo` ∈ `{'pagar','receber'}`
  (Frente 5 — na `main`) — model com comportamento (`esta_vencida`, `para_dict`).

## As 7 frentes (donos e dependências)

| Frente | Responsável | Status | Integra após | Arquivo-bomba |
|---|---|---|---|---|
| 0 · Banco SQLite | Tarso | ✅ na `main` | — (é a base) | `db/schema.sql` (dono único) |
| 1 · Autenticação | João Guilherme Costa ("Jigui") | ✅ na `main` | 0, 2 | `models/__init__.py` |
| 2 · Perfis polimórficos | João Gustavo | ✅ na `main` | — (isolada) | `models/__init__.py` |
| 3 · Gerenciador + Isolamento | Vinícius | ✅ na `main` | 0 | — |
| 4 · Frontend Flask | Lívia + Alice | ✅ na `main` (faltam rotas auth/contas) | 1, 3 | `app.py` (dono único) |
| 5 · Empresa (contas/fluxo de caixa) | Tarso | ✅ na `main` | 2, 3 | `models/__init__.py` |
| 6 · Qualidade (testes) | João Guilherme Teles | ✅ na `main` | todas | — |

Branches correspondentes existem no remoto (`frente-2-perfis`, `frente-3-gerenciador`,
`frente-4-frontend-livia-alice`, `feat/jigui-login-cadastro`, `qualidade`, ...). Antes de
implementar algo de uma frente, confira com `git branch -a` se o trabalho já existe.

## Convenções (para 7 mãos parecerem uma só)

- **Tudo em português** — tabelas, colunas, métodos, classes, variáveis. Única exceção: `id`.
- **Regra de ouro: um conceito, um nome**, no projeto inteiro. Se é `usuario_id` no banco, é
  `usuario_id` no Python — nunca `user_id` num arquivo e `id_usuario` em outro.
- Nomenclatura: `snake_case` para funções/variáveis/arquivos; `PascalCase` para classes;
  `MAIÚSCULAS` para constantes; prefixo `_` para privado/uso interno.
- **Type hints obrigatórios** nas assinaturas. **Docstring curta** em toda função pública (o
  que faz, parâmetros, o que lança). Comentário explica o **porquê**, não o quê.
- Imports na ordem PEP 8: biblioteca padrão primeiro, depois código próprio, um por linha
  (reduz conflito de merge).
- **`id` é responsabilidade do banco**, não dos models; ao carregar, a Persistencia anexa
  `obj.id` dinamicamente.
- Convenções SQLite: `data`/`prazo`/`vencimento` como **texto ISO**
  (`.isoformat()` ⇄ `date.fromisoformat()`); `pago`/booleanos como **`0/1`**; `categoria`
  pode ser `str` ou objeto com `.nome` — normalize com
  `categoria.nome if hasattr(categoria, "nome") else str(categoria)`.

## Git e fluxo de trabalho

- `main` é sagrada — ninguém commita direto nela. **Uma branch por frente**
  (`frente-N-...`), curta, que sai da `main` e volta via **Pull Request** (1 colega revisa).
- Antes de subir: `git pull origin main` e resolva conflitos **localmente**.
- Commits com prefixo `feat:` / `fix:` / `refactor:` / `test:` / `docs:`. **O porquê mora no
  corpo do commit** — é o critério 3 da Definition of Done e vira o roteiro da apresentação.
- Arquivos-bomba e suas regras: `db/schema.sql` (dono único = Frente 0); `app.py` (só
  registra blueprints — dono Frente 4); `__init__.py` de models/services (imports em linhas
  separadas; uma pessoa faz o merge).
- `.gitignore`: `db/*.db` **nunca** versionado (binário = conflito garantido), além de
  `__pycache__/`, `*.pyc`, `venv/`, `.venv/`, `.vscode/`, `.idea/`.
