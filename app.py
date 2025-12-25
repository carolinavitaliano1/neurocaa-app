import streamlit as st
import requests
import os
import time
import unicodedata
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
    Use palavras simples e concretas.
    NÃO use frases compostas.
    Retorne APENAS palavras separadas por vírgula.

    Frase: {texto}
    """
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80
        )
        return [p.strip().lower() for p in r.choices[0].message.content.split(",")]
    except RateLimitError:
        st.warning("⏳ Limite temporário da IA. Aguarde alguns segundos.")
        time.sleep(3)
        return []


def normalizar(palavra):
    palavra = palavra.lower()
    palavra = unicodedata.normalize("NFD", palavra)
    palavra = "".join(c for c in palavra if unicodedata.category(c) != "Mn")
    return palavra


def buscar_pictograma(palavra):
    url = f"https://api.arasaac.org/api/pictograms/pt/{palavra}"
    r = requests.get(url)
    if r.status_code == 200 and r.json():
        return r.json()[0]["_id"]
    return None


def buscar_com_fallback(palavra):
    palavra = normalizar(palavra)

    # quebra frases compostas
    partes = palavra.split()

    # tenta cada parte
    for p in partes:
        if p in ["da", "de", "do", "a", "o", "à"]:
            continue
        pid = buscar_pictograma(p)
        if pid:
            return pid

    # fallback clínico
    fallback = {
        "vovo": ["avo", "mulher", "pessoa"],
        "vovó": ["avo"],
        "querer": ["querer", "pedir"],
        "ir": ["andar"],
        "casa": ["casa"],
        "banheiro": ["banheiro"],
        "comer": ["comida"],
        "beber": ["agua"],
    }

    for alt in fallback.get(palavra, []):
        pid = buscar_pictograma(alt)
        if pid:
            return pid

    # fallback final universal
    return buscar_pictograma("pessoa")


def mostrar_prancha(itens, tamanho_img=100):
    if not itens:
        st.warning("Nenhum item para exibir.")
        return

    max_cols = 4

    for i in range(0, len(itens), max_cols):
        linha = itens[i:i + max_cols]
        cols = st.columns(len(linha))

        for col, item in zip(cols, linha):
            with col:
                img = f"https://api.arasaac.org/api/pictograms/{item['pid']}"
                st.image(img, width=tamanho_img)
                st.markdown(f"**{item['palavra']}**")

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
# EXIBIÇÃO COM ABAS
# ===============================

if st.session_state.prancha_atual:
    aba_ia, aba_manual = st.tabs(["🤖 Sugestão da IA", "✏️ Ajustar manualmente"])

    # ABA IA
    with aba_ia:
        st.subheader("🤖 Prancha sugerida pela IA")
        mostrar_prancha(st.session_state.prancha_atual["itens"])

    # ABA MANUAL
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
                f"https://api.arasaac.org/api/pictograms/pt/{normalizar(nova)}"
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

    # SALVAR
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
        mostrar_prancha(p["itens"], tamanho_img=80)

# ===============================
# RODAPÉ LEGAL
# ===============================

st.markdown("---")
st.caption(
    "Pictogramas: ARASAAC (CC BY-NC-SA). "
    "Ferramenta de apoio clínico e educacional."
)
