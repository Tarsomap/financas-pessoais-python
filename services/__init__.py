# =============================================================================
# services/__init__.py
# -----------------------------------------------------------------------------
# Arquivo de inicialização do pacote 'services'.
# Centraliza os imports das classes de serviço para facilitar o uso
# nos demais módulos:
#   from services import Gerenciador, Relatorio, Persistencia
#
# Os 'services' são a camada de lógica de negócio da aplicação —
# eles ficam entre os modelos (dados) e as views (interface gráfica),
# processando as regras do sistema sem se preocupar com como os dados
# serão exibidos na tela.
# =============================================================================

from .gerenciador import Gerenciador
from .relatorio import Relatorio
from .persistencia import Persistencia
from .autenticacao import Autenticacao

__all__ = ["Gerenciador", "Relatorio", "Persistencia", "Autenticacao"]
