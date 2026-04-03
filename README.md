# 💸 Finanças Pessoais

Sistema de gerenciamento de finanças pessoais desenvolvido em Python com interface gráfica tkinter.

## 👥 Integrantes

- (adicionar nomes do grupo)

## 📋 Descrição

Aplicação desktop para controle de receitas, despesas, metas de economia e geração de relatórios financeiros pessoais.

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10 ou superior
- tkinter (já incluso no Python)
- pytest (para rodar os testes)

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

## 🗂️ Estrutura do Projeto

```
financas_pessoais/
├── main.py                  # Ponto de entrada
├── README.md
├── dados/
│   └── dados.txt            # Persistência simples
├── models/
│   ├── __init__.py
│   ├── transacao.py         # Classes Transacao, Receita, Despesa
│   ├── categoria.py         # Classe Categoria
│   └── meta.py              # Classe Meta
├── services/
│   ├── __init__.py
│   ├── gerenciador.py       # Lógica central
│   ├── relatorio.py         # Cálculos e análises
│   └── persistencia.py      # Leitura e escrita em arquivo
├── views/
│   ├── __init__.py
│   ├── app.py               # Janela principal
│   ├── tela_transacoes.py   # Tela de receitas/despesas
│   ├── tela_metas.py        # Tela de metas
│   └── tela_relatorio.py    # Tela de relatórios
└── tests/
    ├── test_transacao.py
    ├── test_gerenciador.py
    └── test_relatorio.py
```

## ⚙️ Funcionalidades

- ✅ Cadastro de receitas e despesas com categoria e data
- ✅ Listagem e remoção de transações
- ✅ Saldo atual em tempo real
- ✅ Metas de economia com barra de progresso
- ✅ Relatório mensal com comparativo de categorias
- ✅ Persistência de dados em arquivo .txt
- ✅ Testes automatizados com pytest

## 🧠 Conceitos Utilizados

- Programação Orientada a Objetos (classes, herança, encapsulamento)
- Listas, dicionários e list comprehensions
- Tratamento de exceções
- Leitura e escrita de arquivos
- Módulos e imports
- Interface gráfica com tkinter
- Testes automatizados com pytest
