# =============================================================================
# routes/transacoes.py
# -----------------------------------------------------------------------------
# Blueprint de transações (receitas e despesas).
# Permite listar, adicionar e remover transações via formulários HTML.
#
# CONCEITOS APLICADOS:
#   - Blueprint com url_prefix: registrado no app.py com url_prefix='/transacoes',
#     então a rota '/' aqui vira '/transacoes' no navegador, '/nova' vira
#     '/transacoes/nova', etc. Mantém as rotas organizadas por domínio.
#   - GET vs. POST: GET para exibir páginas (listar), POST para modificar
#     dados (adicionar, remover). Isso segue o padrão HTTP/REST: GET é
#     idempotente (pode repetir sem efeito colateral), POST não.
#   - Flash messages: flash() envia mensagens de feedback (sucesso, erro)
#     que aparecem UMA VEZ no próximo carregamento de página. O template
#     Jinja2 as exibe e elas são automaticamente removidas da sessão.
#   - Redirect after POST (PRG): após processar um formulário, redireciona
#     com redirect() em vez de renderizar diretamente. Isso evita que o
#     usuário reenvie o formulário ao dar F5 (refresh) — um problema clássico
#     chamado "double submit".
#   - Validação na view: valores vindos do formulário (request.form) são
#     SEMPRE strings. Precisam ser convertidos (float()) e validados antes
#     de passar ao Gerenciador. A view é a fronteira do sistema — dados
#     externos entram sujos e devem sair limpos.
#
# Rotas:
#     GET  /transacoes               - Lista todas as transações
#     POST /transacoes/nova          - Adiciona nova transação (receita ou despesa)
#     POST /transacoes/<id>/remover  - Remove uma transação pelo ID
#
# RESPONSÁVEL: Lívia + Alice - Frente 4 (Frontend Flask)
# =============================================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services.gerenciador import Gerenciador

# Blueprint com nome 'transacoes'. O url_prefix é definido no app.py ao
# registrar, não aqui — separação de responsabilidades entre o blueprint
# (define as rotas relativas) e o app (define onde elas ficam na URL).
transacoes_bp = Blueprint('transacoes', __name__)


@transacoes_bp.route('/')
def listar():
    """
    Lista todas as transações do usuário logado.

    Se não estiver logado, redireciona para o login.
    Passa a lista de objetos Receita/Despesa para o template Jinja2.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Cria o gerenciador escopado ao usuário logado
    g = Gerenciador(session['usuario_id'])

    # Obtém as transações reais do banco
    transacoes = g.listar_transacoes()

    return render_template('transacoes.html', transacoes=transacoes)


@transacoes_bp.route('/nova', methods=['POST'])
def adicionar():
    """
    Adiciona uma nova transação (receita ou despesa).

    Recebe os dados do formulário HTML (request.form), valida, converte
    tipos e delega ao Gerenciador. Após o processamento, redireciona de
    volta para a listagem (padrão PRG — Post/Redirect/Get).
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Pega os dados do formulário.
    # request.form é um dicionário com os campos do <form> HTML.
    # .get() retorna '' se o campo não existir (evita KeyError).
    tipo = request.form.get('tipo')
    descricao = request.form.get('descricao')
    valor = request.form.get('valor')
    categoria = request.form.get('categoria')
    data = request.form.get('data')

    # Se data não foi fornecida, usa None (o Gerenciador usará date.today())
    if not data:
        data = None

    # Validações básicas — dados do formulário são STRINGS, precisam ser
    # verificados antes de passar ao Gerenciador.
    if not descricao:
        flash('Por favor, informe uma descrição!', 'error')
        return redirect(url_for('transacoes.listar'))

    if not categoria:
        flash('Por favor, informe uma categoria!', 'error')
        return redirect(url_for('transacoes.listar'))

    # Conversão de string para float — pode falhar se o usuário digitar texto.
    try:
        valor_float = float(valor)
        if valor_float <= 0:
            flash('O valor deve ser maior que zero!', 'error')
            return redirect(url_for('transacoes.listar'))
    except (ValueError, TypeError):
        flash('Por favor, informe um valor numérico válido!', 'error')
        return redirect(url_for('transacoes.listar'))

    # Cria o gerenciador e delega a operação.
    # O Gerenciador decide se é Receita ou Despesa pelo método chamado.
    g = Gerenciador(session['usuario_id'])

    try:
        if tipo == 'receita':
            g.adicionar_receita(descricao, valor_float, categoria, data)
            flash(f'Receita de R$ {valor_float:.2f} adicionada com sucesso!', 'success')
        else:
            g.adicionar_despesa(descricao, valor_float, categoria, data)
            flash(f'Despesa de R$ {valor_float:.2f} adicionada com sucesso!', 'success')
    except ValueError as e:
        # Validação do Gerenciador/Model (ex.: descrição vazia, valor negativo).
        flash(f'Erro ao adicionar transação: {str(e)}', 'error')
    except Exception as e:
        # Erro inesperado (ex.: falha no banco).
        flash(f'Erro inesperado: {str(e)}', 'error')

    # PRG: redireciona para a listagem em vez de renderizar direto.
    return redirect(url_for('transacoes.listar'))


@transacoes_bp.route('/<int:id>/remover', methods=['POST'])
def remover(id):
    """
    Remove uma transação pelo ID.

    <int:id> no decorator converte o parâmetro da URL para inteiro
    automaticamente — Flask já faz a validação de tipo.
    Usa POST (não GET) porque remoção é uma operação que modifica dados.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Cria o gerenciador e delega a remoção.
    # O Gerenciador repassa o usuario_id para a Persistencia, que filtra
    # com AND usuario_id = ? (defesa em profundidade).
    g = Gerenciador(session['usuario_id'])

    try:
        g.remover_transacao(id)
        flash('Transação removida com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover transação: {str(e)}', 'error')

    return redirect(url_for('transacoes.listar'))
