import streamlit as st
import requests
import os
import time
from openai import OpenAI, RateLimitError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

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
    Transforme a frase abaixo em palavras funcionais para uma prancha de Comunicação Alternativa.
    Use palavras simples, concretas e funcionais.
    Retorne apenas uma lista separada por vírgulas.

    Frase: {texto}
    """

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return [p.strip().lower() for p in resposta.choices[0].message.content.split(",")]

    except RateLimitError:
        st.warning("⏳ Limite temporário. Aguarde alguns segundos.")
        time.sleep(3)
        return []

def buscar_imagem_arasaac(palavra):
    url = f"https://api.arasaac.org/api/pictograms/pt/{palavra}"
    r = requests.get(url)
    if r.status_code == 200 and r.json():
        pid = r.json()[0]["_id"]
        return f"https://api.arasaac.org/api/pictograms/{pid}"
    return None

def gerar_pdf(paciente, palavras):
    nome_arquivo = f"prancha_{paciente.replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
    estilos = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph(f"<b>Paciente:</b> {paciente}", estilos["Normal"]))
    elementos.append(Paragraph("<br/>", estilos["Normal"]))

    tabela = []
    linha = []

    for palavra in palavras:
        img_url = buscar_imagem_arasaac(palavra)
        if img_url:
            img_data = requests.get(img_url).content
            with open("temp.png", "wb") as f:
                f.write(img_data)
            linha.append(Image("temp.png", width=80, height=80))
        else:
            linha.append(Paragraph(palavra, estilos["Normal"]))

    tabela.append(linha)

    t = Table(tabela)
    t.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 1, colors.black)
    ]))

    elementos.append(t)
    doc.build(elementos)
    return nome_arquivo

# ===============================
# GERAR PRANCHA
# ===============================

if gerar and texto and paciente:
    palavras = gerar_palavras_caa(texto)

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
        st.markdown(f"**Paciente:** {p['paciente']}")

        cols = st.columns(len(p["palavras"]))
        for col, palavra in zip(cols, p["palavras"]):
            with col:
                img = buscar_imagem_arasaac(palavra)
                if img:
                    st.image(img, width=80)
                st.caption(palavra)

        if st.button(f"📄 Gerar PDF – {p['paciente']}", key=i):
            pdf = gerar_pdf(p["paciente"], p["palavras"])
            with open(pdf, "rb") as f:
                st.download_button(
                    label="⬇️ Baixar PDF",
                    data=f,
                    file_name=pdf,
                    mime="application/pdf"
                )
