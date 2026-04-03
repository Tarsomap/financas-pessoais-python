# =============================================================================
# services/persistencia.py
# -----------------------------------------------------------------------------
# Responsável por salvar e carregar os dados da aplicação em um arquivo .txt.
#
# Por que .txt e não JSON ou CSV?
# O formato .txt com separador '|' é uma introdução à leitura/escrita de
# arquivos em Python, sem depender de bibliotecas externas. É suficiente
# para demonstrar os conceitos de open(), read(), write() e split().
#
# Formato do arquivo dados.txt:
#   Cada linha = um registro
#   Campos separados por '|'
#
#   Transação: TIPO|DESCRICAO|VALOR|CATEGORIA|DATA
#   Meta:      META|DESCRICAO|VALOR_ALVO|VALOR_ATUAL|PRAZO
#
# Exemplo de conteúdo do arquivo:
#   receita|Salário|3000.0|Salário|2026-04-01
#   despesa|Mercado|250.5|Alimentação|2026-04-02
#   META|Viagem|2000.0|500.0|2026-12-31
#
# Conceitos demonstrados neste arquivo:
#   - open() com modos 'r' (leitura) e 'w' (escrita)
#   - encoding='utf-8' para suporte a acentos
#   - split('|') para separar campos
#   - date.fromisoformat() para converter string em objeto date
#   - os.path para manipular caminhos de arquivo
#
# RESPONSÁVEL: Pessoa 5
# =============================================================================

import os
from datetime import date
from models import Receita, Despesa, Meta

# Caminho do arquivo de dados (relativo à raiz do projeto)
CAMINHO_ARQUIVO = os.path.join(os.path.dirname(__file__), "..", "dados", "dados.txt")


class Persistencia:
    """Responsável por salvar e carregar dados em arquivo .txt."""

    @staticmethod
    def salvar(transacoes: list, metas: list) -> None:
        """
        Salva todas as transações e metas no arquivo.
        Sobrescreve o arquivo inteiro a cada chamada.

        Args:
            transacoes: Lista de objetos Transacao.
            metas: Lista de objetos Meta.
        """
        # TODO: Implementar
        # Dica: abra o arquivo com open(CAMINHO_ARQUIVO, 'w', encoding='utf-8')
        # Para cada transacao: escreva 'tipo|descricao|valor|categoria|data\n'
        # Para cada meta: escreva 'META|descricao|valor_alvo|valor_atual|prazo\n'
        pass

    @staticmethod
    def carregar() -> tuple:
        """
        Lê o arquivo e reconstrói as listas de transações e metas.

        Returns:
            Tupla (lista_transacoes, lista_metas).
            Retorna ([], []) se o arquivo não existir.
        """
        # TODO: Implementar
        # Dica:
        # 1. Verifique se o arquivo existe com os.path.exists(CAMINHO_ARQUIVO)
        # 2. Abra com open(CAMINHO_ARQUIVO, 'r', encoding='utf-8')
        # 3. Para cada linha: campos = linha.strip().split('|')
        # 4. Se campos[0] == 'receita' -> crie Receita(...)
        #    Se campos[0] == 'despesa' -> crie Despesa(...)
        #    Se campos[0] == 'META'    -> crie Meta(...)
        # 5. Use date.fromisoformat(campos[4]) para converter a data
        pass
