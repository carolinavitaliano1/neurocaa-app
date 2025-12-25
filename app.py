import streamlit as st
import requests
import os
import time
from openai import OpenAI, RateLimitError

# ===============================
# CONFIGURAÇÃO INICIAL
# ===============================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="NeuroCAA", layout="wide")
st.title("🧠 NeuroCAA – Pranchas de Comunicação Alternativa")

if "pranchas" not in st.session_state:
    st.session_state.pranchas = []

# ===============================
# DADOS DO PACIENTE
# ===============================

st.subheader("👤 Paciente")
paciente = st.text_input("Nome do paciente")

# ===============================
# ENTRADA DE TEXTO
# ===============================

st.subheader("💬 Comunicação")
texto = st.text_input("Ex: quero beber água")
gerar = st.button("🧩 Gerar prancha")

# ===============================
# FUNÇÕES
# ===============================

def gerar_palavras_caa(texto):
    prompt = f"""
    Transforme a frase abaixo em palavras funcionais para Comunicação Alternativa.
    Use apenas palavras simples, concretas e isoladas (ex: comer, beber, água, banana).
    Não use frases.
    Retorne SOMENTE uma lista separada por vírgulas.

    Frase: {texto}
    """

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80
        )
        return [p.strip().lower() for p in resposta.choices[0].message.content.split(",")]

    except RateLimitError:
        st.warning("⏳ Aguarde alguns segundos e tente novamente.")
        time.sleep(3)
        return []


def limpar_palavras(palavras):
    stopwords = ["quero", "eu", "de", "da", "do", "para", "com", "um", "uma"]
    palavras_limpas = []

    for p in palavras:
        if p and p not in stopwords and len(p) <= 15:
            palavras_limpas.append(p)

    return list(dict.fromkeys(palavras_limpas))  # remove duplicadas


def buscar_imagem_arasaac(palavra):
    headers = {"User-Agent": "NeuroCAA-App"}

    for idioma in ["pt", "en"]:
        url = f"https://api.arasaac.org/api/pictograms/{idioma}/search/{palavra}"
        r = requests.get(url, headers=headers, timeout=5)

        if r.status_code == 200 and r.json():
            pid = r.json()[0]["_id"]
            return f"https://api.arasaac.org/api/pictograms/{pid}"

    return None


def gerar_html_prancha(paciente, palavras):
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Prancha CAA</title>
        <style>
            body {{ font-family: Arial; }}
            h2 {{ text-align: center; }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }}
            .card {{
                border: 2px solid #000;
                text-align: center;
                padding: 10px;
            }}
            img {{
                width: 100px;
                height: 100px;
            }}
        </style>
    </head>
    <body>
        <h2>Paciente: {paciente}</h2>
        <div class="grid">
    """

    for palavra in palavras:
        img = buscar_imagem_arasaac(palavra)
        if img:
            html += f"""
            <div class="card">
                <img src="{img}">
                <p><b>{palavra}</b></p>
            </div>
            """

    html += "</div></body></html>"
    return html

# ===============================
# GERAR PRANCHA
# ===============================

if gerar and texto and paciente:
    palavras_brutas = gerar_palavras_caa(texto)
    palavras = limpar_palavras(palavras_brutas)

    if palavras:
        st.session_state.pranchas.append({
            "paciente": paciente,
            "palavras": palavras
        })

        st.subheader("🧩 Prancha atual")

        cols = st.columns(len(palavras))
        for col, palavra in zip(cols, palavras):
            with col:
                img = buscar_imagem_arasaac(palavra)
                if img:
                    st.image(img, width=120)
                st.markdown(f"**{palavra}**")

# ===============================
# PRANCHAS SALVAS
# ===============================

if st.session_state.pranchas:
    st.subheader("📂 Pranchas salvas")

    for i, p in enumerate(st.session_state.pranchas):
        st.markdown(f"### 👤 {p['paciente']}")

        cols = st.columns(len(p["palavras"]))
        for col, palavra in zip(cols, p["palavras"]):
            with col:
                img = buscar_imagem_arasaac(palavra)
                if img:
                    st.image(img, width=90)
                st.caption(palavra)

        html = gerar_html_prancha(p["paciente"], p["palavras"])

        st.download_button(
            label="🖨️ Baixar prancha (HTML)",
            data=html,
            file_name=f"prancha_{p['paciente'].replace(' ','_')}.html",
            mime="text/html",
            key=f"html_{i}"
        )
