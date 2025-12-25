import json
import os

ARQUIVO = "data/pacientes.json"
os.makedirs("data", exist_ok=True)

def carregar_dados():
    if not os.path.exists(ARQUIVO):
        return {}
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def adicionar_paciente(nome):
    dados = carregar_dados()
    if nome not in dados:
        dados[nome] = {"pranchas": []}
    salvar_dados(dados)

def salvar_prancha(nome, palavras):
    dados = carregar_dados()
    dados[nome]["pranchas"].append(palavras)
    salvar_dados(dados)
