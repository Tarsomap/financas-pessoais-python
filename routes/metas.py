"""
Blueprint de metas financeiras.
Permite listar, adicionar, depositar e remover metas.

Rotas:
    GET /metas                 - Lista todas as metas
    POST /metas/nova           - Adiciona nova meta
    POST /metas/<id>/depositar - Deposita valor em uma meta
    POST /metas/<id>/remover   - Remove uma meta pelo ID

"""

from flask import Blueprint, render_template, request, redirect, url_for, session

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
    
    # TODO: Quando a Frente 3 entregar o Gerenciador, substituir por:
    # from services.gerenciador import Gerenciador
    # g = Gerenciador(session['usuario_id'])
    # metas = g.listar_metas()
    
    # Dados temporários (fake) para testar a tela
    # Remove quando o Gerenciador estiver pronto
    metas = [
        {'id': 1, 'nome': 'Viagem para praia', 'valor_alvo': 2000.00, 'valor_atual': 750.00, 'prazo': '2025-12-31'},
        {'id': 2, 'nome': 'PS5', 'valor_alvo': 3500.00, 'valor_atual': 1200.00, 'prazo': '2025-08-15'},
        {'id': 3, 'nome': 'Reserva de emergência', 'valor_alvo': 10000.00, 'valor_atual': 3500.00, 'prazo': None},
    ]
    
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
    if not nome or not valor_alvo:
        # TODO: mostrar mensagem de erro
        return redirect(url_for('metas.listar'))
    
    try:
        valor_float = float(valor_alvo)
        if valor_float <= 0:
            # TODO: mostrar mensagem de erro
            return redirect(url_for('metas.listar'))
    except ValueError:
        # TODO: mostrar mensagem de erro
        return redirect(url_for('metas.listar'))
    
    # TODO: Quando a Frente 3 entregar o Gerenciador, substituir por:
    # from services.gerenciador import Gerenciador
    # g = Gerenciador(session['usuario_id'])
    # g.adicionar_meta(nome, valor_float, prazo)
    
    print(f"[DEBUG] Adicionando meta: {nome} - R$ {valor_float} - Prazo: {prazo}")
    
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
        return redirect(url_for('metas.listar'))
    
    try:
        valor_float = float(valor)
        if valor_float <= 0:
            return redirect(url_for('metas.listar'))
    except ValueError:
        return redirect(url_for('metas.listar'))
    
    # TODO: Quando a Frente 3 entregar o Gerenciador, substituir por:
    # from services.gerenciador import Gerenciador
    # g = Gerenciador(session['usuario_id'])
    # g.depositar_em_meta(id, valor_float)
    
    print(f"[DEBUG] Depositando R$ {valor_float} na meta ID: {id}")
    
    return redirect(url_for('metas.listar'))


@metas_bp.route('/<int:id>/remover', methods=['POST'])
def remover(id):
    """
    Remove uma meta pelo ID.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    # TODO: Quando a Frente 3 entregar o Gerenciador, substituir por:
    # from services.gerenciador import Gerenciador
    # g = Gerenciador(session['usuario_id'])
    # g.remover_meta(id)
    
    print(f"[DEBUG] Removendo meta ID: {id}")
    
    return redirect(url_for('metas.listar'))