# Guia de estudo do codigo

Este guia explica o projeto como material de prova. A ideia nao e corrigir o
codigo, e sim entender o que cada parte faz, quais sintaxes aparecem e como voce
pode explicar o sistema em voz alta.

## 1. Visao geral do projeto

O projeto atual e uma aplicacao Flask de financas pessoais com:

- `app.py`: cria o app Flask, importa blueprints e registra rotas.
- `routes/`: camada de rotas HTTP, ou seja, as funcoes chamadas quando o usuario acessa uma URL.
- `templates/`: paginas HTML com Jinja2, renderizadas pelo Flask.
- `static/style.css`: estilo visual das paginas.
- `models/`: classes de dominio, como `Transacao`, `Meta`, `Usuario`, `Conta`.
- `services/`: regras de negocio e persistencia, como `Gerenciador`, `Persistencia`, `Relatorio`, `auth`.
- `db/schema.sql`: criacao das tabelas SQLite.
- `tests/`: testes automatizados com pytest.

Fluxo principal:

1. O navegador acessa uma URL, por exemplo `/transacoes`.
2. O Flask procura qual funcao de rota atende essa URL.
3. A rota verifica se existe `usuario_id` na `session`.
4. A rota cria um `Gerenciador(session["usuario_id"])`.
5. O `Gerenciador` chama `Persistencia`.
6. `Persistencia` executa SQL no SQLite.
7. A rota recebe objetos Python e chama `render_template`.
8. O template HTML mostra os dados na tela.

## 2. Sintaxes importantes que passam de if/else

### Imports e pacotes

`from flask import Flask` importa apenas a classe `Flask` do pacote `flask`.

`from models.transacao import Receita` importa a classe `Receita` de um arquivo
especifico dentro do pacote `models`.

`models/__init__.py` transforma a pasta `models` em pacote e permite escrever:

```python
from models import Receita, Despesa
```

em vez de:

```python
from models.transacao import Receita, Despesa
```

### Type hints

Exemplo:

```python
def gerar_hash(senha: str) -> str:
```

Significa: a funcao espera `senha` como `str` e promete retornar `str`.

Exemplo:

```python
perfil: Perfil | None = None
```

Significa: o parametro pode ser um objeto `Perfil` ou `None`.

Exemplo:

```python
def categorias_disponiveis(self) -> list[str]:
```

Significa: retorna uma lista de strings.

### `from __future__ import annotations`

Permite usar type hints mais modernos sem o Python tentar resolver tudo
imediatamente na hora de carregar o arquivo. Ajuda em casos de tipos que ainda
nao foram definidos completamente ou referencias futuras.

### Classes, objetos e `self`

Uma classe e um molde. Um objeto e uma instancia desse molde.

`self` representa o proprio objeto. Exemplo:

```python
self.email = email.strip().lower()
```

Quer dizer: guarde esse email dentro deste usuario especifico.

### Construtor `__init__`

`__init__` roda automaticamente quando voce cria um objeto.

```python
u = Usuario(id=1, email="a@b.com", senha_hash="h", tipo_perfil="empresa")
```

Isso chama `Usuario.__init__`.

### Encapsulamento com `_atributo` e `@property`

Em `Transacao`, os dados sao salvos como `_descricao`, `_valor`, `_categoria`,
`_data`. O `_` e uma convencao: "isso e interno, nao mexa direto".

O `@property` permite acessar como atributo:

```python
t.valor
```

mas por dentro chama:

```python
def valor(self):
    return self._valor
```

### Heranca e polimorfismo

`Receita(Transacao)` significa: Receita herda de Transacao.

`Despesa(Transacao)` tambem herda. As duas reaproveitam validacao, descricao,
valor, categoria, data e `para_dict`.

Polimorfismo aparece em `tipo()`:

- `Receita.tipo()` retorna `"receita"`.
- `Despesa.tipo()` retorna `"despesa"`.

O codigo pode chamar `t.tipo()` sem saber se `t` e Receita ou Despesa. O objeto
decide a resposta.

### Classe abstrata, `ABC` e `@abstractmethod`

Em `Perfil(ABC)`, a classe vira uma base abstrata. Ela define um contrato:
todo perfil precisa ter `categorias_disponiveis()` e `tipo_str()`.

`@abstractmethod` diz: subclasses sao obrigadas a implementar esse metodo.

Por isso `PessoaFisica` e `Empresa` implementam os dois.

### `@classmethod`

Recebe `cls`, que representa a propria classe.

Em `Categoria.listar_padroes`, `cls(nome, icone)` cria objetos da classe atual.

Em `Meta.from_dict`, `cls(...)` cria uma `Meta` a partir de um dicionario.

Em `Persistencia.configurar_banco`, `cls` permite alterar atributos da classe,
como `_caminho_banco`, sem precisar criar objeto `Persistencia`.

### `@staticmethod`

Metodo dentro de uma classe, mas que nao usa `self` nem `cls`.

Exemplos:

- `Persistencia._conectar()`
- `Persistencia._executar()`
- `Gerenciador._validar_transacao()`
- `Relatorio._vencimento()`

Ele fica dentro da classe por organizacao, nao porque depende de um objeto.

### Decorator de rota Flask

Exemplo:

```python
@transacoes_bp.route("/")
def listar():
```

O decorator registra que a URL `/` daquele blueprint chama a funcao `listar`.

Exemplo com metodo HTTP:

```python
@transacoes_bp.route("/nova", methods=["POST"])
```

Significa: essa rota aceita formulario enviado por POST, nao so abertura de pagina por GET.

Exemplo com parametro:

```python
@metas_bp.route("/<int:id>/depositar", methods=["POST"])
```

O Flask pega a parte da URL, converte para inteiro e passa como parametro `id`
da funcao.

### `session`, `redirect`, `url_for`, `flash`, `request`

- `session`: memoria de sessao do usuario no navegador; guarda, por exemplo, `usuario_id`.
- `redirect(...)`: manda o navegador para outra rota.
- `url_for("transacoes.listar")`: monta a URL correta pelo nome da rota.
- `flash("mensagem", "categoria")`: guarda uma mensagem temporaria para mostrar ao usuario.
- `request.form.get("campo")`: pega dados enviados por formulario HTML.

### Context manager `with`

Em SQLite:

```python
with conn:
    conn.execute(sql, params)
```

Se der certo, faz commit. Se der erro, faz rollback.

Em testes:

```python
with pytest.raises(ValueError):
```

O teste espera uma excecao. Se a excecao nao acontecer, o teste falha.

### `try`, `except`, `finally`

`try`: tente rodar.

`except`: se der um erro esperado, trate.

`finally`: rode sempre, dando erro ou nao. Em `Persistencia`, serve para fechar conexao.

### List comprehension

Exemplo:

```python
despesas = [t for t in transacoes if t.tipo() == "despesa"]
```

Cria uma nova lista somente com transacoes do tipo despesa.

### Generator expression e `next`

Exemplo:

```python
meta = next((m for m in metas if m.id == meta_id), None)
```

Procura a primeira meta com aquele id. Se nao achar, devolve `None`.

### `sum`, `round`, `sorted`, `lambda`

- `sum(...)`: soma valores.
- `round(valor, 2)`: arredonda com duas casas.
- `sorted(lista, key=..., reverse=True)`: ordena uma lista.
- `lambda t: t.data`: funcao anonima pequena usada como chave de ordenacao.

### F-string

Exemplo:

```python
f"R$ {self._valor:.2f}"
```

Monta string interpolando valores. `:.2f` formata numero com duas casas decimais.

### SQL com placeholders

Exemplo:

```python
"WHERE email = ?"
```

O `?` e substituido pelos parametros enviados em tupla:

```python
(email,)
```

Isso evita SQL injection porque os dados nao viram codigo SQL.

### Jinja2 nos templates

- `{% extends "base.html" %}`: herda estrutura de outro template.
- `{% block content %}`: define um bloco substituivel.
- `{{ variavel }}`: imprime valor.
- `{% if condicao %}`: condicional no HTML.
- `{% for item in lista %}`: loop no HTML.
- `{{ "%.2f"|format(valor) }}`: filtro de formatacao.
- `{{ transacoes|length }}`: tamanho da lista.
- `{% set percentual = ... %}`: cria variavel temporaria no template.

### CSS importante

- `:root`: define variaveis globais de CSS, como `--primary-color`.
- `var(--primary-color)`: usa uma variavel CSS.
- `display: flex`: organiza itens em linha/coluna flexivel.
- `display: grid`: cria grade responsiva.
- `@media (max-width: 768px)`: regras para tela pequena.
- `transition`: animacao suave.
- `box-shadow`: sombra.
- `border-radius`: cantos arredondados.

## 3. `app.py`

Responsabilidade: montar a aplicacao Flask.

Pontos principais:

- `app = Flask(__name__)`: cria a aplicacao.
- `app.secret_key = ...`: chave usada para sessao e mensagens temporarias.
- `app.register_blueprint(...)`: conecta grupos de rotas ao app.
- `if __name__ == "__main__": app.run(debug=True)`: roda o servidor so quando o arquivo e executado diretamente.

Atencao: o arquivo importa `routes.auth` e `routes.contas`, mas esses arquivos
nao existem no projeto atual. Por isso a execucao quebra antes de abrir o servidor.

## 4. Models

### `models/transacao.py`

`class Transacao`

Classe base para movimentacoes financeiras. Nao representa receita ou despesa
diretamente; serve como base comum.

Funcoes/metodos:

- `__init__(descricao, valor, categoria, data=None)`: valida descricao e valor, normaliza descricao com `strip`, converte valor para `float`, guarda categoria e usa `date.today()` se data nao vier.
- `descricao`: `@property`; devolve `_descricao`.
- `valor`: `@property`; devolve `_valor`.
- `categoria`: `@property`; devolve `_categoria`.
- `data`: `@property`; devolve `_data`.
- `tipo()`: metodo abstrato manual; na classe base levanta `NotImplementedError` para obrigar subclasses a sobrescreverem.
- `para_dict()`: transforma a transacao em dicionario com tipo, descricao, valor, categoria e data.
- `__str__()`: devolve representacao legivel, usada quando o objeto precisa virar texto.

`class Receita(Transacao)`

- `tipo()`: retorna `"receita"`.

`class Despesa(Transacao)`

- `tipo()`: retorna `"despesa"`.

### `models/categoria.py`

`class Categoria`

Representa uma categoria com nome e icone.

Elementos:

- `CATEGORIAS_PADRAO`: atributo de classe com tuplas `(nome, icone)`.
- `__init__(nome, icone="...")`: valida nome, remove espacos e guarda icone.
- `nome`: `@property`; devolve `_nome`.
- `icone`: `@property`; devolve `_icone`.
- `listar_padroes()`: `@classmethod`; cria uma lista de objetos `Categoria` usando `CATEGORIAS_PADRAO`.
- `__str__()`: devolve texto com icone e nome.

### `models/meta.py`

`class Meta`

Representa uma meta financeira, como juntar dinheiro para viagem.

Funcoes/metodos:

- `__init__(nome, valor_alvo, prazo="Sem prazo")`: valida nome e valor alvo; inicia `valor_atual` em `0.0`.
- `depositar(valor)`: soma dinheiro a meta, mas nao deixa passar do valor alvo.
- `progresso_percentual()`: calcula `valor_atual / valor_alvo * 100`.
- `valor_restante()`: calcula quanto falta.
- `concluida()`: retorna `True` se `valor_atual >= valor_alvo`.
- `__repr__()`: representacao tecnica do objeto, boa para debug/testes.
- `to_dict()`: transforma a meta em dicionario, convertendo prazo para string quando possivel.
- `from_dict(cls, dados)`: `@classmethod`; cria uma `Meta` a partir de um dicionario.

### `models/perfil.py`

`class Perfil(ABC)`

Classe abstrata que define o contrato de perfis.

Funcoes/metodos:

- `categorias_disponiveis()`: abstrato; cada perfil deve retornar suas categorias.
- `tipo_str()`: abstrato; cada perfil deve dizer o texto salvo no banco.
- `__str__()`: retorna `tipo_str()`.

`class PessoaFisica(Perfil)`

- `CATEGORIAS`: lista de categorias de pessoa fisica.
- `categorias_disponiveis()`: retorna uma copia da lista de categorias.
- `tipo_str()`: retorna `"pessoa_fisica"`.

`class Empresa(Perfil)`

- `CATEGORIAS`: lista de categorias empresariais.
- `categorias_disponiveis()`: retorna uma copia da lista empresarial.
- `tipo_str()`: retorna `"empresa"`.

Funcao solta:

- `criar_perfil(tipo)`: factory; recebe texto e devolve `PessoaFisica()` ou `Empresa()`. Se vier vazio ou desconhecido, levanta `ValueError`.

### `models/usuario.py`

`class Usuario`

Representa usuario autenticavel.

Funcoes/metodos:

- `__init__(id, email, senha_hash, perfil=None, tipo_perfil=None)`: valida email e hash. Se nao receber perfil pronto, cria um perfil usando `criar_perfil(tipo_perfil)`.
- `tipo_perfil`: `@property`; retorna `self.perfil.tipo_str()`.
- `__repr__()`: representacao tecnica com id, email e tipo de perfil.

### `models/conta.py`

`class Conta`

Representa conta a pagar ou receber.

Elementos:

- `TIPOS_VALIDOS = ("pagar", "receber")`: tupla com valores permitidos.

Funcoes/metodos:

- `__init__(tipo, descricao, valor, vencimento, pago=False)`: valida tipo, descricao e valor; guarda vencimento como veio; converte `pago` para booleano.
- `_vencimento_date()`: helper privado; converte vencimento string ISO ou `date` para `date`.
- `esta_vencida(referencia=None)`: retorna `True` se nao esta paga e a data de vencimento ja passou.
- `para_dict()`: transforma conta em dicionario, com vencimento em texto ISO.

### `models/__init__.py`

Importa as classes principais dos arquivos de model e define `__all__`.

`__all__` diz quais nomes sao considerados exportados quando alguem usa o pacote
`models`.

## 5. Services

### `services/auth.py`

Responsabilidade: cadastro e login por email/senha.

Constantes:

- `ALGORITMO = "pbkdf2_sha256"`: nome do algoritmo salvo junto ao hash.
- `ITERACOES = 260_000`: quantidade de repeticoes do PBKDF2.
- `TAMANHO_SALT = 16`: quantidade de bytes aleatorios do salt.

Funcoes:

- `gerar_hash(senha: str) -> str`: valida senha, cria salt aleatorio, calcula hash PBKDF2-HMAC-SHA256 e retorna string no formato `algoritmo$iteracoes$salt$hash`.
- `verificar_senha(senha: str, senha_hash: str) -> bool`: quebra a string salva, recalcula o hash da senha digitada e compara com `hmac.compare_digest`.
- `cadastrar_usuario(email, senha, tipo_perfil="pessoa_fisica") -> Usuario`: normaliza email, gera hash, salva no banco e busca o usuario salvo.
- `autenticar(email, senha) -> Usuario | None`: normaliza email, busca usuario e confere senha. Retorna objeto ou `None`.
- `login(email, senha) -> Usuario | None`: alias para `autenticar`, so para deixar chamada mais legivel.
- `_normalizar_email(email) -> str`: helper privado; remove espacos e deixa minusculo.

Seguranca importante:

- Salt faz duas senhas iguais gerarem hashes diferentes.
- PBKDF2 deixa tentativa de ataque mais cara.
- `compare_digest` evita comparacao insegura caractere por caractere.

### `services/persistencia.py`

Responsabilidade: acesso ao SQLite.

Constantes:

- `CAMINHO_BANCO`: caminho do arquivo `db/financas.db`.
- `CAMINHO_SCHEMA`: caminho do arquivo `db/schema.sql`.

`class Persistencia`

Atributos de classe:

- `_caminho_banco`: banco em uso.
- `_uri_mode`: se a conexao usa URI SQLite.
- `_conn_keepalive`: mantem banco em memoria vivo durante testes.

Metodos:

- `configurar_banco(cls, caminho)`: `@classmethod`; troca o banco usado. Se for `":memory:"`, usa cache compartilhado para os testes.
- `_conectar()`: `@staticmethod`; abre conexao SQLite e ativa `PRAGMA foreign_keys = ON`.
- `_executar(sql, params=())`: executa INSERT/UPDATE/DELETE sem retorno.
- `_consultar(sql, params=())`: executa SELECT e retorna `fetchall()`.
- `inicializar_banco()`: le `schema.sql` e cria tabelas com `executescript`.
- `cadastrar_usuario(email, senha_hash, tipo_perfil)`: insere usuario e retorna `lastrowid`.
- `buscar_usuario_por_email(email)`: busca usuario pelo email e retorna `Usuario` ou `None`.
- `buscar_usuario_por_id(usuario_id)`: busca usuario pelo id e retorna `Usuario` ou `None`.
- `salvar_transacao(transacao, usuario_id)`: insere receita/despesa ligada ao usuario.
- `carregar_transacoes(usuario_id)`: busca linhas do banco, usa factory `{"receita": Receita, "despesa": Despesa}` e devolve objetos.
- `remover_transacao(transacao_id, usuario_id)`: deleta somente se id e usuario baterem.
- `salvar_meta(meta, usuario_id)`: insere meta e retorna id.
- `carregar_metas(usuario_id)`: recria objetos `Meta` a partir do banco.
- `atualizar_meta(meta, usuario_id)`: atualiza `valor_atual`.
- `remover_meta(meta_id, usuario_id)`: remove meta do usuario.
- `salvar_conta(conta, usuario_id)`: insere conta a pagar/receber.
- `carregar_contas(usuario_id)`: recria objetos `Conta`.
- `marcar_conta_paga(conta_id, usuario_id)`: atualiza `pago = 1`.
- `remover_conta(conta_id, usuario_id)`: remove conta do usuario.

Conceitos fortes:

- `with conn` faz commit/rollback.
- `finally: conn.close()` fecha conexao sempre.
- `lastrowid` pega o id criado pelo `AUTOINCREMENT`.
- `FOREIGN KEY` so funciona no SQLite se ativar `PRAGMA foreign_keys = ON`.
- `AND usuario_id = ?` evita um usuario mexer no dado de outro.

### `services/gerenciador.py`

Responsabilidade: regra de negocio do usuario logado.

`class Gerenciador`

Metodos:

- `__init__(usuario_id)`: guarda o usuario dono das operacoes.
- `adicionar_receita(descricao, valor, categoria, data=None)`: valida, cria `Receita`, salva e retorna id.
- `adicionar_despesa(descricao, valor, categoria, data=None)`: valida, cria `Despesa`, salva e retorna id.
- `remover_transacao(transacao_id)`: delega remocao para `Persistencia`.
- `listar_transacoes(tipo=None, categoria=None)`: carrega transacoes e filtra por tipo/categoria se informado.
- `saldo_atual()`: soma receitas, soma despesas e retorna receitas menos despesas.
- `adicionar_meta(nome, valor_alvo, prazo=None)`: valida, cria `Meta`, salva e retorna id.
- `depositar_em_meta(meta_id, valor)`: procura meta, soma valor sem passar do alvo e atualiza banco.
- `listar_metas()`: devolve metas do usuario.
- `remover_meta(meta_id)`: remove meta do usuario.
- `adicionar_conta(tipo, descricao, valor, vencimento)`: valida, cria `Conta`, salva e retorna id.
- `marcar_conta_paga(conta_id)`: marca conta como paga.
- `listar_contas(tipo=None)`: lista contas e filtra por tipo se necessario.
- `remover_conta(conta_id)`: remove conta do usuario.
- `_validar_transacao(descricao, valor)`: `@staticmethod`; validacao compartilhada por receita e despesa.

### `services/relatorio.py`

Responsabilidade: calculos de relatorios.

`class Relatorio`

Metodos:

- `__init__(transacoes, contas=None)`: guarda transacoes e contas.
- `_do_mes(ano, mes)`: filtra transacoes daquele mes/ano.
- `total_receitas_mes(ano, mes)`: soma receitas do mes.
- `total_despesas_mes(ano, mes)`: soma despesas do mes.
- `saldo_mes(ano, mes)`: receitas menos despesas.
- `_vencimento(conta)`: `@staticmethod`; normaliza vencimento para `date`.
- `fluxo_de_caixa(ano, mes)`: calcula entradas, saidas e saldo projetado de contas com vencimento no mes.
- `gastos_por_categoria(ano, mes)`: soma despesas agrupadas por categoria.
- `comparativo_mensal(ano, mes)`: compara receita/despesa do mes atual com o mes anterior.
- `sugestoes_corte(ano, mes, limite=30.0)`: sugere cortes em categorias que passam do limite percentual das despesas.

## 6. Routes

### `routes/dashboard.py`

Cria:

```python
dashboard_bp = Blueprint("dashboard", __name__)
```

Funcao:

- `dashboard()`: responde a `/` e `/dashboard`; exige login via `session`; cria `Gerenciador`; calcula saldo, ultimas transacoes e despesas do mes; renderiza `dashboard.html`.

Sintaxes importantes:

- Dois decorators na mesma funcao: a mesma funcao atende duas URLs.
- `sorted(..., key=lambda t: t.data, reverse=True)[:5]`: ordena por data desc e pega cinco.
- List comprehension para filtrar despesas do mes.

### `routes/transacoes.py`

Cria:

```python
transacoes_bp = Blueprint("transacoes", __name__, url_prefix="/transacoes")
```

Funcoes:

- `listar()`: GET `/transacoes/`; exige login; lista transacoes e renderiza `transacoes.html`.
- `adicionar()`: POST `/transacoes/nova`; le formulario, valida dados, decide entre receita/despesa e salva.
- `remover(id)`: POST `/transacoes/<id>/remover`; remove transacao pelo id.

Sintaxes importantes:

- `request.form.get(...)`: captura campo do formulario.
- `methods=["POST"]`: rota so aceita envio de formulario.
- `flash(...)`: mensagem de sucesso ou erro.
- `except (ValueError, TypeError)`: trata mais de um erro no mesmo bloco.

### `routes/metas.py`

Cria:

```python
metas_bp = Blueprint("metas", __name__, url_prefix="/metas")
```

Funcoes:

- `listar()`: GET `/metas/`; exige login; carrega metas e renderiza `metas.html`.
- `adicionar()`: POST `/metas/nova`; le nome, valor alvo e prazo; cria meta.
- `depositar(id)`: POST `/metas/<id>/depositar`; adiciona valor a uma meta.
- `remover(id)`: POST `/metas/<id>/remover`; remove meta.

Sintaxes importantes:

- Parametro dinamico `<int:id>`.
- `LookupError` para meta inexistente.
- Conversao `float(...)` para valores vindos de formulario, que chegam como texto.

## 7. Banco de dados `db/schema.sql`

Tabelas:

### `usuario`

- `id INTEGER PRIMARY KEY AUTOINCREMENT`: id automatico.
- `email TEXT NOT NULL UNIQUE`: email obrigatorio e unico.
- `senha_hash TEXT NOT NULL`: senha em hash.
- `tipo_perfil TEXT NOT NULL CHECK (...)`: so aceita `pessoa_fisica` ou `empresa`.

### `transacao`

- `tipo CHECK (tipo IN ('receita', 'despesa'))`: valida tipo no banco.
- `valor REAL CHECK (valor > 0)`: impede valor zero/negativo.
- `usuario_id`: liga transacao ao usuario.
- `FOREIGN KEY ... ON DELETE CASCADE`: se usuario for apagado, suas transacoes vao junto.

### `meta`

Guarda nome, valor alvo, valor atual, prazo e usuario dono.

### `conta`

Guarda contas a pagar/receber, vencimento, pago `0/1` e usuario dono.

Indices:

- `idx_transacao_usuario`
- `idx_meta_usuario`
- `idx_conta_usuario`

Eles aceleram buscas por `usuario_id`.

## 8. Templates

### `templates/base.html`

Template base comum. Define:

- cabecalho HTML;
- link para CSS via `url_for("static", filename="style.css")`;
- menu de navegacao;
- bloco `{% block content %}`;
- rodape.

### `templates/dashboard.html`

Herda `base.html` e mostra:

- saldo atual;
- resumo de receitas/despesas/metas/transacoes;
- tabela com ultimas transacoes;
- mensagem quando nao ha transacoes.

Sintaxes:

- `{% if saldo >= 0 %}...{% else %}...{% endif %}`
- `{{ "%.2f"|format(saldo) }}`
- `{% for t in ultimas_transacoes %}`

Atencao: no model `tipo` e metodo (`t.tipo()`), mas alguns templates usam
`t.tipo` como se fosse atributo.

### `templates/transacoes.html`

Mostra formulario de nova transacao e tabela de transacoes.

Pontos:

- `form method="POST"` envia dados para rota.
- `action="{{ url_for('transacoes.adicionar') }}"` monta URL da funcao.
- `<input type="number" step="0.01">` aceita centavos.
- formulario de remocao usa `url_for("transacoes.remover", id=t.id)`.

### `templates/metas.html`

Mostra formulario de nova meta, lista de metas, barra de progresso e resumo.

Pontos:

- `{% set percentual = (...)|round %}` cria variavel no template.
- `style="width: {{ percentual }}%;"` muda largura da barra de progresso.
- Formularios separados para depositar e remover.

## 9. CSS `static/style.css`

Responsabilidade: visual do sistema.

Blocos principais:

- Variaveis globais em `:root`.
- Reset com `* { margin: 0; padding: 0; box-sizing: border-box; }`.
- Estilo do `body`.
- Navbar com `flex`.
- Cards, containers e formularios.
- Tabelas e linhas coloridas por tipo.
- Dashboard e cards de saldo.
- Metas e barra de progresso.
- Alertas.
- Responsividade com `@media`.

## 10. Testes

### `tests/conftest.py`

Fixtures:

- `banco_limpo()`: cria banco SQLite em memoria, inicializa schema, entrega para o teste e depois reseta.
- `dois_usuarios(banco_limpo)`: cria dois usuarios para testar isolamento.
- `cliente(banco_limpo)`: cria cliente Flask de teste com `app.test_client()`.

Sintaxes:

- `@pytest.fixture`: registra fixture.
- `yield`: divide fixture em setup e teardown.
- `pytest.skip(...)`: pula teste quando dependencia ainda nao existe.
- `try/except ImportError`: import tolerante.

Atencao: `conftest.py` tenta importar `create_app` de `app`, mas o `app.py`
atual nao define `create_app`.

### `tests/test_transacao.py`

Testa `Receita` e `Despesa`.

Funcoes:

- `test_criar_receita_valida`: verifica atributos e tipo da receita.
- `test_receita_valor_zero_levanta_excecao`: valor zero deve falhar.
- `test_receita_valor_negativo_levanta_excecao`: valor negativo deve falhar.
- `test_receita_descricao_vazia_levanta_excecao`: descricao vazia deve falhar.
- `test_receita_data_padrao_e_hoje`: sem data, usa hoje.
- `test_receita_para_dict`: valida dicionario gerado.
- `test_criar_despesa_valida`: verifica atributos e tipo da despesa.
- `test_despesa_valor_negativo_levanta_excecao`: despesa negativa deve falhar.

### `tests/test_auth.py`

Testa hash, verificacao, cadastro e login.

Funcoes:

- `test_hash_nao_e_texto_puro`: senha nao pode aparecer dentro do hash.
- `test_hash_e_string`: hash deve ser string.
- `test_hash_nao_e_vazio`: hash deve ter conteudo.
- `test_dois_hashes_da_mesma_senha_sao_diferentes`: salt aleatorio.
- `test_senha_correta_retorna_true`: senha certa autentica.
- `test_senha_errada_retorna_false`: senha errada falha.
- `test_senha_vazia_nao_passa`: senha vazia falha.
- `test_senha_similar_nao_passa`: variacoes da senha falham.
- `test_ciclo_completo_hash_e_verificacao`: simula cadastro e login.
- `test_hash_mal_formatado_retorna_false`: hash invalido nao autentica.
- `test_cadastrar_usuario_cria_usuario_com_hash`: cadastro salva hash e normaliza email.
- `test_autenticar_com_senha_correta_retorna_usuario`: login correto retorna usuario.
- `test_autenticar_com_senha_errada_retorna_none`: senha errada retorna `None`.
- `test_autenticar_email_inexistente_retorna_none`: email inexistente retorna `None`.
- `test_login_e_alias_de_autenticar`: `login` chama a mesma logica de `autenticar`.
- `test_cadastro_com_email_vazio_falha`: email vazio falha.
- `test_cadastro_com_senha_vazia_falha`: senha vazia falha.

### `tests/test_usuario.py`

Testa `Usuario` e persistencia de usuario.

Funcoes:

- `test_atributos_basicos`: cria usuario e confere atributos.
- `test_perfil_acessivel_via_usuario`: verifica composicao Usuario -> Perfil.
- `test_cria_perfil_a_partir_do_tipo_perfil`: cria perfil usando texto.
- `test_cadastrar_usuario_retorna_id_inteiro`: insert retorna id.
- `test_buscar_por_email_existente`: busca usuario existente por email.
- `test_buscar_por_email_inexistente_retorna_none`: inexistente retorna `None`.
- `test_buscar_por_id_existente`: busca usuario existente por id.
- `test_buscar_por_id_inexistente_retorna_none`: id inexistente retorna `None`.
- `test_email_duplicado_deve_falhar`: `UNIQUE` do banco rejeita duplicado.
- `test_tipo_perfil_persistido_corretamente`: perfil salvo vira objeto certo.

### `tests/test_perfil.py`

Testa perfis.

Funcoes:

- `test_instanciar_perfil_diretamente_deve_falhar`: ABC nao instancia direto.
- `test_pessoa_fisica_e_subclasse_de_perfil`: heranca funciona.
- `test_empresa_e_subclasse_de_perfil`: heranca funciona.
- `test_tipo_str_retorna_pessoa_fisica`: tipo correto.
- `test_categorias_disponiveis_e_lista_nao_vazia`: lista existe.
- `test_categorias_sao_strings`: categorias sao strings.
- `test_tipo_str_retorna_empresa`: tipo correto.
- `test_categorias_disponiveis_e_lista_nao_vazia`: lista existe para empresa.
- `test_categorias_de_empresa_diferem_de_pessoa_fisica`: polimorfismo real.
- `test_factory_com_pessoa_fisica`: factory cria PessoaFisica.
- `test_factory_com_empresa`: factory cria Empresa.
- `test_factory_com_tipo_invalido_deve_falhar`: tipo desconhecido falha.
- `test_factory_retorna_objeto_com_contrato_completo`: objeto tem metodos esperados.

### `tests/test_gerenciador.py`

Fixtures:

- `usuario_id(banco_limpo)`: cria usuario.
- `gerenciador(usuario_id)`: cria `Gerenciador`.
- `gerenciador_populado(gerenciador)`: adiciona transacoes iniciais.

Funcoes:

- `test_adicionar_receita_retorna_id`: receita salva retorna id.
- `test_adicionar_despesa_retorna_id`: despesa salva retorna id.
- `test_valor_invalido_levanta_excecao`: valor invalido falha.
- `test_descricao_vazia_levanta_excecao`: descricao vazia falha.
- `test_saldo_vazio_e_zero`: sem transacoes, saldo zero.
- `test_saldo_com_receitas_e_despesas`: saldo calcula receita menos despesas.
- `test_listar_todas`: lista todas.
- `test_filtrar_por_tipo_despesa`: filtra despesas.
- `test_filtrar_por_tipo_receita`: filtra receitas.
- `test_filtrar_por_categoria`: filtra categoria.
- `test_filtrar_sem_resultados`: filtro sem resultado retorna lista vazia.
- `test_remover_transacao_por_id`: remove por id.
- `test_remover_transacao_de_outro_usuario_nao_funciona`: isolamento por usuario.
- `test_adicionar_meta_retorna_id`: meta salva retorna id.
- `test_adicionar_meta_persiste_prazo`: prazo sobrevive ao banco.
- `test_depositar_em_meta`: deposito atualiza valor.
- `test_depositar_valor_invalido_levanta`: deposito invalido falha.
- `test_depositar_meta_inexistente_levanta_lookup`: meta inexistente falha.
- `test_remover_meta_por_id`: remove meta.
- `test_usuarios_nao_veem_dados_um_do_outro`: isolamento completo entre usuarios.

### `tests/test_conta.py`

Testa `Conta`, `Persistencia` e `Gerenciador`.

Funcoes:

- `test_atributos_basicos`: conta pagar com atributos corretos.
- `test_conta_receber`: tipo receber aceito.
- `test_pago_padrao_e_false`: conta nasce nao paga.
- `test_salvar_e_listar_conta`: persistencia salva e carrega.
- `test_marcar_conta_como_paga`: pago vira `True`.
- `test_remover_conta`: remove do banco.
- `test_isolamento_contas_entre_usuarios`: usuario B nao ve conta de A.
- `test_remover_conta_de_outro_usuario_nao_funciona`: usuario B nao apaga conta de A.
- `test_gerenciador_adicionar_e_listar_conta`: gerenciador salva/lista.
- `test_gerenciador_filtrar_por_tipo`: filtra pagar/receber.
- `test_tipo_invalido_levanta`: tipo invalido falha.
- `test_valor_invalido_levanta`: valor zero falha.
- `test_descricao_vazia_levanta`: descricao vazia falha.
- `test_esta_vencida_quando_passou_e_nao_paga`: vencida retorna `True`.
- `test_nao_vencida_se_paga`: paga nunca e vencida.
- `test_nao_vencida_se_vencimento_futuro`: futuro nao esta vencido.
- `test_para_dict`: serializacao de conta.

### `tests/test_relatorio.py`

Testa calculos de relatorio.

Funcoes:

- `test_total_receitas`: soma receitas do mes.
- `test_total_receitas_vazio`: lista vazia retorna zero.
- `test_total_despesas`: soma despesas.
- `test_total_despesas_vazio`: lista vazia retorna zero.
- `test_saldo`: receita menos despesa.
- `test_saldo_negativo`: saldo pode ser negativo.
- `test_gastos_por_categoria`: agrupa despesas por categoria.
- `test_gastos_nao_inclui_receitas`: receitas nao entram em gastos.
- `test_comparativo`: compara mes atual e anterior.
- `test_comparativo_virada_ano`: janeiro compara com dezembro do ano anterior.
- `test_sugestao_categoria_pesada`: categoria acima do limite aparece.
- `test_sugestao_vazia`: sem gastos, sem sugestoes.
- `test_sugestao_economia_20_porcento`: economia sugerida e 20%.
- `test_fluxo_entradas_do_mes`: contas a receber entram no mes.
- `test_fluxo_saidas_do_mes`: contas a pagar saem no mes.
- `test_fluxo_saldo_projetado`: entradas menos saidas.
- `test_fluxo_filtra_por_mes_de_vencimento`: filtra vencimento por mes.
- `test_fluxo_mes_sem_contas`: mes vazio retorna zeros.
- `test_fluxo_aceita_vencimento_como_date`: aceita `date` alem de string.

### `tests/test_rotas.py`

Smoke tests de rotas Flask.

Funcoes:

- `test_pagina_inicial_responde`: `/` responde 200.
- `test_login_responde`: `/login` responde 200.
- `test_cadastro_responde`: `/cadastro` responde 200.
- `test_logout_responde`: `/logout` responde 200 ou 302.
- `test_dashboard_responde`: `/dashboard` responde 200 ou 302.
- `test_transacoes_responde`: `/transacoes` responde 200 ou 302.
- `test_metas_responde`: `/metas` responde 200 ou 302.
- `test_contas_responde`: `/contas` responde 200 ou 302.
- `test_rota_inexistente_retorna_404`: URL inexistente deve ser 404.
- `test_get_login`: GET de login deve responder.
- `test_get_cadastro`: GET de cadastro deve responder.

## 11. Pontos de atencao para explicar sem mexer no codigo

- `app.py` referencia `routes.auth` e `routes.contas`, mas esses arquivos nao estao no repositorio atual.
- `routes.dashboard`, `routes.transacoes` e `routes.metas` redirecionam para `auth.login`, mas o blueprint `auth` tambem nao esta presente.
- `tests/conftest.py` espera `create_app`, mas `app.py` cria `app` direto e nao define essa factory.
- O README fala de uma versao CLI com `main.py`, mas o codigo atual esta em formato web Flask.
- Alguns templates usam `t.tipo` como atributo; no model, `tipo` e metodo (`t.tipo()`).
- Arquivos exibidos no terminal aparecem com acentos quebrados por configuracao de encoding, mas a intencao dos comentarios e clara.

## 12. Resumo oral para prova

Uma boa explicacao curta:

"O sistema e uma aplicacao Flask de financas pessoais. As rotas recebem as
requisicoes HTTP, verificam se o usuario esta logado pela sessao e chamam o
Gerenciador. O Gerenciador concentra as regras de negocio de um usuario
especifico e delega a gravacao para Persistencia. A Persistencia usa SQLite,
com tabelas ligadas por `usuario_id`, chaves estrangeiras e checks de validacao.
Os models representam as entidades do dominio: transacoes, metas, contas,
usuarios e perfis. O sistema usa heranca em Receita/Despesa, polimorfismo em
`tipo()`, classe abstrata em Perfil, decorators do Flask para rotas, decorators
do Python como `@property`, `@classmethod` e `@staticmethod`, alem de testes
pytest para validar regras, isolamento entre usuarios e comportamento das rotas."

