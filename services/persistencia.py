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
#   Meta:      META|NOME|VALOR_ALVO|VALOR_ATUAL|PRAZO
#
# Exemplo:
#   receita|Salário|3000.0|Salário|2026-04-01
#   despesa|Mercado|250.5|Alimentação|2026-04-02
#   META|Viagem|2000.0|500.0|2026-12-31
#
# Conceitos demonstrados:
#   - open() com modos 'r' e 'w', encoding='utf-8'
#   - split('|') para separar campos
#   - strip() para remover espaços e quebras de linha residuais
#   - date.fromisoformat() para converter string em date
#   - os.path para caminhos portáteis entre sistemas operacionais
#   - os.makedirs() para criar a pasta 'dados/' se ainda não existir
#
# RESPONSÁVEL: Joao Guilherme
# =============================================================================

import os
from datetime import date

from models.transacao import Receita, Despesa
from models.meta import Meta


# Caminho absoluto e portátil para dados/dados.txt, independente de onde
# o script é executado. __file__ aponta para este próprio arquivo .py.
CAMINHO_ARQUIVO = os.path.join(os.path.dirname(__file__), "..", "dados", "dados.txt")


class Persistencia:
    """Salva e carrega dados da aplicação em arquivo de texto simples."""

    @staticmethod
    def salvar(transacoes: list, metas: list) -> None:
        """
        Persiste todas as transações e metas no arquivo dados.txt.

        Cada objeto é serializado em uma linha com campos separados por '|'.
        Cria a pasta 'dados/' automaticamente se ela ainda não existir.

        Formato por linha:
          - Transação: tipo|descricao|valor|categoria|data
          - Meta:      META|nome|valor_alvo|valor_atual|prazo

        Parâmetros:
            transacoes (list): lista de objetos Receita ou Despesa
            metas      (list): lista de objetos Meta
        """
        # os.makedirs com exist_ok=True cria a pasta sem lançar erro se já existir
        os.makedirs(os.path.dirname(CAMINHO_ARQUIVO), exist_ok=True)

        # Abre o arquivo em modo escrita ('w'): cria se não existir, sobrescreve se existir
        with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as arquivo:

            # Serializa cada transação em uma linha
            for t in transacoes:
                # hasattr garante compatibilidade se categoria for string ou objeto
                categoria = t.categoria.nome if hasattr(t.categoria, "nome") else str(t.categoria)
                linha = f"{t.tipo()}|{t.descricao}|{t.valor}|{categoria}|{t.data.isoformat()}\n"
                arquivo.write(linha)

            # Serializa cada meta em uma linha com prefixo META
            for m in metas:
                linha = f"META|{m.nome}|{m.valor_alvo}|{m.valor_atual}|{m.prazo.isoformat()}\n"
                arquivo.write(linha)

    @staticmethod
    def carregar() -> tuple:
        """
        Lê o arquivo dados.txt e reconstrói os objetos do sistema.

        Se o arquivo não existir (primeira execução), retorna listas vazias
        sem lançar exceção — comportamento esperado na inicialização do app.

        Retorna:
            tuple: (lista_transacoes, lista_metas)
                   Cada elemento é uma lista; ambas são vazias se o arquivo
                   não existir ou se não houver registros daquele tipo.

        Lança:
            ValueError se uma linha tiver formato inválido (campos a menos).
        """
        transacoes = []
        metas = []

        # Se o arquivo não existir, retorna tupla vazia — não é um erro
        if not os.path.exists(CAMINHO_ARQUIVO):
            return transacoes, metas

        with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as arquivo:
            for numero, linha in enumerate(arquivo, start=1):
                # strip() remove '\n' e espaços em branco no início/fim
                linha = linha.strip()

                # Ignora linhas vazias (ex.: linha em branco no final do arquivo)
                if not linha:
                    continue

                # split('|') divide a linha em campos pelo separador
                campos = linha.split("|")

                if campos[0].upper() == "META":
                    # Linha de meta: META|nome|valor_alvo|valor_atual|prazo
                    if len(campos) < 5:
                        raise ValueError(f"Linha {numero} inválida (meta): '{linha}'")

                    nome       = campos[1]
                    valor_alvo = float(campos[2])
                    valor_atual = float(campos[3])
                    prazo      = date.fromisoformat(campos[4])

                    meta = Meta(nome, valor_alvo, prazo)
                    # Restaura o valor já depositado usando depositar(), se houver
                    if valor_atual > 0:
                        meta.depositar(valor_atual)
                    metas.append(meta)

                else:
                    # Linha de transação: tipo|descricao|valor|categoria|data
                    if len(campos) < 5:
                        raise ValueError(f"Linha {numero} inválida (transação): '{linha}'")

                    tipo      = campos[0].lower()
                    descricao = campos[1]
                    valor     = float(campos[2])
                    categoria = campos[3]
                    data      = date.fromisoformat(campos[4])

                    # Instancia o objeto correto conforme o tipo lido do arquivo
                    if tipo == "receita":
                        transacoes.append(Receita(descricao, valor, categoria, data))
                    elif tipo == "despesa":
                        transacoes.append(Despesa(descricao, valor, categoria, data))
                    # Linhas com tipo desconhecido são silenciosamente ignoradas

        return transacoes, metas