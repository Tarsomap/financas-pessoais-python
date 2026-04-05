import json
import os

ARQUIVO = "dados.txt"

def salvar_dados(dados: dict) -> None:
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    print(f"Dados salvos em '{ARQUIVO}'.")

def carregar_dados() -> dict:
    if not os.path.exists(ARQUIVO):
        return {}
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    dados = carregar_dados()
    print("Dados carregados:", dados)

    dados["usuarios"] = dados.get("usuarios", [])
    dados["usuarios"].append({"nome": "Maria", "idade": 30})

    salvar_dados(dados)
