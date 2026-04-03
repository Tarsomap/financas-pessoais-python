from models import Receita, Despesa


class Relatorio:
    """
    Responsável por calcular análises e relatórios financeiros.
    Todas as funções recebem dados como parâmetro (funções puras — fáceis de testar).
    """

    @staticmethod
    def total_receitas(transacoes: list) -> float:
        """
        Soma o valor de todas as Receitas na lista.

        Args:
            transacoes: Lista de objetos Transacao.

        Returns:
            Total das receitas.
        """
        # TODO: Implementar usando list comprehension e isinstance()
        pass

    @staticmethod
    def total_despesas(transacoes: list) -> float:
        """
        Soma o valor de todas as Despesas na lista.

        Returns:
            Total das despesas.
        """
        # TODO: Implementar
        pass

    @staticmethod
    def saldo(transacoes: list) -> float:
        """
        Calcula o saldo: receitas - despesas.

        Returns:
            Saldo como float (pode ser negativo).
        """
        # TODO: Implementar usando total_receitas e total_despesas
        pass

    @staticmethod
    def gastos_por_categoria(transacoes: list) -> dict:
        """
        Agrupa o total gasto por categoria (apenas Despesas).

        Returns:
            Dicionário {categoria: total_gasto}.
            Exemplo: {'Alimentação': 350.0, 'Transporte': 120.0}
        """
        # TODO: Implementar
        # Dica: percorra as transacoes, filtre Despesa, some por categoria
        pass

    @staticmethod
    def categoria_mais_gasta(transacoes: list) -> str:
        """
        Retorna o nome da categoria com maior gasto.

        Returns:
            Nome da categoria ou 'Nenhuma' se não houver despesas.
        """
        # TODO: Implementar usando gastos_por_categoria()
        pass

    @staticmethod
    def transacoes_por_mes(transacoes: list) -> dict:
        """
        Agrupa transações por mês/ano.

        Returns:
            Dicionário {(ano, mes): [transacoes]}.
            Exemplo: {(2026, 3): [...], (2026, 4): [...]}
        """
        # TODO: Implementar
        pass

    @staticmethod
    def resumo_mensal(transacoes: list, mes: int, ano: int) -> dict:
        """
        Retorna resumo financeiro de um mês específico.

        Returns:
            Dicionário com:
            {
                'receitas': float,
                'despesas': float,
                'saldo': float,
                'por_categoria': dict
            }
        """
        # TODO: Implementar
        # Dica: filtre as transações pelo mês e ano, depois use os outros métodos
        pass

    @staticmethod
    def sugestao_corte(transacoes: list, limite_percentual: float = 30.0) -> list:
        """
        Sugere categorias para corte de gastos.
        Uma categoria é sugerida se representa mais de limite_percentual % do total de despesas.

        Args:
            transacoes: Lista de transações.
            limite_percentual: Percentual acima do qual a categoria é sugerida.

        Returns:
            Lista de strings com as sugestões.
            Exemplo: ['Alimentação representa 45% dos seus gastos.']
        """
        # TODO: Implementar
        pass
