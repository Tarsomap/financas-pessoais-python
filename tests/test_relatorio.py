# tests/test_relatorio.py
# RESPONSÁVEL: Pessoa 4
# Execute: python -m pytest tests/test_relatorio.py -v

from datetime import date
from models.categoria import Categoria
from models.transacao import Receita, Despesa
from services.relatorio import Relatorio

# Dados usados em todos os testes
alimentacao = Categoria("Alimentação", "🍔")
transporte  = Categoria("Transporte",  "🚗")
salario     = Categoria("Salário",     "💼")

transacoes = [
    Receita("Salário",  3000.00, salario,     date(2025, 4, 1)),
    Despesa("Mercado",  1200.00, alimentacao, date(2025, 4, 5)),
    Despesa("Gasolina",  600.00, transporte,  date(2025, 4, 10)),
    # Mês anterior (março)
    Receita("Salário",  2500.00, salario,     date(2025, 3, 1)),
    Despesa("Mercado",   800.00, alimentacao, date(2025, 3, 5)),
]

rel = Relatorio(transacoes)
rel_vazio = Relatorio([])


# --- total_receitas_mes ---

def test_total_receitas():
    assert rel.total_receitas_mes(2025, 4) == 3000.00

def test_total_receitas_vazio():
    assert rel_vazio.total_receitas_mes(2025, 4) == 0.0


# --- total_despesas_mes ---

def test_total_despesas():
    assert rel.total_despesas_mes(2025, 4) == 1800.00

def test_total_despesas_vazio():
    assert rel_vazio.total_despesas_mes(2025, 4) == 0.0


# --- saldo_mes ---

def test_saldo():
    assert rel.saldo_mes(2025, 4) == 1200.00

def test_saldo_negativo():
    t = [Despesa("Aluguel", 2000.00, alimentacao, date(2025, 4, 1))]
    assert Relatorio(t).saldo_mes(2025, 4) == -2000.00


# --- gastos_por_categoria ---

def test_gastos_por_categoria():
    g = rel.gastos_por_categoria(2025, 4)
    assert g["Alimentação"] == 1200.00
    assert g["Transporte"]  == 600.00

def test_gastos_nao_inclui_receitas():
    g = rel.gastos_por_categoria(2025, 4)
    assert "Salário" not in g


# --- comparativo_mensal ---

def test_comparativo():
    c = rel.comparativo_mensal(2025, 4)
    assert c["despesa_atual"]    == 1800.00
    assert c["despesa_anterior"] == 800.00
    assert c["variacao_despesa"] == 1000.00

def test_comparativo_virada_ano():
    t = [
        Despesa("Luz", 100.00, alimentacao, date(2024, 12, 1)),
        Despesa("Luz", 150.00, alimentacao, date(2025,  1, 1)),
    ]
    c = Relatorio(t).comparativo_mensal(2025, 1)
    assert c["despesa_anterior"] == 100.00
    assert c["despesa_atual"]    == 150.00


# --- sugestoes_corte ---

def test_sugestao_categoria_pesada():
    # Alimentação = 67% do total → deve aparecer
    s = [x["categoria"] for x in rel.sugestoes_corte(2025, 4)]
    assert "Alimentação" in s

def test_sugestao_vazia():
    assert rel_vazio.sugestoes_corte(2025, 4) == []

def test_sugestao_economia_20_porcento():
    sugestoes = rel.sugestoes_corte(2025, 4)
    alim = next(x for x in sugestoes if x["categoria"] == "Alimentação")
    assert alim["economia_sugerida"] == 240.00