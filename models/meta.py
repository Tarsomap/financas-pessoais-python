# =============================================================================
# models/meta.py
# -----------------------------------------------------------------------------
# Define a classe Meta, que representa um objetivo financeiro com valor-alvo,
# valor acumulado e prazo opcional (ex.: "Viagem para a praia — R$ 1500 até
# dezembro de 2026").
#
# CONCEITOS APLICADOS:
#   - Encapsulamento parcial: atributos são públicos (sem prefixo _) porque
#     o Gerenciador e a Persistencia precisam acessar e modificar valor_atual
#     diretamente ao restaurar do banco. Diferente de Transacao, onde os dados
#     são imutáveis após a criação — aqui o valor_atual muda com depósitos.
#   - Validação no construtor: nome vazio ou valor_alvo negativo são barrados
#     imediatamente, garantindo que toda Meta nasce válida.
#   - Serialização (to_dict / from_dict): converte Meta ↔ dicionário para
#     facilitar a persistência. from_dict é um @classmethod (factory method)
#     que reconstrói a Meta a partir de dados salvos, incluindo o prazo que
#     pode ser date ou string.
#   - Duck typing no prazo: aceita tanto str ("Sem prazo") quanto date
#     (date(2026, 12, 31)). Usa hasattr() para decidir como converter —
#     essa flexibilidade evita quebrar quando a Persistencia envia date e
#     quando o usuário deixa o campo vazio.
#
# RESPONSÁVEL: Pessoa 3 (Vinicius Prado Sobral)
# =============================================================================

from datetime import date


class Meta:
    """
    Meta financeira com valor-alvo, progresso acumulado e prazo opcional.

    O ciclo de vida típico:
        1. Criação: Meta('Viagem', 1500.0, date(2026, 12, 31))
        2. Depósitos: meta.depositar(200.0)  — acumula até atingir o alvo
        3. Consulta: meta.progresso_percentual(), meta.concluida()
        4. Persistência: meta.to_dict() para salvar, Meta.from_dict() para carregar
    """

    def __init__(self, nome: str, valor_alvo: float, prazo="Sem prazo"):
        """
        Inicializa uma meta com validação dos dados de entrada.

        Parâmetros:
            nome      (str)         : identificador da meta (não pode ser vazio)
            valor_alvo (float)      : quantia a atingir em reais (> 0)
            prazo     (str ou date) : data limite ou "Sem prazo" se não informado

        Lança:
            ValueError se nome for vazio ou valor_alvo for zero/negativo.
        """
        # prazo aceita tanto str quanto date — duck typing intencional
        # (os testes passam date(2026, 12, 31) e a persistência usa date.fromisoformat)
        if not nome or not nome.strip():
            raise ValueError("O nome da meta não pode ser vazio.")
        if valor_alvo <= 0:
            raise ValueError("O valor-alvo da meta deve ser maior que zero.")

        self.nome = nome.strip()
        self.valor_alvo = valor_alvo
        # Sempre começa do zero; depósitos incrementam via depositar().
        # Ao restaurar do banco, a Persistencia atribui direto (meta.valor_atual = X).
        self.valor_atual = 0.0
        self.prazo = prazo

    # -------------------------------------------------------------------------
    # Operações sobre a meta
    # -------------------------------------------------------------------------

    def depositar(self, valor: float) -> None:
        """
        Acrescenta um valor ao progresso da meta.

        Usa min() para garantir que valor_atual nunca ultrapasse valor_alvo —
        se o depósito for maior que o restante, a meta simplesmente "completa"
        sem acumular excedente.

        Parâmetros:
            valor (float) : quantia a depositar (> 0)

        Lança:
            ValueError se valor for zero ou negativo.
        """
        if valor <= 0:
            raise ValueError("O valor depositado deve ser maior que zero.")
        self.valor_atual = min(self.valor_atual + valor, self.valor_alvo)

    def progresso_percentual(self) -> float:
        """
        Calcula o percentual atingido da meta (0.0 a 100.0).

        Retorna:
            float representando o progresso em porcentagem.
        """
        return (self.valor_atual / self.valor_alvo) * 100

    def valor_restante(self) -> float:
        """
        Calcula quanto ainda falta para atingir o alvo.

        Retorna:
            float com a diferença entre valor_alvo e valor_atual.
        """
        return self.valor_alvo - self.valor_atual

    def concluida(self) -> bool:
        """
        Verifica se a meta foi atingida.

        Retorna:
            True se valor_atual >= valor_alvo, False caso contrário.
        """
        return self.valor_atual >= self.valor_alvo

    # -------------------------------------------------------------------------
    # Representação e serialização
    # -------------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Representação técnica da meta, útil para debug e logs.

        __repr__ é chamado por repr(obj) e aparece no terminal interativo.
        Diferente de __str__ (para o usuário), __repr__ mostra todos os
        campos internos no formato Meta(nome=..., alvo=..., status=...).
        """
        status = "Concluída" if self.concluida() else f"{self.progresso_percentual():.1f}%"
        return (
            f"Meta(nome='{self.nome}', "
            f"alvo=R${self.valor_alvo:.2f}, "
            f"atual=R${self.valor_atual:.2f}, "
            f"prazo='{self.prazo}', "
            f"status='{status}')"
        )

    def to_dict(self) -> dict:
        """
        Serializa a meta para um dicionário com chaves padronizadas.

        Prazo pode ser date (tem .isoformat()) ou str ("Sem prazo").
        hasattr() verifica em tempo de execução qual é o caso, evitando
        chamar .isoformat() numa string — o que causaria AttributeError.

        Retorna:
            dict com chaves: nome, valor_alvo, valor_atual, prazo.
        """
        # prazo pode ser date ou str; isoformat() só existe em objetos date
        prazo_str = self.prazo.isoformat() if hasattr(self.prazo, "isoformat") else str(self.prazo)
        return {
            "nome":        self.nome,
            "valor_alvo":  self.valor_alvo,
            "valor_atual": self.valor_atual,
            "prazo":       prazo_str,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Meta":
        """
        Reconstrói uma Meta a partir de um dicionário salvo (factory method).

        Usa @classmethod para que a instância seja criada pela própria classe,
        não por código externo — centraliza a lógica de reconstrução num
        único lugar. Se o formato mudar no futuro, só este método é atualizado.

        Parâmetros:
            dados (dict) : dicionário com chaves nome, valor_alvo, valor_atual, prazo

        Retorna:
            Objeto Meta reconstituído com os valores do dicionário.
        """
        # Tenta converter prazo para date; mantém string se não for possível.
        # Isso torna o from_dict resiliente a dados antigos onde o prazo era
        # gravado como texto livre ("Sem prazo") em vez de ISO.
        prazo_raw = dados.get("prazo", "Sem prazo")
        try:
            prazo = date.fromisoformat(prazo_raw)
        except (ValueError, AttributeError, TypeError):
            prazo = prazo_raw

        meta = cls(
            nome=dados["nome"],
            valor_alvo=float(dados["valor_alvo"]),
            prazo=prazo,
        )
        # Restaura valor_atual por atribuição direta, não por depositar() —
        # depositar() valida valor > 0 e acumula incremento. Aqui estamos
        # restaurando estado salvo, não fazendo um novo depósito.
        meta.valor_atual = float(dados.get("valor_atual", 0.0))
        return meta
