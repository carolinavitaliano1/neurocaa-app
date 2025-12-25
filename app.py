import streamlit as st
import requests
import os
import time
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
# FUNÇÕES
# ===============================

def gerar_palavras_caa(texto):
    prompt = f"""
    Transforme a frase abaixo em palavras funcionais para Comunicação Alternativa.
    Use palavras simples, concretas e isoladas.
    Retorne somente palavras separadas por vírgulas.

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
        time.sleep(3)
        return []


def limpar_palavras(palavras):
    stopwords = ["quero", "eu", "de", "da", "do", "para", "com", "um", "uma"]
    return [p for p in palavras if p and p not in stopwords]


def buscar_opcoes_arasaac(palavra, limite=6):
    headers = {"User-Agent": "NeuroCAA-App"}
    url = f"https://api.arasaac.org/api/pictograms/pt/search/{palavra}"
    r = requests.get(url, headers=headers)

    if r.status_code == 200 and r.json():
        return r.json()[:limite]

    return []


def baixar_imagem(pid):
    img_url = f"https://api.arasaac.org/api/pictograms/{pid}"
    img_path = f"{pid}.png"
    with open(img_path, "wb") as f:
        f.write(requests.get(img_url).content)
    return img_path


def gerar_pdf(paciente, itens):
    nome_arquivo = f"prancha_{paciente.replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph(f"<b>Paciente:</b> {paciente}", styles["Title"]))
    elementos.append(Paragraph("<br/>", styles["Normal"]))

    tabela = []
    linha = []

    for item in itens:
        img_path = baixar_imagem(item["pid"])
        celula = [
            Image(img_path, width=80, height=80),
            Paragraph(f"<b>{item['palavra']}</b>", styles["Normal"])
        ]
        linha.append(celula)

        if len(linha) == 4:
            tabela.append(linha)
            linha = []

    if linha:
        tabela.append(linha)

    table = Table(tabela)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))

    elementos.append(table)
    elementos.append(Paragraph("<br/>", styles["Normal"]))
    elementos.append(
        Paragraph("<small>Pictogramas: ARASAAC – CC BY-NC-SA 4.0</small>", styles["Normal"])
    )

    doc.build(elementos)
    return nome_arquivo

# ===============================
# INTERFACE
# ===============================

st.subheader("👤 Paciente")
paciente = st.text_input("Nome do paciente")

st.subheader("💬 Comunicação")
texto = st.text_input("Ex: ir à casa da vovó")

if st.button("🧩 Gerar prancha") and texto and paciente:
    palavras = limpar_palavras(gerar_palavras_caa(texto))
    itens = []

    for palavra in palavras:
        opcoes = buscar_opcoes_arasaac(palavra)
        if opcoes:
            itens.append({
                "palavra": palavra,
                "pid": opcoes[0]["_id"],
                "opcoes": opcoes
            })

    st.session_state.prancha_atual = {
        "paciente": paciente,
        "itens": itens
    }

# ===============================
# EDIÇÃO DA PRANCHA
# ===============================

if st.session_state.prancha_atual:
    st.subheader("🧩 Editar prancha antes de salvar")

    for idx, item in enumerate(st.session_state.prancha_atual["itens"]):
        st.markdown(f"**{item['palavra']}**")

        cols = st.columns(len(item["opcoes"]))
        for col, opcao in zip(cols, item["opcoes"]):
            with col:
                img_url = f"https://api.arasaac.org/api/pictograms/{opcao['_id']}"
                if st.button("Selecionar", key=f"{idx}_{opcao['_id']}"):
                    item["pid"] = opcao["_id"]
                st.image(img_url, width=80)

    if st.button("💾 Salvar prancha"):
        st.session_state.pranchas.append(st.session_state.prancha_atual)
        st.session_state.prancha_atual = None
        st.success("Prancha salva com sucesso!")

# ===============================
# PRANCHAS SALVAS
# ===============================

if st.session_state.pranchas:
    st.subheader("📂 Pranchas salvas")

    for i, p in enumerate(st.session_state.pranchas):
        if st.button(f"📄 Gerar PDF – {p['paciente']}", key=i):
            pdf = gerar_pdf(p["paciente"], p["itens"])
            with open(pdf, "rb") as f:
                st.download_button(
                    "⬇️ Baixar PDF",
                    f,
                    file_name=pdf,
                    mime="application/pdf"
                )
