# =============================================================================
# services/persistencia.py
# -----------------------------------------------------------------------------
# Responsável por salvar e carregar os dados da aplicação em um arquivo .txt.
#
# Por que .txt e não JSON ou CSV?
# O formato .txt com separador '|' é uma introdução à leitura/escrita de
# arquivos em Python sem depender de bibliotecas externas. É suficiente
# para demonstrar os conceitos de open(), read(), write() e split().
#
# Formato do arquivo dados.txt:
#   Cada linha = um registro. Campos separados por '|'.
#
#   Transação: TIPO|DESCRICAO|VALOR|CATEGORIA|DATA
#   Meta:      META|DESCRICAO|VALOR_ALVO|VALOR_ATUAL|PRAZO
#
# Exemplo:
#   receita|Salário|3000.0|Salário|2026-04-01
#   despesa|Mercado|250.5|Alimentação|2026-04-02
#   META|Viagem|2000.0|500.0|2026-12-31
#
# Conceitos demonstrados:
#   - open() com modos 'r' e 'w', encoding='utf-8'
#   - split('|') para separar campos
#   - date.fromisoformat() para converter string em date
#   - os.path para caminhos portáteis entre sistemas operacionais
#
# RESPONSÁVEL: Joao Guilherme
# =============================================================================

import os
from datetime import date
from models import Receita, Despesa, Meta

CAMINHO_ARQUIVO = os.path.join(os.path.dirname(__file__), "..", "dados", "dados.txt")


class Persistencia:
    """Salva e carrega dados em arquivo .txt."""

    @staticmethod
    def salvar(transacoes: list, metas: list) -> None:
        """
        Salva todas as transações e metas no arquivo.
        Dica: open(CAMINHO_ARQUIVO, 'w', encoding='utf-8')
        """
        # TODO: Implementar
        pass

    @staticmethod
    def carregar() -> tuple:
        """
        Lê o arquivo e retorna (lista_transacoes, lista_metas).
        Retorna ([], []) se o arquivo não existir.
        Dica: os.path.exists(), split('|'), date.fromisoformat()
        """
        # TODO: Implementar
        pass
