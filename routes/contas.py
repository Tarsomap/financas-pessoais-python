# =============================================================================
# routes/contas.py
# -----------------------------------------------------------------------------
# Blueprint de contas a pagar/receber (Frente 5 → camada web).
#
# Funcionalidade do perfil empresa. Assim como auth, esta camada não tem
# regra de negócio: ela liga os formulários aos métodos que já existem no
# Gerenciador (adicionar_conta, listar_contas, marcar_conta_paga,
# remover_conta). Segue o mesmo molde de routes/transacoes.py e routes/metas.py.
#
# CONCEITOS APLICADOS:
#   - Blueprint com url_prefix: registrado no app.py com url_prefix='/contas'.
#     Todas as rotas daqui ficam sob /contas/ no navegador.
#   - Padrão PRG (Post/Redirect/Get): após qualquer operação de escrita
#     (adicionar, pagar, remover), redireciona para a listagem.
#   - Validação na fronteira: valores do formulário (strings) são convertidos
#     e validados antes de serem passados ao Gerenciador.
#   - Parâmetro tipado (<int:id>): Flask converte automaticamente para inteiro.
#   - Separação de responsabilidades: a rota não sabe nada de SQL nem de
#     lógica de negócio — tudo é delegado ao Gerenciador, que por sua vez
#     delega à Persistencia.
#
# Rotas:
#     GET  /contas              - lista as contas do usuário
#     POST /contas/nova         - adiciona conta (pagar ou receber)
#     POST /contas/<id>/pagar   - marca conta como paga
#     POST /contas/<id>/remover - remove a conta
#
# RESPONSÁVEL: Tarso - Frente 5 (Empresa: contas a pagar/receber)
#              + Lívia e Alice - Frente 4 (camada web/templates)
# =============================================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services.gerenciador import Gerenciador

contas_bp = Blueprint('contas', __name__)


@contas_bp.route('/')
def listar():
    """
    Lista todas as contas do usuário logado.

    Passa a lista de objetos Conta para o template Jinja2, que decide
    como exibir (ícone de pago/pendente, cor de vencido, etc.).
    """
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    g = Gerenciador(session['usuario_id'])
    contas = g.listar_contas()
    return render_template('contas.html', contas=contas)


@contas_bp.route('/nova', methods=['POST'])
def adicionar():
    """
    Adiciona uma nova conta a pagar ou a receber.

    Recebe tipo ('pagar'/'receber'), descrição, valor e data de vencimento
    do formulário. Valida os dados e delega ao Gerenciador.
    """
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Pega os dados do formulário
    tipo = request.form.get('tipo')
    descricao = request.form.get('descricao')
    valor = request.form.get('valor')
    vencimento = request.form.get('vencimento')

    # Validações básicas — dados do formulário são strings
    if not descricao:
        flash('Por favor, informe uma descricao!', 'error')
        return redirect(url_for('contas.listar'))

    if not vencimento:
        flash('Por favor, informe a data de vencimento!', 'error')
        return redirect(url_for('contas.listar'))

    # Conversão de string para float
    try:
        valor_float = float(valor)
        if valor_float <= 0:
            flash('O valor deve ser maior que zero!', 'error')
            return redirect(url_for('contas.listar'))
    except (ValueError, TypeError):
        flash('Por favor, informe um valor numerico valido!', 'error')
        return redirect(url_for('contas.listar'))

    # Delega ao Gerenciador, que cria o objeto Conta e persiste no banco
    g = Gerenciador(session['usuario_id'])
    try:
        g.adicionar_conta(tipo, descricao, valor_float, vencimento)
        flash('Conta adicionada com sucesso!', 'success')
    except ValueError as e:
        # Validação do Model/Gerenciador (tipo inválido, descrição vazia, etc.)
        flash(f'Erro ao adicionar conta: {e}', 'error')
    except Exception as e:
        flash(f'Erro inesperado: {e}', 'error')

    return redirect(url_for('contas.listar'))


@contas_bp.route('/<int:id>/pagar', methods=['POST'])
def pagar(id):
    """
    Marca uma conta como paga (pago: 0 → 1 no banco).

    Operação irreversível pela interface — não há botão de "desfazer".
    Se no futuro for necessário estornar, um método dedicado
    'estornar_conta()' seria mais seguro que aceitar pago=0.
    """
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
    """
    Remove uma conta pelo id.

    O Gerenciador repassa o usuario_id para a Persistencia, que garante
    AND usuario_id = ? no DELETE (defesa em profundidade — um usuário
    não consegue remover contas de outro).
    """
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    g = Gerenciador(session['usuario_id'])
    try:
        g.remover_conta(id)
        flash('Conta removida com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover conta: {e}', 'error')

    return redirect(url_for('contas.listar'))
