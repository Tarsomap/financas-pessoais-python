# 💸 Finanças Pessoais

> Sistema de gerenciamento de finanças pessoais desenvolvido em Python com interface interativa no terminal.  
> Projeto avaliativo da disciplina de **Laboratório de Programação** — Ciência da Computação, Universidade Tiradentes (UNIT).

---

## 👥 Integrantes e Responsabilidades

| # | Nome | Módulo(s) |
|---|------|-----------|
| 1 | Tarso Monteiro Alves Passos | `main.py` · `views/menu.py` · `tests/test_transacao.py` · `tests/test_gerenciador.py` |
| 2 | João Gustavo Lima dos Santos | `models/transacao.py` · `models/categoria.py` |
| 3 | Vinicius Prado Sobral | `models/meta.py` · `services/gerenciador.py` |
| 4 | João Guilherme Costa Carvalho | `services/relatorio.py` · `tests/test_relatorio.py` |
| 5 | João Guilherme Teles de Souza Lopes | `services/persistencia.py` |
| 6 | Lívia Rodrigues Pinto | Integração da camada de views e testes de interface |
| 7 | Alice Santos Silva | Integração da camada de views e testes de interface |

---

## 📋 Descrição do Projeto

O **Finanças Pessoais** é uma aplicação de linha de comando (CLI) que permite ao usuário controlar suas receitas, despesas e metas de economia de forma simples e organizada. Os dados são persistidos em um arquivo `.txt` local, sem dependência de banco de dados externo.

O projeto foi desenvolvido para demonstrar na prática os principais conceitos estudados na disciplina:

- **Modelagem orientada a objetos** com herança e encapsulamento
- **Separação de responsabilidades** em camadas (models / services / views)
- **Persistência de dados** em arquivo texto com leitura e escrita manual
- **Testes automatizados** com `pytest` cobrindo as regras de negócio

---

## 🗂️ Estrutura do Projeto

```text
financas-pessoais-python/
├── main.py                  # Ponto de entrada — carrega dados e inicia o menu
├── README.md
├── dados/
│   └── dados.txt            # Arquivo de persistencia (criado automaticamente)
├── models/
│   ├── __init__.py
│   ├── transacao.py         # Classes Transacao, Receita e Despesa (heranca)
│   ├── categoria.py         # Classe Categoria com validacao de nome
│   └── meta.py              # Classe Meta com calculo de progresso
├── services/
│   ├── __init__.py
│   ├── gerenciador.py       # Logica central: adicionar, remover, calcular saldo
│   ├── relatorio.py         # Analises: totais por categoria, comparativo mensal
│   └── persistencia.py      # Salvar e carregar dados em arquivo .txt
├── views/
│   └── menu.py              # Interface interativa no terminal (menus e submenus)
└── tests/
    ├── __init__.py
    ├── test_transacao.py    # Testa criacao e validacao de Receita e Despesa
    ├── test_gerenciador.py  # Testa saldo, adicao e remocao de transacoes
    └── test_relatorio.py    # Testa calculo de totais e comparativo por categoria
```

## ⚙️ Funcionalidades

- ✅ Cadastro de **receitas** e **despesas** com descrição, valor, categoria e data
- ✅ Listagem e remoção de transações com atualização automática do saldo
- ✅ **Saldo atual** calculado em tempo real (receitas − despesas)
- ✅ Filtro de transações por tipo (receita/despesa)
- ✅ Cadastro de **metas de economia** com valor-alvo e prazo
- ✅ Barra de progresso por meta no terminal
- ✅ Depósito parcial em metas existentes
- ✅ **Relatório mensal** com total por categoria e sugestões de corte
- ✅ Persistência automática em arquivo `.txt` ao encerrar
- ✅ Testes automatizados com `pytest` nos módulos de negócio

---

## 🚀 Como Executar

### Pré-requisitos

- Python **3.10** ou superior
- `pytest` — apenas para rodar os testes

```bash
pip install pytest
```

### Executar o sistema

```bash
python main.py
```

### Executar os testes

```bash
pytest tests/ -v
```

---

## 🧠 Conceitos Aplicados

| Conceito | Onde é usado |
|----------|-------------|
| **Herança e polimorfismo** | `Receita` e `Despesa` herdam de `Transacao`; `isinstance()` para distingui-las |
| **Encapsulamento** | Atributos privados com `_` em `Gerenciador` e métodos de acesso públicos |
| **List comprehensions** | Filtros de transações por tipo/categoria e cálculo de saldo em `gerenciador.py` |
| **Tratamento de exceções** | `try/except ValueError/IndexError` em validações de entrada e remoção |
| **Leitura/escrita de arquivos** | `open()`, `split('|')`, `write()` em `persistencia.py` |
| **Laços `while`** | Menus e submenus ativos até o usuário escolher sair em `views/menu.py` |
| **Funções** | Cada tela do menu é uma função separada (coesão) em `views/menu.py` |
| **`enumerate()`** | Exibição numerada de transações, metas e categorias no terminal |
| **Módulos e imports** | Separação em pacotes `models`, `services`, `views` |
| **`datetime`** | Conversão e filtragem de datas com `date.fromisoformat()` |
| **`os.path`** | Caminhos portáteis entre sistemas operacionais em `persistencia.py` |
| **Testes com `pytest`** | Fixtures, `pytest.raises` e casos de sucesso/falha por regra de negócio |

---

## 📌 Observações

- O arquivo `dados/dados.txt` é criado automaticamente na primeira execução.
- Os testes **não dependem** de arquivo em disco — usam objetos criados diretamente em memória para garantir isolamento.
- O projeto **não utiliza bibliotecas externas** além do `pytest`.
