import streamlit as st
from modules.storage import adicionar_paciente, carregar_dados

st.title("👤 Pacientes")

nome = st.text_input("Nome do paciente")

if st.button("➕ Cadastrar paciente"):
    if nome:
        adicionar_paciente(nome)
        st.success("Paciente cadastrado!")
    else:
        st.warning("Digite um nome.")

st.subheader("📋 Pacientes cadastrados")
dados = carregar_dados()

for p in dados.keys():
    st.markdown(f"- {p}")
