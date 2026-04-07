# =============================================================================
# views/menu.py
# -----------------------------------------------------------------------------
# Interface de linha de comando (CLI) do sistema de financas pessoais.
# Substitui a interface grafica (tkinter) por um menu interativo no terminal.
#
# Este modulo e responsavel APENAS por apresentar informacoes e coletar
# dados do usuario. Toda a logica de negocio permanece no Gerenciador
# (services/gerenciador.py) -- principio de separacao de responsabilidades.
#
# CONCEITOS APLICADOS:
#   - Funcoes:            cada tela e uma funcao separada (coesao)
#   - Lacos while:        mantem o menu ativo ate o usuario sair
#   - try/except:         tratamento de entradas invalidas do usuario
#   - if/elif/else:       navegacao entre as opcoes do menu
#   - f-strings:          formatacao legivel das saidas
#   - Importacao:         uso dos modulos services e models ja implementados
#   - date.fromisoformat: converte string "AAAA-MM-DD" para objeto date
#
# RESPONSAVEL: Tarso Monteiro Alves Passos (Coordenador)
# =============================================================================

from datetime import date

from services import Gerenciador
from services.relatorio import Relatorio
from models.transacao import Receita, Despesa
from models.categoria import Categoria


# =============================================================================
# UTILITARIOS DE EXIBICAO
# =============================================================================

def _linha(char="-", tamanho=55):
    """Imprime uma linha separadora para organizar a exibicao."""
    print(char * tamanho)


def _cabecalho(titulo):
    """Imprime um cabecalho padronizado para cada secao."""
    print()
    _linha("=")
    print(f"  {titulo}")
    _linha("=")


def _listar_categorias():
    """
    Retorna a lista de categorias padrao do sistema.
    Usa o metodo estatico Categoria.listar_padroes() do model.
    """
    return [c.nome for c in Categoria.listar_padroes()]


def _escolher_categoria():
    """
    Exibe as categorias disponiveis e retorna a escolhida.
    Demonstra uso de enumerate() para exibir indice + valor.
    """
    categorias = _listar_categorias()

    print("\n  Categorias disponiveis:")
    for i, nome in enumerate(categorias, start=1):
        print(f"    [{i}] {nome}")

    while True:
        try:
            opcao = int(input("\n  Escolha uma categoria: "))
            # Verifica se o indice esta dentro do intervalo valido
            if 1 <= opcao <= len(categorias):
                return categorias[opcao - 1]
            print(f"  Aviso: Digite um numero entre 1 e {len(categorias)}.")
        except ValueError:
            # Captura quando o usuario digita algo que nao e numero
            print("  Aviso: Entrada invalida. Digite apenas o numero.")


def _ler_data(prompt="  Data (AAAA-MM-DD) [Enter = hoje]: "):
    """
    Le e valida uma data digitada pelo usuario.
    Se vazio, retorna a data de hoje (date.today()).
    Lanca ValueError se o formato for invalido -- capturado por quem chamar.
    """
    entrada = input(prompt).strip()
    if not entrada:
        return date.today()
    # fromisoformat lanca ValueError se a data nao for valida
    return date.fromisoformat(entrada)


# =============================================================================
# SUBMENU -- TRANSACOES
# =============================================================================

def _exibir_transacoes(gerenciador, tipo=None):
    """
    Lista as transacoes cadastradas, com filtro opcional por tipo.

    Parametros:
        gerenciador : instancia do Gerenciador com as transacoes
        tipo (str)  : "receita", "despesa" ou None (todas)
    """
    transacoes = gerenciador.listar_transacoes(tipo=tipo)

    if not transacoes:
        print("\n  Nenhuma transacao encontrada.")
        return

    # Imprime cabecalho da tabela com larguras fixas para alinhar as colunas
    print(f"\n  {'N':<4} {'Tipo':<10} {'Descricao':<22} {'Valor':>10}  {'Categoria':<15} {'Data'}")
    _linha()
    for i, t in enumerate(transacoes):
        tipo_str = "Receita" if isinstance(t, Receita) else "Despesa"
        print(
            f"  {i:<4} {tipo_str:<10} {t.descricao:<22} "
            f"R${t.valor:>8.2f}  {str(t.categoria):<15} {t.data}"
        )

    # Exibe o saldo no rodape da tabela
    _linha()
    saldo = gerenciador.saldo_atual()
    icone = "[+]" if saldo >= 0 else "[-]"
    print(f"  {icone} Saldo atual: R$ {saldo:.2f}")


def _adicionar_receita(gerenciador):
    """
    Coleta os dados da nova receita e chama gerenciador.adicionar_receita().
    Usa try/except para tratar erros de validacao do model Transacao.
    """
    _cabecalho("ADICIONAR RECEITA")
    try:
        descricao = input("  Descricao: ").strip()
        valor     = float(input("  Valor (R$): ").replace(",", "."))
        categoria = _escolher_categoria()
        data      = _ler_data()

        # Delega a criacao ao Gerenciador -- ele cria o objeto Receita internamente
        receita = gerenciador.adicionar_receita(descricao, valor, categoria, data)
        print(f"\n  [OK] Receita '{receita.descricao}' de R$ {receita.valor:.2f} adicionada!")

    except ValueError as e:
        # ValueError vem das validacoes do model (valor <= 0, descricao vazia, etc.)
        print(f"\n  Erro: {e}")


def _adicionar_despesa(gerenciador):
    """
    Coleta os dados da nova despesa e chama gerenciador.adicionar_despesa().
    """
    _cabecalho("ADICIONAR DESPESA")
    try:
        descricao = input("  Descricao: ").strip()
        valor     = float(input("  Valor (R$): ").replace(",", "."))
        categoria = _escolher_categoria()
        data      = _ler_data()

        despesa = gerenciador.adicionar_despesa(descricao, valor, categoria, data)
        print(f"\n  [OK] Despesa '{despesa.descricao}' de R$ {despesa.valor:.2f} adicionada!")

    except ValueError as e:
        print(f"\n  Erro: {e}")


def _remover_transacao(gerenciador):
    """
    Exibe a lista e remove a transacao escolhida pelo indice.
    Chama gerenciador.remover_transacao(indice) que lanca IndexError se invalido.
    """
    _cabecalho("REMOVER TRANSACAO")
    _exibir_transacoes(gerenciador)

    if not gerenciador.listar_transacoes():
        return

    try:
        indice    = int(input("\n  Digite o N da transacao para remover: "))
        # Confirmacao antes de remover (boa pratica de UX mesmo no terminal)
        confirmar = input(f"  Confirma remocao da transacao {indice}? (s/n): ").strip().lower()
        if confirmar == "s":
            gerenciador.remover_transacao(indice)
            print("  [OK] Transacao removida com sucesso!")
        else:
            print("  Remocao cancelada.")
    except IndexError as e:
        # IndexError lancado pelo Gerenciador quando o indice nao existe
        print(f"\n  Erro - Indice invalido: {e}")
    except ValueError:
        print("\n  Erro: Digite apenas o numero da transacao.")


def menu_transacoes(gerenciador):
    """
    Submenu de transacoes com loop while.
    Permanece ativo ate o usuario digitar '0' para voltar.
    """
    while True:
        _cabecalho("TRANSACOES")
        _exibir_transacoes(gerenciador)
        print("""
  [1] Adicionar Receita
  [2] Adicionar Despesa
  [3] Ver so Receitas
  [4] Ver so Despesas
  [5] Remover Transacao
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
            print("  Opcao invalida. Tente novamente.")


# =============================================================================
# SUBMENU -- METAS
# =============================================================================

def _exibir_metas(gerenciador):
    """
    Lista todas as metas cadastradas com barra de progresso visual.
    Demonstra uso de repeticao de string para montar a barra ("#" * n).
    """
    metas = gerenciador.listar_metas()

    if not metas:
        print("\n  Nenhuma meta cadastrada.")
        return

    print()
    for i, meta in enumerate(metas):
        # Barra de progresso: 20 blocos representam 100%
        pct       = meta.progresso_percentual()
        blocos    = int(pct / 5)          # cada bloco = 5%
        barra     = "#" * blocos + "." * (20 - blocos)
        status    = "CONCLUIDA!" if meta.concluida() else f"R$ {meta.valor_restante():.2f} restantes"
        prazo_str = meta.prazo.isoformat() if hasattr(meta.prazo, "isoformat") else str(meta.prazo)

        print(f"  [{i}] {meta.nome}")
        print(f"      Alvo: R$ {meta.valor_alvo:.2f}  |  Atual: R$ {meta.valor_atual:.2f}  |  Prazo: {prazo_str}")
        print(f"      [{barra}] {pct:.1f}%  --  {status}")
        print()


def menu_metas(gerenciador):
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
            print("  Opcao invalida.")


def _criar_meta(gerenciador):
    """Coleta dados e chama gerenciador.adicionar_meta()."""
    _cabecalho("CRIAR META")
    try:
        nome       = input("  Nome da meta (ex: Viagem, Notebook): ").strip()
        valor_alvo = float(input("  Valor alvo (R$): ").replace(",", "."))
        prazo      = _ler_data("  Prazo (AAAA-MM-DD) [Enter = sem prazo]: ")

        meta = gerenciador.adicionar_meta(nome, valor_alvo, prazo)
        print(f"\n  [OK] Meta '{meta.nome}' criada! Alvo: R$ {meta.valor_alvo:.2f}")

    except ValueError as e:
        print(f"\n  Erro: {e}")


def _depositar_meta(gerenciador):
    """Deposita um valor em uma meta existente."""
    _exibir_metas(gerenciador)
    if not gerenciador.listar_metas():
        return
    try:
        metas  = gerenciador.listar_metas()
        indice = int(input("  N da meta para depositar: "))
        if not (0 <= indice < len(metas)):
            raise IndexError("Indice fora do intervalo.")
        nome  = metas[indice].nome
        valor = float(input(f"  Valor a depositar em '{nome}' (R$): ").replace(",", "."))
        gerenciador.depositar_em_meta(nome, valor)
        meta = gerenciador.buscar_meta(nome)
        print(f"\n  [OK] Deposito realizado! Progresso: {meta.progresso_percentual():.1f}%")
    except (ValueError, IndexError) as e:
        print(f"\n  Erro: {e}")


def _remover_meta(gerenciador):
    """Remove uma meta pelo indice."""
    _exibir_metas(gerenciador)
    if not gerenciador.listar_metas():
        return
    try:
        indice    = int(input("  N da meta para remover: "))
        confirmar = input(f"  Confirma remocao da meta {indice}? (s/n): ").strip().lower()
        if confirmar == "s":
            gerenciador.remover_meta(indice)
            print("  [OK] Meta removida!")
        else:
            print("  Remocao cancelada.")
    except (IndexError, ValueError) as e:
        print(f"\n  Erro: {e}")


# =============================================================================
# SUBMENU -- RELATORIO
# =============================================================================

def menu_relatorio(gerenciador):
    """
    Exibe relatorio financeiro do mes/ano informado.
    Usa a classe Relatorio (services/relatorio.py) para os calculos.
    """
    _cabecalho("RELATORIO FINANCEIRO")

    try:
        hoje    = date.today()
        mes_str = input(f"  Mes (1-12) [Enter = {hoje.month}]: ").strip()
        ano_str = input(f"  Ano        [Enter = {hoje.year}]: ").strip()

        # Usa valor digitado ou o atual como padrao
        mes = int(mes_str) if mes_str else hoje.month
        ano = int(ano_str) if ano_str else hoje.year

        if not (1 <= mes <= 12):
            raise ValueError("Mes deve estar entre 1 e 12.")

    except ValueError as e:
        print(f"\n  Erro: {e}")
        return

    # Obtem o resumo via metodo estatico do Relatorio
    resumo = Relatorio.resumo_mensal(gerenciador, mes, ano)

    _linha("=")
    print(f"  Relatorio de {mes:02d}/{ano}")
    _linha()
    print(f"  Receitas :  R$ {resumo['receitas']:>10.2f}")
    print(f"  Despesas :  R$ {resumo['despesas']:>10.2f}")
    _linha()
    saldo = resumo["saldo"]
    icone = "[+]" if saldo >= 0 else "[-]"
    print(f"  {icone} Saldo  :  R$ {saldo:>10.2f}")

    # Gastos por categoria
    if resumo["categorias"]:
        print("\n  Gastos por categoria:")
        for cat, total in sorted(resumo["categorias"].items(), key=lambda x: x[1], reverse=True):
            print(f"     {cat:<20} R$ {total:.2f}")

    # Categoria que mais pesou no mes
    if resumo["top_categoria"]:
        nome_top, val_top = resumo["top_categoria"]
        print(f"\n  Maior gasto: {nome_top} (R$ {val_top:.2f})")

    # Sugestoes de corte geradas pelo Relatorio
    sugestoes = Relatorio.sugestao_corte(gerenciador, mes, ano)
    if sugestoes:
        print("\n  Sugestoes de corte:")
        for s in sugestoes:
            print(f"     - {s}")
    else:
        print("\n  Nenhuma categoria com gasto excessivo este mes.")

    _linha("=")
    input("\n  Pressione Enter para continuar...")


# =============================================================================
# MENU PRINCIPAL
# =============================================================================

def iniciar(gerenciador):
    """
    Ponto de entrada do menu CLI.
    Loop principal do programa -- fica ativo ate o usuario escolher sair.

    Parametros:
        gerenciador : instancia de Gerenciador ja carregada com os dados salvos
    """
    while True:
        # Exibe o saldo no topo do menu principal para referencia rapida
        saldo = gerenciador.saldo_atual()
        icone = "[+]" if saldo >= 0 else "[-]"

        print(f"""
{"=" * 55}
  FINANCAS PESSOAIS  |  {icone} Saldo: R$ {saldo:.2f}
{"=" * 55}
  [1] Transacoes  (receitas e despesas)
  [2] Metas       (objetivos de economia)
  [3] Relatorio   (resumo financeiro)
  [0] Sair        (salva e encerra)
{"=" * 55}""")

        opcao = input("  Escolha: ").strip()

        if opcao == "1":
            menu_transacoes(gerenciador)
        elif opcao == "2":
            menu_metas(gerenciador)
        elif opcao == "3":
            menu_relatorio(gerenciador)
        elif opcao == "0":
            print("\n  Salvando dados... Ate logo!\n")
            break   # Encerra o loop; main.py salva os dados apos o retorno
        else:
            print("  Opcao invalida. Digite 1, 2, 3 ou 0.")
