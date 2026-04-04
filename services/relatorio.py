# =============================================================================
# services/relatorio.py
# -----------------------------------------------------------------------------
# Responsável por calcular análises e relatórios financeiros.
#
# Todos os métodos são @staticmethod — isso significa que não precisam
# de uma instância da classe para funcionar. Eles recebem os dados
# como parâmetro e retornam um resultado, sem modificar nenhum estado.
# Esse padrão é chamado de 'função pura' e tem uma vantagem enorme:
# é extremamente fácil de testar, porque dado o mesmo input,
# sempre retorna o mesmo output.
#
# Conceitos demonstrados neste arquivo:
#   - @staticmethod
#   - isinstance() para verificar o tipo de um objeto
#   - sum() com generator expression
#   - Dicionários para agrupamento
#   - max() com key= para encontrar maior valor
#
# RESPONSÁVEL: Jigui
# =============================================================================

from models import Receita, Despesa


class Relatorio:
    """Calcula análises e relatórios financeiros."""

    @staticmethod
    def total_receitas(transacoes: list) -> float:
        # TODO: sum(t.valor for t in transacoes if isinstance(t, Receita))
        pass

    @staticmethod
    def total_despesas(transacoes: list) -> float:
        # TODO: Implementar
        pass

    @staticmethod
    def saldo(transacoes: list) -> float:
        # TODO: Implementar usando total_receitas() e total_despesas()
        pass

    @staticmethod
    def gastos_por_categoria(transacoes: list) -> dict:
        """
        Agrupa o total gasto por categoria (apenas Despesas).
        Returns: {'Alimentação': 350.0, 'Transporte': 120.0}
        """
        # TODO: Implementar
        pass

    @staticmethod
    def categoria_mais_gasta(transacoes: list) -> str:
        """
        Retorna a categoria com maior gasto, ou 'Nenhuma' se não houver despesas.
        Dica: max(gastos, key=gastos.get)
        """
        # TODO: Implementar
        pass

    @staticmethod
    def transacoes_por_mes(transacoes: list) -> dict:
        """
        Agrupa por mês/ano.
        Returns: {(2026, 4): [...], (2026, 3): [...]}
        """
        # TODO: Implementar
        pass

    @staticmethod
    def resumo_mensal(transacoes: list, mes: int, ano: int) -> dict:
        """
        Returns: {'receitas': float, 'despesas': float, 'saldo': float, 'por_categoria': dict}
        """
        # TODO: Filtrar por mês/ano e usar os outros métodos
        pass

    @staticmethod
    def sugestao_corte(transacoes: list, limite_percentual: float = 30.0) -> list:
        """
        Sugere categorias que representam mais de limite_percentual % dos gastos.
        Returns: ['Alimentação representa 45% dos seus gastos.']
        """
        # TODO: Implementar
        pass
