from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import requests

def gerar_pdf(paciente, palavras):
    nome = f"prancha_{paciente.replace(' ','_')}.pdf"
    doc = SimpleDocTemplate(nome, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph(f"<b>Paciente:</b> {paciente}", styles["Title"]))
    tabela = []
    linha = []

    for palavra in palavras:
        img_url = f"https://api.arasaac.org/api/pictograms/pt/{palavra}"
        img = Image(img_url, 70, 70)
        linha.append([img, Paragraph(palavra, styles["Normal"])])
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
    elementos.append(
        Paragraph(
            "<small>Pictogramas: ARASAAC – CC BY-NC-SA 4.0</small>",
            styles["Normal"]
        )
    )

    doc.build(elementos)
    return nome
