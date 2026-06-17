"""
Blueprint de transações (receitas e despesas).
Permite listar, adicionar e remover transações.

Rotas:
    GET /transacoes           - Lista todas as transações
    POST /transacoes/nova     - Adiciona nova transação (receita ou despesa)
    POST /transacoes/<id>/remover - Remove uma transação pelo ID

"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.gerenciador import Gerenciador

transacoes_bp = Blueprint('transacoes', __name__)


@transacoes_bp.route('/')
def listar():
    """
    Lista todas as transações do usuário logado.
    Se não estiver logado, redireciona para o login.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Cria o gerenciador para o usuário logado
    g = Gerenciador(session['usuario_id'])

    # Obtém as transações reais do banco
    transacoes = g.listar_transacoes()

    return render_template('transacoes.html', transacoes=transacoes)


@transacoes_bp.route('/nova', methods=['POST'])
def adicionar():
    """
    Adiciona uma nova transação (receita ou despesa).
    Recebe os dados do formulário e cria a transação.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Pega os dados do formulário
    tipo = request.form.get('tipo')
    descricao = request.form.get('descricao')
    valor = request.form.get('valor')
    categoria = request.form.get('categoria')
    data = request.form.get('data')

    # Se data não foi fornecida, usa None (o Gerenciador usará data atual)
    if not data:
        data = None

    # Validações básicas
    if not descricao:
        flash('Por favor, informe uma descrição!', 'error')
        return redirect(url_for('transacoes.listar'))

    if not categoria:
        flash('Por favor, informe uma categoria!', 'error')
        return redirect(url_for('transacoes.listar'))

    try:
        valor_float = float(valor)
        if valor_float <= 0:
            flash('O valor deve ser maior que zero!', 'error')
            return redirect(url_for('transacoes.listar'))
    except (ValueError, TypeError):
        flash('Por favor, informe um valor numérico válido!', 'error')
        return redirect(url_for('transacoes.listar'))

    # Cria o gerenciador e adiciona a transação
    g = Gerenciador(session['usuario_id'])

    try:
        if tipo == 'receita':
            g.adicionar_receita(descricao, valor_float, categoria, data)
            flash(f'Receita de R$ {valor_float:.2f} adicionada com sucesso!', 'success')
        else:
            g.adicionar_despesa(descricao, valor_float, categoria, data)
            flash(f'Despesa de R$ {valor_float:.2f} adicionada com sucesso!', 'success')
    except ValueError as e:
        flash(f'Erro ao adicionar transação: {str(e)}', 'error')
    except Exception as e:
        flash(f'Erro inesperado: {str(e)}', 'error')

    return redirect(url_for('transacoes.listar'))


@transacoes_bp.route('/<int:id>/remover', methods=['POST'])
def remover(id):
    """
    Remove uma transação pelo ID.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Cria o gerenciador e remove a transação
    g = Gerenciador(session['usuario_id'])

    try:
        g.remover_transacao(id)
        flash('Transação removida com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover transação: {str(e)}', 'error')

    return redirect(url_for('transacoes.listar'))