from flask import Flask

# ============================================================================
# IMPORTS DOS BLUEPRINTS (rotas da aplicação)
# ============================================================================
# Cada blueprint é um arquivo .py dentro da pasta routes/
# A Frente 4 é responsável por: dashboard, transacoes e metas
# Frente 1 entregou auth; Frente 5 entregou contas.

from routes.dashboard import dashboard_bp
from routes.transacoes import transacoes_bp
from routes.metas import metas_bp
from routes.auth import auth_bp
from routes.contas import contas_bp


# ============================================================================
# FACTORY DA APLICAÇÃO (create_app)
# ============================================================================
# O padrão factory permite que os testes criem uma instância independente
# (banco :memory:, TESTING=True) sem interferir na instância de produção.
# É o que o conftest.py espera: create_app({"TESTING": True, ...}).

def create_app(config: dict | None = None) -> Flask:
    """
    Cria e configura a aplicação Flask.

    Parâmetros:
        config: dicionário opcional com sobrescritas de configuração.
                Útil para testes (ex: TESTING=True, SECRET_KEY diferente).

    Retorna:
        A instância Flask configurada e com todos os blueprints registrados.
    """
    app = Flask(__name__)

    # strict_slashes=False: aceita /transacoes e /transacoes/ sem redirecionar.
    # Sem isso, /transacoes retornaria 308 → /transacoes/, e os smoke tests
    # (que esperam 200 ou 302) falhariam.
    app.url_map.strict_slashes = False

    # Chave secreta para a sessão (login). TEMPORÁRIA — ambiente de desenvolvimento.
    app.secret_key = 'chave-temporaria-para-desenvolvimento-frontend'

    # Sobrescritas de configuração (ex.: testes passam TESTING e SECRET_KEY).
    if config:
        app.config.update(config)

    # ------------------------------------------------------------------
    # REGISTRO DOS BLUEPRINTS
    # ------------------------------------------------------------------
    # Blueprints são como "sub-aplicações" dentro do Flask.
    # O url_prefix faz todas as rotas do blueprint começarem com esse caminho.
    # Exemplo: url_prefix='/transacoes' → /transacoes/, /transacoes/nova, etc.

    # Dashboard (página inicial) - sem prefixo, fica na raiz (/ e /dashboard)
    app.register_blueprint(dashboard_bp)

    # Transações - prefixo /transacoes
    app.register_blueprint(transacoes_bp, url_prefix='/transacoes')

    # Metas - prefixo /metas
    app.register_blueprint(metas_bp, url_prefix='/metas')

    # Autenticação (Frente 1) - sem prefixo: /login, /cadastro, /logout
    app.register_blueprint(auth_bp)

    # Contas a pagar/receber (Frente 5) - prefixo /contas
    app.register_blueprint(contas_bp, url_prefix='/contas')

    return app


# ============================================================================
# INSTÂNCIA DE NÍVEL DE MÓDULO (para python app.py e flask run)
# ============================================================================
app = create_app()


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
