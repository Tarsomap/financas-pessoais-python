# =============================================================================
# routes/dashboard.py
# -----------------------------------------------------------------------------
# Blueprint do dashboard — página inicial da aplicação após o login.
# Exibe o saldo atual, as últimas transações e o total de despesas do mês.
#
# CONCEITOS APLICADOS:
#   - Blueprint (Flask): agrupa rotas relacionadas numa "sub-aplicação".
#     O app.py registra este blueprint, e o Flask roteia as requisições
#     para as funções definidas aqui. Blueprints permitem separar o código
#     por funcionalidade sem um único arquivo gigante.
#   - Sessão (session): dicionário criptografado armazenado no cookie do
#     navegador. Contém usuario_id (colocado pelo login) que identifica
#     quem está logado. Cada rota verifica se usuario_id está na sessão
#     antes de prosseguir — se não estiver, redireciona para /login.
#   - Separação de responsabilidades: a rota NÃO calcula saldo nem filtra
#     transações. Ela pede ao Gerenciador (que pede à Persistencia) e
#     só exibe o resultado no template. A view cuida da tela, o service
#     cuida da regra, o banco cuida do dado.
#
# RESPONSÁVEL: Lívia + Alice - Frente 4 (Frontend Flask)
# =============================================================================

from datetime import date

from flask import Blueprint, render_template, session, redirect, url_for

from services.gerenciador import Gerenciador

# Cria o blueprint do dashboard.
# Primeiro parâmetro: nome do blueprint (usado internamente pelo Flask para
# gerar URLs com url_for, ex.: url_for('dashboard.dashboard')).
# Segundo parâmetro: __name__ (módulo atual — Flask usa para localizar
# templates e arquivos estáticos relativos a este módulo).
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def dashboard():
    """
    Rota principal do dashboard.

    Acessível via '/' (raiz) e '/dashboard' (ambas apontam para a mesma função).
    Verifica se o usuário está logado e monta os dados para o template:
        - saldo: receitas − despesas (via Gerenciador)
        - ultimas_transacoes: as 5 mais recentes, ordenadas por data
        - total_despesas_mes: soma das despesas do mês corrente
    """
    # PROTEÇÃO: verifica se o usuário está logado.
    # O 'usuario_id' é colocado na sessão pela rota de login (routes/auth.py)
    # após autenticação bem-sucedida. Se não estiver lá, o usuário não fez login.
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Cria o gerenciador escopado ao usuário logado.
    # Todas as operações abaixo ficam isoladas a este usuario_id —
    # um usuário nunca vê os dados de outro.
    g = Gerenciador(session['usuario_id'])

    # Obtém o saldo real do banco via Gerenciador (receitas − despesas).
    saldo = g.saldo_atual()

    # Lista todas as transações e pega as 5 mais recentes.
    todas_transacoes = g.listar_transacoes()
    # sorted() com key=lambda ordena por data; reverse=True coloca a mais
    # recente primeiro. [:5] pega só as 5 primeiras (slice).
    ultimas_transacoes = sorted(
        todas_transacoes,
        key=lambda t: t.data,
        reverse=True
    )[:5]

    # Calcula o total de despesas do mês atual.
    # Filtra transações que são despesa E pertencem ao mês/ano corrente.
    hoje = date.today()
    despesas_mes = [
        t for t in todas_transacoes
        if t.tipo() == 'despesa' and t.data.year == hoje.year and t.data.month == hoje.month
    ]
    total_despesas_mes = sum(d.valor for d in despesas_mes)

    # render_template: pega o arquivo HTML em templates/ e injeta as variáveis.
    # O template acessa saldo, ultimas_transacoes e total_despesas_mes via Jinja2.
    return render_template(
        'dashboard.html',
        saldo=saldo,
        ultimas_transacoes=ultimas_transacoes,
        total_despesas_mes=total_despesas_mes
    )
