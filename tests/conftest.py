"""
conftest.py — Fixtures compartilhadas por todos os arquivos de teste.

O pytest carrega este arquivo automaticamente antes de qualquer teste.
Tudo que está aqui fica disponível para qualquer test_*.py sem importar.

O que é uma FIXTURE?
    É uma função decorada com @pytest.fixture que prepara um cenário limpo
    e isolado para cada teste. Em vez de repetir "criar app, criar banco,
    criar usuário" em cada função de teste, você declara a fixture uma vez
    e o pytest a injeta onde precisar, pelo nome do parâmetro.

    Exemplo: def test_algo(cliente, banco_limpo): ...
    O pytest vê "cliente" e "banco_limpo", busca as fixtures com esses nomes
    e as executa antes do teste. Após o teste, executa o código após o yield
    (a limpeza).

NOTA DE INTEGRAÇÃO (Frente 6)
    Algumas fixtures dependem de frentes que ainda NÃO entraram na main:
    services.auth (Frente 1), app.create_app (Frente 4) e o suporte a banco
    :memory: na Persistencia (Frente 0). Por isso os imports abaixo são
    tolerantes a falha e as fixtures fazem pytest.skip() quando a dependência
    ainda não existe — a suíte continua VERDE hoje e os testes se ativam
    sozinhos quando cada frente for mergeada.
"""

import pytest

from services.persistencia import Persistencia

# Dependências de outras frentes — podem ainda não existir na main.
# Import tolerante: se faltar, a fixture correspondente faz skip em vez de
# quebrar a coleção de TODA a suíte.
try:
    from services.auth import gerar_hash
except ImportError:
    gerar_hash = None

try:
    from app import create_app
except ImportError:
    create_app = None


# ---------------------------------------------------------------------------
# Fixture: banco_limpo
# ---------------------------------------------------------------------------
@pytest.fixture
def banco_limpo():
    """
    Configura um banco SQLite em memória (:memory:) para cada teste.

    Por que :memory:?
        - O banco vive só durante o teste e some quando a conexão fecha.
        - Não suja o banco real (financas.db) nem o repositório Git.
        - É instantâneo — sem I/O de disco.

    O yield divide a fixture em duas partes:
        - Tudo ANTES do yield: setup (preparação).
        - Tudo DEPOIS do yield: teardown (limpeza).
    O pytest garante que o teardown roda mesmo se o teste falhar.
    """
    # configurar_banco(":memory:") é o gancho de teste da Persistencia.
    # Enquanto a Frente 0 não expõe esse método na main, pulamos os testes
    # que dependem de banco — sem quebrar a suíte.
    if not hasattr(Persistencia, "configurar_banco"):
        pytest.skip("Persistencia.configurar_banco ainda não disponível (integração da Frente 0)")

    # Aponta o banco para a memória RAM — sem arquivo, sem sujeira
    Persistencia.configurar_banco(":memory:")
    Persistencia.inicializar_banco()

    yield  # aqui o teste roda

    # Teardown: volta para :memory: (já está limpo, mas é boa prática explicitar)
    Persistencia.configurar_banco(":memory:")


# ---------------------------------------------------------------------------
# Fixture: dois_usuarios
# ---------------------------------------------------------------------------
@pytest.fixture
def dois_usuarios(banco_limpo):
    """
    Cria dois usuários distintos no banco de teste.

    Usada pelos testes de ISOLAMENTO — o teste mais importante da suíte.
    Recebe banco_limpo como parâmetro: o pytest resolve dependências entre
    fixtures automaticamente (composição de fixtures).

    Retorna um dict com os ids para os testes usarem.
    """
    if gerar_hash is None:
        pytest.skip("services.auth ainda não disponível (Frente 1)")

    id_a = Persistencia.cadastrar_usuario(
        email="alice@teste.com",
        senha_hash=gerar_hash("senha_alice"),
        tipo_perfil="pessoa_fisica"
    )
    id_b = Persistencia.cadastrar_usuario(
        email="bob@teste.com",
        senha_hash=gerar_hash("senha_bob"),
        tipo_perfil="empresa"
    )
    return {"id_a": id_a, "id_b": id_b}


# ---------------------------------------------------------------------------
# Fixture: cliente
# ---------------------------------------------------------------------------
@pytest.fixture
def cliente(banco_limpo):
    """
    Cria um cliente de teste do Flask (sem servidor real).

    Flask fornece app.test_client() que simula requisições HTTP sem abrir
    uma porta de rede — ideal para smoke tests de rotas.

    TESTING=True desativa o tratamento de erros do Flask para que exceções
    apareçam nos testes em vez de virar páginas 500 silenciosas.
    """
    if create_app is None:
        pytest.skip("app.create_app ainda não disponível (Frente 4)")

    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret"})
    with app.test_client() as c:
        yield c
