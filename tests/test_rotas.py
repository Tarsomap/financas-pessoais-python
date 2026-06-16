"""
test_rotas.py — Smoke tests das rotas Flask (Frente 4).

O que é um smoke test?
    É o teste mais básico possível: "a máquina liga e não pega fogo?"
    Não verifica lógica de negócio — só garante que cada rota responde
    sem explodir (status HTTP 200 ou redirecionamento 302).

    "Smoke test" vem de hardware: ao ligar um circuito novo pela primeira
    vez, se não sair fumaça, passou no smoke test.

Conceitos cobertos:
    - Rotas públicas (login, cadastro) respondem com 200
    - O cliente de teste Flask simula requisições HTTP sem servidor real
    - Verificação de status HTTP básico
"""

import pytest

# Depende da Frente 4 (app.py com create_app). Enquanto não estiver na main,
# este arquivo é PULADO inteiro — não quebra a suíte.
pytest.importorskip("app")


class TestRotasPublicas:
    """Rotas que devem ser acessíveis sem estar logado."""

    def test_pagina_inicial_responde(self, cliente):
        """
        cliente é a fixture do conftest que cria um app.test_client().
        .get() simula uma requisição GET — como o navegador faria.
        response.status_code deve ser 200 (OK).
        """
        resposta = cliente.get("/")
        assert resposta.status_code == 200

    def test_login_responde(self, cliente):
        resposta = cliente.get("/login")
        assert resposta.status_code == 200

    def test_cadastro_responde(self, cliente):
        resposta = cliente.get("/cadastro")
        assert resposta.status_code == 200

    def test_logout_responde(self, cliente):
        """Logout deve funcionar mesmo sem estar logado."""
        resposta = cliente.get("/logout")
        # Aceita tanto 200 (ok) quanto 302 (redireciona para login)
        assert resposta.status_code in (200, 302)


class TestRotasInternas:
    """
    Rotas internas — idealmente exigem login.
    Smoke test: verificam que a rota existe e responde sem erro 500.
    Status 302 (redirect para /login) é comportamento correto e esperado.
    """

    def test_dashboard_responde(self, cliente):
        resposta = cliente.get("/dashboard")
        assert resposta.status_code in (200, 302)

    def test_transacoes_responde(self, cliente):
        resposta = cliente.get("/transacoes")
        assert resposta.status_code in (200, 302)

    def test_metas_responde(self, cliente):
        resposta = cliente.get("/metas")
        assert resposta.status_code in (200, 302)

    def test_contas_responde(self, cliente):
        resposta = cliente.get("/contas")
        assert resposta.status_code in (200, 302)

    def test_rota_inexistente_retorna_404(self, cliente):
        """
        Uma URL que não existe deve retornar 404, não 500.
        500 indicaria um bug no servidor; 404 é o comportamento correto.
        """
        resposta = cliente.get("/pagina_que_nao_existe")
        assert resposta.status_code == 404


class TestMetodosHTTP:
    """Verifica que os métodos HTTP corretos são aceitos."""

    def test_get_login(self, cliente):
        """GET /login mostra o formulário."""
        resposta = cliente.get("/login")
        assert resposta.status_code in (200, 302)

    def test_get_cadastro(self, cliente):
        """GET /cadastro mostra o formulário."""
        resposta = cliente.get("/cadastro")
        assert resposta.status_code in (200, 302)
