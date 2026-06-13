"""
test_auth.py — Testa o serviço de autenticação (Frente 1).

Conceitos cobertos:
    - Hash não é texto puro (a senha não aparece em claro)
    - Senha correta passa na verificação
    - Senha errada BARRA o login — o teste de segurança mais direto
    - Dois hashes da mesma senha são diferentes (salt aleatório)
"""

import pytest

# Depende da Frente 1 (services/auth.py). Enquanto não estiver na main,
# este arquivo é PULADO inteiro — não quebra a suíte.
pytest.importorskip("services.auth")

from services.auth import gerar_hash, verificar_senha


class TestHash:

    def test_hash_nao_e_texto_puro(self):
        """
        REGRA DE SEGURANÇA: a senha nunca pode aparecer em texto puro
        no banco. O hash deve ser completamente diferente da senha original.

        Por que hash e não criptografia?
            Hash é via única — não tem "desembaralhar". No login,
            embaralhamos a senha digitada e comparamos os dois hashes.
            Mesmo que o banco vaze, as senhas reais não aparecem.
        """
        senha = "minha_senha_secreta"
        h = gerar_hash(senha)

        # O hash NÃO deve conter a senha em texto puro
        assert senha not in h

    def test_hash_e_string(self):
        """gerar_hash deve devolver uma string (para salvar no banco como TEXT)."""
        h = gerar_hash("qualquer")
        assert isinstance(h, str)

    def test_hash_nao_e_vazio(self):
        h = gerar_hash("abc")
        assert len(h) > 0

    def test_dois_hashes_da_mesma_senha_sao_diferentes(self):
        """
        Por que isso importa?
            O werkzeug usa um SALT aleatório em cada hash. Se dois usuários
            tiverem a mesma senha, os hashes são diferentes — impossibilitando
            ataques de "rainbow table" que comparam hashes conhecidos.
        """
        senha = "senha_igual"
        hash1 = gerar_hash(senha)
        hash2 = gerar_hash(senha)
        assert hash1 != hash2  # salts diferentes → hashes diferentes


class TestVerificacaoSenha:

    def test_senha_correta_retorna_true(self):
        """O fluxo normal do login deve funcionar."""
        senha = "senha_correta_123"
        h = gerar_hash(senha)
        assert verificar_senha(senha, h) is True

    def test_senha_errada_retorna_false(self):
        """
        TESTE DE SEGURANÇA CRÍTICO: uma senha errada deve SEMPRE retornar False.
        Se retornar True, qualquer pessoa entraria em qualquer conta.
        """
        h = gerar_hash("senha_real")
        assert verificar_senha("senha_errada", h) is False

    def test_senha_vazia_nao_passa(self):
        """Senha vazia não deve autenticar contra um hash de senha real."""
        h = gerar_hash("senha_com_conteudo")
        assert verificar_senha("", h) is False

    def test_senha_similar_nao_passa(self):
        """
        Variações da senha correta (maiúscula, espaço extra) devem falhar.
        Garante que a verificação é exata, não aproximada.
        """
        h = gerar_hash("SenhaExata")
        assert verificar_senha("senhaexata", h) is False   # minúscula
        assert verificar_senha("SenhaExata ", h) is False  # espaço extra
        assert verificar_senha(" SenhaExata", h) is False  # espaço antes

    def test_ciclo_completo_hash_e_verificacao(self):
        """
        Testa o ciclo que acontece no sistema real:
            1. Usuário cadastra com senha X → banco recebe gerar_hash(X)
            2. Usuário faz login com senha X → verificar_senha(X, hash) == True
            3. Atacante tenta senha Y → verificar_senha(Y, hash) == False
        """
        senha_cadastro = "senha_do_usuario"
        hash_salvo = gerar_hash(senha_cadastro)

        # Login legítimo
        assert verificar_senha(senha_cadastro, hash_salvo) is True
        # Tentativa de ataque
        assert verificar_senha("tentativa_hacker", hash_salvo) is False
