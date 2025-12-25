import streamlit as st
from modules.storage import carregar_dados
from modules.arasaac import buscar_imagem_arasaac

st.title("📂 Histórico por paciente")

dados = carregar_dados()
paciente = st.selectbox("Paciente", list(dados.keys()))

for i, prancha in enumerate(dados[paciente]["pranchas"]):
    st.markdown(f"### Prancha {i+1}")
    cols = st.columns(min(len(prancha), 6))

    for col, palavra in zip(cols, prancha):
        with col:
            img = buscar_imagem_arasaac(palavra)
            if img:
                st.image(img, width=80)
            st.caption(palavra)
