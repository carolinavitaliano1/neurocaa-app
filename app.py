import streamlit as st
import requests
import os
from openai import OpenAI

# ===============================
# CONFIG
# ===============================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="NeuroCAA", layout="wide")
st.title("🧠 NeuroCAA – Pranchas de Comunicação Alternativa")

if "prancha_atual" not in st.session_state:
    st.session_state.prancha_atual = None

if "pranchas_salvas" not in st.session_state:
    st.session_state.pranchas_salvas = []

# ===============================
# FUNÇÕES
# ===============================
def gerar_palavras_caa(texto):
    prompt = f"""
    Transforme a frase abaixo em palavras funcionais
    para uma prancha de Comunicação Alternativa.
    Retorne apenas uma lista separada por vírgulas.

    Frase: {texto}
    """
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    return [p.strip().lower() for p in resp.choices[0].message.content.split(",")]

def buscar_opcoes_arasaac(palavra, limite=6):
    url = f"https://api.arasaac.org/api/pictograms/pt/{palavra}"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()[:limite]
    return []

# ===============================
# DADOS DO PACIENTE
# ===============================
st.subheader("👤 Paciente")
paciente = st.text_input("Nome do paciente")

# ===============================
# ENTRADA
# ===============================
st.subheader("💬 Comunicação")
texto = st.text_input("Ex: quero ir à casa da vovó")

if st.button("🧩 Gerar prancha"):
    if paciente and texto:
        palavras = gerar_palavras_caa(texto)
        itens = []

        for palavra in palavras:
            opcoes = buscar_opcoes_arasaac(palavra)
            if opcoes:
                itens.append({
                    "palavra": palavra,
                    "pid": opcoes[0]["_id"]
                })

        st.session_state.prancha_atual = {
            "paciente": paciente,
            "itens": itens
        }

# ===============================
# PRANCHA GERADA
# ===============================
if st.session_state.prancha_atual:
    aba_ia, aba_manual = st.tabs([
        "🤖 Sugestão da IA",
        "✏️ Ajustar manualmente (opcional)"
    ])

    # -------------------------------
    # ABA IA
    # -------------------------------
    with aba_ia:
        st.subheader("🤖 Prancha sugerida automaticamente")

        cols = st.columns(len(st.session_state.prancha_atual["itens"]))
        for col, item in zip(cols, st.session_state.prancha_atual["itens"]):
            with col:
                img_url = f"https://api.arasaac.org/api/pictograms/{item['pid']}"
                st.image(img_url, width=100)
                st.markdown(f"**{item['palavra']}**")

    # -------------------------------
    # ABA MANUAL
    # -------------------------------
    with aba_manual:
        st.subheader("✏️ Ajustar palavras e imagens")

        for i, item in enumerate(st.session_state.prancha_atual["itens"]):
            st.markdown("---")
            col1, col2 = st.columns([1, 3])

            with col1:
                img_url = f"https://api.arasaac.org/api/pictograms/{item['pid']}"
                st.image(img_url, width=90)

            with col2:
                nova_palavra = st.text_input(
                    "Palavra",
                    value=item["palavra"],
                    key=f"pal_{i}"
                )
                item["palavra"] = nova_palavra

                opcoes = buscar_opcoes_arasaac(nova_palavra)

                cols = st.columns(len(opcoes))
                for col, opcao in zip(cols, opcoes):
                    with col:
                        img_opcao = f"https://api.arasaac.org/api/pictograms/{opcao['_id']}"
                        if st.button("Usar", key=f"img_{i}_{opcao['_id']}"):
                            item["pid"] = opcao["_id"]
                        st.image(img_opcao, width=70)

    # -------------------------------
    # SALVAR
    # -------------------------------
    if st.button("💾 Salvar prancha"):
        st.session_state.pranchas_salvas.append(
            st.session_state.prancha_atual.copy()
        )
        st.success("Prancha salva com sucesso!")

# ===============================
# PRANCHAS SALVAS
# ===============================
if st.session_state.pranchas_salvas:
    st.subheader("📂 Pranchas salvas")

    for p in st.session_state.pranchas_salvas:
        st.markdown(f"**Paciente:** {p['paciente']}")
        cols = st.columns(len(p["itens"]))
        for col, item in zip(cols, p["itens"]):
            with col:
                img_url = f"https://api.arasaac.org/api/pictograms/{item['pid']}"
                st.image(img_url, width=80)
                st.caption(item["palavra"])

st.markdown(
    "<hr><center>Imagens: ARASAAC (CC BY-NC-SA 4.0) | Texto: OpenAI</center>",
    unsafe_allow_html=True
)
