# 💸 Finanças Pessoais

> Sistema desktop de gerenciamento de finanças pessoais desenvolvido em Python com interface gráfica tkinter.  
> Projeto avaliativo da disciplina de **Laboratório de Programação** — Ciência da Computação, Universidade Tiradentes (UNIT).

---

## 👥 Integrantes e Responsabilidades

| # | Nome | Módulo(s) |
|---|------|-----------|
| 1 | Tarso Monteiro Alves Passos | `main.py` · `tests/test_transacao.py` · `tests/test_gerenciador.py` |
| 2 | João Gustavo Lima dos Santos | `models/transacao.py` · `models/categoria.py` |
| 3 | Vinicius Prado Sobral | `models/meta.py` · `services/gerenciador.py` |
| 4 | João Guilherme Costa Carvalho | `services/relatorio.py` · `tests/test_relatorio.py` |
| 5 | João Guilherme Teles de Souza Lopes | `services/persistencia.py` |
| 6 | Lívia Rodrigues Pinto | `views/app.py` · `views/tela_transacoes.py` |
| 7 | Alice Santos Silva | `views/tela_metas.py` · `views/tela_relatorio.py` |

---

## 📋 Descrição do Projeto

O **Finanças Pessoais** é uma aplicação desktop que permite ao usuário controlar suas receitas, despesas e metas de economia de forma simples e visual. Os dados são persistidos em um arquivo `.txt` local, sem dependência de banco de dados externo.

O projeto foi desenvolvido para demonstrar na prática os principais conceitos estudados na disciplina:

- **Modelagem orientada a objetos** com herança e encapsulamento
- **Separação de responsabilidades** em camadas (models / services / views)
- **Persistência de dados** em arquivo texto com leitura e escrita manual
- **Testes automatizados** com `pytest` cobrindo regras de negócio
- **Interface gráfica** com `tkinter` (biblioteca padrão do Python)

---

## 🗂️ Estrutura do Projeto

```
financas-pessoais-python/
├── main.py                      # Ponto de entrada — instancia e inicia a App
├── README.md
├── dados/
│   └── dados.txt                # Arquivo de persistência (criado automaticamente)
├── models/
│   ├── __init__.py
│   ├── transacao.py             # Classes base Transacao, Receita e Despesa (herança)
│   ├── categoria.py             # Classe Categoria com validação de nome
│   └── meta.py                  # Classe Meta com cálculo de progresso
├── services/
│   ├── __init__.py
│   ├── gerenciador.py           # Lógica central: adicionar, remover, calcular saldo
│   ├── relatorio.py             # Análises: totais por categoria, comparativo mensal
│   └── persistencia.py          # Salvar e carregar dados em arquivo .txt com split('|')
├── views/
│   ├── __init__.py
│   ├── app.py                   # Janela principal (notebook com abas)
│   ├── tela_transacoes.py       # Aba de receitas e despesas
│   ├── tela_metas.py            # Aba de metas com barra de progresso
│   └── tela_relatorio.py        # Aba de relatório mensal
└── tests/
    ├── test_transacao.py        # Testa criação e validação de Receita/Despesa
    ├── test_gerenciador.py      # Testa saldo, adição e remoção de transações
    └── test_relatorio.py        # Testa cálculo de totais e comparativo por categoria
```

---

## ⚙️ Funcionalidades

- ✅ Cadastro de **receitas** e **despesas** com descrição, valor, categoria e data
- ✅ Listagem e remoção de transações com atualização automática do saldo
- ✅ **Saldo atual** calculado em tempo real (receitas − despesas)
- ✅ Cadastro de **metas de economia** com valor-alvo e prazo
- ✅ Barra de progresso visual por meta
- ✅ **Relatório mensal** com total por categoria e comparativo entre meses
- ✅ Persistência automática em arquivo `.txt` local
- ✅ Testes automatizados com `pytest` nos módulos de negócio

---

## 🚀 Como Executar

### Pré-requisitos

- Python **3.10** ou superior
- `tkinter` — já incluso na instalação padrão do Python
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
| **Herança e polimorfismo** | `Receita` e `Despesa` herdam de `Transacao` |
| **Encapsulamento** | Atributos privados com `_` e métodos de acesso |
| **List comprehensions** | Filtros de transações por mês/categoria em `relatorio.py` |
| **Tratamento de exceções** | Validações de valor negativo, data inválida, arquivo inexistente |
| **Leitura/escrita de arquivos** | `open()`, `split('|')`, `write()` em `persistencia.py` |
| **Módulos e imports** | Separação em pacotes `models`, `services`, `views` |
| **`datetime`** | Conversão e filtragem de datas com `date.fromisoformat()` |
| **`os.path`** | Caminhos portáteis entre sistemas operacionais |
| **Interface gráfica** | Janelas, abas, formulários e eventos com `tkinter` |
| **Testes com `pytest`** | Casos de sucesso e falha para cada regra de negócio |

---

## 📌 Observações

- O arquivo `dados/dados.txt` é criado automaticamente na primeira execução. Não é necessário criá-lo manualmente.
- Os testes **não dependem** de arquivo em disco — usam objetos criados diretamente em memória para garantir isolamento.
- O projeto **não utiliza bibliotecas externas** além do `pytest`, tornando a execução simples em qualquer máquina com Python instalado.
