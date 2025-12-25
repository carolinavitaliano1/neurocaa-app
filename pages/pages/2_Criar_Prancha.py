import streamlit as st
from modules.caa import gerar_palavras_caa
from modules.arasaac import buscar_imagem_arasaac
from modules.storage import carregar_dados, salvar_prancha

st.title("🧩 Criar Prancha")

dados = carregar_dados()
paciente = st.selectbox("Selecione o paciente", list(dados.keys()))

texto = st.text_input("Digite a frase")

if st.button("Gerar prancha") and texto and paciente:
    palavras = gerar_palavras_caa(texto)

    st.subheader("Visualização")
    cols = st.columns(min(len(palavras), 6))

    for col, palavra in zip(cols, palavras):
        with col:
            img = buscar_imagem_arasaac(palavra)
            if img:
                st.image(img, width=100)
            st.caption(palavra)

    if st.button("💾 Salvar prancha"):
        salvar_prancha(paciente, palavras)
        st.success("Prancha salva no histórico do paciente!")
