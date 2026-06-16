"""
Blueprint de metas financeiras.
Permite listar, adicionar, depositar e remover metas.

Rotas:
    GET /metas                 - Lista todas as metas
    POST /metas/nova           - Adiciona nova meta
    POST /metas/<id>/depositar - Deposita valor em uma meta
    POST /metas/<id>/remover   - Remove uma meta pelo ID

"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.gerenciador import Gerenciador

# Cria o blueprint com prefixo /metas
metas_bp = Blueprint('metas', __name__, url_prefix='/metas')


@metas_bp.route('/')
def listar():
    """
    Lista todas as metas do usuário logado.
    Se não estiver logado, redireciona para o login.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Cria o gerenciador para o usuário logado
    g = Gerenciador(session['usuario_id'])

    # Obtém as metas reais do banco
    metas = g.listar_metas()

    return render_template('metas.html', metas=metas)


@metas_bp.route('/nova', methods=['POST'])
def adicionar():
    """
    Adiciona uma nova meta.
    Recebe os dados do formulário e cria a meta.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Pega os dados do formulário
    nome = request.form.get('nome')
    valor_alvo = request.form.get('valor_alvo')
    prazo = request.form.get('prazo')

    # Se prazo for vazio, vira None
    if not prazo:
        prazo = None

    # Validações básicas
    if not nome:
        flash('Por favor, informe o nome da meta!', 'error')
        return redirect(url_for('metas.listar'))

    if not valor_alvo:
        flash('Por favor, informe o valor alvo da meta!', 'error')
        return redirect(url_for('metas.listar'))

    try:
        valor_float = float(valor_alvo)
        if valor_float <= 0:
            flash('O valor alvo deve ser maior que zero!', 'error')
            return redirect(url_for('metas.listar'))
    except ValueError:
        flash('Por favor, informe um valor numérico válido!', 'error')
        return redirect(url_for('metas.listar'))

    # Cria o gerenciador e adiciona a meta
    g = Gerenciador(session['usuario_id'])

    try:
        g.adicionar_meta(nome, valor_float, prazo)
        flash(f'Meta "{nome}" criada com sucesso!', 'success')
    except ValueError as e:
        flash(f'Erro ao criar meta: {str(e)}', 'error')
    except Exception as e:
        flash(f'Erro inesperado: {str(e)}', 'error')

    return redirect(url_for('metas.listar'))


@metas_bp.route('/<int:id>/depositar', methods=['POST'])
def depositar(id):
    """
    Deposita um valor em uma meta existente.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Pega o valor do depósito
    valor = request.form.get('valor')

    if not valor:
        flash('Por favor, informe um valor para depositar!', 'error')
        return redirect(url_for('metas.listar'))

    try:
        valor_float = float(valor)
        if valor_float <= 0:
            flash('O valor do depósito deve ser maior que zero!', 'error')
            return redirect(url_for('metas.listar'))
    except ValueError:
        flash('Por favor, informe um valor numérico válido!', 'error')
        return redirect(url_for('metas.listar'))

    # Cria o gerenciador e deposita na meta
    g = Gerenciador(session['usuario_id'])

    try:
        g.depositar_em_meta(id, valor_float)
        flash(f'Depósito de R$ {valor_float:.2f} realizado com sucesso!', 'success')
    except LookupError as e:
        flash(f'Meta não encontrada: {str(e)}', 'error')
    except ValueError as e:
        flash(f'Erro no depósito: {str(e)}', 'error')
    except Exception as e:
        flash(f'Erro inesperado: {str(e)}', 'error')

    return redirect(url_for('metas.listar'))


@metas_bp.route('/<int:id>/remover', methods=['POST'])
def remover(id):
    """
    Remove uma meta pelo ID.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Cria o gerenciador e remove a meta
    g = Gerenciador(session['usuario_id'])

    try:
        g.remover_meta(id)
        flash('Meta removida com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover meta: {str(e)}', 'error')

    return redirect(url_for('metas.listar'))