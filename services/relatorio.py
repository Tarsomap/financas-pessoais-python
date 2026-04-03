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
#   - @staticmethod: métodos sem acesso ao 'self' ou 'cls'
#   - isinstance(): verificar se um objeto é de uma classe específica
#   - sum() com list comprehension: somar valores filtrados
#   - Dicionários para agrupamento de dados
#   - max() com key= para encontrar o maior valor de um dicionário
#
# RESPONSÁVEL: Pessoa 4
# =============================================================================

from models import Receita, Despesa


class Relatorio:
    """
    Responsável por calcular análises e relatórios financeiros.
    Todas as funções são puras (recebem dados, retornam resultado).
    """

    @staticmethod
    def total_receitas(transacoes: list) -> float:
        """
        Soma o valor de todas as Receitas na lista.

        Args:
            transacoes: Lista de objetos Transacao.

        Returns:
            Total das receitas (0.0 se não houver nenhuma).
        """
        # TODO: Implementar usando isinstance() para filtrar só Receitas
        # Dica: sum(t.valor for t in transacoes if isinstance(t, Receita))
        pass

    @staticmethod
    def total_despesas(transacoes: list) -> float:
        """
        Soma o valor de todas as Despesas na lista.

        Returns:
            Total das despesas (0.0 se não houver nenhuma).
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
        # TODO: Implementar usando total_receitas() e total_despesas()
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
        # Dica: crie um dicionário vazio e percorra as transações
        # Para cada Despesa, some o valor na chave da categoria
        pass

    @staticmethod
    def categoria_mais_gasta(transacoes: list) -> str:
        """
        Retorna o nome da categoria com maior gasto.

        Returns:
            Nome da categoria ou 'Nenhuma' se não houver despesas.
        """
        # TODO: Implementar usando gastos_por_categoria()
        # Dica: max(gastos, key=gastos.get) retorna a chave com maior valor
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
        # Dica: use t.data.month e t.data.year como chave da tupla
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
        Uma categoria é sugerida se representa mais de limite_percentual %
        do total de despesas.

        Args:
            transacoes: Lista de transações.
            limite_percentual: Percentual acima do qual a categoria é sugerida.

        Returns:
            Lista de strings com as sugestões.
            Exemplo: ['Alimentação representa 45% dos seus gastos.']
        """
        # TODO: Implementar
        # Dica: calcule o total de despesas, depois para cada categoria
        # verifique se (gasto_categoria / total_despesas * 100) > limite_percentual
        pass
