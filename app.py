import streamlit as st
import json
import os
from services.pdf import gerar_pdf

# =========================
# CONFIGURAÇÃO INICIAL
# =========================
st.set_page_config(
    page_title="NeuroCAA – Comunicação Alternativa",
    layout="wide"
)

DATA_PATH = "data/pacientes.json"

# =========================
# FUNÇÕES AUXILIARES
# =========================
def carregar_pacientes():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_pacientes(dados):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# =========================
# ESTADO INICIAL
# =========================
if "pacientes" not in st.session_state:
    st.session_state.pacientes = carregar_pacientes()

if "paciente_atual" not in st.session_state:
    st.session_state.paciente_atual = None

if "prancha_atual" not in st.session_state:
    st.session_state.prancha_atual = []


# =========================
# MENU LATERAL (AGORA APARECE!)
# =========================
st.sidebar.title("🧠 NeuroCAA")
menu = st.sidebar.radio(
    "Navegação",
    ["👤 Pacientes", "🖼️ Criar Prancha", "📚 Histórico"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Pictogramas: ARASAAC\nLicença CC BY-NC-SA 4.0")


# =========================
# TELA 1 – PACIENTES
# =========================
if menu == "👤 Pacientes":
    st.title("👤 Cadastro e Seleção de Pacientes")

    nome_novo = st.text_input("Nome do paciente")

    if st.button("➕ Cadastrar paciente"):
        if nome_novo.strip() == "":
            st.warning("Digite um nome válido.")
        elif nome_novo in st.session_state.pacientes:
            st.warning("Paciente já cadastrado.")
        else:
            st.session_state.pacientes[nome_novo] = {
                "pranchas": []
            }
            salvar_pacientes(st.session_state.pacientes)
            st.success("Paciente cadastrado com sucesso!")

    st.markdown("---")

    if st.session_state.pacientes:
        paciente = st.selectbox(
            "Selecione um paciente",
            list(st.session_state.pacientes.keys())
        )

        if st.button("✅ Usar este paciente"):
            st.session_state.paciente_atual = paciente
            st.session_state.prancha_atual = []
            st.success(f"Paciente ativo: {paciente}")


# =========================
# TELA 2 – CRIAÇÃO DE PRANCHA
# =========================
elif menu == "🖼️ Criar Prancha":
    st.title("🖼️ Criar Prancha de Comunicação")

    if not st.session_state.paciente_atual:
        st.warning("Selecione um paciente primeiro.")
        st.stop()

    st.info(f"Paciente ativo: **{st.session_state.paciente_atual}**")

    palavra = st.text_input("Digite uma palavra ou frase (ex: QUERO ÁGUA)")

    if st.button("➕ Adicionar à prancha"):
        if palavra.strip():
            st.session_state.prancha_atual.append(palavra.upper())

    if st.session_state.prancha_atual:
        st.subheader("Prancha atual")
        st.write(st.session_state.prancha_atual)

    st.markdown("---")

    # 🔒 BOTÃO PDF BLINDADO
    if st.button("📄 Salvar prancha em PDF"):
        if not st.session_state.prancha_atual:
            st.warning("⚠️ A prancha está vazia. Adicione pelo menos um item.")
        else:
            pdf = gerar_pdf(
                st.session_state.paciente_atual,
                st.session_state.prancha_atual
            )

            # salva no histórico do paciente
            st.session_state.pacientes[
                st.session_state.paciente_atual
            ]["pranchas"].append(st.session_state.prancha_atual)

            salvar_pacientes(st.session_state.pacientes)

            st.success("✅ PDF gerado e prancha salva no histórico!")


# =========================
# TELA 3 – HISTÓRICO
# =========================
elif menu == "📚 Histórico":
    st.title("📚 Histórico de Pranchas")

    if not st.session_state.paciente_atual:
        st.warning("Selecione um paciente primeiro.")
        st.stop()

    paciente = st.session_state.paciente_atual
    historico = st.session_state.pacientes[paciente]["pranchas"]

    st.info(f"Paciente: **{paciente}**")

    if not historico:
        st.warning("Nenhuma prancha salva ainda.")
    else:
        for i, prancha in enumerate(historico, start=1):
            st.markdown(f"**Prancha {i}:**")
            st.write(prancha)
            st.markdown("---")

