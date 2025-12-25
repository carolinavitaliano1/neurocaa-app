import streamlit as st

st.set_page_config(page_title="NeuroCAA", layout="wide")

# -------------------------------
# FUNÇÕES AUXILIARES
# -------------------------------

def gerar_pictogramas_mock(frase):
    """
    Simulação de geração automática (IA).
    Depois você liga na API real.
    """
    palavras = frase.lower().split()
    itens = []

    for p in palavras:
        itens.append({
            "texto": p,
            "imagem": "https://via.placeholder.com/150?text=" + p
        })

    return itens


def fallback_columns(itens):
    """
    Garante que o número de colunas nunca seja inválido
    """
    if not itens or len(itens) == 0:
        return st.columns(1)
    return st.columns(len(itens))


# -------------------------------
# SESSION STATE
# -------------------------------

if "prancha_ia" not in st.session_state:
    st.session_state.prancha_ia = []

if "prancha_manual" not in st.session_state:
    st.session_state.prancha_manual = []


# -------------------------------
# INTERFACE
# -------------------------------

st.title("🧠 NeuroCAA – Pranchas de Comunicação")

abas = st.tabs([
    "➕ Gerar Prancha",
    "🤖 Prancha IA",
    "✋ Prancha Manual"
])

# ======================================================
# ABA 1 – GERAR
# ======================================================
with abas[0]:
    st.subheader("Criar nova prancha")

    frase = st.text_input(
        "Digite a frase",
        placeholder="Ex: Eu quero ir à casa da vovó"
    )

    if st.button("✨ Gerar Prancha"):
        if frase.strip() == "":
            st.warning("Digite uma frase primeiro 😉")
        else:
            st.session_state.prancha_ia = gerar_pictogramas_mock(frase)
            st.success("Prancha gerada! Agora escolha como deseja usar 👇")


# ======================================================
# ABA 2 – PRANCHA IA
# ======================================================
with abas[1]:
    st.subheader("🤖 Prancha gerada automaticamente")

    if not st.session_state.prancha_ia:
        st.info("Nenhuma prancha gerada ainda.")
    else:
        cols = fallback_columns(st.session_state.prancha_ia)

        for idx, item in enumerate(st.session_state.prancha_ia):
            with cols[idx]:
                st.image(item["imagem"], use_container_width=True)

                novo_texto = st.text_input(
                    "Editar palavra",
                    value=item["texto"],
                    key=f"texto_ia_{idx}"
                )
                st.session_state.prancha_ia[idx]["texto"] = novo_texto

                nova_imagem = st.text_input(
                    "Trocar imagem (URL)",
                    value=item["imagem"],
                    key=f"img_ia_{idx}"
                )
                st.session_state.prancha_ia[idx]["imagem"] = nova_imagem


# ======================================================
# ABA 3 – PRANCHA MANUAL
# ======================================================
with abas[2]:
    st.subheader("✋ Criar prancha manualmente")

    with st.form("add_manual"):
        texto = st.text_input("Palavra")
        imagem = st.text_input(
            "Imagem (URL)",
            placeholder="https://..."
        )
        add = st.form_submit_button("Adicionar")

        if add:
            if texto.strip() == "":
                st.warning("A palavra não pode ficar vazia.")
            else:
                st.session_state.prancha_manual.append({
                    "texto": texto,
                    "imagem": imagem if imagem else "https://via.placeholder.com/150?text=" + texto
                })

    if not st.session_state.prancha_manual:
        st.info("Nenhum item adicionado ainda.")
    else:
        cols = fallback_columns(st.session_state.prancha_manual)

        for idx, item in enumerate(st.session_state.prancha_manual):
            with cols[idx]:
                st.image(item["imagem"], use_container_width=True)

                novo_texto = st.text_input(
                    "Editar palavra",
                    value=item["texto"],
                    key=f"texto_manual_{idx}"
                )
                st.session_state.prancha_manual[idx]["texto"] = novo_texto

                nova_img = st.text_input(
                    "Trocar imagem (URL)",
                    value=item["imagem"],
                    key=f"img_manual_{idx}"
                )
                st.session_state.prancha_manual[idx]["imagem"] = nova_img
