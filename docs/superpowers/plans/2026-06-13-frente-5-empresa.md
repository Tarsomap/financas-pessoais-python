# Frente 5 — Empresa (contas / fluxo de caixa) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar o model `Conta`, a camada de fluxo de caixa e a diferenciação empresa × pessoa física, destravando os testes de contas.

**Architecture:** `Conta` é um model com comportamento (validação, `esta_vencida`, `para_dict`). `FluxoCaixa` é uma classe desacoplada que recebe `list[Conta]` e calcula indicadores, adaptando-os pelo `perfil`. O `Gerenciador` ganha `fluxo_de_caixa(perfil)` que carrega as contas e delega. O `Perfil` ganha `tipos_conta()` polimórfico. O CRUD de contas (Persistência/Gerenciador) já existe na `main`.

**Tech Stack:** Python 3 (stdlib), `sqlite3`, `pytest`. Banco de teste `:memory:` via `Persistencia.configurar_banco`.

**Branch:** `frente-5-empresa` (já criada a partir da `main`).

**Comando de teste:** `./venv/bin/python -m pytest tests/ -q`

---

### Task 1: Desacoplar `test_conta.py` e a fixture `dois_usuarios` de `services.auth`

Hoje `test_conta.py` skipa por `models.conta` **e** `services.auth`; e a fixture `dois_usuarios` (conftest) faz `pytest.skip` sem `gerar_hash`. Removemos a dependência de `services.auth` (que não existe ainda) — `cadastrar_usuario` só precisa de uma string como hash.

**Files:**
- Modify: `tests/conftest.py`
- Modify: `tests/test_conta.py`

- [ ] **Step 1: Substituir a fixture `dois_usuarios` no conftest**

Em `tests/conftest.py`, substituir a função `dois_usuarios` inteira por:

```python
@pytest.fixture
def dois_usuarios(banco_limpo):
    """
    Cria dois usuários distintos no banco de teste.

    Usa hashes fictícios — cadastrar_usuario só precisa de uma string, então
    a fixture não depende de services.auth (Frente 1).
    """
    id_a = Persistencia.cadastrar_usuario(
        email="alice@teste.com", senha_hash="hash_ficticio_a", tipo_perfil="pessoa_fisica"
    )
    id_b = Persistencia.cadastrar_usuario(
        email="bob@teste.com", senha_hash="hash_ficticio_b", tipo_perfil="empresa"
    )
    return {"id_a": id_a, "id_b": id_b}
```

- [ ] **Step 2: Remover a dependência de `services.auth` em `test_conta.py`**

Em `tests/test_conta.py`:
1. Remover a linha `pytest.importorskip("services.auth")` (manter `pytest.importorskip("models.conta")`).
2. Remover a linha `from services.auth import gerar_hash`.
3. Substituir todas as ocorrências de `gerar_hash("s")` por `"hash_ficticio"`.

- [ ] **Step 3: Rodar a suíte — `test_conta` ainda skipa só por `models.conta`**

Run: `./venv/bin/python -m pytest tests/ -q`
Expected: `54 passed, 4 skipped` (igual ao atual; `test_conta` continua skipando por `models.conta`, agora não mais por `services.auth`).

- [ ] **Step 4: Commit**

```bash
git add tests/conftest.py tests/test_conta.py
git commit -m "test: desacopla test_conta e fixture dois_usuarios de services.auth"
```

---

### Task 2: Model `Conta` (com validação, `esta_vencida`, `para_dict`)

**Files:**
- Create: `models/conta.py`
- Modify: `models/__init__.py`
- Modify: `tests/test_conta.py` (adicionar testes de comportamento)

- [ ] **Step 1: Escrever os testes de comportamento do model em `test_conta.py`**

Em `tests/test_conta.py`, adicionar `from datetime import date` no topo (após `import pytest`) e acrescentar esta classe ao final do arquivo:

```python
class TestContaComportamento:
    """Validação no construtor e métodos esta_vencida/para_dict."""

    def test_tipo_invalido_levanta(self):
        with pytest.raises(ValueError):
            Conta(tipo="xpto", descricao="X", valor=10.0, vencimento="2026-01-01")

    def test_valor_invalido_levanta(self):
        with pytest.raises(ValueError):
            Conta(tipo="pagar", descricao="X", valor=0, vencimento="2026-01-01")

    def test_descricao_vazia_levanta(self):
        with pytest.raises(ValueError):
            Conta(tipo="pagar", descricao="   ", valor=10.0, vencimento="2026-01-01")

    def test_esta_vencida_quando_passou_e_nao_paga(self):
        c = Conta(tipo="pagar", descricao="X", valor=10.0, vencimento="2026-01-01")
        assert c.esta_vencida(date(2026, 6, 1)) is True

    def test_nao_vencida_se_paga(self):
        c = Conta(tipo="pagar", descricao="X", valor=10.0, vencimento="2026-01-01", pago=True)
        assert c.esta_vencida(date(2026, 6, 1)) is False

    def test_nao_vencida_se_vencimento_futuro(self):
        c = Conta(tipo="pagar", descricao="X", valor=10.0, vencimento="2026-12-31")
        assert c.esta_vencida(date(2026, 6, 1)) is False

    def test_para_dict(self):
        c = Conta(tipo="pagar", descricao="Aluguel", valor=1500.0, vencimento="2026-06-01")
        assert c.para_dict() == {
            "tipo": "pagar", "descricao": "Aluguel", "valor": 1500.0,
            "vencimento": "2026-06-01", "pago": False,
        }
```

- [ ] **Step 2: Rodar — deve skipar (model ainda não existe)**

Run: `./venv/bin/python -m pytest tests/test_conta.py -q`
Expected: SKIPPED (`could not import 'models.conta'`).

- [ ] **Step 3: Criar `models/conta.py`**

```python
# models/conta.py
# RESPONSÁVEL: Tarso - Frente 5 (Empresa: contas a pagar/receber)

from datetime import date


class Conta:
    """
    Conta a pagar ou a receber — funcionalidade central do perfil Empresa.

    vencimento é guardado COMO VEIO (str ISO ou date): a conversão para texto
    do banco é responsabilidade da Persistencia. O id é anexado dinamicamente
    pelo banco ao carregar, como em Transacao e Meta.
    """

    TIPOS_VALIDOS = ("pagar", "receber")

    def __init__(self, tipo: str, descricao: str, valor: float,
                 vencimento, pago: bool = False):
        # Validação no construtor — defesa em profundidade, igual a Transacao/Meta.
        if tipo not in self.TIPOS_VALIDOS:
            raise ValueError("tipo deve ser 'pagar' ou 'receber'.")
        if not descricao or not descricao.strip():
            raise ValueError("A descrição da conta não pode ser vazia.")
        if valor <= 0:
            raise ValueError("O valor da conta deve ser maior que zero.")

        self.tipo = tipo
        self.descricao = descricao.strip()
        self.valor = float(valor)
        self.vencimento = vencimento     # cru: str ISO ou date
        self.pago = bool(pago)

    def _vencimento_date(self) -> date:
        """Normaliza vencimento (str ISO ou date) para um date, para comparar."""
        if isinstance(self.vencimento, date):
            return self.vencimento
        return date.fromisoformat(self.vencimento)

    def esta_vencida(self, referencia: date | None = None) -> bool:
        """True se a conta NÃO está paga e já passou do vencimento (default hoje)."""
        if self.pago:
            return False
        referencia = referencia or date.today()
        return self._vencimento_date() < referencia

    def para_dict(self) -> dict:
        """Serializa a conta; vencimento sai como texto ISO."""
        return {
            "tipo": self.tipo,
            "descricao": self.descricao,
            "valor": self.valor,
            "vencimento": self._vencimento_date().isoformat(),
            "pago": self.pago,
        }
```

- [ ] **Step 4: Exportar `Conta` em `models/__init__.py`**

Adicionar a linha de import (em linha separada, junto aos outros imports de model):

```python
from .conta import Conta
```

E incluir `"Conta"` na lista `__all__`.

- [ ] **Step 5: Rodar — `test_conta.py` inteiro deve passar**

Run: `./venv/bin/python -m pytest tests/test_conta.py -q`
Expected: PASS (os 10 originais + 7 de comportamento = 17 passed).

- [ ] **Step 6: Rodar a suíte completa**

Run: `./venv/bin/python -m pytest tests/ -q`
Expected: `71 passed, 3 skipped` (test_conta ativou; restam skips de `test_auth`, `test_rotas`, `test_usuario`).

- [ ] **Step 7: Commit**

```bash
git add models/conta.py models/__init__.py tests/test_conta.py
git commit -m "feat: model Conta com validacao, esta_vencida e para_dict (Frente 5)"
```

---

### Task 3: `Perfil.tipos_conta()` + `permite_tipo_conta()`

**Files:**
- Modify: `models/perfil.py`
- Test: `tests/test_fluxo_caixa.py` (criar arquivo com a primeira classe de teste)

- [ ] **Step 1: Escrever o teste em `tests/test_fluxo_caixa.py`**

Criar `tests/test_fluxo_caixa.py` com:

```python
# tests/test_fluxo_caixa.py
# RESPONSÁVEL: Tarso - Frente 5 (fluxo de caixa e diferenciação por perfil)

import pytest
from datetime import date

pytest.importorskip("models.conta")

from models.perfil import PessoaFisica, Empresa


class TestPerfilTiposConta:
    def test_empresa_tem_pagar_e_receber(self):
        assert Empresa().tipos_conta() == ("pagar", "receber")

    def test_pessoa_fisica_so_pagar(self):
        assert PessoaFisica().tipos_conta() == ("pagar",)

    def test_permite_tipo_conta(self):
        assert Empresa().permite_tipo_conta("receber") is True
        assert PessoaFisica().permite_tipo_conta("receber") is False
        assert PessoaFisica().permite_tipo_conta("pagar") is True
```

- [ ] **Step 2: Rodar — deve falhar (`tipos_conta` não existe)**

Run: `./venv/bin/python -m pytest tests/test_fluxo_caixa.py -q`
Expected: FAIL (`AttributeError`/`TypeError`: `tipos_conta`).

- [ ] **Step 3: Implementar em `models/perfil.py`**

No `Perfil(ABC)`, adicionar o método abstrato e o helper concreto (após `tipo_str`):

```python
    @abstractmethod
    def tipos_conta(self) -> tuple[str, ...]:
        """Tipos de conta a pagar/receber que este perfil pode ter."""
        pass

    def permite_tipo_conta(self, tipo: str) -> bool:
        """Indica se este perfil pode ter uma conta do tipo informado."""
        return tipo in self.tipos_conta()
```

Em `PessoaFisica`, adicionar:

```python
    def tipos_conta(self) -> tuple[str, ...]:
        return ("pagar",)  # pessoa física: só contas a pagar
```

Em `Empresa`, adicionar:

```python
    def tipos_conta(self) -> tuple[str, ...]:
        return ("pagar", "receber")  # empresa: pagar + recebíveis
```

- [ ] **Step 4: Rodar — deve passar**

Run: `./venv/bin/python -m pytest tests/test_fluxo_caixa.py -q`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add models/perfil.py tests/test_fluxo_caixa.py
git commit -m "feat: Perfil.tipos_conta polimorfico p/ diferenciar empresa x pessoa fisica"
```

---

### Task 4: `services/fluxo_caixa.py` — classe `FluxoCaixa`

**Files:**
- Create: `services/fluxo_caixa.py`
- Test: `tests/test_fluxo_caixa.py` (adicionar classes de teste)

- [ ] **Step 1: Escrever os testes de `FluxoCaixa`**

Em `tests/test_fluxo_caixa.py`, adicionar o import e as classes de teste ao final:

```python
from models.conta import Conta
from services.fluxo_caixa import FluxoCaixa


def _conta(tipo, valor, vencimento="2026-06-01", pago=False):
    return Conta(tipo=tipo, descricao="x", valor=valor, vencimento=vencimento, pago=pago)


class TestTotais:
    def test_total_a_pagar_soma_pendentes(self):
        contas = [_conta("pagar", 100), _conta("pagar", 50), _conta("receber", 999)]
        assert FluxoCaixa(contas).total_a_pagar() == 150.0

    def test_total_a_receber_soma_pendentes(self):
        contas = [_conta("receber", 300), _conta("receber", 200), _conta("pagar", 999)]
        assert FluxoCaixa(contas).total_a_receber() == 500.0

    def test_pagas_nao_contam(self):
        contas = [_conta("pagar", 100, pago=True), _conta("pagar", 40)]
        assert FluxoCaixa(contas).total_a_pagar() == 40.0


class TestVencimento:
    HOJE = date(2026, 6, 15)

    def test_contas_vencidas_e_total(self):
        contas = [_conta("pagar", 100, vencimento="2026-06-01"),   # vencida
                  _conta("pagar", 50, vencimento="2026-06-30")]    # a vencer
        fc = FluxoCaixa(contas)
        assert len(fc.contas_vencidas(self.HOJE)) == 1
        assert fc.total_vencido(self.HOJE) == 100.0

    def test_contas_a_vencer(self):
        contas = [_conta("pagar", 100, vencimento="2026-06-01"),
                  _conta("pagar", 50, vencimento="2026-06-30")]
        assert len(FluxoCaixa(contas).contas_a_vencer(self.HOJE)) == 1

    def test_paga_nunca_e_vencida(self):
        contas = [_conta("pagar", 100, vencimento="2026-06-01", pago=True)]
        assert FluxoCaixa(contas).contas_vencidas(self.HOJE) == []


class TestDiferenciacaoPerfil:
    def test_empresa_mostra_recebiveis_e_saldo_completo(self):
        contas = [_conta("receber", 1000), _conta("pagar", 400)]
        fc = FluxoCaixa(contas, Empresa())
        assert fc.mostra_recebiveis() is True
        assert fc.saldo_projetado() == 600.0

    def test_pessoa_fisica_sem_recebiveis(self):
        contas = [_conta("pagar", 400)]
        fc = FluxoCaixa(contas, PessoaFisica())
        assert fc.mostra_recebiveis() is False
        assert fc.saldo_projetado() == -400.0

    def test_sem_perfil_assume_empresa(self):
        contas = [_conta("receber", 1000), _conta("pagar", 400)]
        fc = FluxoCaixa(contas)
        assert fc.mostra_recebiveis() is True
        assert fc.saldo_projetado() == 600.0
```

- [ ] **Step 2: Rodar — deve falhar (`services.fluxo_caixa` não existe)**

Run: `./venv/bin/python -m pytest tests/test_fluxo_caixa.py -q`
Expected: FAIL (`ModuleNotFoundError: No module named 'services.fluxo_caixa'`).

- [ ] **Step 3: Criar `services/fluxo_caixa.py`**

```python
# services/fluxo_caixa.py
# RESPONSÁVEL: Tarso - Frente 5 (fluxo de caixa)

from datetime import date


class FluxoCaixa:
    """
    Indicadores de contas a pagar/receber de um usuário.

    Desacoplado da origem: recebe uma lista de Conta e calcula em cima dela,
    no mesmo espírito do Relatorio. O perfil, quando informado, adapta os
    indicadores — pessoa física não tem recebíveis, então não há saldo
    projetado "completo". Sem perfil, assume o comportamento de empresa.
    """

    def __init__(self, contas: list, perfil=None):
        self._contas = list(contas)
        self._perfil = perfil

    def _pendentes(self, tipo: str) -> list:
        """Contas não pagas de um tipo ('pagar'/'receber')."""
        return [c for c in self._contas if c.tipo == tipo and not c.pago]

    def total_a_pagar(self) -> float:
        return round(sum(c.valor for c in self._pendentes("pagar")), 2)

    def total_a_receber(self) -> float:
        return round(sum(c.valor for c in self._pendentes("receber")), 2)

    def mostra_recebiveis(self) -> bool:
        """Pessoa física não tem 'receber'; sem perfil, assume empresa."""
        return self._perfil is None or "receber" in self._perfil.tipos_conta()

    def saldo_projetado(self) -> float:
        """Empresa: receber − pagar. Pessoa física (sem recebíveis): −pagar."""
        if self.mostra_recebiveis():
            return round(self.total_a_receber() - self.total_a_pagar(), 2)
        return round(-self.total_a_pagar(), 2)

    def contas_vencidas(self, referencia: date | None = None) -> list:
        return [c for c in self._contas if c.esta_vencida(referencia)]

    def contas_a_vencer(self, referencia: date | None = None) -> list:
        return [
            c for c in self._contas
            if not c.pago and not c.esta_vencida(referencia)
        ]

    def total_vencido(self, referencia: date | None = None) -> float:
        return round(sum(c.valor for c in self.contas_vencidas(referencia)), 2)
```

- [ ] **Step 4: Rodar — deve passar**

Run: `./venv/bin/python -m pytest tests/test_fluxo_caixa.py -q`
Expected: PASS (todas as classes de teste do arquivo).

- [ ] **Step 5: Commit**

```bash
git add services/fluxo_caixa.py tests/test_fluxo_caixa.py
git commit -m "feat: FluxoCaixa com totais, vencidas e saldo projetado por perfil"
```

---

### Task 5: `Gerenciador.fluxo_de_caixa(perfil)`

**Files:**
- Modify: `services/gerenciador.py` (adicionar método após `remover_conta`, antes da seção de helpers privados)
- Test: `tests/test_fluxo_caixa.py` (adicionar teste de integração com banco)

- [ ] **Step 1: Escrever o teste de integração**

Em `tests/test_fluxo_caixa.py`, adicionar ao final:

```python
class TestGerenciadorFluxo:
    def test_fluxo_de_caixa_via_gerenciador(self, banco_limpo):
        from services.persistencia import Persistencia
        from services.gerenciador import Gerenciador

        uid = Persistencia.cadastrar_usuario("e@e.com", "hash_ficticio", "empresa")
        g = Gerenciador(uid)
        g.adicionar_conta("pagar", "Fornecedor", 300.0, "2026-06-01")
        g.adicionar_conta("receber", "Cliente", 500.0, "2026-06-10")

        fc = g.fluxo_de_caixa(Empresa())
        assert fc.total_a_pagar() == 300.0
        assert fc.total_a_receber() == 500.0
        assert fc.saldo_projetado() == 200.0
```

- [ ] **Step 2: Rodar — deve falhar (`fluxo_de_caixa` não existe)**

Run: `./venv/bin/python -m pytest "tests/test_fluxo_caixa.py::TestGerenciadorFluxo" -q`
Expected: FAIL (`AttributeError: 'Gerenciador' object has no attribute 'fluxo_de_caixa'`).

- [ ] **Step 3: Implementar `fluxo_de_caixa` no `Gerenciador`**

Em `services/gerenciador.py`, logo após o método `remover_conta` (fim da seção "CONTAS A PAGAR / RECEBER"), adicionar:

```python
    def fluxo_de_caixa(self, perfil=None) -> "FluxoCaixa":
        """
        Monta o fluxo de caixa do usuário (contas a pagar/receber).

        Recebe o perfil (da sessão) para adaptar os indicadores; None cai no
        comportamento completo de empresa. Não busca o usuário no banco — assim
        não depende da Frente 1 (models/usuario.py).
        """
        from services.fluxo_caixa import FluxoCaixa

        contas = Persistencia.carregar_contas(self._usuario_id)
        return FluxoCaixa(contas, perfil)
```

- [ ] **Step 4: Rodar — o teste de integração deve passar**

Run: `./venv/bin/python -m pytest "tests/test_fluxo_caixa.py::TestGerenciadorFluxo" -q`
Expected: PASS.

- [ ] **Step 5: Rodar a suíte completa**

Run: `./venv/bin/python -m pytest tests/ -q`
Expected: `PASS` — todos os testes verdes; só os 3 skips de Frentes 1/4 (`test_auth`, `test_rotas`, `test_usuario`).

- [ ] **Step 6: Commit**

```bash
git add services/gerenciador.py tests/test_fluxo_caixa.py
git commit -m "feat: Gerenciador.fluxo_de_caixa(perfil) carrega contas e delega ao FluxoCaixa"
```

---

## Notas de integração

- **`models/perfil.py` é da Frente 2 (João Gustavo):** a extensão `tipos_conta()` precisa ser combinada com ele (estende o Contrato C). Coordenar antes do merge.
- **Merge:** abrir PR de `frente-5-empresa` para `main`. `models/__init__.py` é arquivo-bomba — conferir conflito antes de subir.
- **Pós-merge esperado na `main`:** suíte com `test_conta.py` e `test_fluxo_caixa.py` ativos; apenas `test_auth`, `test_rotas`, `test_usuario` skipando (Frentes 1 e 4).
