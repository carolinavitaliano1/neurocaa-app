import streamlit as st
from services.ia import gerar_palavras_caa, limpar_palavras
from services.arasaac import buscar_imagem_arasaac
from services.pdf import gerar_pdf
import json
import os

st.set_page_config(page_title="NeuroCAA", layout="wide")

st.title("🧠 NeuroCAA – Comunicação Alternativa")
st.markdown(
    "<small>🖼️ Pictogramas: ARASAAC – Licença CC BY-NC-SA 4.0</small>",
    unsafe_allow_html=True
)

# ===============================
# BASE DE DADOS SIMPLES
# ===============================
DATA_PATH = "data/pacientes.json"
os.makedirs("data", exist_ok=True)

if not os.path.exists(DATA_PATH):
    with open(DATA_PATH, "w") as f:
        json.dump({}, f)

with open(DATA_PATH, "r") as f:
    pacientes_db = json.load(f)

# ===============================
# MENU LATERAL
# ===============================
menu = st.sidebar.radio(
    "📂 Navegação",
    ["👤 Pacientes", "🧩 Criar Prancha", "📂 Histórico"]
)

# ===============================
# 👤 PACIENTES
# ===============================
if menu == "👤 Pacientes":
    st.header("👤 Cadastro de Pacientes")

    novo = st.text_input("Nome do paciente")
    if st.button("➕ Cadastrar paciente"):
        if novo and novo not in pacientes_db:
            pacientes_db[novo] = []
            with open(DATA_PATH, "w") as f:
                json.dump(pacientes_db, f, indent=2, ensure_ascii=False)
            st.success("Paciente cadastrado!")
        else:
            st.warning("Paciente já existe ou nome vazio.")

    st.subheader("📋 Pacientes cadastrados")
    for p in pacientes_db:
        st.write("•", p)

# ===============================
# 🧩 CRIAR PRANCHA
# ===============================
elif menu == "🧩 Criar Prancha":
    st.header("🧩 Criar prancha de comunicação")

    paciente = st.selectbox("Selecione o paciente", list(pacientes_db.keys()))
    texto = st.text_input("Frase (ex: quero beber água)")

    if st.button("🧠 Gerar prancha"):
        palavras = limpar_palavras(gerar_palavras_caa(texto))

        if palavras:
            st.session_state.prancha_atual = {
                "paciente": paciente,
                "palavras": palavras
            }

    if "prancha_atual" in st.session_state:
        st.subheader("👀 Visualização")

        palavras = st.session_state.prancha_atual["palavras"]
        cols = st.columns(min(len(palavras), 6))

        for col, palavra in zip(cols, palavras):
            with col:
                img = buscar_imagem_arasaac(palavra)
                if img:
                    st.image(img, width=100)
                st.caption(palavra)

        if st.button("💾 Salvar prancha"):
            pacientes_db[paciente].append(palavras)
            with open(DATA_PATH, "w") as f:
                json.dump(pacientes_db, f, indent=2, ensure_ascii=False)
            del st.session_state.prancha_atual
            st.success("Prancha salva no histórico do paciente!")

# ===============================
# 📂 HISTÓRICO
# ===============================
elif menu == "📂 Histórico":
    st.header("📂 Histórico por paciente")

    paciente = st.selectbox("Paciente", list(pacientes_db.keys()))

    if pacientes_db[paciente]:
        for i, prancha in enumerate(pacientes_db[paciente]):
            st.markdown(f"### 🧩 Prancha {i+1}")

            cols = st.columns(min(len(prancha), 6))
            for col, palavra in zip(cols, prancha):
                with col:
                    img = buscar_imagem_arasaac(palavra)
                    if img:
                        st.image(img, width=80)
                    st.caption(palavra)

            if st.button(f"📄 Gerar PDF {i+1}", key=f"{paciente}_{i}"):
                pdf = gerar_pdf(paciente, prancha)
                with open(pdf, "rb") as f:
                    st.download_button(
                        "⬇️ Baixar PDF",
                        f,
                        file_name=pdf,
                        mime="application/pdf"
                    )
    else:
        st.info("Este paciente ainda não possui pranchas.")
