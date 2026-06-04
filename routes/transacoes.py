"""
Blueprint de transações (receitas e despesas).
Permite listar, adicionar e remover transações.

Rotas:
    GET /transacoes           - Lista todas as transações
    POST /transacoes/nova     - Adiciona nova transação (receita ou despesa)
    POST /transacoes/<id>/remover - Remove uma transação pelo ID

"""

from flask import Blueprint, render_template, request, redirect, url_for, session

# Cria o blueprint com prefixo /transacoes
transacoes_bp = Blueprint('transacoes', __name__, url_prefix='/transacoes')


@transacoes_bp.route('/')
def listar():
    """
    Lista todas as transações do usuário logado.
    Se não estiver logado, redireciona para o login.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    # TODO: Quando a Frente 3 entregar o Gerenciador, substituir por:
    # from services.gerenciador import Gerenciador
    # g = Gerenciador(session['usuario_id'])
    # transacoes = g.listar_transacoes()
    
    # Dados temporários (fake) para testar a tela
    # Remove quando o Gerenciador estiver pronto
    transacoes = [
        {'id': 1, 'tipo': 'receita', 'descricao': 'Salário', 'valor': 5000.00, 'categoria': 'Salário', 'data': '2025-04-01'},
        {'id': 2, 'tipo': 'despesa', 'descricao': 'Aluguel', 'valor': 1500.00, 'categoria': 'Moradia', 'data': '2025-04-05'},
        {'id': 3, 'tipo': 'despesa', 'descricao': 'Supermercado', 'valor': 600.00, 'categoria': 'Alimentação', 'data': '2025-04-10'},
        {'id': 4, 'tipo': 'receita', 'descricao': 'Freelance', 'valor': 800.00, 'categoria': 'Outros', 'data': '2025-04-15'},
    ]
    
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
    
    # Validações básicas
    if not descricao or not valor or not categoria:
        # TODO: mostrar mensagem de erro
        return redirect(url_for('transacoes.listar'))
    
    try:
        valor_float = float(valor)
        if valor_float <= 0:
            # TODO: mostrar mensagem de erro
            return redirect(url_for('transacoes.listar'))
    except ValueError:
        # TODO: mostrar mensagem de erro
        return redirect(url_for('transacoes.listar'))
    
    # TODO: Quando a Frente 3 entregar o Gerenciador, substituir por:
    # from services.gerenciador import Gerenciador
    # g = Gerenciador(session['usuario_id'])
    # 
    # if tipo == 'receita':
    #     g.adicionar_receita(descricao, valor_float, categoria, data)
    # else:
    #     g.adicionar_despesa(descricao, valor_float, categoria, data)
    
    # Por enquanto, só redireciona (dados fake não são salvos)
    print(f"[DEBUG] Adicionando {tipo}: {descricao} - R$ {valor_float} - {categoria} - {data}")
    
    return redirect(url_for('transacoes.listar'))


@transacoes_bp.route('/<int:id>/remover', methods=['POST'])
def remover(id):
    """
    Remove uma transação pelo ID.
    """
    # Proteção: verifica se usuário está logado
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    # TODO: Quando a Frente 3 entregar o Gerenciador, substituir por:
    # from services.gerenciador import Gerenciador
    # g = Gerenciador(session['usuario_id'])
    # g.remover_transacao(id)
    
    print(f"[DEBUG] Removendo transação ID: {id}")
    
    return redirect(url_for('transacoes.listar'))