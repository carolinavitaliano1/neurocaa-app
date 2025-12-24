import streamlit as st
import requests
import os
import time
from openai import OpenAI
from openai import RateLimitError

# Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="NeuroCAA",
    layout="wide"
)

st.title("🧠 NeuroCAA – Criador de Pranchas de Comunicação Alternativa")
st.write("Digite uma frase funcional e clique no botão para gerar a prancha.")

# Entrada do usuário
texto = st.text_input("Ex: quero ir ao banheiro")
gerar = st.button("🧩 Gerar prancha")

# Função IA: texto → palavras funcionais
def gerar_palavras_caa(texto):
    prompt = f"""
    Transforme a frase abaixo em palavras funcionais para uma prancha de Comunicação Alternativa.
    Use palavras simples, concretas e funcionais.
    Não use artigos desnecessários.
    Retorne apenas uma lista separada por vírgulas.

    Frase: {texto}
    """

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )

        palavras = resposta.choices[0].message.content.split(",")
        return [p.strip().lower() for p in palavras]

    except RateLimitError:
        st.warning("⏳ Limite temporário atingido. Aguarde alguns segundos e tente novamente.")
        time.sleep(3)
        return []

    except Exception as e:
        st.error("Erro ao gerar a prancha.")
        return []

# Função ARASAAC: palavra → pictograma
def buscar_imagem_arasaac(palavra):
    url = f"https://api.arasaac.org/api/pictograms/pt/{palavra}"
    r = requests.get(url)

    if r.status_code == 200 and r.json():
        picto_id = r.json()[0]["_id"]
        return f"https://api.arasaac.org/api/pictograms/{picto_id}"

    return None

# Geração da prancha
if gerar and texto:
    palavras = gerar_palavras_caa(texto)

    if palavras:
        st.subheader("🧩 Prancha gerada")
        cols = st.columns(len(palavras))

        for col, palavra in zip(cols, palavras):
            with col:
                img = buscar_imagem_arasaac(palavra)
                if img:
                    st.image(img, width=120)
                st.markdown(f"**{palavra}**")

