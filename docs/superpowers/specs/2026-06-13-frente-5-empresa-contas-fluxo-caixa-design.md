# Frente 5 — Empresa: contas a pagar/receber e fluxo de caixa

**Data:** 2026-06-13
**Responsável:** Tarso
**Frente:** 5 (Empresa / fluxo de caixa)
**Branch:** `frente-5-empresa`

## Contexto

O encanamento de contas já existe na `main` (Frentes 0 e 3 integradas):

- **Banco:** tabela `conta` (`tipo`, `descricao`, `valor`, `vencimento` ISO, `pago` 0/1, `usuario_id`).
- **Persistência:** `salvar_conta`, `carregar_contas`, `marcar_conta_paga`, `remover_conta` — isoladas por `usuario_id`. `carregar_contas` já faz `from models.conta import Conta`.
- **Gerenciador:** `adicionar_conta`, `marcar_conta_paga`, `listar_contas(tipo=...)`, `remover_conta`, com validação de `tipo ∈ {pagar,receber}`, descrição não-vazia e `valor > 0`.
- **Testes:** `tests/test_conta.py` já escrito, hoje **skipando** à espera de `models/conta.py`.

Falta: o **model `Conta`** (destrava o CRUD e os testes) e a camada de **fluxo de caixa** (análise — hoje inexistente), com **diferenciação por perfil** (empresa × pessoa física).

## Objetivos

1. Criar `models/conta.py` cumprindo o Contrato C.
2. Criar a camada de fluxo de caixa (`services/fluxo_caixa.py`) desacoplada da origem dos dados.
3. Diferenciar empresa × pessoa física via polimorfismo no `Perfil` (extensão mínima do Contrato C).
4. Ativar `tests/test_conta.py` e adicionar `tests/test_fluxo_caixa.py`.

## Não-objetivos (fora de escopo)

- Alterar `Relatorio` (continua só sobre transações).
- Alterar o CRUD de contas (Persistência/Gerenciador já prontos).
- Aplicar a validação de tipo-por-perfil na criação dentro do `Gerenciador.adicionar_conta` (fica para a view / Frente 4, que tem o perfil em mãos). A Frente 5 entrega a **regra** pronta e testada.
- Restringir rotas/telas por perfil (Frente 4).
- Depender da Frente 1 (`models/usuario.py`, `buscar_usuario_por_id`): o perfil é recebido **como parâmetro**, não buscado no banco pelo Gerenciador.

## Componentes

### 1. `models/conta.py` (novo) — model com comportamento

```
Conta(tipo, descricao, valor, vencimento, pago=False)
```

- **Atributos públicos** (contrato congelado de `test_conta.py`): `.tipo` (`"pagar"`/`"receber"`, string — não método), `.descricao`, `.valor` (float), `.vencimento` (preservado **cru**: str ISO ou `date`), `.pago` (bool; nasce `False`).
- **Validação no construtor** (defesa em profundidade, paralela a `Transacao`/`Meta`):
  - `tipo` deve estar em `("pagar", "receber")` → `ValueError`.
  - descrição não-vazia (após `strip()`) → `ValueError`.
  - `valor > 0` → `ValueError`.
  - Não quebra `test_conta.py` (todos os casos de teste são válidos).
- **Comportamento:**
  - `_vencimento_date() -> date` — normaliza `str ISO | date → date` internamente (`date.fromisoformat` quando string).
  - `esta_vencida(referencia: date | None = None) -> bool` — `True` se **não paga** e `_vencimento_date() < (referencia or date.today())`.
  - `para_dict() -> dict` — serialização (espelha `Transacao.para_dict`); `vencimento` como texto ISO.
- `id` é anexado dinamicamente pela Persistência (já implementado).

**Contrato de instanciação** (consumidores existentes, não alterar):
- `Gerenciador.adicionar_conta`: `Conta(tipo, descricao.strip(), valor, vencimento)` (posicional).
- `Persistencia.carregar_contas`: `Conta(tipo, descricao, valor, vencimento, pago=pago)` com `vencimento = date.fromisoformat(...)` (vira `date`), depois `obj.id = id_bd`.

### 2. `models/perfil.py` (extensão — coordenar com João Gustavo, dono da Frente 2)

Adiciona o polimorfismo que diferencia o domínio de contas, espelhando `categorias_disponiveis()`:

```python
# Perfil(ABC)
@abstractmethod
def tipos_conta(self) -> tuple[str, ...]:
    """Tipos de conta que este perfil pode ter ('pagar' / 'receber')."""

def permite_tipo_conta(self, tipo: str) -> bool:
    """Helper concreto: usa o polimórfico tipos_conta()."""
    return tipo in self.tipos_conta()

# PessoaFisica
def tipos_conta(self) -> tuple[str, ...]:
    return ("pagar",)              # pessoa física: só contas a pagar

# Empresa
def tipos_conta(self) -> tuple[str, ...]:
    return ("pagar", "receber")    # empresa: pagar + recebíveis
```

### 3. `services/fluxo_caixa.py` (novo) — classe `FluxoCaixa`

Desacoplada da origem: recebe uma lista de `Conta` e calcula em cima dela (espelha `Relatorio`). Recebe opcionalmente o `perfil` para adaptar os indicadores.

```python
FluxoCaixa(contas: list, perfil=None)
```

- `total_a_pagar() -> float` — soma do `valor` das contas **pendentes** (`not pago`) de tipo `"pagar"`.
- `total_a_receber() -> float` — idem para `"receber"`.
- `total_vencido(referencia=None) -> float` — soma do `valor` das contas que `esta_vencida()`.
- `contas_vencidas(referencia=None) -> list` — pendentes vencidas.
- `contas_a_vencer(referencia=None) -> list` — pendentes não vencidas.
- `mostra_recebiveis() -> bool` — `perfil is None or "receber" in perfil.tipos_conta()`. (Sem perfil = comportamento completo de empresa; retrocompatível.)
- `saldo_projetado() -> float` — empresa: `total_a_receber() - total_a_pagar()`; pessoa física (sem recebíveis): `-total_a_pagar()`.

Decisões:
- Os totais contam apenas **pendentes** (não pagas) — é o que importa para projeção de caixa.
- "Vencida" = não paga e `vencimento < referência` (default hoje).

### 4. `services/gerenciador.py` (um método novo)

```python
def fluxo_de_caixa(self, perfil=None) -> FluxoCaixa:
    from services.fluxo_caixa import FluxoCaixa          # import local, como os demais
    contas = Persistencia.carregar_contas(self._usuario_id)
    return FluxoCaixa(contas, perfil)
```

A view chamará `g.fluxo_de_caixa(perfil).saldo_projetado()` etc. — não calcula, só invoca. O `perfil` vem da sessão (Frente 4); `None` é aceito e cai no comportamento de empresa.

### 5. `models/__init__.py` (arquivo-bomba)

Adicionar `from .conta import Conta` (linha separada) e incluir `"Conta"` em `__all__`. Uma pessoa faz o merge.

## Fluxo de dados

```
View (Frente 4)
  │  perfil (sessão)
  ▼
Gerenciador(usuario_id).fluxo_de_caixa(perfil)
  │  carrega contas
  ▼
Persistencia.carregar_contas(usuario_id)  → list[Conta]
  │
  ▼
FluxoCaixa(contas, perfil)  → total_a_pagar / a_receber / saldo_projetado / vencidas
```

Criação de conta (já existente): `View → Gerenciador.adicionar_conta → Persistencia.salvar_conta`. A regra `perfil.permite_tipo_conta(tipo)` fica disponível para a view aplicar antes de chamar `adicionar_conta`.

## Testes

### `tests/test_conta.py` (ajuste)
Hoje skipa por `models.conta` **e** `services.auth`. Remover a dependência de `services.auth`: trocar `gerar_hash("s")` por um hash fictício (string literal), pois `cadastrar_usuario` só precisa de uma string. Manter `pytest.importorskip("models.conta")`.

### `tests/conftest.py` (ajuste na fixture `dois_usuarios`)
Os testes de isolamento de `test_conta.py` usam a fixture `dois_usuarios`, que hoje depende de `gerar_hash` (`services.auth`) e faz `pytest.skip` se ausente. Trocar os hashes por strings fictícias e remover o `skip`, desacoplando a fixture da Frente 1 (igual ao ajuste em `test_conta`). Seguro: `test_usuario.py` (outro consumidor de `dois_usuarios`) já skipa inteiro por `importorskip("services.auth")` no topo, então não é afetado. Sem esse ajuste, `test_conta.py` ativa só parcialmente (os 2 testes de isolamento continuariam skipando).

### `tests/test_fluxo_caixa.py` (novo)
Testa a classe com listas de `Conta` montadas à mão (sem banco):
- `total_a_pagar` / `total_a_receber` somam só pendentes; contas pagas não contam.
- `saldo_projetado` para empresa = receber − pagar.
- `total_vencido` / `contas_vencidas` / `contas_a_vencer` com `referencia` fixa (data determinística, sem depender de `date.today()`).
- **Diferenciação por perfil:**
  - `Empresa().tipos_conta() == ("pagar", "receber")`, `PessoaFisica().tipos_conta() == ("pagar",)`.
  - `permite_tipo_conta`: empresa permite `receber`, pessoa física não.
  - `FluxoCaixa(contas, PessoaFisica()).mostra_recebiveis() is False` e `saldo_projetado() == -total_a_pagar()`.
  - `FluxoCaixa(contas, Empresa()).mostra_recebiveis() is True`.

### Estado esperado da suíte
Após a Frente 5, na `main`: `test_conta.py` (9) e `test_fluxo_caixa.py` ativam e passam; `test_perfil.py` ganha cobertura de `tipos_conta`. Os skips restantes (`test_auth`, `test_rotas`, `test_usuario`) seguem aguardando Frentes 1 e 4.

## Convenções

- Tudo em português; `snake_case`/`PascalCase`; type hints nas assinaturas; docstring curta no público; comentário explica o porquê.
- `vencimento`/datas: texto ISO ⇄ `date.fromisoformat`; `pago` 0/1 no banco, `bool` no model.
- `id` é responsabilidade do banco (anexado dinamicamente).

## Ordem de implementação sugerida

1. `models/conta.py` + exportar em `models/__init__.py`.
2. Ajustar `tests/test_conta.py` e a fixture `dois_usuarios` em `tests/conftest.py` (remover dep de `services.auth`) → rodar (deve passar).
3. `models/perfil.py`: `tipos_conta()` + `permite_tipo_conta()`.
4. `services/fluxo_caixa.py`.
5. `services/gerenciador.py`: `fluxo_de_caixa(perfil=None)`.
6. `tests/test_fluxo_caixa.py` → rodar a suíte completa.
