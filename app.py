import streamlit as st
import json
import os
import requests
from datetime import datetime

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="🧠 NeuroCAA", layout="wide")

DATA_PATH = "data/pacientes.json"
ARASAAC_SEARCH = "https://api.arasaac.org/api/pictograms/pt/search/"

COLUNAS_PRANCHA = 4

# ======================
# DADOS
# ======================
def carregar_dados():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados():
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(pacientes, f, ensure_ascii=False, indent=2)

# ======================
# ARASAAC
# ======================
def buscar_opcoes_arasaac(palavra):
    try:
        r = requests.get(ARASAAC_SEARCH + palavra)
        if r.status_code == 200:
            return [
                f"https://static.arasaac.org/pictograms/{p['_id']}/{p['_id']}_300.png"
                for p in r.json()[:8]
            ]
    except:
        pass
    return []

# ======================
# HISTÓRICO
# ======================
def salvar_prancha(paciente, frase, prancha):
    pacientes[paciente]["historico"].append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "frase": frase,
        "prancha": prancha
    })
    salvar_dados()

# ======================
# STATE
# ======================
pacientes = carregar_dados()

st.session_state.setdefault("paciente", None)
st.session_state.setdefault("prancha", [])

# ======================
# SIDEBAR
# ======================
st.sidebar.title("🧠 NeuroCAA")

menu = st.sidebar.radio("Navegação", ["Pacientes", "Criar Prancha", "Histórico"])

st.sidebar.markdown(
    "<small>🖼️ ARASAAC – CC BY-NC-SA 4.0</small>",
    unsafe_allow_html=True
)

# ======================
# PACIENTES
# ======================
if menu == "Pacientes":
    st.header("👤 Pacientes")

    novo = st.text_input("Novo paciente")
    if st.button("Adicionar"):
        if novo and novo not in pacientes:
            pacientes[novo] = {"historico": []}
            salvar_dados()
            st.success("Paciente criado!")

    if pacientes:
        sel = st.selectbox("Selecionar paciente", pacientes.keys())
        if st.button("Usar paciente"):
            st.session_state["paciente"] = sel
            st.success(f"Paciente ativo: {sel}")

# ======================
# CRIAR PRANCHA
# ======================
if menu == "Criar Prancha":
    st.header("🧩 Criar Prancha")

    if not st.session_state["paciente"]:
        st.warning("Selecione um paciente primeiro.")
        st.stop()

    frase = st.text_input("Digite a frase")

    if st.button("✨ Gerar prancha"):
        palavras = frase.lower().split()
        prancha = []

        for p in palavras:
            opcoes = buscar_opcoes_arasaac(p)
            prancha.append({
                "palavra": p,
                "imagem": opcoes[0] if opcoes else None,
                "opcoes": opcoes
            })

        st.session_state["prancha"] = prancha

    # ===== VISUALIZAÇÃO EM GRID =====
    if st.session_state["prancha"]:
        st.subheader("🖼️ Prancha gerada")

        prancha = st.session_state["prancha"]

        for i in range(0, len(prancha), COLUNAS_PRANCHA):
            linha = prancha[i:i + COLUNAS_PRANCHA]
            cols = st.columns(COLUNAS_PRANCHA)

            for idx, item in enumerate(linha):
                with cols[idx]:
                    if item["imagem"]:
                        st.image(item["imagem"], width=140)
                    st.caption(item["palavra"])

                    if item["opcoes"]:
                        nova = st.selectbox(
                            "Trocar imagem",
                            item["opcoes"],
                            key=f"img_{i+idx}"
                        )
                        st.session_state["prancha"][i+idx]["imagem"] = nova

        if st.button("💾 Salvar prancha no histórico"):
            salvar_prancha(
                st.session_state["paciente"],
                frase,
                st.session_state["prancha"]
            )
            st.success("Prancha salva!")

# ======================
# HISTÓRICO
# ======================
if menu == "Histórico":
    st.header("📚 Histórico")

    if not st.session_state["paciente"]:
        st.warning("Selecione um paciente.")
        st.stop()

    hist = pacientes[st.session_state["paciente"]]["historico"]

    if not hist:
        st.info("Nenhuma prancha salva.")
    else:
        for item in reversed(hist):
            with st.expander(f"{item['data']} – {item['frase']}"):
                prancha = item["prancha"]
                for i in range(0, len(prancha), COLUNAS_PRANCHA):
                    linha = prancha[i:i + COLUNAS_PRANCHA]
                    cols = st.columns(COLUNAS_PRANCHA)
                    for idx, p in enumerate(linha):
                        with cols[idx]:
                            if p["imagem"]:
                                st.image(p["imagem"], width=120)
                            st.caption(p["palavra"])
