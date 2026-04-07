# =============================================================================
# views/tela_relatorio.py
# -----------------------------------------------------------------------------
# Tela de relatórios e análises financeiras.
#
# Exibe:
#   - Seletor de mês/ano
#   - Resumo: total receitas, despesas e saldo
#   - Gráfico de barras horizontal desenhado com tk.Canvas
#   - Categoria que mais gastou
#   - Sugestões automáticas de corte de gastos
#
# Como o gráfico funciona:
#   O tkinter não tem gráfico nativo, mas o Canvas permite desenhar
#   formas geométricas. Cada barra é um create_rectangle() com largura
#   proporcional ao valor da categoria:
#     largura = (valor / valor_maximo) * largura_disponivel
#
# Conceitos demonstrados:
#   - tk.Canvas com create_rectangle() e create_text()
#   - Chamada a @staticmethod da classe Relatorio
#   - f-strings com :.2f para formatar valores monetários
#
# RESPONSÁVEL: Alice
# =============================================================================

import tkinter as tk
from tkinter import ttk
from datetime import date
from services import Gerenciador, Relatorio

# Lista de cores para o gráfico - cada categoria terá uma cor diferente
# Cores no estilo Catppuccin (tema moderno e agradável)
CORES_GRAFICO = ["#89b4fa", "#a6e3a1", "#fab387", "#f38ba8",
                 "#cba6f7", "#f9e2af", "#94e2d5", "#eba0ac"]


class TelaRelatorio(tk.Frame):
    """Tela de relatórios e análises financeiras."""

    def __init__(self, parent, gerenciador: Gerenciador):
        super().__init__(parent, bg="#1e1e2e")
        self.pack(fill=tk.BOTH, expand=True)
        self.gerenciador = gerenciador
        self._construir_ui()
        self._gerar_relatorio()

    def _construir_ui(self):
        """
        Constrói a interface gráfica da tela de relatórios.
        
        Estrutura:
        1. Frame de controles (seletor de mês/ano + botão)
        2. Frame de resumo (cards com totais e categoria destaque)
        3. Canvas para desenhar o gráfico de barras
        4. Frame de sugestões (dicas para economizar)
        """
        
        # =====================================================================
        # 1. FRAME DE CONTROLES - Seleção de mês e ano
        # =====================================================================
        frame_controles = tk.Frame(self, bg="#1e1e2e")
        frame_controles.pack(fill=tk.X, padx=10, pady=10)
        
        # Label e Spinbox do MÊS
        # Spinbox permite selecionar valores de 1 a 12 (janeiro a dezembro)
        lbl_mes = tk.Label(
            frame_controles, 
            text="Mês:", 
            bg="#1e1e2e", 
            fg="white",
            font=("Arial", 10)
        )
        lbl_mes.pack(side=tk.LEFT, padx=5)
        
        # Spinbox: from_=1 (mínimo), to=12 (máximo), width=3 (largura)
        self.spin_mes = tk.Spinbox(
            frame_controles,
            from_=1,
            to=12,
            width=3,
            font=("Arial", 10),
            bg="#2a2a3e",
            fg="white",
            relief="flat"
        )
        self.spin_mes.pack(side=tk.LEFT, padx=5)
        
        # Define o mês atual como padrão
        mes_atual = date.today().month
        self.spin_mes.delete(0, tk.END)
        self.spin_mes.insert(0, str(mes_atual))
        
        # Label e Spinbox do ANO
        lbl_ano = tk.Label(
            frame_controles, 
            text="Ano:", 
            bg="#1e1e2e", 
            fg="white",
            font=("Arial", 10)
        )
        lbl_ano.pack(side=tk.LEFT, padx=5)
        
        # Spinbox para ano: de 2020 a 2030 (pode ajustar)
        ano_atual = date.today().year
        self.spin_ano = tk.Spinbox(
            frame_controles,
            from_=2020,
            to=2030,
            width=5,
            font=("Arial", 10),
            bg="#2a2a3e",
            fg="white",
            relief="flat"
        )
        self.spin_ano.pack(side=tk.LEFT, padx=5)
        self.spin_ano.delete(0, tk.END)
        self.spin_ano.insert(0, str(ano_atual))
        
        # Botão para gerar o relatório
        btn_gerar = tk.Button(
            frame_controles,
            text="📊 Gerar Relatório",
            bg="#89b4fa",
            fg="#1e1e2e",
            font=("Arial", 10, "bold"),
            padx=10,
            command=self._gerar_relatorio
        )
        btn_gerar.pack(side=tk.LEFT, padx=20)
        
        # =====================================================================
        # 2. FRAME DE RESUMO - Cards com totais e categoria destaque
        # =====================================================================
        # Frame organizado em 2 colunas
        frame_resumo = tk.Frame(self, bg="#1e1e2e")
        frame_resumo.pack(fill=tk.X, padx=10, pady=10)
        
        # Configuração das colunas (50% cada)
        frame_resumo.columnconfigure(0, weight=1)
        frame_resumo.columnconfigure(1, weight=1)
        
        # ----- Card de Receitas (lado esquerdo) -----
        card_receitas = tk.Frame(
            frame_resumo,
            bg="#2a2a3e",
            relief="groove",
            bd=1
        )
        card_receitas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Título do card
        lbl_titulo_receitas = tk.Label(
            card_receitas,
            text="💰 RECEITAS",
            bg="#2a2a3e",
            fg="#a6e3a1",  # Verde
            font=("Arial", 11, "bold")
        )
        lbl_titulo_receitas.pack(pady=(10, 5))
        
        # Valor das receitas (será atualizado dinamicamente)
        self.lbl_total_receitas = tk.Label(
            card_receitas,
            text="R$ 0,00",
            bg="#2a2a3e",
            fg="white",
            font=("Arial", 16, "bold")
        )
        self.lbl_total_receitas.pack(pady=(0, 10))
        
        # ----- Card de Despesas (lado direito) -----
        card_despesas = tk.Frame(
            frame_resumo,
            bg="#2a2a3e",
            relief="groove",
            bd=1
        )
        card_despesas.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        lbl_titulo_despesas = tk.Label(
            card_despesas,
            text="💸 DESPESAS",
            bg="#2a2a3e",
            fg="#f38ba8",  # Vermelho
            font=("Arial", 11, "bold")
        )
        lbl_titulo_despesas.pack(pady=(10, 5))
        
        self.lbl_total_despesas = tk.Label(
            card_despesas,
            text="R$ 0,00",
            bg="#2a2a3e",
            fg="white",
            font=("Arial", 16, "bold")
        )
        self.lbl_total_despesas.pack(pady=(0, 10))
        
        # ----- Linha extra para SALDO e CATEGORIA TOP (2 colunas) -----
        # Card de Saldo (esquerda)
        card_saldo = tk.Frame(
            frame_resumo,
            bg="#2a2a3e",
            relief="groove",
            bd=1
        )
        card_saldo.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        lbl_titulo_saldo = tk.Label(
            card_saldo,
            text="⚖️ SALDO",
            bg="#2a2a3e",
            fg="#89b4fa",  # Azul
            font=("Arial", 11, "bold")
        )
        lbl_titulo_saldo.pack(pady=(10, 5))
        
        self.lbl_saldo = tk.Label(
            card_saldo,
            text="R$ 0,00",
            bg="#2a2a3e",
            fg="white",
            font=("Arial", 16, "bold")
        )
        self.lbl_saldo.pack(pady=(0, 10))
        
        # Card da Categoria que mais gastou (direita)
        card_top = tk.Frame(
            frame_resumo,
            bg="#2a2a3e",
            relief="groove",
            bd=1
        )
        card_top.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        lbl_titulo_top = tk.Label(
            card_top,
            text="🏆 CATEGORIA TOP",
            bg="#2a2a3e",
            fg="#f9e2af",  # Amarelo
            font=("Arial", 11, "bold")
        )
        lbl_titulo_top.pack(pady=(10, 5))
        
        self.lbl_top_categoria = tk.Label(
            card_top,
            text="Nenhum dado",
            bg="#2a2a3e",
            fg="white",
            font=("Arial", 12)
        )
        self.lbl_top_categoria.pack(pady=(0, 10))
        
        # =====================================================================
        # 3. FRAME DO GRÁFICO (Canvas)
        # =====================================================================
        frame_grafico = tk.LabelFrame(
            self,
            text="📊 Gastos por Categoria",
            bg="#1e1e2e",
            fg="white",
            font=("Arial", 10, "bold")
        )
        frame_grafico.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas onde o gráfico será desenhado
        # bg="#181825" é um fundo escuro para contraste
        self.canvas = tk.Canvas(
            frame_grafico,
            bg="#181825",
            height=250,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # =====================================================================
        # 4. FRAME DE SUGESTÕES - Dicas para economizar
        # =====================================================================
        frame_sugestoes = tk.LabelFrame(
            self,
            text="💡 Sugestões de Corte de Gastos",
            bg="#1e1e2e",
            fg="white",
            font=("Arial", 10, "bold")
        )
        frame_sugestoes.pack(fill=tk.X, padx=10, pady=10)
        
        # Frame interno para as sugestões (será preenchido dinamicamente)
        self.frame_sugestoes_interno = tk.Frame(frame_sugestoes, bg="#1e1e2e")
        self.frame_sugestoes_interno.pack(fill=tk.X, padx=10, pady=10)
        
        # Label inicial enquanto não há dados
        self.lbl_sugestoes = tk.Label(
            self.frame_sugestoes_interno,
            text="Selecione um mês e ano para ver sugestões personalizadas",
            bg="#1e1e2e",
            fg="gray",
            font=("Arial", 10)
        )
        self.lbl_sugestoes.pack()

    def _gerar_relatorio(self):
        """
        Gera o relatório financeiro para o mês/ano selecionado.
        
        Fluxo:
        1. Lê mês e ano dos Spinboxes
        2. Chama o método estático Relatorio.resumo_mensal()
        3. Atualiza os labels com os valores calculados
        4. Chama _desenhar_grafico() para exibir o gráfico
        5. Atualiza as sugestões de corte de gastos
        """
        
        # Passo 1: Lê os valores dos Spinboxes
        try:
            mes = int(self.spin_mes.get())
            ano = int(self.spin_ano.get())
        except ValueError:
            # Se não conseguir converter (ex: campo vazio), usa valores padrão
            mes = date.today().month
            ano = date.today().year
        
        # Passo 2: Chama o método estático da classe Relatorio
        # O método resumo_mensal retorna um dicionário com:
        # - 'receitas': total de receitas
        # - 'despesas': total de despesas
        # - 'saldo': receitas - despesas
        # - 'top_categoria': (nome_categoria, valor)
        # - 'categorias': dict com totais por categoria
        resumo = Relatorio.resumo_mensal(self.gerenciador, mes, ano)
        
        # Passo 3: Atualiza os labels com os valores calculados
        # Formata os valores com 2 casas decimais (ex: R$ 1.234,56)
        total_receitas = resumo.get('receitas', 0)
        total_despesas = resumo.get('despesas', 0)
        saldo = resumo.get('saldo', 0)
        
        self.lbl_total_receitas.config(text=f"R$ {total_receitas:.2f}")
        self.lbl_total_despesas.config(text=f"R$ {total_despesas:.2f}")
        
        # Altera a cor do saldo: verde se positivo, vermelho se negativo
        cor_saldo = "#a6e3a1" if saldo >= 0 else "#f38ba8"
        self.lbl_saldo.config(text=f"R$ {saldo:.2f}", fg=cor_saldo)
        
        # Atualiza a categoria que mais gerou gastos
        top_categoria = resumo.get('top_categoria')
        if top_categoria and top_categoria[0]:
            nome_categoria, valor = top_categoria
            self.lbl_top_categoria.config(
                text=f"{nome_categoria}\nR$ {valor:.2f}",
                fg="#f9e2af"
            )
        else:
            self.lbl_top_categoria.config(text="Nenhuma despesa", fg="gray")
        
        # Passo 4: Desenha o gráfico com os dados por categoria
        dados_categorias = resumo.get('categorias', {})
        self._desenhar_grafico(dados_categorias)
        
        # Passo 5: Atualiza as sugestões de corte de gastos
        self._atualizar_sugestoes(mes, ano)

    def _atualizar_sugestoes(self, mes: int, ano: int):
        """
        Atualiza as sugestões de corte de gastos com base nos dados do mês.
        
        Args:
            mes: Mês selecionado (1-12)
            ano: Ano selecionado
        """
        # Remove os widgets antigos do frame de sugestões
        for widget in self.frame_sugestoes_interno.winfo_children():
            widget.destroy()
        
        # Gera as sugestões usando o método estático da classe Relatorio
        sugestoes = Relatorio.sugestao_corte(self.gerenciador, mes, ano)
        
        if not sugestoes:
            # Se não há sugestões, exibe mensagem informativa
            lbl_vazio = tk.Label(
                self.frame_sugestoes_interno,
                text="✅ Nenhuma sugestão de corte neste período.\nSeus gastos estão controlados!",
                bg="#1e1e2e",
                fg="#a6e3a1",
                font=("Arial", 10),
                justify="center"
            )
            lbl_vazio.pack(pady=10)
            return
        
        # Para cada sugestão, cria um card com a dica
        for i, sugestao in enumerate(sugestoes):
            # Card individual para cada sugestão
            card = tk.Frame(
                self.frame_sugestoes_interno,
                bg="#2a2a3e",
                relief="flat",
                bd=1
            )
            card.pack(fill=tk.X, pady=3)
            
            # Ícone da sugestão (alterna entre os ícones)
            icone = "🔴" if i == 0 else "🟡"
            
            # Label com o texto da sugestão
            lbl_sugestao = tk.Label(
                card,
                text=f"{icone} {sugestao}",
                bg="#2a2a3e",
                fg="#f9e2af",
                font=("Arial", 10),
                anchor="w",
                padx=10,
                pady=5
            )
            lbl_sugestao.pack(fill=tk.X)

    def _desenhar_grafico(self, dados_categorias: dict):
        """
        Desenha um gráfico de barras horizontais no Canvas.
        
        Funcionamento:
        1. Limpa o canvas atual (remove desenhos antigos)
        2. Se não há dados, exibe mensagem "Sem dados"
        3. Encontra o maior valor para usar como referência de escala
        4. Para cada categoria, calcula a largura proporcional:
           largura = (valor / valor_maximo) * largura_disponivel
        5. Desenha o retângulo (create_rectangle) e os textos
        
        Args:
            dados_categorias: Dicionário {nome_categoria: valor_total}
        """
        
        # Passo 1: Limpa o canvas (remove tudo que foi desenhado antes)
        self.canvas.delete("all")
        
        # Passo 2: Verifica se há dados
        if not dados_categorias:
            self.canvas.create_text(
                300, 100,  # Posição central aproximada
                text="📭 Nenhum dado para o período selecionado",
                fill="gray",
                font=("Arial", 12),
                anchor="center"
            )
            return
        
        # Passo 3: Encontra o maior valor para usar como escala
        # Isso garante que a barra maior ocupe quase toda a largura disponível
        valores = list(dados_categorias.values())
        valor_maximo = max(valores) if valores else 1
        
        # Configurações de layout do gráfico
        largura_total = self.canvas.winfo_width() if self.canvas.winfo_width() > 100 else 600
        x_inicio = 150  # Posição X onde as barras começam
        largura_maxima = largura_total - x_inicio - 100  # Espaço disponível para as barras
        altura_linha = 40  # Altura de cada barra (espaçamento entre categorias)
        y_inicio = 20  # Posição Y onde começa a primeira barra
        
        # Passo 4: Desenha cada barra
        for i, (categoria, valor) in enumerate(dados_categorias.items()):
            # Calcula a posição Y desta barra
            y_topo = y_inicio + i * altura_linha
            y_base = y_topo + 25  # Altura da barra (25 pixels)
            meio_y = y_topo + 12  # Posição central para o texto
            
            # Calcula a largura da barra proporcional ao valor máximo
            # Se valor_maximo == 0, usa 0 para evitar divisão por zero
            if valor_maximo > 0:
                proporcao = valor / valor_maximo
            else:
                proporcao = 0
            
            largura_barra = proporcao * largura_maxima
            x_fim = x_inicio + largura_barra
            
            # Escolhe uma cor para esta categoria (reutiliza cores se tiver mais categorias)
            cor = CORES_GRAFICO[i % len(CORES_GRAFICO)]
            
            # Desenha o retângulo da barra
            # create_rectangle(x1, y1, x2, y2, fill=cor, outline="")
            self.canvas.create_rectangle(
                x_inicio, y_topo,
                x_fim, y_base,
                fill=cor,
                outline=""
            )
            
            # Desenha o nome da categoria (alinhado à direita antes da barra)
            # anchor='e' significa que o texto termina no ponto X (alinhado à direita)
            self.canvas.create_text(
                x_inicio - 10,
                meio_y,
                text=categoria,
                fill="white",
                font=("Arial", 9),
                anchor="e"  # Alinhado à direita
            )
            
            # Desenha o valor da categoria (após a barra)
            self.canvas.create_text(
                x_fim + 10,
                meio_y,
                text=f"R$ {valor:.2f}",
                fill="white",
                font=("Arial", 9),
                anchor="w"  # Alinhado à esquerda
            )
        
        # Passo 5: Desenha linha de referência zero (eixo Y)
        self.canvas.create_line(
            x_inicio - 5, y_inicio - 5,
            x_inicio - 5, y_inicio + len(dados_categorias) * altura_linha + 20,
            fill="gray",
            width=2
        )
    
    def _desenhar_grafico_vertical(self, dados_categorias: dict):
        """
        VERSÃO ALTERNATIVA: Gráfico de barras VERTICAIS.
        
        Útil para comparar valores lado a lado de forma diferente.
        Este método não é usado por padrão, mas mantido como referência.
        """
        self.canvas.delete("all")
        
        if not dados_categorias:
            return
        
        valores = list(dados_categorias.values())
        valor_maximo = max(valores) if valores else 1
        
        largura_total = self.canvas.winfo_width() if self.canvas.winfo_width() > 100 else 600
        altura_total = 200
        largura_barra = min(60, (largura_total - 50) // len(dados_categorias))
        
        x_inicio = 40
        y_base = altura_total + 20
        
        for i, (categoria, valor) in enumerate(dados_categorias.items()):
            x_centro = x_inicio + i * (largura_barra + 10)
            altura_barra = (valor / valor_maximo) * altura_total
            
            cor = CORES_GRAFICO[i % len(CORES_GRAFICO)]
            
            self.canvas.create_rectangle(
                x_centro - largura_barra // 2,
                y_base - altura_barra,
                x_centro + largura_barra // 2,
                y_base,
                fill=cor,
                outline=""
            )
            
            self.canvas.create_text(
                x_centro,
                y_base + 15,
                text=categoria[:10],
                fill="white",
                font=("Arial", 8),
                anchor="n"
            )
            
            self.canvas.create_text(
                x_centro,
                y_base - altura_barra - 5,
                text=f"R$ {valor:.0f}",
                fill="white",
                font=("Arial", 8)
            )