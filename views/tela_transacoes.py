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
        # CORREÇÃO: usa enumerate para obter o índice posicional da transação
        # na lista. Esse índice é armazenado na coluna ID da Treeview e
        # utilizado em _remover_transacao para chamar gerenciador.remover_transacao(indice).
        # O modelo Transacao não possui atributo .id, portanto a posição na
        # lista é a forma correta de identificar a transação para remoção.
        for idx, transacao in enumerate(transacoes):
            # Define o tipo (Receita ou Despesa) baseado na classe do objeto
            tipo      = "Receita" if isinstance(transacao, Receita) else "Despesa"
            # Formata o valor com 2 casas decimais
            valor_str = f"R$ {transacao.valor:.2f}"
            # Formata a data para exibição (YYYY-MM-DD)
            data_str  = transacao.data.isoformat()

            # Insere a linha na tabela
            self.tree.insert(
                "",       # Parente vazio (raiz)
                tk.END,   # Insere no final
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
        # O primeiro valor da linha é o índice posicional gravado em _atualizar_lista
        item         = self.tree.item(selecionado[0])
        id_transacao = int(item['values'][0])   # converte para int (Treeview retorna str)

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
            # CORREÇÃO: usa try/except para tratar IndexError do Gerenciador
            # em vez de checar o valor de retorno, pois remover_transacao
            # lança IndexError para índices inválidos (comportamento exigido pelos testes)
            # =================================================================
            try:
                self.gerenciador.remover_transacao(id_transacao)
                messagebox.showinfo("Sucesso", "Transação removida com sucesso!")
                self._atualizar_lista()   # Atualiza a tabela
                self._atualizar_saldo()   # Atualiza o saldo
            except IndexError:
                messagebox.showerror("Erro", "Não foi possível remover a transação!")