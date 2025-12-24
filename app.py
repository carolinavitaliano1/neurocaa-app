import streamlit as st
import requests
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="NeuroCAA", layout="wide")

st.title("🧠 NeuroCAA – Criador de Pranchas de Comunicação")

st.write("Digite o que a pessoa quer comunicar.")

texto = st.text_input("Ex: quero comer banana")

def gerar_palavras_caa(texto):
    prompt = f"""
    Transforme a frase abaixo em palavras funcionais para uma prancha de Comunicação Alternativa.
    Use palavras simples e concretas.
    Retorne apenas uma lista separada por vírgulas.

    Frase: {texto}
    """

    resposta = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return [p.strip().lower() for p in resposta.choices[0].message.content.split(",")]

def buscar_imagem_arasaac(palavra):
    url = f"https://api.arasaac.org/api/pictograms/pt/{palavra}"
    r = requests.get(url)
    if r.status_code == 200 and r.json():
        picto_id = r.json()[0]["_id"]
        return f"https://api.arasaac.org/api/pictograms/{picto_id}"
    return None

if texto:
    palavras = gerar_palavras_caa(texto)

    st.subheader("🧩 Prancha")
    cols = st.columns(len(palavras))

    for col, palavra in zip(cols, palavras):
        with col:
            img = buscar_imagem_arasaac(palavra)
            if img:
                st.image(img, width=120)
            st.markdown(f"**{palavra}**")
