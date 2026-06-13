# =============================================================================
# models/__init__.py
# -----------------------------------------------------------------------------
# Arquivo de inicialização do pacote 'models'.
# Em Python, um arquivo __init__.py transforma uma pasta em um pacote,
# permitindo importar seus módulos com 'from models import ...'.
#
# Aqui centralizamos os imports das classes principais do pacote para que
# outros módulos possam fazer simplesmente:
#   from models import Transacao, Receita, Despesa, Categoria, Meta
# em vez de precisar especificar o arquivo exato de cada classe.
# =============================================================================

from .transacao import Transacao, Receita, Despesa
from .categoria import Categoria
from .meta import Meta
from .perfil import Perfil, PessoaFisica, Empresa, criar_perfil

__all__ = [
    "Transacao", "Receita", "Despesa", "Categoria", "Meta",
    "Perfil", "PessoaFisica", "Empresa", "criar_perfil",
]
