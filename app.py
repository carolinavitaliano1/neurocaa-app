import streamlit as st
import requests
import os
import time
from openai import OpenAI, RateLimitError

# ===============================
# CONFIGURAÇÃO
# ===============================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="NeuroCAA", layout="wide")
st.title("🧠 NeuroCAA – Pranchas de Comunicação Alternativa")

# ===============================
# SESSION STATE
# ===============================

if "prancha_atual" not in st.session_state:
    st.session_state.prancha_atual = None

if "pranchas_salvas" not in st.session_state:
    st.session_state.pranchas_salvas = []

# ===============================
# PACIENTE
# ===============================

st.subheader("👤 Paciente")
paciente = st.text_input("Nome do paciente")

# ===============================
# ENTRADA
# ===============================

st.subheader("💬 Comunicação")
texto = st.text_input("Ex: quero ir à casa da vovó")
gerar = st.button("🧩 Gerar prancha")

# ===============================
# FUNÇÕES
# ===============================

def gerar_palavras_caa(texto):
    prompt = f"""
    Transforme a frase abaixo em palavras funcionais para Comunicação Alternativa.
    Use palavras simples, concretas.
    Retorne APENAS palavras separadas por vírgula.

    Frase: {texto}
    """

    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60
        )
        return [p.strip().lower() for p in r.choices[0].message.content.split(",")]

    except RateLimitError:
        st.warning("⏳ Limite temporário da IA. Aguarde alguns segundos.")
        time.sleep(3)
        return []


def buscar_pictograma(palavra):
    url = f"https://api.arasaac.org/api/pictograms/pt/{palavra}"
    r = requests.get(url)
    if r.status_code == 200 and r.json():
        return r.json()[0]["_id"]
    return None


def buscar_com_fallback(palavra):
    # tenta palavra direta
    pid = buscar_pictograma(palavra)
    if pid:
        return pid

    # fallback simples
    fallback = {
        "vovó": ["avó", "mulher", "pessoa"],
        "vovô": ["avô", "homem", "pessoa"],
        "casa da vovó": ["casa", "família"],
        "banheiro": ["banheiro", "lavar"],
        "comer": ["comida"],
        "beber": ["água"],
        "ir": ["andar"],
        "querer": ["querer", "pedir"]
    }

    for alt in fallback.get(palavra, []):
        pid = buscar_pictograma(alt)
        if pid:
            return pid

    # fallback final universal
    return buscar_pictograma("pessoa")


# ===============================
# GERAR PRANCHA
# ===============================

if gerar and texto and paciente:
    palavras = gerar_palavras_caa(texto)

    itens = []
    for p in palavras:
        pid = buscar_com_fallback(p)
        if pid:
            itens.append({"palavra": p, "pid": pid})

    if itens:
        st.session_state.prancha_atual = {
            "paciente": paciente,
            "itens": itens
        }
    else:
        st.warning("⚠️ Não foi possível gerar pictogramas para esta frase.")

# ===============================
# MOSTRAR PRANCHA (ABAS)
# ===============================

if st.session_state.prancha_atual:
    aba_ia, aba_manual = st.tabs(["🤖 Sugestão da IA", "✏️ Ajustar manualmente"])

    # -------------------------------
    # ABA IA
    # -------------------------------
    with aba_ia:
        st.subheader("🤖 Prancha sugerida pela IA")

        itens = st.session_state.prancha_atual["itens"]

        if itens:
            cols = st.columns(len(itens))
            for col, item in zip(cols, itens):
                with col:
                    img = f"https://api.arasaac.org/api/pictograms/{item['pid']}"
                    st.image(img, width=100)
                    st.markdown(f"**{item['palavra']}**")
        else:
            st.warning("Nenhum item para mostrar.")

    # -------------------------------
    # ABA MANUAL
    # -------------------------------
    with aba_manual:
        st.subheader("✏️ Ajustar palavras e imagens")

        for i, item in enumerate(st.session_state.prancha_atual["itens"]):
            st.markdown("---")
            nova = st.text_input(
                "Palavra",
                value=item["palavra"],
                key=f"pal_{i}"
            )
            item["palavra"] = nova

            resultados = requests.get(
                f"https://api.arasaac.org/api/pictograms/pt/{nova}"
            ).json()[:6]

            if resultados:
                cols = st.columns(len(resultados))
                for col, r in zip(cols, resultados):
                    with col:
                        img = f"https://api.arasaac.org/api/pictograms/{r['_id']}"
                        if st.button("Usar", key=f"use_{i}_{r['_id']}"):
                            item["pid"] = r["_id"]
                        st.image(img, width=80)
            else:
                st.info("Nenhuma imagem encontrada para esta palavra.")

    # -------------------------------
    # SALVAR
    # -------------------------------
    if st.button("💾 Salvar prancha"):
        st.session_state.pranchas_salvas.append(st.session_state.prancha_atual)
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
                img = f"https://api.arasaac.org/api/pictograms/{item['pid']}"
                st.image(img, width=80)
                st.caption(item["palavra"])

# ===============================
# RODAPÉ LEGAL
# ===============================

st.markdown("---")
st.caption(
    "Pictogramas: ARASAAC (CC BY-NC-SA). "
    "Este app é uma ferramenta de apoio clínico e educacional."
)
