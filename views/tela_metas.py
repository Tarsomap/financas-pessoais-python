# =============================================================================
# views/tela_metas.py
# -----------------------------------------------------------------------------
# Tela de gerenciamento de metas de economia.
#
# Exibe:
#   - Formulário para criar nova meta
#   - Cards de metas com barra de progresso (ttk.Progressbar)
#   - Status colorido: em andamento / concluída / atrasada
#   - Botão Depositar (abre janela popup tk.Toplevel)
#   - Botão Remover
#
# Conceitos demonstrados:
#   - ttk.Progressbar para visualizar progresso
#   - tk.Toplevel para janela secundária (popup)
#   - Criação dinâmica de widgets em loop
#   - lambda com argumento fixo para evitar closure incorreta:
#     command=lambda i=indice: self._depositar(i)
#     (sem o i=indice, todos os botões usariam o último valor do loop)
#
# RESPONSÁVEL: Alice
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from services import Gerenciador


class TelaMetas(tk.Frame):
    """Tela de gerenciamento de metas de economia."""

    def __init__(self, parent, gerenciador: Gerenciador):
        super().__init__(parent, bg="#1e1e2e")
        self.pack(fill=tk.BOTH, expand=True)
        self.gerenciador = gerenciador
        self._construir_ui()
        self._atualizar_lista()

    def _construir_ui(self):
        """
        Constrói a interface gráfica da tela de metas.
        Divide-se em duas áreas principais:
        1. Frame de formulário para criar novas metas
        2. Frame scrollável para exibir os cards das metas existentes
        """
        
        # =====================================================================
        # 1. FRAME DE FORMULÁRIO - Cadastro de novas metas
        # =====================================================================
        # LabelFrame cria uma borda com título - organiza visualmente o formulário
        frame_form = ttk.LabelFrame(
            self, 
            text="🎯 Criar Nova Meta", 
            padding=10
        )
        frame_form.pack(fill=tk.X, padx=10, pady=5)
        
        # Configuração de grid para o frame_form (2 colunas: label + entrada)
        # Column 0: labels, Column 1: campos de entrada, Column 2: botão
        frame_form.columnconfigure(1, weight=1)  # Coluna dos campos expande
        
        # ----- Campo: Descrição da meta -----
        # Label (rótulo) para identificar o campo
        lbl_descricao = ttk.Label(frame_form, text="Descrição:")
        lbl_descricao.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Entry (campo de texto) para o usuário digitar a descrição
        self.entry_descricao = ttk.Entry(frame_form, width=30)
        self.entry_descricao.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # ----- Campo: Valor Alvo (quanto quer economizar) -----
        lbl_valor = ttk.Label(frame_form, text="Valor Alvo (R$):")
        lbl_valor.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.entry_valor = ttk.Entry(frame_form, width=15)
        self.entry_valor.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # ----- Campo: Prazo (data limite para atingir a meta) -----
        lbl_prazo = ttk.Label(frame_form, text="Prazo (AAAA-MM-DD):")
        lbl_prazo.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.entry_prazo = ttk.Entry(frame_form, width=15)
        self.entry_prazo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Dica para o usuário sobre o formato da data
        lbl_dica = ttk.Label(
            frame_form, 
            text="💡 Exemplo: 2025-12-31", 
            foreground="gray"
        )
        lbl_dica.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # ----- Botão para criar a meta -----
        btn_criar = ttk.Button(
            frame_form, 
            text="✅ Criar Meta", 
            command=self._criar_meta
        )
        btn_criar.grid(row=0, column=2, rowspan=3, padx=20, pady=5)
        
        # =====================================================================
        # 2. FRAME DE LISTAGEM - Exibe as metas em cards com barra de progresso
        # =====================================================================
        # LabelFrame para agrupar a lista de metas
        frame_lista = ttk.LabelFrame(self, text="📋 Minhas Metas", padding=10)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Criamos um Canvas + Scrollbar para permitir rolagem
        # Isso é útil quando o usuário tem muitas metas e a tela não é grande o suficiente
        canvas = tk.Canvas(frame_lista, bg="#1e1e2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=canvas.yview)
        
        # Frame interno que conterá os cards de metas
        # Este frame será inserido dentro do Canvas
        self.frame_cards = tk.Frame(canvas, bg="#1e1e2e")
        
        # Configuração do Canvas para rolagem
        self.frame_cards.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Cria uma janela dentro do Canvas que exibe o frame_cards
        canvas.create_window((0, 0), window=self.frame_cards, anchor="nw", width=canvas.winfo_reqwidth())
        
        # Configura o Canvas para usar a scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Atualiza a largura do Canvas quando a janela é redimensionada
        def _configurar_largura_canvas(event):
            canvas.itemconfig(1, width=event.width)
        
        canvas.bind("<Configure>", _configurar_largura_canvas)
        
        # Posiciona os elementos na tela
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Variável para armazenar os cards (usada na atualização)
        self.cards = []

    def _criar_meta(self):
        """
        Cria uma nova meta a partir dos dados inseridos no formulário.
        
        Fluxo:
        1. Lê os campos: descrição, valor alvo, prazo
        2. Valida se os campos não estão vazios
        3. Converte valor para float e prazo para date
        4. Chama o gerenciador para adicionar a meta
        5. Limpa os campos e atualiza a lista na tela
        6. Exibe mensagem de sucesso ou erro
        """
        
        # Passo 1: Ler os dados dos campos de entrada
        descricao = self.entry_descricao.get().strip()
        valor_str = self.entry_valor.get().strip()
        prazo_str = self.entry_prazo.get().strip()
        
        # Passo 2: Validação - verifica se os campos estão preenchidos
        if not descricao:
            messagebox.showerror("Erro", "Por favor, digite uma descrição para a meta!")
            return
        
        if not valor_str:
            messagebox.showerror("Erro", "Por favor, digite o valor alvo!")
            return
        
        if not prazo_str:
            messagebox.showerror("Erro", "Por favor, digite o prazo da meta!")
            return
        
        # Passo 3: Conversão e validação dos tipos
        try:
            # Converte a string para float (número decimal)
            # Exemplo: "1500.50" vira 1500.50
            valor_alvo = float(valor_str)
            
            # Valida se o valor é positivo
            if valor_alvo <= 0:
                messagebox.showerror("Erro", "O valor alvo deve ser maior que zero!")
                return
                
        except ValueError:
            # Se o usuário digitou algo que não é número (ex: "abc")
            messagebox.showerror("Erro", "Digite um valor numérico válido (ex: 1500.50)!")
            return
        
        try:
            # Converte a string para objeto date usando fromisoformat
            # O formato esperado é YYYY-MM-DD (ex: 2025-12-31)
            prazo = date.fromisoformat(prazo_str)
            
        except ValueError:
            messagebox.showerror(
                "Erro", 
                "Data inválida! Use o formato AAAA-MM-DD (ex: 2025-12-31)"
            )
            return
        
        # Passo 4: Adicionar a meta através do gerenciador
        # O método adicionar_meta recebe: descrição, valor_alvo, prazo
        self.gerenciador.adicionar_meta(descricao, valor_alvo, prazo)
        
        # Passo 5: Limpar os campos do formulário
        self.entry_descricao.delete(0, tk.END)
        self.entry_valor.delete(0, tk.END)
        self.entry_prazo.delete(0, tk.END)
        
        # Passo 6: Atualizar a lista de metas na tela
        self._atualizar_lista()
        
        # Passo 7: Mensagem de confirmação
        messagebox.showinfo("Sucesso", f"Meta '{descricao}' criada com sucesso!")

    def _depositar(self, indice: int):
        """
        Abre uma janela popup para o usuário informar o valor a depositar na meta.
        
        Args:
            indice: Índice da meta na lista (posição na lista do gerenciador)
        """
        
        # Obtém a meta pelo índice
        meta = self.gerenciador.listar_metas()[indice]
        
        # =====================================================================
        # CRIAÇÃO DA JANELA POPUP (Tk.Toplevel)
        # Toplevel é uma janela secundária que fica sobre a janela principal
        # =====================================================================
        popup = tk.Toplevel(self)
        popup.title(f"Depositar - {meta.descricao}")
        popup.geometry("400x200")
        popup.resizable(False, False)
        popup.configure(bg="#1e1e2e")
        
        # Centraliza a janela popup em relação à janela principal
        popup.transient(self)  # Indica que esta janela é temporária (relacionada à principal)
        popup.grab_set()       # Impede interação com a janela principal enquanto popup estiver aberta
        
        # ----- Widgets da janela popup -----
        # Label informativo
        lbl_info = tk.Label(
            popup, 
            text=f"Meta: {meta.descricao}\n"
                 f"Valor Alvo: R$ {meta.valor_alvo:.2f}\n"
                 f"Valor Atual: R$ {meta.valor_atual:.2f}\n\n"
                 f"Quanto você quer depositar?",
            bg="#1e1e2e",
            fg="white",
            justify="left"
        )
        lbl_info.pack(pady=20)
        
        # Frame para organizar Entry e Botão
        frame_deposito = tk.Frame(popup, bg="#1e1e2e")
        frame_deposito.pack(pady=10)
        
        # Entry para o valor do depósito
        entry_valor = ttk.Entry(frame_deposito, width=15, font=("Arial", 12))
        entry_valor.pack(side="left", padx=5)
        
        # Label de exemplo
        lbl_exemplo = tk.Label(
            frame_deposito, 
            text="R$", 
            bg="#1e1e2e", 
            fg="gray",
            font=("Arial", 10)
        )
        lbl_exemplo.pack(side="left")
        
        # Função interna para processar o depósito
        def _processar_deposito():
            valor_str = entry_valor.get().strip()
            
            # Valida se o campo não está vazio
            if not valor_str:
                messagebox.showerror("Erro", "Digite um valor para depositar!")
                return
            
            try:
                # Converte para float
                valor = float(valor_str)
                
                # Valida se o valor é positivo
                if valor <= 0:
                    messagebox.showerror("Erro", "O valor do depósito deve ser positivo!")
                    return
                
                # Chama o método depositar da meta
                # IMPORTANTE: O método depositar SOMA o valor ao valor_atual
                meta.depositar(valor)
                
                # Fecha a janela popup
                popup.destroy()
                
                # Atualiza a lista de metas na tela principal
                self._atualizar_lista()
                
                # Mensagem de sucesso
                messagebox.showinfo(
                    "Sucesso", 
                    f"Depósito de R$ {valor:.2f} realizado na meta '{meta.descricao}'!"
                )
                
            except ValueError:
                messagebox.showerror("Erro", "Digite um valor numérico válido!")
        
        # Botão para confirmar o depósito
        btn_depositar = ttk.Button(popup, text="Confirmar Depósito", command=_processar_deposito)
        btn_depositar.pack(pady=10)
        
        # Botão para cancelar
        btn_cancelar = ttk.Button(popup, text="Cancelar", command=popup.destroy)
        btn_cancelar.pack(pady=5)
        
        # Coloca o foco no campo de entrada para facilitar digitação
        entry_valor.focus()

    def _remover_meta(self, indice: int):
        """
        Remove uma meta após confirmação do usuário.
        
        Args:
            indice: Índice da meta na lista (posição na lista do gerenciador)
        """
        
        # Obtém a meta para mostrar o nome na mensagem de confirmação
        meta = self.gerenciador.listar_metas()[indice]
        
        # Pergunta se o usuário realmente quer remover
        # askyesno retorna True se clicar em "Sim", False se clicar em "Não"
        if messagebox.askyesno("Confirmar", f"Deseja remover a meta '{meta.descricao}'?"):
            # Chama o gerenciador para remover a meta pelo índice
            self.gerenciador.remover_meta(indice)
            
            # Atualiza a lista na tela
            self._atualizar_lista()
            
            # Mensagem de confirmação
            messagebox.showinfo("Sucesso", "Meta removida com sucesso!")

    def _atualizar_lista(self):
        """
        Atualiza a exibição dos cards de metas.
        
        Fluxo:
        1. Destroi todos os cards existentes (limpa a tela)
        2. Obtém a lista atualizada de metas do gerenciador
        3. Para cada meta, cria um novo card com:
           - Descrição e prazo
           - Barra de progresso (ttk.Progressbar)
           - Valores atual x alvo
           - Status colorido
           - Botões Depositar e Remover
        """
        
        # Passo 1: Destruir todos os cards existentes
        # Isso evita duplicação ao atualizar a lista
        for widget in self.frame_cards.winfo_children():
            widget.destroy()
        
        # Passo 2: Obter a lista atualizada de metas do gerenciador
        metas = self.gerenciador.listar_metas()
        
        # Verifica se não há metas cadastradas
        if not metas:
            # Exibe uma mensagem informativa quando não há metas
            lbl_vazio = tk.Label(
                self.frame_cards,
                text="📭 Nenhuma meta cadastrada.\nClique em 'Criar Meta' para começar!",
                bg="#1e1e2e",
                fg="gray",
                font=("Arial", 12),
                justify="center"
            )
            lbl_vazio.pack(pady=50)
            return
        
        # Passo 3: Criar um card para cada meta
        for indice, meta in enumerate(metas):
            # =================================================================
            # CARD PRINCIPAL - Cada meta é exibida em um frame com borda
            # =================================================================
            card = tk.Frame(
                self.frame_cards,
                bg="#2a2a3e",
                relief="groove",  # Borda com efeito 3D
                bd=2
            )
            card.pack(fill=tk.X, padx=5, pady=5)
            
            # Configuração do grid dentro do card
            # Column 0: informações (descrição, progresso, valores)
            # Column 1: botões (Depositar e Remover)
            card.columnconfigure(0, weight=1)  # Coluna das informações expande
            
            # ----- INFORMAÇÕES DA META -----
            # Linha 0: Descrição da meta
            lbl_descricao = tk.Label(
                card,
                text=f"🎯 {meta.descricao}",
                bg="#2a2a3e",
                fg="white",
                font=("Arial", 11, "bold"),
                anchor="w"
            )
            lbl_descricao.grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 0))
            
            # Linha 1: Prazo da meta
            lbl_prazo = tk.Label(
                card,
                text=f"📅 Prazo: {meta.prazo.strftime('%d/%m/%Y')}",
                bg="#2a2a3e",
                fg="gray",
                font=("Arial", 9),
                anchor="w"
            )
            lbl_prazo.grid(row=1, column=0, sticky=tk.W, padx=10, pady=(0, 5))
            
            # ----- CÁLCULO DO PROGRESSO -----
            # Calcula o percentual concluído: (valor_atual / valor_alvo) * 100
            # Se valor_alvo for 0, evita divisão por zero
            if meta.valor_alvo > 0:
                percentual = (meta.valor_atual / meta.valor_alvo) * 100
                percentual = min(percentual, 100)  # Limita a no máximo 100%
            else:
                percentual = 0
            
            # ----- BARRA DE PROGRESSO (ttk.Progressbar) -----
            # mode="determinate" = barra que preenche progressivamente
            frame_progresso = tk.Frame(card, bg="#2a2a3e")
            frame_progresso.grid(row=2, column=0, sticky=tk.EW, padx=10, pady=5)
            frame_progresso.columnconfigure(0, weight=1)
            
            # Progressbar do ttk (estilo mais moderno)
            barra = ttk.Progressbar(
                frame_progresso,
                mode="determinate",
                value=percentual,
                length=200
            )
            barra.pack(side="left", fill=tk.X, expand=True, padx=(0, 10))
            
            # Label com o percentual escrito
            lbl_percentual = tk.Label(
                frame_progresso,
                text=f"{percentual:.1f}%",
                bg="#2a2a3e",
                fg="white",
                font=("Arial", 9)
            )
            lbl_percentual.pack(side="right")
            
            # ----- VALORES (Atual / Alvo) -----
            lbl_valores = tk.Label(
                card,
                text=f"💰 R$ {meta.valor_atual:.2f} / R$ {meta.valor_alvo:.2f}",
                bg="#2a2a3e",
                fg="#89b4fa",  # Azul claro
                font=("Arial", 10)
            )
            lbl_valores.grid(row=3, column=0, sticky=tk.W, padx=10, pady=(0, 5))
            
            # ----- STATUS COLORIDO -----
            # Calcula se a meta está em dia ou atrasada
            hoje = date.today()
            if percentual >= 100:
                # Meta concluída com sucesso
                status_texto = "✅ CONCLUÍDA"
                status_cor = "#a6e3a1"  # Verde claro
            elif meta.prazo < hoje:
                # Prazo venceu mas a meta não foi concluída
                status_texto = "⚠️ ATRASADA"
                status_cor = "#f38ba8"  # Vermelho
            else:
                # Em andamento e dentro do prazo
                status_texto = "🟢 EM ANDAMENTO"
                status_cor = "#a6e3a1"  # Verde
            
            lbl_status = tk.Label(
                card,
                text=status_texto,
                bg="#2a2a3e",
                fg=status_cor,
                font=("Arial", 9, "bold")
            )
            lbl_status.grid(row=4, column=0, sticky=tk.W, padx=10, pady=(0, 10))
            
            # ----- BOTÕES -----
            # Frame para agrupar os botões (coluna 1)
            frame_botoes = tk.Frame(card, bg="#2a2a3e")
            frame_botoes.grid(row=0, column=1, rowspan=5, padx=10, pady=5)
            
            # Botão Depositar
            # IMPORTANTE: Usamos lambda com i=indice para capturar o valor atual do índice
            # Sem isso, todos os botões usariam o último valor do loop (closure problem)
            btn_depositar = tk.Button(
                frame_botoes,
                text="💰 Depositar",
                bg="#89b4fa",
                fg="#1e1e2e",
                font=("Arial", 9),
                padx=10,
                command=lambda i=indice: self._depositar(i)
            )
            btn_depositar.pack(pady=2)
            
            # Botão Remover
            btn_remover = tk.Button(
                frame_botoes,
                text="🗑️ Remover",
                bg="#f38ba8",
                fg="#1e1e2e",
                font=("Arial", 9),
                padx=10,
                command=lambda i=indice: self._remover_meta(i)
            )
            btn_remover.pack(pady=2)
            
            # Armazena referência do card (opcional, para uso futuro)
            self.cards.append(card)

    def _atualizar_lista_simples(self):
        """
        Versão alternativa e mais simples do _atualizar_lista.
        Remove todos os cards e recria usando apenas texto (sem barra de progresso).
        Útil para testes ou versões mais básicas.
        """
        # Limpa todos os widgets do frame de cards
        for widget in self.frame_cards.winfo_children():
            widget.destroy()
        
        # Obtém as metas
        metas = self.gerenciador.listar_metas()
        
        if not metas:
            lbl_vazio = tk.Label(
                self.frame_cards,
                text="Nenhuma meta cadastrada.",
                bg="#1e1e2e",
                fg="gray"
            )
            lbl_vazio.pack(pady=20)
            return
        
        # Versão simplificada: apenas texto, sem barra de progresso
        for indice, meta in enumerate(metas):
            # Calcula percentual
            percentual = (meta.valor_atual / meta.valor_alvo) * 100 if meta.valor_alvo > 0 else 0
            
            # Texto com as informações
            texto = f"{indice+1}. {meta.descricao} - " \
                    f"R$ {meta.valor_atual:.2f} / R$ {meta.valor_alvo:.2f} " \
                    f"({percentual:.1f}%) - Prazo: {meta.prazo}"
            
            lbl = tk.Label(self.frame_cards, text=texto, bg="#1e1e2e", fg="white", anchor="w")
            lbl.pack(fill=tk.X, padx=10, pady=2)