# =============================================================================
# routes/metas.py
# -----------------------------------------------------------------------------
# Blueprint de metas financeiras.
# Permite listar, adicionar, depositar e remover metas via formulários HTML.
#
# CONCEITOS APLICADOS:
#   - Blueprint com url_prefix: registrado no app.py com url_prefix='/metas'.
#     A rota '/' aqui vira '/metas', '/nova' vira '/metas/nova', etc.
#   - Padrão PRG (Post/Redirect/Get): após processar POST (adicionar, depositar,
#     remover), redireciona para GET (listar). Evita reenvio de formulário
#     quando o usuário dá F5.
#   - Flash messages: feedback visual que aparece uma vez e desaparece.
#     'success' para ações concluídas, 'error' para falhas.
#   - Validação na fronteira: request.form vem como strings — convertemos para
#     float e validamos antes de passar ao Gerenciador. A view é o ponto onde
#     dados externos (do navegador) entram no sistema.
#   - Parâmetro de URL tipado (<int:id>): Flask converte automaticamente para
#     inteiro e retorna 404 se o valor não for numérico.
#
# Rotas:
#     GET  /metas                 - Lista todas as metas
#     POST /metas/nova            - Adiciona nova meta
#     POST /metas/<id>/depositar  - Deposita valor em uma meta
#     POST /metas/<id>/remover    - Remove uma meta pelo ID
#
# RESPONSÁVEL: Lívia + Alice - Frente 4 (Frontend Flask)
# =============================================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services.gerenciador import Gerenciador

metas_bp = Blueprint('metas', __name__)


@metas_bp.route('/')
def listar():
    """
    Lista todas as metas do usuário logado.

    Se não estiver logado, redireciona para o login.
    Passa a lista de objetos Meta para o template Jinja2.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Cria o gerenciador escopado ao usuário logado
    g = Gerenciador(session['usuario_id'])

    # Obtém as metas reais do banco
    metas = g.listar_metas()

    return render_template('metas.html', metas=metas)


@metas_bp.route('/nova', methods=['POST'])
def adicionar():
    """
    Adiciona uma nova meta financeira.

    Recebe nome, valor_alvo e prazo (opcional) do formulário.
    Prazo vazio vira None — o Gerenciador e o Model tratam como "sem prazo".
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Pega os dados do formulário
    nome = request.form.get('nome')
    valor_alvo = request.form.get('valor_alvo')
    prazo = request.form.get('prazo')

    # Se prazo for vazio, vira None — Gerenciador trata como "sem prazo"
    if not prazo:
        prazo = None

    # Validações básicas — dados do formulário são strings
    if not nome:
        flash('Por favor, informe o nome da meta!', 'error')
        return redirect(url_for('metas.listar'))

    if not valor_alvo:
        flash('Por favor, informe o valor alvo da meta!', 'error')
        return redirect(url_for('metas.listar'))

    # Conversão de string para float — pode falhar com texto não-numérico
    try:
        valor_float = float(valor_alvo)
        if valor_float <= 0:
            flash('O valor alvo deve ser maior que zero!', 'error')
            return redirect(url_for('metas.listar'))
    except ValueError:
        flash('Por favor, informe um valor numérico válido!', 'error')
        return redirect(url_for('metas.listar'))

    # Cria o gerenciador e delega a criação da meta
    g = Gerenciador(session['usuario_id'])

    try:
        g.adicionar_meta(nome, valor_float, prazo)
        flash(f'Meta "{nome}" criada com sucesso!', 'success')
    except ValueError as e:
        # Validação do Gerenciador/Model (nome vazio, valor <= 0).
        flash(f'Erro ao criar meta: {str(e)}', 'error')
    except Exception as e:
        flash(f'Erro inesperado: {str(e)}', 'error')

    # PRG: redireciona para a listagem
    return redirect(url_for('metas.listar'))


@metas_bp.route('/<int:id>/depositar', methods=['POST'])
def depositar(id):
    """
    Deposita um valor em uma meta existente.

    Incrementa o valor_atual da meta. O Gerenciador garante que o depósito
    não ultrapasse o valor_alvo (usa min() internamente).
    LookupError é levantado se a meta não existir ou não pertencer ao usuário.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Pega o valor do depósito do formulário
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

    # Cria o gerenciador e delega o depósito
    g = Gerenciador(session['usuario_id'])

    try:
        g.depositar_em_meta(id, valor_float)
        flash(f'Depósito de R$ {valor_float:.2f} realizado com sucesso!', 'success')
    except LookupError as e:
        # Meta não encontrada para este usuário (id inválido ou de outro usuário).
        flash(f'Meta não encontrada: {str(e)}', 'error')
    except ValueError as e:
        # Valor inválido (ex.: <= 0, embora já validado acima — dupla proteção).
        flash(f'Erro no depósito: {str(e)}', 'error')
    except Exception as e:
        flash(f'Erro inesperado: {str(e)}', 'error')

    return redirect(url_for('metas.listar'))


@metas_bp.route('/<int:id>/remover', methods=['POST'])
def remover(id):
    """
    Remove uma meta pelo ID.

    O Gerenciador repassa o usuario_id para a Persistencia, que filtra
    com AND usuario_id = ? — garantindo que um usuário não remova
    metas de outro (defesa em profundidade).
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Cria o gerenciador e delega a remoção
    g = Gerenciador(session['usuario_id'])

    try:
        g.remover_meta(id)
        flash('Meta removida com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover meta: {str(e)}', 'error')

    return redirect(url_for('metas.listar'))
