"""
services/gerenciador.py
-----------------------
API que as views (rotas Flask) chamam para operar sobre os dados de UM usuário.

Por que usuario_id no construtor?
    Um servidor web é stateless: cada requisição é isolada e vários usuários
    o acessam ao mesmo tempo. Não dá para manter "uma lista na memória".
    O Gerenciador nasce amarrado a um usuario_id e todas as operações ficam
    escopadas a ele — a view nunca precisa saber qual usuário está logado,
    só passa o id para cá e esquece.

Por que delegar para Persistencia?
    Separação de responsabilidades: o Gerenciador sabe O QUE fazer (regra
    de negócio); a Persistencia sabe COMO guardar (SQL). Trocar de banco
    um dia não muda uma linha aqui.

Remoção por id (não por posição):
    Com banco, cada linha tem um id permanente (PRIMARY KEY). Remover por
    posição quebraria com filtros, ordenação e paginação.
"""

from datetime import date
from services.persistencia import Persistencia


class Gerenciador:
    """
    Fachada de operações financeiras de um único usuário.

    Uso típico dentro de uma rota Flask:
        g = Gerenciador(session['usuario_id'])
        g.adicionar_receita('Salário', 3000.0, 'Salário')
        saldo = g.saldo_atual()
    """

    def __init__(self, usuario_id: int):
        # Grava o dono de todas as operações deste objeto.
        # Nenhum método expõe esse id para a camada de views.
        self._usuario_id = usuario_id

    # ------------------------------------------------------------------ #
    #  TRANSAÇÕES                                                          #
    # ------------------------------------------------------------------ #

    def adicionar_receita(
        self,
        descricao: str,
        valor: float,
        categoria: str,
        data: str | None = None,
    ) -> int:
        """
        Cria e persiste uma receita para o usuário deste Gerenciador.

        Args:
            descricao : Texto livre. Ex.: 'Salário março'
            valor     : Valor positivo em reais. Ex.: 3000.0
            categoria : String de categoria. Ex.: 'Salário'
            data      : ISO 'AAAA-MM-DD'. Padrão: hoje.

        Returns:
            id gerado no banco para a transação criada.

        Raises:
            ValueError: se valor <= 0 ou descricao vazio.
        """
        self._validar_transacao(descricao, valor)
        data = data or date.today().isoformat()

        # Importação local evita importar Receita em todo lugar;
        # a Persistencia devolve objetos tipados — só precisamos do modelo
        # para montar o dict que ela espera.
        from models.transacao import Receita

        transacao = Receita(descricao, valor, categoria, data)
        return Persistencia.salvar_transacao(transacao, self._usuario_id)

    def adicionar_despesa(
        self,
        descricao: str,
        valor: float,
        categoria: str,
        data: str | None = None,
    ) -> int:
        """
        Cria e persiste uma despesa para o usuário deste Gerenciador.

        Mesmos parâmetros de adicionar_receita; tipo fica como 'despesa'.
        """
        self._validar_transacao(descricao, valor)
        data = data or date.today().isoformat()

        from models.transacao import Despesa

        transacao = Despesa(descricao, valor, categoria, data)
        return Persistencia.salvar_transacao(transacao, self._usuario_id)

    def remover_transacao(self, transacao_id: int) -> None:
        """
        Remove uma transação pelo seu id no banco.

        Por que passar usuario_id aqui também?
            Defesa em profundidade: o WHERE id = ? AND usuario_id = ?
            garante que ninguém apague o dado de outro usuário mesmo
            conhecendo o id da transação.
        """
        Persistencia.remover_transacao(transacao_id, self._usuario_id)

    def listar_transacoes(
        self,
        tipo: str | None = None,
        categoria: str | None = None,
    ) -> list:
        """
        Retorna objetos Receita/Despesa do usuário, opcionalmente filtrados.

        Args:
            tipo      : 'receita' | 'despesa' | None (todos)
            categoria : string ou None (todas)

        Returns:
            Lista de objetos Receita/Despesa ordenados por data desc.
        """
        transacoes = Persistencia.carregar_transacoes(self._usuario_id)

        if tipo:
            transacoes = [t for t in transacoes if t.tipo == tipo]
        if categoria:
            transacoes = [t for t in transacoes if t.categoria == categoria]

        return transacoes

    def saldo_atual(self) -> float:
        """
        Calcula receitas − despesas a partir do banco.

        A view chama isso sem passar usuario_id — ele fica encapsulado aqui.
        É a separação de responsabilidades funcionando: a view cuida da tela,
        o gerenciador da regra, a persistência do banco.
        """
        transacoes = Persistencia.carregar_transacoes(self._usuario_id)
        receitas = sum(t.valor for t in transacoes if t.tipo == "receita")
        despesas = sum(t.valor for t in transacoes if t.tipo == "despesa")
        return round(receitas - despesas, 2)

    # ------------------------------------------------------------------ #
    #  METAS                                                               #
    # ------------------------------------------------------------------ #

    def adicionar_meta(
        self,
        nome: str,
        valor_alvo: float,
        prazo: str | None = None,
    ) -> int:
        """
        Cria e persiste uma meta financeira.

        Args:
            nome       : Nome da meta. Ex.: 'Viagem para a praia'
            valor_alvo : Valor total a atingir. Ex.: 1500.0
            prazo      : Data ISO opcional. Ex.: '2026-12-31'

        Returns:
            id gerado no banco.

        Raises:
            ValueError: se nome vazio ou valor_alvo <= 0.
        """
        if not nome or not nome.strip():
            raise ValueError("O nome da meta não pode ser vazio.")
        if valor_alvo <= 0:
            raise ValueError("O valor-alvo da meta deve ser maior que zero.")

        from models.meta import Meta

        meta = Meta(nome.strip(), valor_alvo, prazo)
        return Persistencia.salvar_meta(meta, self._usuario_id)

    def depositar_em_meta(self, meta_id: int, valor: float) -> None:
        """
        Incrementa valor_atual de uma meta existente.

        Por que atualizar_meta é separado de salvar_meta?
            Depositar muda uma linha existente (UPDATE); criar insere uma
            nova (INSERT). São operações SQL diferentes.

        Raises:
            ValueError: se valor <= 0.
            LookupError: se a meta não existir ou não pertencer ao usuário.
        """
        if valor <= 0:
            raise ValueError("O valor do depósito deve ser maior que zero.")

        metas = Persistencia.carregar_metas(self._usuario_id)
        meta = next((m for m in metas if m.id == meta_id), None)

        if meta is None:
            raise LookupError(f"Meta {meta_id} não encontrada para este usuário.")

        # Acumula sem ultrapassar o alvo (opcional — ajuste se o grupo quiser)
        meta.valor_atual = min(meta.valor_atual + valor, meta.valor_alvo)
        Persistencia.atualizar_meta(meta, self._usuario_id)

    def listar_metas(self) -> list:
        """Retorna todos os objetos Meta do usuário."""
        return Persistencia.carregar_metas(self._usuario_id)

    def remover_meta(self, meta_id: int) -> None:
        """Remove uma meta pelo id, garantindo que pertence ao usuário."""
        Persistencia.remover_meta(meta_id, self._usuario_id)

    # ------------------------------------------------------------------ #
    #  CONTAS A PAGAR / RECEBER  (funcionalidade empresa)                  #
    # ------------------------------------------------------------------ #

    def adicionar_conta(
        self,
        tipo: str,
        descricao: str,
        valor: float,
        vencimento: str,
    ) -> int:
        """
        Cria e persiste uma conta a pagar ou receber.

        Args:
            tipo       : 'pagar' | 'receber'
            descricao  : Texto. Ex.: 'Aluguel maio'
            valor      : Valor positivo.
            vencimento : Data ISO. Ex.: '2026-06-20'

        Returns:
            id gerado no banco.

        Raises:
            ValueError: se tipo inválido, descricao vazio ou valor <= 0.
        """
        if tipo not in ("pagar", "receber"):
            raise ValueError("tipo deve ser 'pagar' ou 'receber'.")
        if not descricao or not descricao.strip():
            raise ValueError("A descrição da conta não pode ser vazia.")
        if valor <= 0:
            raise ValueError("O valor da conta deve ser maior que zero.")

        from models.conta import Conta

        conta = Conta(tipo, descricao.strip(), valor, vencimento)
        return Persistencia.salvar_conta(conta, self._usuario_id)

    def marcar_conta_paga(self, conta_id: int) -> None:
        """
        Marca uma conta como paga (pago: 0 → 1).

        Por que pago é 0/1?
            SQLite não tem tipo booleano; a convenção universal é
            0 = falso, 1 = verdadeiro.
        """
        Persistencia.marcar_conta_paga(conta_id, self._usuario_id)

    def listar_contas(self, tipo: str | None = None) -> list:
        """
        Retorna objetos Conta do usuário, opcionalmente filtrados por tipo.

        Args:
            tipo : 'pagar' | 'receber' | None (todas)
        """
        contas = Persistencia.carregar_contas(self._usuario_id)

        if tipo:
            contas = [c for c in contas if c.tipo == tipo]

        return contas

    def remover_conta(self, conta_id: int) -> None:
        """Remove uma conta pelo id, garantindo que pertence ao usuário."""
        Persistencia.remover_conta(conta_id, self._usuario_id)

    # ------------------------------------------------------------------ #
    #  HELPERS PRIVADOS                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validar_transacao(descricao: str, valor: float) -> None:
        """Validação compartilhada entre adicionar_receita e adicionar_despesa."""
        if not descricao or not descricao.strip():
            raise ValueError("A descrição da transação não pode ser vazia.")
        if valor <= 0:
            raise ValueError("O valor da transação deve ser maior que zero.")
