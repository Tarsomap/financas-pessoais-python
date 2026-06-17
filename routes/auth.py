# =============================================================================
# routes/auth.py
# -----------------------------------------------------------------------------
# Blueprint de autenticação (Frente 1 → camada web).
#
# Esta camada NÃO reimplementa segurança: a lógica de hash, verificação e
# cadastro já existe em services/auth.py (Frente 1). Aqui só cuidamos do que
# é responsabilidade da view: receber o formulário, conversar com o service,
# guardar/limpar a sessão e redirecionar. É a "ligação" que faltava entre a
# lógica do Jigui (Frente 1) e o frontend (Frente 4).
#
# CONCEITOS APLICADOS:
#   - Separação view/service: a rota NÃO faz hash de senha nem acessa o banco.
#     Ela chama auth.login() ou auth.cadastrar_usuario() e reage ao resultado.
#     Se a lógica de autenticação mudar, só services/auth.py é alterado.
#   - Sessão do Flask (session): dicionário criptografado guardado no cookie
#     do navegador. Após login, session['usuario_id'] identifica quem está
#     logado — as outras rotas consultam esse campo para criar o Gerenciador.
#   - Mensagens genéricas de erro: "E-mail ou senha inválidos" sem revelar
#     se o email existe ou se a senha está errada — prática de segurança
#     para não dar pistas a um atacante sobre quais emails estão cadastrados.
#   - Padrão PRG: após POST de login/cadastro, sempre redireciona (redirect)
#     em vez de renderizar diretamente, evitando reenvio do formulário com F5.
#
# Rotas:
#     GET/POST /login     - tela de login e processamento
#     GET/POST /cadastro  - tela de cadastro e processamento
#     GET      /logout    - encerra a sessão
#
# RESPONSÁVEL: João Guilherme Costa ("Jigui") - Frente 1 (auth service)
#              + Lívia e Alice - Frente 4 (camada web/templates)
# =============================================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services import auth

# Sem url_prefix aqui — o app.py registra sem prefixo para que as rotas
# fiquem em /login, /cadastro, /logout (mais natural para o usuário).
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Exibe o formulário de login (GET) e autentica o usuário (POST).

    GET: renderiza templates/login.html com o formulário vazio.
    POST: recebe email/senha, chama o service e redireciona:
        - Sucesso → guarda na sessão e vai para o dashboard.
        - Falha → flash de erro e volta para o login.
    """
    # Quem já está logado não precisa ver o login: manda direto pro dashboard.
    if 'usuario_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '')
        senha = request.form.get('senha', '')

        # Toda a verificação de senha (hash + comparação) fica no service.
        usuario = auth.login(email, senha)
        if usuario is None:
            # Mensagem genérica de propósito: não revela se o e-mail existe.
            flash('E-mail ou senha invalidos.', 'error')
            return redirect(url_for('auth.login'))

        # Sucesso: a sessão guarda quem está logado.
        # usuario_id é o que as outras rotas precisam (criam Gerenciador(session['usuario_id'])).
        # tipo_perfil fica guardado só para a view decidir o que mostrar
        # (ex.: o menu de Contas aparece apenas para empresa).
        session['usuario_id'] = usuario.id
        session['email'] = usuario.email
        session['tipo_perfil'] = usuario.tipo_perfil
        flash(f'Bem-vindo(a), {usuario.email}!', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('login.html')


@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """
    Exibe o formulário de cadastro (GET) e cria o usuário (POST).

    Delega para auth.cadastrar_usuario(), que cuida do hash e do INSERT.
    Trata ValueError (email/senha vazios) e exceções genéricas (email
    duplicado no banco — coluna email é UNIQUE no schema).
    """
    # Quem já está logado não precisa se cadastrar de novo
    if 'usuario_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '')
        senha = request.form.get('senha', '')
        # Default 'pessoa_fisica' espelha o default do próprio service.
        tipo_perfil = request.form.get('tipo_perfil', 'pessoa_fisica')

        try:
            auth.cadastrar_usuario(email, senha, tipo_perfil)
        except ValueError as e:
            # E-mail/senha vazios: o service valida e lança ValueError.
            flash(str(e), 'error')
            return redirect(url_for('auth.cadastro'))
        except Exception:
            # E-mail repetido cai aqui (coluna email é UNIQUE no schema).
            # Mensagem amigável, sem vazar o erro técnico do banco.
            flash('Nao foi possivel cadastrar: e-mail ja esta em uso.', 'error')
            return redirect(url_for('auth.cadastro'))

        flash('Cadastro realizado! Faca login para entrar.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('cadastro.html')


@auth_bp.route('/logout')
def logout():
    """
    Encerra a sessão do usuário logado.

    session.clear() remove TUDO da sessão — o usuário deixa de estar
    autenticado e qualquer rota protegida o mandará de volta para /login.
    """
    session.clear()
    flash('Voce saiu da sua conta.', 'success')
    return redirect(url_for('auth.login'))
