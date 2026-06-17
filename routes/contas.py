"""
Blueprint de contas a pagar/receber (Frente 5 -> camada web).

Funcionalidade do perfil empresa. Assim como auth, esta camada nao tem
regra de negocio: ela liga os formularios aos metodos que ja existem no
Gerenciador (adicionar_conta, listar_contas, marcar_conta_paga,
remover_conta). Segue o mesmo molde de routes/transacoes.py e routes/metas.py.

Rotas:
    GET  /contas              - lista as contas do usuario
    POST /contas/nova         - adiciona conta (pagar ou receber)
    POST /contas/<id>/pagar   - marca conta como paga
    POST /contas/<id>/remover - remove a conta
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services.gerenciador import Gerenciador

contas_bp = Blueprint('contas', __name__)


@contas_bp.route('/')
def listar():
    """Lista todas as contas do usuario logado."""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    g = Gerenciador(session['usuario_id'])
    contas = g.listar_contas()
    return render_template('contas.html', contas=contas)


@contas_bp.route('/nova', methods=['POST'])
def adicionar():
    """Adiciona uma nova conta a pagar ou a receber."""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    tipo = request.form.get('tipo')
    descricao = request.form.get('descricao')
    valor = request.form.get('valor')
    vencimento = request.form.get('vencimento')

    if not descricao:
        flash('Por favor, informe uma descricao!', 'error')
        return redirect(url_for('contas.listar'))

    if not vencimento:
        flash('Por favor, informe a data de vencimento!', 'error')
        return redirect(url_for('contas.listar'))

    try:
        valor_float = float(valor)
        if valor_float <= 0:
            flash('O valor deve ser maior que zero!', 'error')
            return redirect(url_for('contas.listar'))
    except (ValueError, TypeError):
        flash('Por favor, informe um valor numerico valido!', 'error')
        return redirect(url_for('contas.listar'))

    g = Gerenciador(session['usuario_id'])
    try:
        g.adicionar_conta(tipo, descricao, valor_float, vencimento)
        flash('Conta adicionada com sucesso!', 'success')
    except ValueError as e:
        flash(f'Erro ao adicionar conta: {e}', 'error')
    except Exception as e:
        flash(f'Erro inesperado: {e}', 'error')

    return redirect(url_for('contas.listar'))


@contas_bp.route('/<int:id>/pagar', methods=['POST'])
def pagar(id):
    """Marca uma conta como paga (pago: 0 -> 1)."""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    g = Gerenciador(session['usuario_id'])
    try:
        g.marcar_conta_paga(id)
        flash('Conta marcada como paga!', 'success')
    except Exception as e:
        flash(f'Erro ao marcar conta: {e}', 'error')

    return redirect(url_for('contas.listar'))


@contas_bp.route('/<int:id>/remover', methods=['POST'])
def remover(id):
    """Remove uma conta pelo id."""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    g = Gerenciador(session['usuario_id'])
    try:
        g.remover_conta(id)
        flash('Conta removida com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover conta: {e}', 'error')

    return redirect(url_for('contas.listar'))
