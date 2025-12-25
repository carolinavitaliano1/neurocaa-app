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
    with open(PACIENTES_FILE, "w", encoding="utf-8") as f:
        json.dump(pacientes, f, indent=2, ensure_ascii=False)

def gerar_palavras_caa(frase):
    prompt = f"""
    Transforme a frase abaixo em palavras para Comunicação Alternativa.
    Mantenha artigos, preposições e verbos.
    Retorne apenas palavras separadas por vírgula.

    Frase: {frase}
    """
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80
    )
    return [p.strip().lower() for p in r.choices[0].message.content.split(",")]

def buscar_opcoes_arasaac(palavra):
    url = f"https://api.arasaac.org/api/pictograms/pt/search/{palavra}"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()[:5]  # até 5 opções
    return []

def baixar_imagem(pid, palavra):
    url = f"https://api.arasaac.org/api/pictograms/{pid}"
    path = f"tmp_{palavra}_{pid}.png"
    with open(path, "wb") as f:
        f.write(requests.get(url).content)
    return path

def gerar_pdf(paciente, itens):
    nome = f"prancha_{paciente.replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(nome, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph(f"<b>Paciente:</b> {paciente}", styles["Title"]))
    elementos.append(Paragraph("<br/>", styles["Normal"]))

    tabela = []
    linha = []

    for item in itens:
        if item["img"]:
            conteudo = [
                Image(item["img"], 70, 70),
                Paragraph(item["palavra"], styles["Normal"])
            ]
        else:
            conteudo = Paragraph(item["palavra"], styles["Normal"])

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
    elementos.append(Paragraph("Pictogramas: ARASAAC – Licença CC BY-NC-SA 4.0", styles["Normal"]))

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
        st.session_state["paciente"] = st.selectbox("Paciente ativo", list(pacientes.keys()))

# ===============================
# 🧩 CRIAR PRANCHA
# ===============================
if menu == "🧩 Criar Prancha":
    if "paciente" not in st.session_state:
        st.warning("Selecione um paciente primeiro.")
    else:
        frase = st.text_input("Digite uma frase")

        if st.button("🤖 Gerar prancha com IA"):
            palavras = gerar_palavras_caa(frase)
            itens = []

            for p in palavras:
                opcoes = buscar_opcoes_arasaac(p)
                img = baixar_imagem(opcoes[0]["_id"], p) if opcoes else None
                itens.append({"palavra": p, "img": img, "opcoes": opcoes})

            st.session_state["prancha"] = itens

        if "prancha" in st.session_state:
            st.subheader("Prancha atual")

            cols = st.columns(min(len(st.session_state["prancha"]), 6))

            for col, item in zip(cols, st.session_state["prancha"]):
                with col:
                    if item["img"]:
                        st.image(item["img"], width=100)
                    st.caption(item["palavra"])

                    if item["opcoes"]:
                        escolha = st.selectbox(
                            "Trocar imagem",
                            options=item["opcoes"],
                            format_func=lambda x: x["keywords"][0]["keyword"],
                            key=item["palavra"]
                        )
                        item["img"] = baixar_imagem(escolha["_id"], item["palavra"])

            if st.button("💾 Salvar prancha"):
                pacientes[st.session_state["paciente"]].append(st.session_state["prancha"])
                salvar_dados()
                del st.session_state["prancha"]
                st.success("Prancha salva!")

# ===============================
# 📂 HISTÓRICO
# ===============================
if menu == "📂 Histórico":
    if "paciente" not in st.session_state:
        st.warning("Selecione um paciente.")
    else:
        for i, prancha in enumerate(pacientes[st.session_state["paciente"]]):
            st.markdown(f"### Prancha {i+1}")

            cols = st.columns(min(len(prancha), 6))
            for col, item in zip(cols, prancha):
                with col:
                    if item["img"]:
                        st.image(item["img"], width=80)
                    st.caption(item["palavra"])

            if st.button(f"📄 Gerar PDF {i+1}", key=f"pdf_{i}"):
                pdf = gerar_pdf(st.session_state["paciente"], prancha)
                with open(pdf, "rb") as f:
                    st.download_button(
                        "⬇️ Baixar PDF",
                        f,
                        file_name=pdf,
                        mime="application/pdf"
                    )
