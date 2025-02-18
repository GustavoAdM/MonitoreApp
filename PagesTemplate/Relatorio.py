import streamlit as st
from Utilities.Utilidades import primerio_dia_mes, data_atual
from Src.Database.QuerieRelatorio import vendedores, relatorio_vendedor
from Src.GerarRelatorio.Relatorio_Vendedor import PDF


def formatar_nome_vendedor(vendedor):
    """Formata o nome do vendedor removendo sobrenome e extrai o nome completo"""
    if vendedor is not None:
        partes = vendedor.split('-')
        nome_completo = partes[1].strip()  # Obtém o nome completo
        nome_partes = nome_completo.split()  # Divide o nome completo em partes
        return ' '.join(nome_partes[:-1])  # Remove o sobrenome
    return vendedor


def gerar_pdf(vendedor, dados_relatorio, nome_arquivo):
    """Gera o PDF com os dados fornecidos"""
    pdf = PDF()
    pdf.add_page()
    pdf.sub_header(subs_header=["Dt Emissão", "Nota Fiscal", "Nome Pessoa", "Quantidade", "Valor Nota"])
    pdf.chapter_title(vendedor)
    pdf.chapter_body(data=dados_relatorio)
    pdf.summary()
    pdf.output(f'Relatorio/{nome_arquivo}.pdf')


# Função para extrair apenas os números da string
def extrair_numeros(string):
    numeros = string.split('-')[0].strip()
    return numeros

def gerar_relatorio():
    st.markdown("""
    <style>
        .stMainBlockContainer {
            padding: 3rem 15rem        
        }
    </style>
    """, unsafe_allow_html=True)

    # Interface de entrada de dados
    with st.container(border=True, key="GerarRelatorio"):
        col_dtinicio, col_dtfim = st.columns(2)
        with col_dtinicio:
            data_inicio = st.date_input("Dt Início - Pedido", value=primerio_dia_mes(), format="DD/MM/YYYY", key="GR_DTINICIO")
        with col_dtfim:
            data_fim = st.date_input("Dt Fim - Pedido", format="DD/MM/YYYY", key="GR_DTFIM")

        vendedor = st.selectbox("Selecione o vendedor", vendedores()["NM_VENDEDOR"].to_list(), index=None)
        nome_arquivo = st.text_input("Nome do Arquivo (Opcional)", max_chars=50)

        # Formata o nome do vendedor
        vendedor_formatado = formatar_nome_vendedor(vendedor)

        if nome_arquivo == "":
            nome_arquivo = f"{vendedor_formatado}-{data_atual()}"

        # Variável de controle
        relatorio_gerado = False
        
        # Layout para os botões de gerar e baixar o relatório
        col_aux, col_aux_2 = st.columns(2)
        with col_aux:
            btn_gerar, btn_download = st.columns(2)

            with btn_gerar:
                if st.button("Gerar Relatório", key="BTN_Gerar_Relatorio"):
                    if vendedor is not None:
                        # Obter codigo vendedor
                        cod_vendedor = extrair_numeros(vendedor)
                        # Obter os dados do relatório
                        dados_relatorio = relatorio_vendedor(dt_inicio=data_inicio, dt_fim=data_fim, cd_vendedor=cod_vendedor)

                        # Gerar o PDF
                        gerar_pdf(vendedor_formatado, dados_relatorio, nome_arquivo)

                        # Indica que o relatório foi gerado
                        relatorio_gerado = True

            with btn_download:
                if relatorio_gerado:
                    # Caminho para o arquivo PDF
                    file_path = f"relatorio/{nome_arquivo}.pdf"

                    # Lê o arquivo PDF
                    with open(file_path, "rb") as pdf_file:
                        pdf_data = pdf_file.read()

                    # Botão de download
                    st.download_button(label="Baixar PDF", data=pdf_data, file_name=f"{nome_arquivo}.pdf", mime="application/pdf")
