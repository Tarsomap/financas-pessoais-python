"""
Blueprint de autenticacao (Frente 1 -> camada web).

Esta camada NAO reimplementa seguranca: a logica de hash, verificacao e
cadastro ja existe em services/auth.py (Frente 1). Aqui so cuidamos do que
e responsabilidade da view: receber o formulario, conversar com o service,
guardar/limpar a sessao e redirecionar. E a "ligacao" que faltava entre a
logica do Jigui (Frente 1) e o frontend (Frente 4).

Rotas:
    GET/POST /auth/login     - tela de login e processamento
    GET/POST /auth/cadastro  - tela de cadastro e processamento
    GET      /auth/logout    - encerra a sessao
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services import auth

# url_prefix='/auth' tambem e aplicado no app.py ao registrar; manter aqui
# deixa o blueprint autossuficiente e alinhado ao padrao de transacoes/metas.
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Exibe o formulario de login (GET) e autentica o usuario (POST)."""
    # Quem ja esta logado nao precisa ver o login: manda direto pro dashboard.
    if 'usuario_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '')
        senha = request.form.get('senha', '')

        # Toda a verificacao de senha (hash + comparacao) fica no service.
        usuario = auth.login(email, senha)
        if usuario is None:
            # Mensagem generica de proposito: nao revela se o e-mail existe.
            flash('E-mail ou senha invalidos.', 'error')
            return redirect(url_for('auth.login'))

        # Sucesso: a sessao guarda quem esta logado. usuario_id e o que as
        # outras rotas precisam (elas criam Gerenciador(session['usuario_id'])).
        # tipo_perfil fica guardado so para a view decidir o que mostrar
        # (ex.: o menu de Contas aparece apenas para empresa).
        session['usuario_id'] = usuario.id
        session['email'] = usuario.email
        session['tipo_perfil'] = usuario.tipo_perfil
        flash(f'Bem-vindo(a), {usuario.email}!', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('login.html')


@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Exibe o formulario de cadastro (GET) e cria o usuario (POST)."""
    if 'usuario_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '')
        senha = request.form.get('senha', '')
        # Default 'pessoa_fisica' espelha o default do proprio service.
        tipo_perfil = request.form.get('tipo_perfil', 'pessoa_fisica')

        try:
            auth.cadastrar_usuario(email, senha, tipo_perfil)
        except ValueError as e:
            # E-mail/senha vazios: o service valida e lanca ValueError.
            flash(str(e), 'error')
            return redirect(url_for('auth.cadastro'))
        except Exception:
            # E-mail repetido cai aqui (coluna email e UNIQUE no schema).
            # Mensagem amigavel, sem vazar o erro tecnico do banco.
            flash('Nao foi possivel cadastrar: e-mail ja esta em uso.', 'error')
            return redirect(url_for('auth.cadastro'))

        flash('Cadastro realizado! Faca login para entrar.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('cadastro.html')


@auth_bp.route('/logout')
def logout():
    """Encerra a sessao do usuario logado."""
    # clear() remove tudo da sessao — o usuario deixa de estar autenticado.
    session.clear()
    flash('Voce saiu da sua conta.', 'success')
    return redirect(url_for('auth.login'))
