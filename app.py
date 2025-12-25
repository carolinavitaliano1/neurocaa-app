import streamlit as st
import urllib.parse

st.set_page_config(page_title="NeuroCAA", layout="wide")

# ===============================
# FUNÇÕES
# ===============================

def gerar_placeholder(texto):
    texto = texto.strip() if texto else "CAA"
    texto = urllib.parse.quote(texto)
    return f"https://via.placeholder.com/150?text={texto}"


def imagem_segura(imagem, texto):
    if not imagem or not imagem.startswith("http"):
        return gerar_placeholder(texto)
    return imagem


def gerar_pictogramas_mock(frase):
    palavras = frase.lower().split()
    itens = []

    for p in palavras:
        itens.append({
            "texto": p,
            "imagem": gerar_placeholder(p)
        })

    return itens


def safe_columns(itens):
    try:
        qtd = len(itens)
    except:
        qtd = 1

    if qtd < 1:
        qtd = 1

    return st.columns(qtd)


# ===============================
# SESSION STATE
# ===============================

if "prancha_ia" not in st.session_state:
    st.session_state.prancha_ia = []

if "prancha_manual" not in st.session_state:
    st.session_state.prancha_manual = []


# ===============================
# INTERFACE
# ===============================

st.title("🧠 NeuroCAA – Pranchas de Comunicação")

abas = st.tabs([
    "➕ Gerar Prancha",
    "🤖 Prancha IA",
    "✋ Prancha Manual"
])

# ===============================
# ABA 1 – GERAR
# ===============================
with abas[0]:
    st.subheader("Criar nova prancha")

    frase = st.text_input(
        "Digite a frase",
        placeholder="Ex: eu quero ir à casa da vovó"
    )

    if st.button("✨ Gerar Prancha"):
        if frase.strip():
            st.session_state.prancha_ia = gerar_pictogramas_mock(frase)
            st.success("Prancha criada! Vá para a aba 🤖 Prancha IA")
        else:
            st.warning("Digite uma frase.")


# ===============================
# ABA 2 – PRANCHA IA
# ===============================
with abas[1]:
    st.subheader("🤖 Prancha gerada pela IA")

    if not st.session_state.prancha_ia:
        st.info("Nenhuma prancha gerada.")
    else:
        cols = safe_columns(st.session_state.prancha_ia)

        for i, item in enumerate(st.session_state.prancha_ia):
            with cols[i]:
                img = imagem_segura(item["imagem"], item["texto"])
                st.image(img, use_container_width=True)

                novo_texto = st.text_input(
                    "Editar palavra",
                    value=item["texto"],
                    key=f"ia_txt_{i}"
                )

                nova_img = st.text_input(
                    "Imagem (URL)",
                    value=item["imagem"],
                    key=f"ia_img_{i}"
                )

                st.session_state.prancha_ia[i]["texto"] = novo_texto
                st.session_state.prancha_ia[i]["imagem"] = nova_img


# ===============================
# ABA 3 – PRANCHA MANUAL
# ===============================
with abas[2]:
    st.subheader("✋ Criação manual")

    with st.form("manual"):
        texto = st.text_input("Palavra")
        imagem = st.text_input("Imagem (URL)")
        ok = st.form_submit_button("Adicionar")

        if ok and texto.strip():
            st.session_state.prancha_manual.append({
                "texto": texto,
                "imagem": imagem if imagem else gerar_placeholder(texto)
            })

    if not st.session_state.prancha_manual:
        st.info("Nenhum item adicionado.")
    else:
        cols = safe_columns(st.session_state.prancha_manual)

        for i, item in enumerate(st.session_state.prancha_manual):
            with cols[i]:
                img = imagem_segura(item["imagem"], item["texto"])
                st.image(img, use_container_width=True)

                novo_texto = st.text_input(
                    "Editar palavra",
                    value=item["texto"],
                    key=f"man_txt_{i}"
                )

                nova_img = st.text_input(
                    "Imagem (URL)",
                    value=item["imagem"],
                    key=f"man_img_{i}"
                )

                st.session_state.prancha_manual[i]["texto"] = novo_texto
                st.session_state.prancha_manual[i]["imagem"] = nova_img
