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
#   - Polimorfismo: adicionar_receita/despesa aceitam objeto ou parâmetros
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

    def adicionar_receita(self, descricao_ou_objeto, valor=None, categoria=None, data=None) -> Receita:
        """
        Cria uma Receita e a registra na lista de transações.

        Aceita dois modos de chamada:
          Modo 1 — separado (usado nos testes):
            adicionar_receita("Salário", 3000.0, "Salário", date(2026, 4, 1))
          Modo 2 — objeto pronto (usado pelas views):
            adicionar_receita(objeto_Receita)

        Parâmetros:
            descricao_ou_objeto : str com a descrição OU objeto Receita já criado
            valor     (float)   : valor positivo em reais (Modo 1)
            categoria (str)     : categoria da receita (Modo 1)
            data      (date)    : data da transação, padrão date.today() (Modo 1)

        Retorna:
            Objeto Receita registrado.

        Lança:
            ValueError se descrição vazia ou valor <= 0 (vem do model Transacao).
        """
        if isinstance(descricao_ou_objeto, Receita):
            # Modo 2: view já construiu o objeto, só registra
            self._transacoes.append(descricao_ou_objeto)
            return descricao_ou_objeto
        # Modo 1: constrói o objeto com os parâmetros separados
        receita = Receita(descricao_ou_objeto, valor, categoria, data)
        self._transacoes.append(receita)
        return receita

    def adicionar_despesa(self, descricao_ou_objeto, valor=None, categoria=None, data=None) -> Despesa:
        """
        Cria uma Despesa e a registra na lista de transações.

        Aceita dois modos de chamada (mesma lógica de adicionar_receita):
          Modo 1 — separado (usado nos testes):
            adicionar_despesa("Mercado", 200.0, "Alimentação", date(2026, 4, 1))
          Modo 2 — objeto pronto (usado pelas views):
            adicionar_despesa(objeto_Despesa)

        Retorna:
            Objeto Despesa registrado.

        Lança:
            ValueError se descrição vazia ou valor <= 0 (vem do model Transacao).
        """
        if isinstance(descricao_ou_objeto, Despesa):
            # Modo 2: view já construiu o objeto, só registra
            self._transacoes.append(descricao_ou_objeto)
            return descricao_ou_objeto
        # Modo 1: constrói o objeto com os parâmetros separados
        despesa = Despesa(descricao_ou_objeto, valor, categoria, data)
        self._transacoes.append(despesa)
        return despesa

    def remover_transacao(self, indice: int) -> bool:
        """
        Remove a transação na posição `indice` da lista (0-based).

        A Treeview exibe as transações com um índice sequencial (0, 1, 2...)
        que corresponde diretamente à posição na lista interna. Ao selecionar
        e remover, a view passa esse índice aqui.

        Parâmetros:
            indice (int): posição da transação a remover

        Retorna:
            True se removida com sucesso.

        Lança:
            IndexError se o índice estiver fora do intervalo da lista.
        """
        if not isinstance(indice, int) or indice < 0 or indice >= len(self._transacoes):
            raise IndexError(f"Índice {indice} fora do intervalo.")
        del self._transacoes[indice]
        return True

    def listar_transacoes(self, tipo: str = None, categoria: str = None) -> list:
        """
        Retorna todas as transações com filtros opcionais.

        Usa list comprehension para filtrar em uma linha — conceito
        de programação funcional aplicado ao Python.

        Parâmetros:
            tipo      (str, opt): "receita" ou "despesa"
            categoria (str, opt): nome exato da categoria

        Retorna:
            Lista de transações que satisfazem os filtros informados.
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

        Usa list comprehension + sum() — forma pythônica de somar valores
        de uma lista filtrada sem precisar de variável de loop explícita.

        Retorna:
            float com o saldo atual (pode ser negativo).
        """
        receitas = sum(t.valor for t in self._transacoes if t.tipo() == "receita")
        despesas = sum(t.valor for t in self._transacoes if t.tipo() == "despesa")
        return receitas - despesas

    def calcular_saldo(self) -> float:
        """
        Alias de saldo_atual() para compatibilidade com as views.
        Mantém retrocompatibilidade sem duplicar lógica.
        """
        return self.saldo_atual()

    # -------------------------------------------------------------------------
    # METAS
    # -------------------------------------------------------------------------

    def adicionar_meta(self, nome: str, valor_alvo: float, prazo) -> Meta:
        """
        Cria uma Meta de economia e a registra na lista de metas.

        Parâmetros:
            nome       (str)         : nome descritivo (ex.: "Viagem")
            valor_alvo (float)       : valor total que se deseja atingir
            prazo      (date ou str) : data limite para alcançar a meta

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

    def remover_meta(self, indice: int) -> bool:
        """
        Remove a meta na posição `indice` da lista (0-based).

        Lança:
            IndexError se o índice estiver fora do intervalo.
        """
        if indice < 0 or indice >= len(self._metas):
            raise IndexError(f"Índice {indice} fora do intervalo.")
        del self._metas[indice]
        return True

    def listar_metas(self) -> List[Meta]:
        """Retorna cópia da lista de metas cadastradas."""
        return list(self._metas)

    def buscar_meta(self, nome: str) -> Optional[Meta]:
        """
        Busca uma meta pelo nome (case-insensitive).

        Retorna:
            Objeto Meta ou None se não encontrar.
        """
        for meta in self._metas:
            if meta.nome.lower() == nome.strip().lower():
                return meta
        return None

    def depositar_em_meta(self, nome: str, valor: float) -> None:
        """Deposita um valor em uma meta existente pelo nome."""
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
    # PERSISTÊNCIA — auxiliar para services/persistencia.py e views/app.py
    # -------------------------------------------------------------------------

    def carregar_transacoes(self, lista_transacoes: list) -> None:
        """
        Carrega transações restauradas do arquivo ao iniciar o app.
        Chamado por app.py em _carregar_dados() logo após Persistencia.carregar().

        Parâmetros:
            lista_transacoes (list): objetos Receita e Despesa reconstruídos
                                     pela camada de persistência.
        """
        self._transacoes = list(lista_transacoes)

    def carregar_metas(self, lista) -> None:
        """
        Carrega metas restauradas do arquivo ao iniciar o app.
        Aceita lista de objetos Meta ou lista de dicionários (from_dict).

        Parâmetros:
            lista: lista de objetos Meta ou lista de dicts serializados.
        """
        if lista and isinstance(lista[0], dict):
            self._metas = [Meta.from_dict(d) for d in lista]
        else:
            self._metas = list(lista)

    def get_transacoes(self) -> list:
        """Retorna todas as transações — usado por app.py ao fechar para salvar."""
        return list(self._transacoes)

    def get_metas(self) -> list:
        """Retorna todas as metas — usado por app.py ao fechar para salvar."""
        return list(self._metas)

    def metas_para_salvar(self) -> List[dict]:
        """Serializa as metas para persistência em arquivo."""
        return [m.to_dict() for m in self._metas]

    def resumo(self) -> dict:
        """Retorna dicionário com totais gerais do sistema."""
        return {
            "total_transacoes": len(self._transacoes),
            "total_metas":      len(self._metas),
        }