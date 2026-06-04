from flask import Flask

# ============================================================================
# IMPORTS DOS BLUEPRINTS (rotas da aplicação)
# ============================================================================
# Cada blueprint é um arquivo .py dentro da pasta routes/
# A Frente 4 é responsável por: dashboard, transacoes e metas
# As demais frentes adicionarão seus imports aqui quando entregarem:
#   from routes.auth import auth_bp           (Frente 1)
#   from routes.contas import contas_bp       (Frente 5)

from routes.dashboard import dashboard_bp
from routes.transacoes import transacoes_bp
from routes.metas import metas_bp


# ============================================================================
# CONFIGURAÇÃO DA APLICAÇÃO FLASK
# ============================================================================

# Cria a instância principal do Flask
# O parâmetro __name__ indica o módulo atual - o Flask usa isso para localizar
# as pastas templates/ e static/
app = Flask(__name__)

# Define a chave secreta para a sessão
# A sessão é usada pelo sistema de login para lembrar qual usuário está logado
# entre uma requisição e outra. Esta chave é TEMPORÁRIA - a Frente 1 pode
# substituir por uma mais segura posteriormente.
app.secret_key = 'chave-temporaria-para-desenvolvimento-frontend'


# ============================================================================
# REGISTRO DOS BLUEPRINTS
# ============================================================================
# Blueprints são como "sub-aplicações" dentro do Flask.
# Cada um tem seu próprio conjunto de rotas e pode ter um prefixo de URL.
# Exemplo: um blueprint com prefixo '/transacoes' faz com que todas as suas
# rotas comecem com /transacoes (ex: /transacoes/novo, /transacoes/1/remover)

# Dashboard (página inicial) - sem prefixo, fica na raiz
app.register_blueprint(dashboard_bp)

# Transações - prefixo /transacoes
# Livia vai criar este blueprint no arquivo routes/transacoes.py
app.register_blueprint(transacoes_bp, url_prefix='/transacoes')

# Metas - prefixo /metas
# Livia vai criar este blueprint no arquivo routes/metas.py
app.register_blueprint(metas_bp, url_prefix='/metas')

# ============================================================================
# BLUEPRINTS QUE SERÃO ADICIONADOS PELAS OUTRAS FRENTES (futuramente)
# ============================================================================
# Quando as outras frentes entregarem, basta descomentar as linhas abaixo:
#
# from routes.auth import auth_bp           # Frente 1 (Autenticação)
# app.register_blueprint(auth_bp, url_prefix='/auth')
#
# from routes.contas import contas_bp       # Frente 5 (Empresa/Contas)
# app.register_blueprint(contas_bp, url_prefix='/contas')


# ============================================================================
# PONTO DE ENTRADA PRINCIPAL
# ============================================================================

if __name__ == '__main__':
    """
    Executa o servidor Flask apenas se este arquivo for rodado diretamente.
    Se este arquivo for importado por outro módulo, o servidor NÃO é iniciado.
    
    Parâmetros do app.run():
        debug=True : Ativa o modo debug - recarrega automaticamente quando
                     o código muda e mostra erros detalhados no navegador.
                     MUITO ÚTIL durante o desenvolvimento.
                     Em produção, isso deve ser desligado (debug=False).
    """
    app.run(debug=True)