"""
Blueprint do dashboard (página inicial).
Exibe o saldo atual e um resumo das finanças.
"""
from flask import Blueprint, render_template, session, redirect, url_for
from datetime import date
from services.gerenciador import Gerenciador

# Cria o blueprint do dashboard
# O primeiro parâmetro é o nome do blueprint (usado internamente pelo Flask)
# O segundo parâmetro é o nome do módulo (__name__)
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def dashboard():
    """
    Rota principal do dashboard.
    Acessível via '/' e '/dashboard'.
    Verifica se o usuário está logado antes de mostrar a página.
    """
    # PROTEÇÃO: verifica se o usuário está logado
    # O 'usuario_id' é colocado na sessão pela Frente 1 (Autenticação) após o login
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Cria o gerenciador para o usuário logado
    g = Gerenciador(session['usuario_id'])

    # Obtém os dados reais do banco via Gerenciador
    saldo = g.saldo_atual()

    # Lista todas as transações e pega as 5 mais recentes
    todas_transacoes = g.listar_transacoes()
    # Ordena por data (mais recente primeiro) e pega as 5 primeiras
    ultimas_transacoes = sorted(
        todas_transacoes,
        key=lambda t: t.data,
        reverse=True
    )[:5]

    # Calcula o total de despesas do mês atual
    hoje = date.today()
    despesas_mes = [
        t for t in todas_transacoes
        if t.tipo() == 'despesa' and t.data.year == hoje.year and t.data.month == hoje.month
    ]
    total_despesas_mes = sum(d.valor for d in despesas_mes)

    # Renderiza o template, passando os dados reais
    return render_template(
        'dashboard.html',
        saldo=saldo,
        ultimas_transacoes=ultimas_transacoes,
        total_despesas_mes=total_despesas_mes
    )