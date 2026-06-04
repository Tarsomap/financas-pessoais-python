"""
Blueprint do dashboard (página inicial).
Exibe o saldo atual e um resumo das finanças.
"""
from flask import Blueprint, render_template, session, redirect, url_for

# Cria o blueprint do dashboard
# O primeiro parâmetro é o nome do blueprint (usado internamente pelo Flask)
# O segundo parâmetro é o nome do módulo (__name__)
dashboard_bp = Blueprint('dashboard', __name__)


# Dados fake enquanto o Gerenciador não está pronto
# Quando a Frente 3 entregar, isso será substituído por chamadas reais ao banco
def get_saldo_fake():
    """Retorna um saldo falso para teste enquanto o backend não está pronto."""
    return 1250.75


def get_ultimas_transacoes_fake():
    """Retorna transações falsas para teste."""
    return [
        {'descricao': 'Salário', 'valor': 5000.00, 'tipo': 'receita', 'data': '2026-06-01'},
        {'descricao': 'Aluguel', 'valor': 1500.00, 'tipo': 'despesa', 'data': '2026-06-02'},
        {'descricao': 'Supermercado', 'valor': 800.00, 'tipo': 'despesa', 'data': '2026-06-03'},
        {'descricao': 'Freela', 'valor': 1200.00, 'tipo': 'receita', 'data': '2026-06-04'},
    ]


def get_total_despesas_mes_fake():
    """Retorna o total de despesas do mês falso."""
    return 2300.00


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
    # Se não existir, redireciona para a página de login
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))  # Rota que a Frente 1 vai criar
    
    # TODO: Quando a Frente 3 entregar o Gerenciador, substituir os dados fake por:
    #
    # from services.gerenciador import Gerenciador
    # g = Gerenciador(session['usuario_id'])
    # saldo = g.saldo_atual()
    # transacoes = g.listar_transacoes()[:5]  # últimas 5 transações
    # total_despesas = sum(t.valor for t in g.listar_transacoes(tipo='despesa')
    #                      if t.data.month == data_atual.month)
    
    # Dados temporários (fake) para teste
    saldo = get_saldo_fake()
    ultimas_transacoes = get_ultimas_transacoes_fake()
    total_despesas_mes = get_total_despesas_mes_fake()
    
    # Renderiza o template, passando os dados para serem exibidos
    return render_template(
        'dashboard.html',
        saldo=saldo,
        ultimas_transacoes=ultimas_transacoes,
        total_despesas_mes=total_despesas_mes
    )