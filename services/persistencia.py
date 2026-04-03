import os
from datetime import date
from models import Receita, Despesa, Meta

CAMINHO_ARQUIVO = os.path.join(os.path.dirname(__file__), "..", "dados", "dados.txt")


class Persistencia:
    """
    Responsável por salvar e carregar dados em arquivo .txt.

    Formato do arquivo:
        Cada linha representa um registro.
        Campos separados por '|'.

        Transação: TIPO|DESCRICAO|VALOR|CATEGORIA|DATA
        Meta:      META|DESCRICAO|VALOR_ALVO|VALOR_ATUAL|PRAZO

    Exemplo:
        receita|Salário|3000.0|Salário|2026-04-01
        despesa|Mercado|250.5|Alimentação|2026-04-02
        META|Viagem|2000.0|500.0|2026-12-31
    """

    @staticmethod
    def salvar(transacoes: list, metas: list) -> None:
        """
        Salva todas as transações e metas no arquivo.

        Args:
            transacoes: Lista de objetos Transacao.
            metas: Lista de objetos Meta.
        """
        # TODO: Implementar
        # Dica: abra o arquivo com open(CAMINHO_ARQUIVO, 'w', encoding='utf-8')
        # Para cada transacao, escreva: tipo|descricao|valor|categoria|data\n
        # Para cada meta, escreva: META|descricao|valor_alvo|valor_atual|prazo\n
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
        # Dica: use os.path.exists(CAMINHO_ARQUIVO) para verificar se existe
        # Para cada linha, faça split('|') e reconstrua o objeto correto
        # Para datas, use date.fromisoformat(string_data)
        pass
