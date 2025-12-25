import streamlit as st
import requests
import json
import os

# =============================
# CONFIGURAÇÃO INICIAL
# =============================
st.set_page_config(
    page_title="NeuroCAA",
    layout="wide"
)

st.title("🧠 NeuroCAA – Comunicação Alternativa")
st.caption("Pictogramas: ARASAAC – Licença CC BY-NC-SA 4.0")

# =============================
# DADOS
# =============================
DATA_PATH = "data/pacientes.json"
os.makedirs("data", exist_ok=True)

if not os.path.exists(DATA_PATH):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    pacientes = json.load(f)

# =============================
# FUNÇÕES
# =============================

MAPA_SEMANTICO = {
    "fazer": ["fazer", "preparar", "cozinhar"],
    "comer": ["comer", "alimentar"],
    "beber": ["beber", "tomar"],
    "chocolate": ["chocolate", "doce"],
    "cozinha": ["cozinha", "cozinhar"],
}

def expandir_semantica(palavra):
    palavra = palavra.lower()
    for chave, relacionados in MAPA_SEMANTICO.items():
        if palavra == chave or palavra in relacionados:
            return list(set(relacionados + [chave]))
    return [palavra]

def buscar_arasaac_variacoes(palavra, limite=8):
    termos = expandir_semantica(palavra)
    imagens = []

    for termo in termos:
        url = f"https://api.arasaac.org/api/pictograms/pt/search/{termo}"
        r = requests.get(url)
        if r.status_code == 200:
            for item in r.json():
                img = f"https://api.arasaac.org/api/pictograms/{item['_id']}"
                if img not in imagens:
                    imagens.append(img)
        if len(imagens) >= limite:
            break

    return imagens[:limite]

def gerar_prancha_por_frase(frase):
    palavras = frase.lower().split()
    prancha = []

    for palavra in palavras:
        imgs = buscar_arasaac_variacoes(palavra, limite=1)
        if imgs:
            prancha.append({
                "palavra": palavra,
                "imagem": imgs[0]
            })

    return prancha

def salvar_dados():
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(pacientes, f, ensure_ascii=False, indent=2)

# =============================
# SIDEBAR
# =============================
st.sidebar.title("🧠 NeuroCAA")
menu = st.sidebar.radio(
    "Navegação",
    ["Pacientes", "Criar Prancha", "Histórico"]
)

# =============================
# PACIENTES
# =============================
if menu == "Pacientes":
    st.header("👤 Cadastro e Seleção de Pacientes")

    novo = st.text_input("Nome do novo paciente")
    if st.button("Adicionar paciente"):
        if novo and novo not in pacientes:
            pacientes[novo] = {"historico": []}
            salvar_dados()
            st.success("Paciente adicionado!")

    if pacientes:
        selecionado = st.selectbox(
            "Paciente ativo",
            list(pacientes.keys())
        )
        st.session_state["paciente"] = selecionado
        st.info(f"Paciente ativo: {selecionado}")

# =============================
# CRIAR PRANCHA
# =============================
if menu == "Criar Prancha":
    st.header("🧩 Criar Prancha")

    if "paciente" not in st.session_state:
        st.warning("Selecione um paciente primeiro.")
        st.stop()

    frase = st.text_input("Digite uma frase")

    if st.button("🤖 Gerar com IA"):
        prancha = gerar_prancha_por_frase(frase)
        st.session_state["prancha"] = prancha

    prancha = st.session_state.get("prancha", [])

    if prancha:
        st.subheader("Prancha atual")

        cols = st.columns(len(prancha))

        for i, item in enumerate(prancha):
            with cols[i]:
                if st.button("🔄", key=f"editar_{i}", help="Trocar imagem"):
                    st.session_state["editar_palavra"] = item["palavra"]
                    st.session_state["editar_indice"] = i

                st.image(item["imagem"], width=120)
                st.caption(item["palavra"])

    # =============================
    # TROCA DE IMAGEM
    # =============================
    if "editar_palavra" in st.session_state:
        palavra = st.session_state["editar_palavra"]
        idx = st.session_state["editar_indice"]

        st.markdown("---")
        st.subheader(f"🔍 Escolha outra imagem para: **{palavra}**")

        opcoes = buscar_arasaac_variacoes(palavra)

        cols = st.columns(len(opcoes))
        for i, img in enumerate(opcoes):
            with cols[i]:
                if st.button("Selecionar", key=f"sel_{i}"):
                    st.session_state["prancha"][idx]["imagem"] = img
                    del st.session_state["editar_palavra"]
                    del st.session_state["editar_indice"]
                    st.experimental_rerun()

                st.image(img, width=100)

# =============================
# HISTÓRICO
# =============================
if menu == "Histórico":
    st.header("📚 Histórico")

    if "paciente" not in st.session_state:
        st.warning("Selecione um paciente.")
        st.stop()

    historico = pacientes[st.session_state["paciente"]]["historico"]

    if not historico:
        st.info("Nenhuma prancha salva ainda.")
    else:
        for i, h in enumerate(historico):
            st.markdown(f"**{i+1}.** {h}")
