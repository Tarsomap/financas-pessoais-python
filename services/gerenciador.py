# =============================================================================
# services/gerenciador.py
# -----------------------------------------------------------------------------
# Camada de serviço central do sistema de finanças pessoais.
# O Gerenciador coordena todas as operações de negócio: cria e remove
# transações (receitas e despesas), calcula saldo e gerencia metas.
#
# CONCEITOS APLICADOS:
#   - Encapsulamento: atributos _transacoes e _metas são privados
#   - Composição: Gerenciador usa objetos Receita, Despesa e Meta
#   - List comprehensions: usadas nos filtros e no cálculo de saldo
#   - Tratamento de exceções: IndexError e ValueError com mensagens claras
#   - Separação de responsabilidades: lógica de negócio isolada da view
#
# RESPONSÁVEL: Pessoa 3 (Vinicius Prado Sobral)
# =============================================================================

from __future__ import annotations

from datetime import date
from typing import List, Optional

from models.transacao import Receita, Despesa
from models.meta import Meta


class Gerenciador:
    """
    Serviço central que gerencia transações financeiras e metas de economia.
    Mantém listas internas e expõe métodos de negócio para a camada de views.
    """

    def __init__(self):
        self._transacoes: list = []
        self._metas: List[Meta] = []

    # -------------------------------------------------------------------------
    # TRANSAÇÕES
    # -------------------------------------------------------------------------

    def adicionar_receita(
        self,
        descricao: str,
        valor: float,
        categoria: str,
        data: date = None,
    ) -> Receita:
        """
        Cria uma Receita e a registra na lista de transações.

        Parâmetros:
            descricao (str)       : descrição da receita (ex.: "Salário")
            valor     (float)     : valor positivo em reais
            categoria (str)       : categoria (ex.: "Salário", "Freelance")
            data      (date, opt) : data da transação; usa date.today() se None

        Retorna:
            Objeto Receita recém-criado.

        Lança:
            ValueError se descrição vazia ou valor <= 0 (vem do model Transacao).
        """
        receita = Receita(descricao, valor, categoria, data)
        self._transacoes.append(receita)
        return receita

    def adicionar_despesa(
        self,
        descricao: str,
        valor: float,
        categoria: str,
        data: date = None,
    ) -> Despesa:
        """
        Cria uma Despesa e a registra na lista de transações.

        Parâmetros:
            descricao (str)       : descrição da despesa (ex.: "Mercado")
            valor     (float)     : valor positivo em reais
            categoria (str)       : categoria (ex.: "Alimentação", "Transporte")
            data      (date, opt) : data da transação; usa date.today() se None

        Retorna:
            Objeto Despesa recém-criado.

        Lança:
            ValueError se descrição vazia ou valor <= 0 (vem do model Transacao).
        """
        despesa = Despesa(descricao, valor, categoria, data)
        self._transacoes.append(despesa)
        return despesa

    def remover_transacao(self, indice: int) -> None:
        """
        Remove a transação na posição `indice` da lista (0-based).

        Parâmetros:
            indice (int): posição da transação a remover

        Lança:
            IndexError se o índice estiver fora do intervalo da lista.
        """
        if indice < 0 or indice >= len(self._transacoes):
            raise IndexError(f"Índice {indice} fora do intervalo.")
        del self._transacoes[indice]

    def listar_transacoes(
        self,
        tipo: str = None,
        categoria: str = None,
    ) -> list:
        """
        Retorna todas as transações, com filtros opcionais.

        Parâmetros:
            tipo      (str, opt) : "receita" ou "despesa"
            categoria (str, opt) : nome exato da categoria

        Retorna:
            Lista de transações que satisfazem os filtros informados.
            Sem filtros, retorna todas as transações.

        Exemplo de uso com list comprehension interna:
            [t for t in resultado if t.tipo() == tipo]
        """
        resultado = list(self._transacoes)

        if tipo is not None:
            resultado = [t for t in resultado if t.tipo() == tipo.strip().lower()]

        if categoria is not None:
            resultado = [
                t for t in resultado
                if str(t.categoria).strip().lower() == categoria.strip().lower()
            ]

        return resultado

    def saldo_atual(self) -> float:
        """
        Calcula o saldo atual: total de receitas menos total de despesas.

        Usa list comprehension + sum() para percorrer as transações em uma linha.
        O resultado pode ser negativo se as despesas superarem as receitas.

        Retorna:
            float com o saldo atual.
        """
        receitas = sum(t.valor for t in self._transacoes if t.tipo() == "receita")
        despesas = sum(t.valor for t in self._transacoes if t.tipo() == "despesa")
        return receitas - despesas

    # -------------------------------------------------------------------------
    # METAS
    # -------------------------------------------------------------------------

    def adicionar_meta(
        self,
        nome: str,
        valor_alvo: float,
        prazo: date,
    ) -> Meta:
        """
        Cria uma Meta de economia e a registra na lista de metas.

        Parâmetros:
            nome       (str)   : nome descritivo da meta (ex.: "Viagem")
            valor_alvo (float) : valor total que se deseja atingir
            prazo      (date)  : data limite para alcançar a meta

        Retorna:
            Objeto Meta recém-criado.

        Lança:
            ValueError se já existir uma meta com o mesmo nome.
        """
        nomes_existentes = [m.nome.lower() for m in self._metas]
        if nome.strip().lower() in nomes_existentes:
            raise ValueError(f"Já existe uma meta com o nome '{nome}'.")

        meta = Meta(nome, valor_alvo, prazo)
        self._metas.append(meta)
        return meta

    def remover_meta(self, indice: int) -> None:
        """
        Remove a meta na posição `indice` da lista (0-based).

        Parâmetros:
            indice (int): posição da meta a remover

        Lança:
            IndexError se o índice estiver fora do intervalo da lista.
        """
        if indice < 0 or indice >= len(self._metas):
            raise IndexError(f"Índice {indice} fora do intervalo.")
        del self._metas[indice]

    def listar_metas(self) -> List[Meta]:
        """Retorna cópia da lista de metas cadastradas."""
        return list(self._metas)

    def buscar_meta(self, nome: str) -> Optional[Meta]:
        """
        Busca uma meta pelo nome (case-insensitive).

        Retorna:
            Objeto Meta encontrado ou None se não existir.
        """
        for meta in self._metas:
            if meta.nome.lower() == nome.strip().lower():
                return meta
        return None

    def depositar_em_meta(self, nome: str, valor: float) -> None:
        """
        Deposita um valor em uma meta existente.

        Lança:
            ValueError se a meta não for encontrada.
        """
        meta = self.buscar_meta(nome)
        if meta is None:
            raise ValueError(f"Meta '{nome}' não encontrada.")
        meta.depositar(valor)

    def metas_concluidas(self) -> List[Meta]:
        """Retorna apenas as metas que já atingiram o valor-alvo."""
        return [m for m in self._metas if m.concluida()]

    def metas_pendentes(self) -> List[Meta]:
        """Retorna apenas as metas que ainda não atingiram o valor-alvo."""
        return [m for m in self._metas if not m.concluida()]

    # -------------------------------------------------------------------------
    # PERSISTÊNCIA (auxiliar para services/persistencia.py)
    # -------------------------------------------------------------------------

    def resumo(self) -> dict:
        """Retorna dicionário com totais gerais do sistema."""
        return {
            "total_transacoes": len(self._transacoes),
            "total_metas":      len(self._metas),
            "metas_concluidas": len(self.metas_concluidas()),
            "metas_pendentes":  len(self.metas_pendentes()),
        }

    def metas_para_salvar(self) -> List[dict]:
        """Serializa as metas para persistência em arquivo."""
        return [m.to_dict() for m in self._metas]

    def carregar_metas(self, lista_dicts: List[dict]) -> None:
        """Desserializa e carrega metas a partir de lista de dicionários."""
        self._metas = [Meta.from_dict(d) for d in lista_dicts]

def carregar_transacoes(self, lista_transacoes: list) -> None:
    """
    Carrega transações previamente persistidas de volta para a memória.
    Chamado pela view ao iniciar o app, restaurando o estado salvo em arquivo.

    Parâmetros:
        lista_transacoes (list): lista de objetos Receita e Despesa
                                 reconstruídos pela camada de persistência.
    """
    self._transacoes = list(lista_transacoes)