import streamlit as st
import requests
import os
import time
import uuid
from openai import OpenAI, RateLimitError

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ===============================
# CONFIGURAÇÃO INICIAL
# ===============================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="NeuroCAA", layout="wide")
st.title("🧠 NeuroCAA – Pranchas de Comunicação Alternativa")

st.markdown(
    "<small>🖼️ Pictogramas: ARASAAC – Licença CC BY-NC-SA 4.0</small>",
    unsafe_allow_html=True
)

if "pranchas" not in st.session_state:
    st.session_state.pranchas = []

if "prancha_atual" not in st.session_state:
    st.session_state.prancha_atual = None

# ===============================
# FUNÇÕES DE SEGURANÇA
# ===============================

def safe_columns(itens):
    try:
        n = len(itens)
    except:
        n = 1
    if n < 1:
        n = 1
    return st.columns(n)

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
# FUNÇÕES PRINCIPAIS
# ===============================

def gerar_palavras_caa(texto):
    prompt = f"""
    Transforme a frase abaixo em palavras funcionais para Comunicação Alternativa.
    Use apenas palavras simples, concretas e isoladas.
    Não use frases.
    Retorne somente uma lista separada por vírgulas.

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
    stopwords = [ "de", "da", "do", "com", "um", "uma"]
    palavras_limpas = []

    for p in palavras:
        if p and p not in stopwords and len(p) <= 15:
            palavras_limpas.append(p)

    return list(dict.fromkeys(palavras_limpas))


@st.cache_data(show_spinner=False)
def buscar_imagem_arasaac(palavra):
    headers = {"User-Agent": "NeuroCAA-App"}

    for idioma in ["pt", "en"]:
        url = f"https://api.arasaac.org/api/pictograms/{idioma}/search/{palavra}"
        r = requests.get(url, headers=headers)

        if r.status_code == 200 and r.json():
            pid = r.json()[0]["_id"]
            img_url = f"https://api.arasaac.org/api/pictograms/{pid}"
            img_name = f"{palavra}_{uuid.uuid4().hex}.png"

            with open(img_name, "wb") as f:
                f.write(requests.get(img_url).content)

            return img_name

    return None


def gerar_pdf(paciente, palavras):
    nome_arquivo = f"prancha_{paciente.replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
    styles = getSampleStyleSheet()

    elementos = []

    elementos.append(Paragraph(f"<b>Paciente:</b> {paciente}", styles["Title"]))
    elementos.append(Paragraph("<br/>", styles["Normal"]))

    tabela = []
    linha = []

    for palavra in palavras:
        img_path = buscar_imagem_arasaac(palavra)
        if img_path:
            linha.append([
                Image(img_path, width=80, height=80),
                Paragraph(f"<b>{palavra}</b>", styles["Normal"])
            ])

        if len(linha) == 4:
            tabela.append(linha)
            linha = []

    if linha:
        tabela.append(linha)

    table = Table(tabela)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))

    elementos.append(table)
    elementos.append(Paragraph("<br/><br/>", styles["Normal"]))
    elementos.append(
        Paragraph(
            "<small>Pictogramas: ARASAAC – Licença CC BY-NC-SA 4.0</small>",
            styles["Normal"]
        )
    )

    doc.build(elementos)
    return nome_arquivo

# ===============================
# GERAR PRANCHA (NÃO SALVA AUTOMÁTICO)
# ===============================

if gerar and texto and paciente:
    palavras = limpar_palavras(gerar_palavras_caa(texto))

    if palavras:
        st.session_state.prancha_atual = {
            "paciente": paciente,
            "palavras": palavras
        }
    else:
        st.warning("⚠️ Não foi possível gerar pictogramas para esta frase.")

# ===============================
# VISUALIZAÇÃO + SALVAR
# ===============================

if st.session_state.prancha_atual:
    st.subheader("🧩 Prancha gerada (visualização)")

    palavras = st.session_state.prancha_atual["palavras"]
    cols = safe_columns(palavras)

    for col, palavra in zip(cols, palavras):
        with col:
            img = buscar_imagem_arasaac(palavra)
            if img:
                st.image(img, width=100)
            st.caption(palavra)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Salvar prancha"):
            st.session_state.pranchas.append(st.session_state.prancha_atual)
            st.session_state.prancha_atual = None
            st.success("✅ Prancha salva com sucesso!")

    with col2:
        if st.button("🗑️ Descartar prancha"):
            st.session_state.prancha_atual = None
            st.warning("Prancha descartada.")

# ===============================
# PRANCHAS SALVAS + PDF
# ===============================

if st.session_state.pranchas:
    st.subheader("📂 Pranchas salvas")

    for i, p in enumerate(st.session_state.pranchas):
        st.markdown(f"### 👤 {p['paciente']}")

        cols = safe_columns(p["palavras"])
        for col, palavra in zip(cols, p["palavras"]):
            with col:
                img = buscar_imagem_arasaac(palavra)
                if img:
                    st.image(img, width=80)
                st.caption(palavra)

        if st.button(f"📄 Gerar PDF – {p['paciente']}", key=f"pdf_{i}"):
            pdf = gerar_pdf(p["paciente"], p["palavras"])
            with open(pdf, "rb") as f:
                st.download_button(
                    "⬇️ Baixar PDF",
                    f,
                    file_name=pdf,
                    mime="application/pdf"
                )
