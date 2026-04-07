# =============================================================================
# views/tela_transacoes.py
# -----------------------------------------------------------------------------
# Tela de gerenciamento de receitas e despesas.
# É a tela principal do sistema, exibida ao abrir o programa.
#
# Exibe:
# - Saldo atual em destaque (verde se positivo, vermelho se negativo)
# - Formulário para adicionar receita ou despesa
# - Tabela (Treeview) com todas as transações
# - Filtros por tipo e categoria
# - Botão para remover a transação selecionada
#
# Conceitos demonstrados:
# - Herança: class TelaTransacoes(tk.Frame)
# - try/except para capturar ValueError e exibir com messagebox
# - StringVar: variável reativa do tkinter ligada a widgets
# - ttk.Treeview: tabela com colunas e linhas
# - OptionMenu: lista de seleção suspensa
#
# RESPONSÁVEL: Lívia Unit Rodrigues
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from services import Gerenciador
from models import Categoria, Receita, Despesa  # Importando classes de transação


class TelaTransacoes(tk.Frame):
    """Tela de gerenciamento de receitas e despesas."""

    def __init__(self, parent, gerenciador: Gerenciador):
        """
        Construtor da tela de transações.

        Args:
            parent: Widget pai (geralmente o notebook da janela principal)
            gerenciador: Instância do GerenciadorFinanceiro que contém a lógica de negócio
        """
        super().__init__(parent, bg="#1e1e2e")  # Fundo escuro para contraste
        self.pack(fill=tk.BOTH, expand=True)    # Expande para preencher todo o espaço
        self.gerenciador = gerenciador           # Referência ao gerenciador

        # =====================================================================
        # Obtém lista de categorias padrão do sistema
        # Exemplo: ["Alimentação", "Transporte", "Moradia", "Saúde", ...]
        # =====================================================================
        self.categorias = [c.nome for c in Categoria.listar_padroes()]

        # =====================================================================
        # Variáveis de controle do formulário (usando StringVar para binding)
        # StringVar é uma variável especial do tkinter que notifica quando muda
        # =====================================================================
        self.tipo_var      = tk.StringVar(value="Receita")       # Receita ou Despesa
        self.descricao_var = tk.StringVar()                       # Descrição da transação
        self.valor_var     = tk.StringVar()                       # Valor (string para validação)
        self.categoria_var = tk.StringVar()                       # Categoria selecionada
        self.data_var      = tk.StringVar(value=str(date.today())) # Data padrão = hoje

        # =====================================================================
        # Variáveis para os filtros da tabela
        # =====================================================================
        self.filtro_tipo_var      = tk.StringVar(value="Todos")  # Todos, Receita ou Despesa
        self.filtro_categoria_var = tk.StringVar(value="Todas")  # Todas ou categoria específica

        # =====================================================================
        # Constroi a interface gráfica (chama método principal)
        # =====================================================================
        self._construir_ui()

        # =====================================================================
        # Atualiza a lista de transações (carrega dados iniciais)
        # =====================================================================
        self._atualizar_lista()

    def _construir_ui(self):
        """
        Constrói todos os componentes da interface gráfica.

        Organização vertical:
            1. Label do saldo (topo, em destaque)
            2. Frame do formulário (adicionar nova transação)
            3. Frame dos filtros (para filtrar a tabela)
            4. Treeview (tabela com as transações)
            5. Botão Remover (parte inferior)
        """
        # =====================================================================
        # 1. LABEL DO SALDO - Exibe o saldo atual com cores
        # =====================================================================
        # Frame para centralizar o saldo
        frame_saldo = tk.Frame(self, bg="#1e1e2e")
        frame_saldo.pack(fill=tk.X, pady=(10, 5))

        # Label do saldo com fonte grande e em negrito
        self.label_saldo = tk.Label(
            frame_saldo,
            text="Saldo: R$ 0,00",
            font=("Arial", 24, "bold"),
            bg="#1e1e2e",
            fg="white"
        )
        self.label_saldo.pack(pady=10)

        # =====================================================================
        # 2. FRAME DO FORMULÁRIO - Para adicionar novas transações
        # =====================================================================
        frame_form = tk.LabelFrame(
            self, text="➕ Adicionar Transação",
            font=("Arial", 12, "bold"),
            bg="#2a2a3a", fg="white",
            padx=10, pady=10
        )
        frame_form.pack(fill=tk.X, padx=10, pady=5)

        # ----- Linha 1: Tipo (Receita/Despesa) -----
        linha1 = tk.Frame(frame_form, bg="#2a2a3a")
        linha1.pack(fill=tk.X, pady=5)

        tk.Label(linha1, text="Tipo:", font=("Arial", 10), bg="#2a2a3a", fg="white").pack(side=tk.LEFT, padx=5)

        # Radiobuttons para escolher entre Receita e Despesa
        # O comando chama _atualizar_cor_formulario para mudar cor do botão
        rb_receita = tk.Radiobutton(
            linha1, text="💰 Receita",
            variable=self.tipo_var, value="Receita",
            bg="#2a2a3a", fg="white", selectcolor="#2a2a3a",
            command=self._atualizar_cor_formulario
        )
        rb_receita.pack(side=tk.LEFT, padx=10)

        rb_despesa = tk.Radiobutton(
            linha1, text="💸 Despesa",
            variable=self.tipo_var, value="Despesa",
            bg="#2a2a3a", fg="white", selectcolor="#2a2a3a",
            command=self._atualizar_cor_formulario
        )
        rb_despesa.pack(side=tk.LEFT, padx=10)

        # ----- Linha 2: Descrição e Valor -----
        linha2 = tk.Frame(frame_form, bg="#2a2a3a")
        linha2.pack(fill=tk.X, pady=5)

        tk.Label(linha2, text="Descrição:", font=("Arial", 10), bg="#2a2a3a", fg="white").pack(side=tk.LEFT, padx=5)
        entry_descricao = tk.Entry(linha2, textvariable=self.descricao_var, width=30, font=("Arial", 10))
        entry_descricao.pack(side=tk.LEFT, padx=5)

        tk.Label(linha2, text="Valor (R$):", font=("Arial", 10), bg="#2a2a3a", fg="white").pack(side=tk.LEFT, padx=5)
        entry_valor = tk.Entry(linha2, textvariable=self.valor_var, width=15, font=("Arial", 10))
        entry_valor.pack(side=tk.LEFT, padx=5)

        # ----- Linha 3: Categoria e Data -----
        linha3 = tk.Frame(frame_form, bg="#2a2a3a")
        linha3.pack(fill=tk.X, pady=5)

        tk.Label(linha3, text="Categoria:", font=("Arial", 10), bg="#2a2a3a", fg="white").pack(side=tk.LEFT, padx=5)

        # OptionMenu para selecionar categoria (lista suspensa)
        # Se não houver categorias, cria uma lista vazia
        if self.categorias:
            categoria_inicial = self.categorias[0]
        else:
            categoria_inicial = "Sem categorias"
            self.categorias = ["Sem categorias"]

        self.categoria_var.set(categoria_inicial)
        om_categoria = tk.OptionMenu(linha3, self.categoria_var, *self.categorias)
        om_categoria.config(width=20, font=("Arial", 10))
        om_categoria.pack(side=tk.LEFT, padx=5)

        tk.Label(linha3, text="Data (AAAA-MM-DD):", font=("Arial", 10), bg="#2a2a3a", fg="white").pack(side=tk.LEFT, padx=5)
        entry_data = tk.Entry(linha3, textvariable=self.data_var, width=15, font=("Arial", 10))
        entry_data.pack(side=tk.LEFT, padx=5)

        # ----- Linha 4: Botão Adicionar -----
        linha4 = tk.Frame(frame_form, bg="#2a2a3a")
        linha4.pack(fill=tk.X, pady=10)

        self.btn_adicionar = tk.Button(
            linha4,
            text="➕ Adicionar Transação",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",   # Verde para receita (padrão)
            fg="white",
            padx=20, pady=5,
            command=self._adicionar_transacao,
            cursor="hand2"  # Muda o cursor para mãozinha
        )
        self.btn_adicionar.pack()

        # =====================================================================
        # 3. FRAME DOS FILTROS - Para filtrar a tabela
        # =====================================================================
        frame_filtros = tk.LabelFrame(
            self, text="🔍 Filtros",
            font=("Arial", 11, "bold"),
            bg="#2a2a3a", fg="white",
            padx=10, pady=5
        )
        frame_filtros.pack(fill=tk.X, padx=10, pady=5)

        # Frame interno para organizar os filtros horizontalmente
        filtros_interno = tk.Frame(frame_filtros, bg="#2a2a3a")
        filtros_interno.pack()

        # Filtro por tipo
        tk.Label(filtros_interno, text="Tipo:", font=("Arial", 10), bg="#2a2a3a", fg="white").grid(row=0, column=0, padx=5, pady=5)

        # OptionMenu para filtrar por tipo (Todos, Receita, Despesa)
        opcoes_tipo = ["Todos", "Receita", "Despesa"]
        om_filtro_tipo = tk.OptionMenu(filtros_interno, self.filtro_tipo_var, *opcoes_tipo)
        om_filtro_tipo.config(width=10, font=("Arial", 10))
        om_filtro_tipo.grid(row=0, column=1, padx=5, pady=5)

        # Filtro por categoria
        tk.Label(filtros_interno, text="Categoria:", font=("Arial", 10), bg="#2a2a3a", fg="white").grid(row=0, column=2, padx=5, pady=5)

        # Lista de categorias para o filtro (inclui opção "Todas")
        opcoes_categoria = ["Todas"] + self.categorias
        om_filtro_categoria = tk.OptionMenu(filtros_interno, self.filtro_categoria_var, *opcoes_categoria)
        om_filtro_categoria.config(width=15, font=("Arial", 10))
        om_filtro_categoria.grid(row=0, column=3, padx=5, pady=5)

        # Botão para aplicar os filtros
        btn_filtrar = tk.Button(
            filtros_interno, text="🔍 Filtrar",
            font=("Arial", 9, "bold"),
            bg="#2196F3",  # Azul
            fg="white", padx=15,
            command=self._aplicar_filtro, cursor="hand2"
        )
        btn_filtrar.grid(row=0, column=4, padx=20, pady=5)

        # Botão para limpar os filtros
        btn_limpar = tk.Button(
            filtros_interno, text="🗑️ Limpar Filtros",
            font=("Arial", 9, "bold"),
            bg="#FF9800",  # Laranja
            fg="white", padx=15,
            command=self._limpar_filtros, cursor="hand2"
        )
        btn_limpar.grid(row=0, column=5, padx=5, pady=5)

        # =====================================================================
        # 4. TREEVIEW (TABELA) - Exibe as transações
        # =====================================================================
        frame_tabela = tk.LabelFrame(
            self, text="📋 Lista de Transações",
            font=("Arial", 11, "bold"),
            bg="#2a2a3a", fg="white",
            padx=10, pady=5
        )
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Frame para Treeview + Scrollbars
        frame_tree = tk.Frame(frame_tabela, bg="#2a2a3a")
        frame_tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbars para rolagem vertical e horizontal
        scroll_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL)

        # Define as colunas da tabela
        colunas = ("ID", "Tipo", "Descrição", "Valor", "Categoria", "Data")

        # Cria a Treeview (tabela)
        self.tree = ttk.Treeview(
            frame_tree,
            columns=colunas,
            show="headings",   # Mostra apenas os cabeçalhos (não mostra a coluna #0)
            height=12,
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        # Configura as scrollbars
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Define os cabeçalhos das colunas
        self.tree.heading("ID",        text="ID",         anchor="center")
        self.tree.heading("Tipo",      text="Tipo",       anchor="center")
        self.tree.heading("Descrição", text="Descrição",  anchor="w")
        self.tree.heading("Valor",     text="Valor (R$)", anchor="e")
        self.tree.heading("Categoria", text="Categoria",  anchor="w")
        self.tree.heading("Data",      text="Data",       anchor="center")

        # Define a largura e alinhamento das colunas
        self.tree.column("ID",        width=40,  anchor="center")
        self.tree.column("Tipo",      width=80,  anchor="center")
        self.tree.column("Descrição", width=250, anchor="w")
        self.tree.column("Valor",     width=100, anchor="e")
        self.tree.column("Categoria", width=120, anchor="w")
        self.tree.column("Data",      width=100, anchor="center")

        # Posiciona os widgets usando grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        # Configura o grid para expandir corretamente
        frame_tree.grid_rowconfigure(0, weight=1)
        frame_tree.grid_columnconfigure(0, weight=1)

        # =====================================================================
        # 5. BOTÃO REMOVER - Remove a transação selecionada
        # =====================================================================
        frame_botoes = tk.Frame(frame_tabela, bg="#2a2a3a")
        frame_botoes.pack(fill=tk.X, pady=10)

        self.btn_remover = tk.Button(
            frame_botoes,
            text="🗑️ Remover Transação Selecionada",
            font=("Arial", 10, "bold"),
            bg="#f44336",  # Vermelho
            fg="white",
            padx=20, pady=5,
            command=self._remover_transacao,
            cursor="hand2"
        )
        self.btn_remover.pack()

        # Label para mostrar total de transações
        self.label_total = tk.Label(
            frame_botoes, text="",
            font=("Arial", 9),
            bg="#2a2a3a", fg="#aaa"
        )
        self.label_total.pack(pady=5)

    def _atualizar_cor_formulario(self):
        """
        Atualiza a cor do botão Adicionar baseado no tipo selecionado.
        Verde para Receita, Vermelho para Despesa.
        """
        if self.tipo_var.get() == "Receita":
            self.btn_adicionar.config(bg="#4CAF50", text="➕ Adicionar Receita")
        else:
            self.btn_adicionar.config(bg="#f44336", text="💸 Adicionar Despesa")

    def _adicionar_transacao(self):
        """
        Lê os campos do formulário, valida e adiciona uma nova transação.
        Usa try/except para capturar ValueError (ex: valor negativo, data inválida).
        """
        try:
            # =================================================================
            # 1. OBTÉM OS VALORES DOS CAMPOS
            # =================================================================
            tipo       = self.tipo_var.get()
            descricao  = self.descricao_var.get().strip()
            valor_str  = self.valor_var.get().strip()
            categoria  = self.categoria_var.get()
            data_str   = self.data_var.get().strip()

            # =================================================================
            # 2. VALIDAÇÕES BÁSICAS
            # =================================================================
            # Verifica se a descrição não está vazia
            if not descricao:
                messagebox.showwarning("Campo Obrigatório", "Por favor, informe uma descrição!")
                return

            # Converte valor para float (pode lançar ValueError)
            valor = float(valor_str)

            # Verifica se o valor é positivo
            if valor <= 0:
                raise ValueError("O valor deve ser positivo!")

            # Verifica se a data está no formato correto
            # O método fromisoformat lança ValueError se a data for inválida
            data = date.fromisoformat(data_str)

            # =================================================================
            # 3. ADICIONA A TRANSAÇÃO CONFORME O TIPO
            # =================================================================
            if tipo == "Receita":
                # Cria uma nova Receita (herda de Transacao)
                nova_transacao = Receita(
                    descricao=descricao,
                    valor=valor,
                    categoria=categoria,
                    data=data
                )
                # Adiciona ao gerenciador
                self.gerenciador.adicionar_receita(nova_transacao)
                messagebox.showinfo("Sucesso", f"Receita de R$ {valor:.2f} adicionada com sucesso!")
            else:
                # Cria uma nova Despesa (herda de Transacao)
                nova_transacao = Despesa(
                    descricao=descricao,
                    valor=valor,
                    categoria=categoria,
                    data=data
                )
                # Adiciona ao gerenciador
                self.gerenciador.adicionar_despesa(nova_transacao)
                messagebox.showinfo("Sucesso", f"Despesa de R$ {valor:.2f} adicionada com sucesso!")

            # =================================================================
            # 4. LIMPA O FORMULÁRIO (MANTÉM TIPO E DATA ATUAL)
            # =================================================================
            self.descricao_var.set("")
            self.valor_var.set("")
            self.data_var.set(str(date.today()))

            # =================================================================
            # 5. ATUALIZA A INTERFACE
            # =================================================================
            self._atualizar_lista()   # Atualiza a tabela
            self._atualizar_saldo()   # Atualiza o label do saldo

        except ValueError as e:
            # Captura erros de conversão (valor não numérico, data inválida, etc.)
            messagebox.showerror("Erro de Validação", f"Erro ao adicionar transação:\n{str(e)}")
        except Exception as e:
            # Captura outros erros inesperados
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado:\n{str(e)}")

    def _remover_transacao(self):
        """
        Pega a transação selecionada na Treeview e chama o método de remoção.
        Solicita confirmação antes de remover.
        """
        # =====================================================================
        # 1. VERIFICA SE ALGO ESTÁ SELECIONADO
        # =====================================================================
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Seleção Necessária", "Por favor, selecione uma transação para remover!")
            return

        # =====================================================================
        # 2. OBTÉM O ÍNDICE DA TRANSAÇÃO SELECIONADA
        # =====================================================================
        # O primeiro valor da linha é o índice posicional gravado em _atualizar_lista.
        # CORREÇÃO: o modelo Transacao não possui atributo .id — usamos o índice
        # posicional (enumerate) em vez disso, para chamar remover_transacao(indice).
        item         = self.tree.item(selecionado[0])
        id_transacao = int(item['values'][0])  # converte para int (Treeview retorna str)

        # =====================================================================
        # 3. SOLICITA CONFIRMAÇÃO
        # =====================================================================
        descricao = item['values'][2]
        confirmar = messagebox.askyesno(
            "Confirmar Remoção",
            f"Tem certeza que deseja remover a transação:\n\n'{descricao}'?\n\nEsta ação não pode ser desfeita!"
        )

        if confirmar:
            # =================================================================
            # 4. REMOVE A TRANSAÇÃO
            # CORREÇÃO: usa try/except para tratar IndexError do Gerenciador,
            # pois remover_transacao lança IndexError para índices inválidos
            # (comportamento exigido pelos testes unitários).
            # =================================================================
            try:
                self.gerenciador.remover_transacao(id_transacao)
                messagebox.showinfo("Sucesso", "Transação removida com sucesso!")
                self._atualizar_lista()   # Atualiza a tabela
                self._atualizar_saldo()   # Atualiza o saldo
            except IndexError:
                messagebox.showerror("Erro", "Não foi possível remover a transação!")

    def _atualizar_saldo(self):
        """
        Atualiza o label do saldo com o valor atual.
        Muda a cor: verde para saldo positivo, vermelho para negativo.
        """
        saldo = self.gerenciador.calcular_saldo()
        cor = "#4CAF50" if saldo >= 0 else "#f44336"  # Verde ou vermelho
        self.label_saldo.config(text=f"💰 Saldo: R$ {saldo:.2f}", fg=cor)

    def _atualizar_lista(self):
        """
        Limpa a Treeview e a repopula com todas as transações (ou filtradas).
        Também atualiza o label do saldo e o total de transações.
        """
        # =====================================================================
        # 1. LIMPA A TABELA (remove todas as linhas existentes)
        # =====================================================================
        for item in self.tree.get_children():
            self.tree.delete(item)

        # =====================================================================
        # 2. OBTÉM AS TRANSAÇÕES (COM OU SEM FILTRO)
        # =====================================================================
        tipo_filtro      = self.filtro_tipo_var.get()
        categoria_filtro = self.filtro_categoria_var.get()

        # Chama o método de listagem do gerenciador com os filtros
        transacoes = self.gerenciador.listar_transacoes(
            tipo=None      if tipo_filtro      == "Todos"  else tipo_filtro,
            categoria=None if categoria_filtro == "Todas"  else categoria_filtro
        )

        # =====================================================================
        # 3. POPULA A TABELA COM OS DADOS
        # =====================================================================
        # CORREÇÃO: usa enumerate para obter o índice posicional de cada transação.
        # Esse índice é gravado na coluna ID da Treeview e usado em _remover_transacao
        # para chamar gerenciador.remover_transacao(indice). O modelo Transacao não
        # possui atributo .id, portanto a posição na lista é a forma correta de
        # identificar a transação para remoção.
        for idx, transacao in enumerate(transacoes):
            # Define o tipo baseado na classe do objeto (polimorfismo)
            tipo      = "Receita" if isinstance(transacao, Receita) else "Despesa"
            # Formata o valor com 2 casas decimais
            valor_str = f"R$ {transacao.valor:.2f}"
            # Formata a data para exibição (YYYY-MM-DD)
            data_str  = transacao.data.isoformat()

            # Insere a linha na tabela
            self.tree.insert(
                "",      # Parente vazio (raiz)
                tk.END,  # Insere no final
                values=(
                    idx,                   # Índice posicional (usado para remover)
                    tipo,
                    transacao.descricao,
                    valor_str,
                    transacao.categoria,
                    data_str
                )
            )

        # =====================================================================
        # 4. ATUALIZA O SALDO E O TOTAL DE TRANSAÇÕES
        # =====================================================================
        self._atualizar_saldo()
        total = len(transacoes)
        self.label_total.config(text=f"Total de transações: {total}")

        # =====================================================================
        # 5. MUDA A COR DAS LINHAS BASEADO NO TIPO (Receita verde, Despesa vermelha)
        # =====================================================================
        # Itera sobre todos os itens da tabela e aplica cor de fundo
        for i, item in enumerate(self.tree.get_children()):
            valores = self.tree.item(item)['values']
            tipo    = valores[1]
            if tipo == "Receita":
                # Linha verde bem clarinho para receitas
                self.tree.tag_configure('receita', background='#1a3a1a')
                self.tree.item(item, tags=('receita',))
            else:
                # Linha vermelha bem clarinho para despesas
                self.tree.tag_configure('despesa', background='#3a1a1a')
                self.tree.item(item, tags=('despesa',))

    def _aplicar_filtro(self):
        """
        Aplica os filtros selecionados e atualiza a tabela.
        Chama _atualizar_lista que já lê os valores dos filtros.
        """
        tipo      = self.filtro_tipo_var.get()
        categoria = self.filtro_categoria_var.get()

        # Mostra mensagem informativa sobre o filtro aplicado
        if tipo == "Todos" and categoria == "Todas":
            filtro_msg = "Nenhum filtro aplicado"
        elif tipo == "Todos":
            filtro_msg = f"Filtrando por categoria: {categoria}"
        elif categoria == "Todas":
            filtro_msg = f"Filtrando por tipo: {tipo}"
        else:
            filtro_msg = f"Filtrando por: {tipo} na categoria {categoria}"

        print(f"[DEBUG] {filtro_msg}")  # Para debug no console
        self._atualizar_lista()         # Recarrega a tabela com os filtros

        # Mostra feedback visual (opcional)
        self.label_total.config(text=f"{self.label_total.cget('text')} [Filtrado]")

    def _limpar_filtros(self):
        """
        Limpa os filtros selecionados e restaura a visualização completa.
        """
        self.filtro_tipo_var.set("Todos")
        self.filtro_categoria_var.set("Todas")
        self._atualizar_lista()
        messagebox.showinfo("Filtros Limpos", "Todos os filtros foram removidos!")