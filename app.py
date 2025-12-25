import streamlit as st

st.set_page_config(
    page_title="NeuroCAA",
    layout="wide"
)

st.title("🧠 NeuroCAA – Comunicação Alternativa")

st.markdown(
    "<small>🖼️ Pictogramas: ARASAAC – Licença CC BY-NC-SA 4.0</small>",
    unsafe_allow_html=True
)

st.info("Use o menu lateral para navegar entre pacientes, criação de pranchas e histórico.")
