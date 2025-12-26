import streamlit as st
import requests
import json
import os
from datetime import datetime

# =====================
# CONFIG
# =====================
st.set_page_config(page_title="NeuroCAA", layout="wide")

DATA_DIR = "data"
PACIENTES_FILE = os.path.join(DATA_DIR, "pacientes.json")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(PACIENTES_FILE):
    with open(PACIENTES_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

ARASAAC_API = "https://api.arasaac.org/api/pictograms/pt/search/"

# =====================
# MAPA SEMÂNTICO
# =====================
SEMANTIC_MAP = {
    "comer": ["comer", "comida", "almoço", "lanche", "jantar"],
    "beber": ["beber", "água", "copo", "sede", "suco"],
    "banheiro": ["banheiro", "xixi", "cocô", "vaso", "lavar mãos"],
    "dormir": ["dormir", "sono", "cama", "descansar"],
    "brincar": ["brincar", "jogar", "brinquedo"],
    "querer": ["querer", "quero", "vontade"],
    "não": ["não", "negação"],
}

# =====================
# FUNÇÕES
# =====================
def carregar_pacientes():
    with open(PACIENTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_pacientes(dados):
    with open(PACIENTES_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def buscar_pictogramas(palavra):
    termos = SEMANTIC_MAP.get(palavra, [palavra])
    resultados = []
    ids = set()

    for termo in termos:
        try:
            r = requests.get(ARASAAC_API + termo, timeout=5)
            if r.ok:
                for p in r.json()[:5]:
                    if p["_id"] not in ids:
                        ids.add(p["_id"])
                        resultados.append({
                            "id": p["_id"],
                            "url": f"https://static.arasaac.org/pictograms/{p['_id']}/{p['_id']}_300.png"
                        })
        except:
            pass

    return resultados

def gerar_prancha(frase):
    palavras = frase.lower().split()
    prancha = []

    for p in palavras:
        imgs = buscar_pictogramas(p)
        prancha.append({
            "palavra": p,
            "imagem": imgs[0]["url"] if imgs else None,
            "opcoes": imgs
        })
    return prancha

# =====================
# ESTADO
# =====================
if "paciente" not in st.session_state:
    st.session_state.paciente = None

if "prancha" not in st.session_state:
    st.session_state.prancha = []

# =====================
# SIDEBAR
# =====================
st.sidebar.title("🧠 NeuroCAA")
menu = st.sidebar.radio("Navegação", ["Pacientes", "Criar Prancha", "Histórico"])

pacientes = carregar_pacientes()

# =====================
# PACIENTES
# =====================
if menu == "Pacientes":
    st.title("👤 Cadastro de Pacientes")

    novo = st.text_input("Nome do paciente")
    if st.button("➕ Cadastrar"):
        if novo:
            pacientes[novo] = {"historico": []}
            salvar_pacientes(pacientes)
            st.success("Paciente cadastrado!")

    if pacientes:
        st.session_state.paciente = st.selectbox(
            "Selecione o paciente ativo",
            list(pacientes.keys())
        )

# =====================
# CRIAR PRANCHA
# =====================
if menu == "Criar Prancha" and st.session_state.paciente:
    st.title("🧩 Criar Prancha")

    frase = st.text_input("Digite a frase")

    if st.button("✨ Gerar prancha"):
        st.session_state.pran_
