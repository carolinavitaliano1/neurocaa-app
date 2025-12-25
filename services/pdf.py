from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import requests
import os
import uuid

def baixar_imagem(url):
    nome = f"temp_{uuid.uuid4().hex}.png"
    r = requests.get(url)
    if r.status_code == 200 and r.content:
        with open(nome, "wb") as f:
            f.write(r.content)
        return nome
    return None

def gerar_pdf(paciente, palavras):
    nome_pdf = f"prancha_{paciente.replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(nome_pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph(f"<b>Paciente:</b> {paciente}", styles["Title"]))
    elementos.append(Paragraph("<br/>", styles["Normal"]))

    tabela = []
    linha = []
    arquivos_temp = []

    for palavra in palavras:
        url = f"https://api.arasaac.org/api/pictograms/pt/{palavra}"
        img_path = baixar_imagem(url)

        if img_path:
            arquivos_temp.append(img_path)
            conteudo = [
                Image(img_path, width=70, height=70),
                Paragraph(palavra, styles["Normal"])
            ]
        else:
            # fallback seguro: palavra escrita
            conteudo = Paragraph(palavra, styles["Normal"])

        linha.append(conteudo)

        if len(linha) == 4:
            tabela.append(linha)
            linha = []

    if linha:
        tabela.append(linha)

    # 🔐 PROTEÇÃO FINAL (NUNCA TABELA VAZIA)
    if not tabela:
        tabela = [[Paragraph("Nenhum pictograma disponível.", styles["Normal"])]]

    table = Table(tabela)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))

    elementos.append(table)
    elementos.append(Paragraph("<br/>", styles["Normal"]))
    elementos.append(
        Paragraph(
            "<small>Pictogramas: ARASAAC – Licença CC BY-NC-SA 4.0</small>",
            styles["Normal"]
        )
    )

    doc.build(elementos)

    # limpa arquivos temporários
    for f in arquivos_temp:
        if os.path.exists(f):
            os.remove(f)

    return nome_pdf
