import streamlit as st
import requests
import os
import json
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ===============================
# CONFIGURAÇÕES
# ===============================
st.set_page_config(page_title="NeuroCAA", layout="wide")
st.title("🧠 NeuroCAA – Comunicação Alternativa")
st.markdown("🖼️ Pictogramas: ARASAAC – Licença CC BY-NC-SA 4.0")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_PATH = "data"
PACIENTES_FILE = f"{DATA_PATH}/pacientes.json"
os.makedirs(DATA_PATH, exist_ok=True)

# ===============================
# DADOS
# ===============================
if not os.path.exists(PACIENTES_FILE):
    with open(PACIENTES_FILE, "w") as f:
        json.dump({}, f)

with open(PACIENTES_FILE, "r") as f:
    pacientes = json.load(f)

# ===============================
# SIDEBAR
# ===============================
st.sidebar.title("🧠 NeuroCAA")
menu = st.sidebar.radio(
    "Navegação",
    ["👤 Pacientes", "🧩 Criar Prancha", "📂 Histórico"]
)

# ===============================
# FUNÇÕES
# ===============================
def salvar_dados():
    with open(PACIENTES_FILE, "w") as f:
        json.dump(pacientes, f, indent=2, ensure_ascii=False)

def gerar_palavras_caa(frase):
    prompt = f"""
    Transforme a frase abaixo em palavras para Comunicação Alternativa.
    Mantenha artigos, preposições e verbos (ex: quero, e, de).
    Retorne apenas palavras separadas por vírgula.

    Frase: {frase}
    """
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80
    )
    return [p.strip().lower() for p in r.choices[0].message.content.split(",")]

def buscar_imagem(palavra):
    for lang in ["pt", "en"]:
        url = f"https://api.arasaac.org/api/pictograms/{lang}/search/{palavra}"
        r = requests.get(url)
        if r.status_code == 200 and r.json():
            pid = r.json()[0]["_id"]
            img_url = f"https://api.arasaac.org/api/pictograms/{pid}"
            img_path = f"tmp_{palavra}.png"
            with open(img_path, "wb") as f:
                f.write(requests.get(img_url).content)
            return img_path
    return None

def gerar_pdf(paciente, palavras):
    nome = f"prancha_{paciente.replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(nome, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph(f"<b>Paciente:</b> {paciente}", styles["Title"]))
    elementos.append(Paragraph("<br/>", styles["Normal"]))

    tabela = []
    linha = []

    for palavra in palavras:
        img = buscar_imagem(palavra)
        if img:
            conteudo = [
                Image(img, 70, 70),
                Paragraph(palavra, styles["Normal"])
            ]
        else:
            conteudo = Paragraph(palavra, styles["Normal"])

        linha.append(conteudo)

        if len(linha) == 4:
            tabela.append(linha)
            linha = []

    if linha:
        tabela.append(linha)

    if tabela:
        table = Table(tabela)
        table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ]))
        elementos.append(table)

    elementos.append(Paragraph("<br/><br/>", styles["Normal"]))
    elementos.append(
        Paragraph(
            "Pictogramas: ARASAAC – Licença CC BY-NC-SA 4.0",
            styles["Normal"]
        )
    )

    doc.build(elementos)
    return nome

# ===============================
# 👤 PACIENTES
# ===============================
if menu == "👤 Pacientes":
    st.header("Cadastro e Seleção de Pacientes")

    novo = st.text_input("Novo paciente")
    if st.button("➕ Cadastrar"):
        if novo and novo not in pacientes:
            pacientes[novo] = []
            salvar_dados()
            st.success("Paciente cadastrado!")

    if pacientes:
        selecionado = st.selectbox("Paciente ativo", list(pacientes.keys()))
        st.session_state["paciente"] = selecionado

# ===============================
# 🧩 CRIAR PRANCHA
# ===============================
if menu == "🧩 Criar Prancha":
    if "paciente" not in st.session_state:
        st.warning("Selecione um paciente primeiro.")
    else:
        st.subheader(f"Paciente ativo: {st.session_state['paciente']}")

        frase = st.text_input("Digite uma frase")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🤖 Gerar com IA"):
                palavras = gerar_palavras_caa(frase)
                st.session_state["prancha"] = palavras

        with col2:
            if st.button("✋ Criar manual"):
                st.session_state["prancha"] = [frase.lower()]

        if "prancha" in st.session_state:
            st.subheader("Prancha atual")

            palavras = st.session_state["prancha"]
            cols = st.columns(min(len(palavras), 6))

            for col, palavra in zip(cols, palavras):
                with col:
                    img = buscar_imagem(palavra)
                    if img:
                        st.image(img, width=100)
                    st.caption(palavra)

            if st.button("💾 Salvar prancha"):
                pacientes[st.session_state["paciente"]].append(palavras)
                salvar_dados()
                st.success("Prancha salva!")
                del st.session_state["prancha"]

# ===============================
# 📂 HISTÓRICO
# ===============================
if menu == "📂 Histórico":
    if "paciente" not in st.session_state:
        st.warning("Selecione um paciente.")
    else:
        st.header(f"Histórico – {st.session_state['paciente']}")

        pranchas = pacientes[st.session_state["paciente"]]

        for i, prancha in enumerate(pranchas):
            st.markdown(f"### Prancha {i+1}")
            cols = st.columns(min(len(prancha), 6))
            for col, palavra in zip(cols, prancha):
                with col:
                    img = buscar_imagem(palavra)
                    if img:
                        st.image(img, width=80)
                    st.caption(palavra)

            if st.button(f"📄 PDF {i+1}", key=f"pdf_{i}"):
                pdf = gerar_pdf(st.session_state["paciente"], prancha)
                with open(pdf, "rb") as f:
                    st.download_button(
                        "⬇️ Baixar PDF",
                        f,
                        file_name=pdf,
                        mime="application/pdf"
                    )
