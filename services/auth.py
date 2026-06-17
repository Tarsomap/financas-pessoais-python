# =============================================================================
# services/auth.py
# -----------------------------------------------------------------------------
# Camada de autenticação: cadastro de usuários, geração de hash de senha e
# verificação de credenciais. Este módulo é a "ponte de segurança" entre o
# formulário de login/cadastro (view) e o banco de dados (Persistencia).
#
# CONCEITOS APLICADOS:
#   - Hashing de senha (PBKDF2-SHA256): senhas NUNCA são salvas em texto puro.
#     São transformadas num hash irreversível usando PBKDF2 com 260.000
#     iterações e um salt aleatório de 16 bytes. Mesmo que o banco vaze,
#     o atacante não consegue recuperar a senha original.
#   - Salt aleatório: cada senha recebe um salt único (secrets.token_bytes).
#     Isso impede ataques de rainbow table, onde o atacante pré-computa
#     hashes de senhas comuns. Com salt, "123456" gera hashes diferentes
#     para cada usuário.
#   - Comparação segura (hmac.compare_digest): compara o hash digitado com
#     o salvo em tempo constante. Uma comparação normal (==) retorna False
#     assim que encontra o primeiro byte diferente — um atacante poderia
#     medir o tempo de resposta para adivinhar o hash byte a byte (timing
#     attack). compare_digest sempre leva o mesmo tempo.
#   - Separação de responsabilidades: este módulo não sabe nada de Flask,
#     sessão ou formulários. Ele recebe strings (email, senha) e devolve
#     objetos (Usuario ou None). A view (routes/auth.py) cuida da sessão
#     e dos redirecionamentos.
#   - Formato do hash: "pbkdf2_sha256$260000$salt_hex$hash_hex". O algoritmo
#     e as iterações ficam embutidos no próprio hash — se no futuro mudarmos
#     para argon2, hashes antigos continuam validáveis.
#
# RESPONSÁVEL: João Guilherme Costa ("Jigui") - Frente 1
# =============================================================================

from __future__ import annotations

import hashlib
import hmac
import secrets

from models.usuario import Usuario
from services.persistencia import Persistencia


# -------------------------------------------------------------------------
# Constantes de configuração do hashing
# -------------------------------------------------------------------------

# Nome do algoritmo embutido no hash — permite migrar sem quebrar senhas antigas.
ALGORITMO = "pbkdf2_sha256"

# 260.000 iterações: valor recomendado pelo OWASP (2023) para PBKDF2-SHA256.
# Quanto mais iterações, mais lento o cálculo — dificulta ataques de força bruta.
ITERACOES = 260_000

# 16 bytes de salt = 128 bits de aleatoriedade; suficiente para garantir
# unicidade prática (colisão improvável mesmo com bilhões de usuários).
TAMANHO_SALT = 16


# -------------------------------------------------------------------------
# Funções de hashing
# -------------------------------------------------------------------------

def gerar_hash(senha: str) -> str:
    """
    Gera um hash seguro para salvar a senha no banco.

    O formato salvo é "algoritmo$iteracoes$salt_hex$hash_hex", tudo numa
    única string. Ao verificar, basta fazer split('$') para recuperar
    cada parte.

    Parâmetros:
        senha (str) : senha em texto puro digitada pelo usuário

    Retorna:
        String no formato "pbkdf2_sha256$260000$<salt_hex>$<hash_hex>".

    Lança:
        ValueError se a senha for vazia.
    """
    if not senha:
        raise ValueError("Senha nao pode ser vazia.")

    # secrets.token_bytes gera bytes criptograficamente seguros — mais seguro
    # que random.randbytes(), que usa PRNG não-criptográfico.
    salt = secrets.token_bytes(TAMANHO_SALT)

    # pbkdf2_hmac: Password-Based Key Derivation Function 2.
    # Aplica SHA-256 repetidamente (ITERACOES vezes) sobre a senha + salt,
    # tornando o cálculo deliberadamente lento para dificultar força bruta.
    senha_hash = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        ITERACOES,
    )

    # Junta tudo numa string auto-descritiva com $ como separador.
    # .hex() converte bytes em string hexadecimal legível.
    return f"{ALGORITMO}${ITERACOES}${salt.hex()}${senha_hash.hex()}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """
    Confere se a senha digitada corresponde ao hash salvo no banco.

    Recalcula o hash com o mesmo salt e iterações que foram usados na
    criação, depois compara os resultados com hmac.compare_digest
    (tempo constante, imune a timing attacks).

    Parâmetros:
        senha      (str) : senha em texto puro digitada agora
        senha_hash (str) : hash salvo no banco (formato "alg$iter$salt$hash")

    Retorna:
        True se a senha está correta, False caso contrário.
    """
    if not senha or not senha_hash:
        return False

    try:
        # Decompõe o hash salvo nas suas 4 partes: algoritmo, iterações, salt, hash.
        algoritmo, iteracoes_txt, salt_hex, hash_hex = senha_hash.split("$", 3)

        # Se o algoritmo não bate, o hash foi gerado com outro método — rejeita.
        if algoritmo != ALGORITMO:
            return False

        iteracoes = int(iteracoes_txt)
        salt = bytes.fromhex(salt_hex)         # reconstrói o salt original
        hash_salvo = bytes.fromhex(hash_hex)   # reconstrói o hash salvo
    except (ValueError, TypeError):
        # Hash malformado (formato diferente ou caracteres inválidos) → rejeita.
        return False

    # Recalcula o hash com a senha digitada + salt original + mesmas iterações.
    hash_digitado = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        iteracoes,
    )

    # compare_digest: comparação em tempo constante.
    # Um == normal para quando encontra o primeiro byte diferente, vazando
    # informação sobre quais bytes estão certos (timing attack). Esta função
    # sempre compara TODOS os bytes, levando o mesmo tempo independente de
    # quantos bytes coincidem.
    return hmac.compare_digest(hash_digitado, hash_salvo)


# -------------------------------------------------------------------------
# Funções de cadastro e login
# -------------------------------------------------------------------------

def cadastrar_usuario(
    email: str,
    senha: str,
    tipo_perfil: str = "pessoa_fisica",
) -> Usuario:
    """
    Cadastra um usuário novo e devolve o objeto carregado do banco.

    Fluxo: normaliza email → gera hash da senha → insere no banco via
    Persistencia → carrega o objeto recém-criado (com id gerado pelo banco).

    Parâmetros:
        email       (str) : endereço de e-mail (será normalizado)
        senha       (str) : senha em texto puro (será hasheada)
        tipo_perfil (str) : 'pessoa_fisica' ou 'empresa' (padrão PF)

    Retorna:
        Objeto Usuario com id, email, hash e perfil.

    Lança:
        ValueError: se email ou senha forem vazios.
        RuntimeError: se o banco não encontrar o usuário recém-cadastrado
                      (erro grave — indica bug no fluxo).
    """
    email_normalizado = _normalizar_email(email)
    senha_hash = gerar_hash(senha)
    usuario_id = Persistencia.cadastrar_usuario(
        email=email_normalizado,
        senha_hash=senha_hash,
        tipo_perfil=tipo_perfil,
    )
    # Recarrega do banco para obter o objeto completo (com id e perfil).
    # Se retornar None, algo deu muito errado — o INSERT foi feito mas o
    # SELECT não encontrou. RuntimeError sinaliza um bug interno, não erro do usuário.
    usuario = Persistencia.buscar_usuario_por_id(usuario_id)
    if usuario is None:
        raise RuntimeError("Usuario cadastrado nao foi encontrado no banco.")
    return usuario


def autenticar(email: str, senha: str) -> Usuario | None:
    """
    Valida login por email e senha.

    Busca o usuário pelo email normalizado, depois compara o hash da senha
    digitada com o hash salvo. Retorna None em QUALQUER falha (email
    inexistente, senha errada, email inválido) — mensagem genérica de
    propósito, para não revelar se o email existe no sistema.

    Parâmetros:
        email (str) : endereço digitado no formulário
        senha (str) : senha digitada no formulário

    Retorna:
        Objeto Usuario se as credenciais estiverem corretas, None se não.
    """
    try:
        email_normalizado = _normalizar_email(email)
    except ValueError:
        # Email vazio ou inválido: retorna None sem vazar o motivo.
        return None

    usuario = Persistencia.buscar_usuario_por_email(email_normalizado)
    if usuario is None:
        # Email não encontrado no banco.
        return None

    if verificar_senha(senha, usuario.senha_hash):
        return usuario
    return None


def login(email: str, senha: str) -> Usuario | None:
    """
    Alias para autenticar() — deixa as rotas mais legíveis.

    Permite escrever auth.login(email, senha) nas views, que é mais
    natural do que auth.autenticar(email, senha).
    """
    return autenticar(email, senha)


# -------------------------------------------------------------------------
# Helpers privados
# -------------------------------------------------------------------------

def _normalizar_email(email: str) -> str:
    """
    Remove espaços e converte para minúsculas.

    Centraliza a normalização num único ponto — tanto cadastrar_usuario
    quanto autenticar passam por aqui, garantindo que "Fulano@Email.COM"
    e "fulano@email.com" sempre correspondam ao mesmo registro.

    Lança:
        ValueError se o email for vazio ou apenas espaços.
    """
    if not email or not email.strip():
        raise ValueError("Email nao pode ser vazio.")
    return email.strip().lower()
