import streamlit as st
import json
import os
from datetime import datetime
import requests

# =========================
# CONFIGURAÇÃO INICIAL
# =========================
st.set_page_config(page_title="🧠 NeuroCAA", layout="wide")

DATA_PATH = "data/pacientes.json"
ARASAAC_API = "https://api.arasaac.org/api/pictograms/pt/search/"

# =========================
# FUNÇÕES DE DADOS
# =========================
def carregar_dados():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados():
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(pacientes, f, ensure_ascii=False, indent=2)

# =========================
# ARASAAC
# =========================
def buscar_pictogramas(palavra):
    try:
        r = requests.get(ARASAAC_API + palavra)
        if r.status_code == 200:
            dados = r.json()
            return [
                f"https://static.arasaac.org/pictograms/{d['_id']}/{d['_id']}_300.png"
                for d in dados[:6]
            ]
    except:
        pass
    return []

# =========================
# SALVAR HISTÓRICO
# =========================
def salvar_prancha_no_historico(paciente, frase, prancha):
    registro = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "frase": frase,
        "prancha": prancha
    }
    pacientes[paciente]["historico"].append(registro)
    salvar_dados()

# =========================
# CARREGAMENTO
# =========================
pacientes = carregar_dados()

if "paciente" not in st.session_state:
    st.session_state["paciente"] = None

if "prancha" not in st.session_state:
    st.session_state["prancha"] = []

# =========================
# MENU LATERAL
# =========================
st.sidebar.title("🧠 NeuroCAA")

menu = st.sidebar.radio(
    "Navegação",
    ["Pacientes", "Criar Prancha", "Histórico"]
)

# =========================
# PACIENTES
# =========================
if menu == "Pacientes":
    st.header("👤 Cadastro de Pacientes")

    novo = st.text_input("Nome do paciente")

    if st.button("➕ Adicionar paciente"):
        if novo.strip():
            if novo not in pacientes:
                pacientes[novo] = {"historico": []}
                salvar_dados()
                st.success("Paciente cadastrado!")
            else:
                st.warning("Paciente já existe.")

    if pacientes:
        escolhido = st.selectbox("Selecione o paciente", list(pacientes.keys()))
        if st.button("Usar este paciente"):
            st.session_state["paciente"] = escolhido
            st.success(f"Paciente ativo: {escolhido}")

# =========================
# CRIAR PRANCHA
# =========================
if menu == "Criar Prancha":
    st.header("🧩 Criar Prancha de Comunicação")

    if not st.session_state["paciente"]:
        st.warning("Selecione um paciente primeiro.")
        st.stop()

    frase = st.text_input("Digite a frase")

    if st.button("✨ Gerar prancha"):
        palavras = frase.lower().split()
        prancha = []

        for p in palavras:
            imagens = buscar_pictogramas(p)
            prancha.append({
                "palavra": p,
                "imagem": imagens[0] if imagens else None,
                "opcoes": imagens
            })

        st.session_state["prancha"] = prancha

    # EXIBIR PRANCHA
    if st.session_state["prancha"]:
        st.subheader("🖼️ Prancha gerada")

        cols = st.columns(len(st.session_state["prancha"]))

        for i, item in enumerate(st.session_state["prancha"]):
            with cols[i]:
                if item["imagem"]:
                    st.image(item["imagem"], width=120)
                else:
                    st.markdown("**(sem imagem)**")

                st.caption(item["palavra"])

                # TROCAR IMAGEM
                if item["opcoes"]:
                    nova = st.selectbox(
                        "Trocar imagem",
                        item["opcoes"],
                        key=f"img_{i}"
                    )
                    st.session_state["prancha"][i]["imagem"] = nova

        st.markdown("---")

        if st.button("💾 Salvar prancha no histórico"):
            salvar_prancha_no_historico(
                st.session_state["paciente"],
                frase,
                st.session_state["prancha"]
            )
            st.success("Prancha salva no histórico!")

# =========================
# HISTÓRICO
# =========================
if menu == "Histórico":
    st.header("📚 Histórico do Paciente")

    if not st.session_state["paciente"]:
        st.warning("Selecione um paciente.")
        st.stop()

    historico = pacientes[st.session_state["paciente"]]["historico"]

    if not historico:
        st.info("Nenhuma prancha salva ainda.")
    else:
        for item in reversed(historico):
            with st.expander(f"{item['data']} – {item['frase']}"):
                if item["prancha"]:
                    cols = st.columns(len(item["prancha"]))
                    for i, p in enumerate(item["prancha"]):
                        with cols[i]:
                            if p["imagem"]:
                                st.image(p["imagem"], width=100)
                            st.caption(p["palavra"])
