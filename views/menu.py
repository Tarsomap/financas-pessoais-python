# =============================================================================
# views/menu.py
# -----------------------------------------------------------------------------
# Interface de linha de comando (CLI) do sistema de finanças pessoais.
# Substitui a interface gráfica (tkinter) por um menu interativo no terminal.
#
# Este módulo é responsável APENAS por apresentar informações e coletar
# dados do usuário. Toda a lógica de negócio permanece no Gerenciador
# (services/gerenciador.py) — princípio de separação de responsabilidades.
#
# CONCEITOS APLICADOS:
#   - Funções:           cada tela é uma função separada (coesão)
#   - Laços while:       mantêm o menu ativo até o usuário sair
#   - try/except:        tratamento de entradas inválidas do usuário
#   - if/elif/else:      navegação entre as opções do menu
#   - f-strings:         formatação legível das saídas
#   - Importação:        uso dos módulos services e models já implementados
#   - date.fromisoformat: converte string "AAAA-MM-DD" para objeto date
#
# RESPONSÁVEL: Tarso Monteiro Alves Passos (Coordenador)
# =============================================================================

from datetime import date

from services import Gerenciador
from services.relatorio import Relatorio
from models.transacao import Receita, Despesa
from models.categoria import Categoria


# =============================================================================
# UTILITÁRIOS DE EXIBIÇÃO
# =============================================================================

def _linha(char: str = "-", tamanho: int = 55) -> None:
    """Imprime uma linha separadora para organizar a exibição."""
    print(char * tamanho)


def _cabecalho(titulo: str) -> None:
    """Imprime um cabeçalho padronizado para cada seção."""
    print()
    _linha("=")
    print(f"  {titulo}")
    _linha("=")


def _listar_categorias() -> list:
    """
    Retorna a lista de categorias padrão do sistema.
    Usa o método estático Categoria.listar_padroes() do model.
    """
    return [c.nome for c in Categoria.listar_padroes()]


def _escolher_categoria() -> str:
    """
    Exibe as categorias disponíveis e retorna a escolhida.
    Demonstra uso de enumerate() para exibir índice + valor.
    """
    categorias = _listar_categorias()

    print("\n  Categorias disponíveis:")
    for i, nome in enumerate(categorias, start=1):
        print(f"    [{i}] {nome}")

    while True:
        try:
            opcao = int(input("\n  Escolha uma categoria: "))
            # Verifica se o índice está dentro do intervalo válido
            if 1 <= opcao <= len(categorias):
                return categorias[opcao - 1]
            print(f"  ⚠  Digite um número entre 1 e {len(categorias)}.")
        except ValueError:
            # Captura quando o usuário digita algo que não é número
            print("  ⚠  Entrada inválida. Digite apenas o número.")


def _ler_data(prompt: str = "  Data (AAAA-MM-DD) [Enter = hoje]: ") -> date:
    """
    Lê e valida uma data digitada pelo usuário.
    Se vazio, retorna a data de hoje (date.today()).
    Lança ValueError se o formato for inválido — capturado por quem chamar.
    """
    entrada = input(prompt).strip()
    if not entrada:
        return date.today()
    # fromisoformat lança ValueError se a data não for válida
    return date.fromisoformat(entrada)


# =============================================================================
# SUBMENU — TRANSAÇÕES
# =============================================================================

def _exibir_transacoes(gerenciador: Gerenciador, tipo: str = None) -> None:
    """
    Lista as transações cadastradas, com filtro opcional por tipo.

    Parâmetros:
        gerenciador : instância do Gerenciador com as transações
        tipo (str)  : "receita", "despesa" ou None (todas)
    """
    transacoes = gerenciador.listar_transacoes(tipo=tipo)

    if not transacoes:
        print("\n  Nenhuma transação encontrada.")
        return

    # Imprime o cabeçalho da tabela com larguras fixas para alinhar as colunas
    print(f"\n  {'Nº':<4} {'Tipo':<10} {'Descrição':<22} {'Valor':>10}  {'Categoria':<15} {'Data'}")
    _linha()
    for i, t in enumerate(transacoes):
        tipo_str = "Receita" if isinstance(t, Receita) else "Despesa"
        print(
            f"  {i:<4} {tipo_str:<10} {t.descricao:<22} "
            f"R${t.valor:>8.2f}  {str(t.categoria):<15} {t.data}"
        )

    # Exibe o saldo no rodapé da tabela
    _linha()
    saldo = gerenciador.saldo_atual()
    cor   = "✅" if saldo >= 0 else "❌"
    print(f"  {cor} Saldo atual: R$ {saldo:.2f}")


def _adicionar_receita(gerenciador: Gerenciador) -> None:
    """
    Coleta os dados da nova receita e chama gerenciador.adicionar_receita().
    Usa try/except para tratar erros de validação do model Transacao.
    """
    _cabecalho("ADICIONAR RECEITA")
    try:
        descricao = input("  Descrição: ").strip()
        valor     = float(input("  Valor (R$): ").replace(",", "."))
        categoria = _escolher_categoria()
        data      = _ler_data()

        # Delega a criação ao Gerenciador — ele cria o objeto Receita internamente
        receita = gerenciador.adicionar_receita(descricao, valor, categoria, data)
        print(f"\n  ✅ Receita '{receita.descricao}' de R$ {receita.valor:.2f} adicionada!")

    except ValueError as e:
        # ValueError vem das validações do model (valor <= 0, descrição vazia, etc.)
        print(f"\n  ⚠  Erro: {e}")


def _adicionar_despesa(gerenciador: Gerenciador) -> None:
    """
    Coleta os dados da nova despesa e chama gerenciador.adicionar_despesa().
    """
    _cabecalho("ADICIONAR DESPESA")
    try:
        descricao = input("  Descrição: ").strip()
        valor     = float(input("  Valor (R$): ").replace(",", "."))
        categoria = _escolher_categoria()
        data      = _ler_data()

        despesa = gerenciador.adicionar_despesa(descricao, valor, categoria, data)
        print(f"\n  ✅ Despesa '{despesa.descricao}' de R$ {despesa.valor:.2f} adicionada!")

    except ValueError as e:
        print(f"\n  ⚠  Erro: {e}")


def _remover_transacao(gerenciador: Gerenciador) -> None:
    """
    Exibe a lista e remove a transação escolhida pelo índice.
    Chama gerenciador.remover_transacao(indice) que lança IndexError se inválido.
    """
    _cabecalho("REMOVER TRANSAÇÃO")
    _exibir_transacoes(gerenciador)

    if not gerenciador.listar_transacoes():
        return

    try:
        indice = int(input("\n  Digite o Nº da transação para remover: "))
        # Confirmação antes de remover (boa prática de UX mesmo no terminal)
        confirmar = input(f"  Confirma remoção da transação {indice}? (s/n): ").strip().lower()
        if confirmar == "s":
            gerenciador.remover_transacao(indice)
            print("  ✅ Transação removida com sucesso!")
        else:
            print("  Remoção cancelada.")
    except IndexError as e:
        print(f"\n  ⚠  Índice inválido: {e}")
    except ValueError:
        print("\n  ⚠  Digite apenas o número da transação.")


def menu_transacoes(gerenciador: Gerenciador) -> None:
    """
    Submenu de transações com loop while.
    Permanece ativo até o usuário digitar '0' para voltar.
    """
    while True:
        _cabecalho("TRANSAÇÕES")
        _exibir_transacoes(gerenciador)
        print("""
  [1] Adicionar Receita
  [2] Adicionar Despesa
  [3] Ver só Receitas
  [4] Ver só Despesas
  [5] Remover Transação
  [0] Voltar ao menu principal""")

        opcao = input("\n  Escolha: ").strip()

        if opcao == "1":
            _adicionar_receita(gerenciador)
        elif opcao == "2":
            _adicionar_despesa(gerenciador)
        elif opcao == "3":
            _cabecalho("RECEITAS")
            _exibir_transacoes(gerenciador, tipo="receita")
            input("\n  Pressione Enter para continuar...")
        elif opcao == "4":
            _cabecalho("DESPESAS")
            _exibir_transacoes(gerenciador, tipo="despesa")
            input("\n  Pressione Enter para continuar...")
        elif opcao == "5":
            _remover_transacao(gerenciador)
        elif opcao == "0":
            break   # Sai do while e volta ao menu principal
        else:
            print("  ⚠  Opção inválida. Tente novamente.")


# =============================================================================
# SUBMENU — METAS
# =============================================================================

def _exibir_metas(gerenciador: Gerenciador) -> None:
    """
    Lista todas as metas cadastradas com barra de progresso visual.
    Demonstra uso de string repetition para a barra ("█" * n).
    """
    metas = gerenciador.listar_metas()

    if not metas:
        print("\n  Nenhuma meta cadastrada.")
        return

    print()
    for i, meta in enumerate(metas):
        # Barra de progresso: 20 blocos representam 100%
        pct        = meta.progresso_percentual()
        blocos     = int(pct / 5)          # cada bloco = 5%
        barra      = "█" * blocos + "░" * (20 - blocos)
        status     = "✅ Concluída!" if meta.concluida() else f"R$ {meta.valor_restante():.2f} restantes"
        prazo_str  = meta.prazo.isoformat() if hasattr(meta.prazo, "isoformat") else str(meta.prazo)

        print(f"  [{i}] {meta.nome}")
        print(f"      Alvo: R$ {meta.valor_alvo:.2f}  |  Atual: R$ {meta.valor_atual:.2f}  |  Prazo: {prazo_str}")
        print(f"      [{barra}] {pct:.1f}%  —  {status}")
        print()


def menu_metas(gerenciador: Gerenciador) -> None:
    """Submenu de metas de economia."""
    while True:
        _cabecalho("METAS DE ECONOMIA")
        _exibir_metas(gerenciador)
        print("""  [1] Criar nova meta
  [2] Depositar em uma meta
  [3] Remover meta
  [0] Voltar""")

        opcao = input("\n  Escolha: ").strip()

        if opcao == "1":
            _criar_meta(gerenciador)
        elif opcao == "2":
            _depositar_meta(gerenciador)
        elif opcao == "3":
            _remover_meta(gerenciador)
        elif opcao == "0":
            break
        else:
            print("  ⚠  Opção inválida.")


def _criar_meta(gerenciador: Gerenciador) -> None:
    """Coleta dados e chama gerenciador.adicionar_meta()."""
    _cabecalho("CRIAR META")
    try:
        nome       = input("  Nome da meta (ex: Viagem, Notebook): ").strip()
        valor_alvo = float(input("  Valor alvo (R$): ").replace(",", "."))
        prazo      = _ler_data("  Prazo (AAAA-MM-DD) [Enter = sem prazo]: ")

        meta = gerenciador.adicionar_meta(nome, valor_alvo, prazo)
        print(f"\n  ✅ Meta '{meta.nome}' criada! Alvo: R$ {meta.valor_alvo:.2f}")

    except ValueError as e:
        print(f"\n  ⚠  Erro: {e}")


def _depositar_meta(gerenciador: Gerenciador) -> None:
    """Deposita um valor em uma meta existente."""
    _exibir_metas(gerenciador)
    if not gerenciador.listar_metas():
        return
    try:
        metas  = gerenciador.listar_metas()
        indice = int(input("  Nº da meta para depositar: "))
        if not (0 <= indice < len(metas)):
            raise IndexError("Índice fora do intervalo.")
        nome  = metas[indice].nome
        valor = float(input(f"  Valor a depositar em '{nome}' (R$): ").replace(",", "."))
        gerenciador.depositar_em_meta(nome, valor)
        meta = gerenciador.buscar_meta(nome)
        print(f"\n  ✅ Depósito realizado! Progresso: {meta.progresso_percentual():.1f}%")
    except (ValueError, IndexError) as e:
        print(f"\n  ⚠  Erro: {e}")


def _remover_meta(gerenciador: Gerenciador) -> None:
    """Remove uma meta pelo índice."""
    _exibir_metas(gerenciador)
    if not gerenciador.listar_metas():
        return
    try:
        indice    = int(input("  Nº da meta para remover: "))
        confirmar = input(f"  Confirma remoção da meta {indice}? (s/n): ").strip().lower()
        if confirmar == "s":
            gerenciador.remover_meta(indice)
            print("  ✅ Meta removida!")
        else:
            print("  Remoção cancelada.")
    except (IndexError, ValueError) as e:
        print(f"\n  ⚠  Erro: {e}")


# =============================================================================
# SUBMENU — RELATÓRIO
# =============================================================================

def menu_relatorio(gerenciador: Gerenciador) -> None:
    """
    Exibe relatório financeiro do mês/ano informado.
    Usa a classe Relatorio (services/relatorio.py) para os cálculos.
    """
    _cabecalho("RELATÓRIO FINANCEIRO")

    try:
        hoje = date.today()
        mes_str = input(f"  Mês (1-12) [Enter = {hoje.month}]: ").strip()
        ano_str = input(f"  Ano       [Enter = {hoje.year}]: ").strip()

        # Usa valor digitado ou o atual como padrão
        mes = int(mes_str) if mes_str else hoje.month
        ano = int(ano_str) if ano_str else hoje.year

        if not (1 <= mes <= 12):
            raise ValueError("Mês deve estar entre 1 e 12.")

    except ValueError as e:
        print(f"\n  ⚠  {e}")
        return

    # Obtém o resumo via método estático do Relatorio
    resumo = Relatorio.resumo_mensal(gerenciador, mes, ano)

    _linha("=")
    print(f"  📅 Relatório de {mes:02d}/{ano}")
    _linha()
    print(f"  💰 Receitas:  R$ {resumo['receitas']:>10.2f}")
    print(f"  💸 Despesas:  R$ {resumo['despesas']:>10.2f}")
    _linha()
    saldo = resumo["saldo"]
    icone = "✅" if saldo >= 0 else "❌"
    print(f"  {icone} Saldo:     R$ {saldo:>10.2f}")

    # Gastos por categoria
    if resumo["categorias"]:
        print("\n  📊 Gastos por categoria:")
        for cat, total in sorted(resumo["categorias"].items(), key=lambda x: x[1], reverse=True):
            print(f"     {cat:<20} R$ {total:.2f}")

    # Categoria que mais pesou
    if resumo["top_categoria"]:
        nome_top, val_top = resumo["top_categoria"]
        print(f"\n  🏆 Maior gasto: {nome_top} (R$ {val_top:.2f})")

    # Sugestões de corte
    sugestoes = Relatorio.sugestao_corte(gerenciador, mes, ano)
    if sugestoes:
        print("\n  💡 Sugestões de corte:")
        for s in sugestoes:
            print(f"     • {s}")
    else:
        print("\n  💡 Nenhuma categoria com gasto excessivo este mês.")

    _linha("=")
    input("\n  Pressione Enter para continuar...")


# =============================================================================
# MENU PRINCIPAL
# =============================================================================

def iniciar(gerenciador: Gerenciador) -> None:
    """
    Ponto de entrada do menu CLI.
    Loop principal do programa — fica ativo até o usuário escolher sair.

    Parâmetros:
        gerenciador : instância de Gerenciador já carregada com os dados salvos
    """
    while True:
        # Exibe o saldo no topo do menu principal para referência rápida
        saldo = gerenciador.saldo_atual()
        icone = "✅" if saldo >= 0 else "❌"

        print(f"""
{'=' * 55}
  💸  FINANÇAS PESSOAIS  |  {icone} Saldo: R$ {saldo:.2f}
{'=' * 55}
  [1] Transações  (receitas e despesas)
  [2] Metas       (objetivos de economia)
  [3] Relatório   (resumo financeiro)
  [0] Sair        (salva e encerra)
{'=' * 55}""")

        opcao = input("  Escolha: ").strip()

        if opcao == "1":
            menu_transacoes(gerenciador)
        elif opcao == "2":
            menu_metas(gerenciador)
        elif opcao == "3":
            menu_relatorio(gerenciador)
        elif opcao == "0":
            print("\n  Salvando dados... Até logo! 👋\n")
            break   # Encerra o loop; main.py salva os dados após o retorno
        else:
            print("  ⚠  Opção inválida. Digite 1, 2, 3 ou 0.")