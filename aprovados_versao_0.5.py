import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader

# Função para normalizar nomes (remover acentos e ajustar formatação)
def normalize_name(name):
    replacements = str.maketrans(
        "ÁÀÂÃÄÅÇÉÈÊËÍÌÎÏÑÓÒÔÕÖÚÙÛÜÝáàâãäåçéèêëíìîïñóòôõöúùûüýÿ",
        "AAAAAACEEEEIIIINOOOOOUUUUYaaaaaaceeeeiiiinooooouuuuyy"
    )
    return name.translate(replacements).lower().strip()

# Função para extrair nomes completos do PDF
def extract_approved_names_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    # Regex para capturar nomes completos (nome e sobrenome)
    matches = re.findall(r'\b[A-ZÀ-Ú][A-ZÀ-Ú]+\s[A-ZÀ-Ú ]+\b', text)
    return {normalize_name(name) for name in matches}

# Configuração da interface
st.title("Comparador de Alunos Aprovados")
st.write("Carregue um arquivo CSV com os nomes dos alunos e um ou mais PDFs com as listas de aprovados.")

# Upload dos arquivos
csv_file = st.file_uploader("Carregar arquivo CSV", type=["csv"])
pdf_files = st.file_uploader("Carregar arquivos PDF", type=["pdf"], accept_multiple_files=True)

if csv_file and pdf_files:
    # Processar o arquivo CSV
    df_csv = pd.read_csv(csv_file)
    csv_names = {normalize_name(name) for name in df_csv.iloc[:, 0]}  # Ajuste para a coluna correta

    # Processar os PDFs
    results = []
    for pdf_file in pdf_files:
        approved_names = extract_approved_names_from_pdf(pdf_file)
        # Comparar nomes do CSV com os nomes do PDF
        common_names = csv_names.intersection(approved_names)
        for name in common_names:
            results.append({"Nome": name, "Arquivo PDF": pdf_file.name})

    # Exibir resultados
    if results:
        st.success("Alunos aprovados encontrados!")
        results_df = pd.DataFrame(results)
        st.dataframe(results_df)

        # Download dos resultados
        csv_download = results_df.to_csv(index=False).encode("utf-8")
        st.download_button("Baixar resultados como CSV", data=csv_download, file_name="alunos_aprovados.csv")
    else:
        st.warning("Nenhum aluno aprovado foi encontrado nos PDFs enviados.")
