# =============================================================================
# routes/__init__.py
# -----------------------------------------------------------------------------
# Arquivo de inicialização do pacote 'routes'.
#
# Em Python, a presença de um __init__.py transforma uma pasta em um pacote
# importável. Sem ele, 'from routes.dashboard import dashboard_bp' falharia
# com ModuleNotFoundError.
#
# Este arquivo está VAZIO intencionalmente (sem imports centralizados) porque
# cada blueprint é importado individualmente pelo app.py. Centralizar aqui
# criaria dependências circulares: os blueprints importam services, que
# importam models, e qualquer erro de import quebraria TODOS os blueprints
# de uma vez. Com imports individuais no app.py, um blueprint com problema
# não impede os outros de carregar.
# =============================================================================
