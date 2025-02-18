import streamlit as st
from Src.Database.Queries import consultar_estoque

def clear_text_input():
    empresa = st.session_state.get("EMPRESA")
    barra = st.session_state.get("consultar_item")
    
    # Consulta o estoque
    df_item = consultar_estoque(cd_empresa=empresa, cd_codigobarra=barra)

    if not df_item.empty:
        # Ajusta o posicionamento dos containers
        st.html("""
        <style>
            div[data-testid="stVerticalBlockBorderWrapper"]  {
                position: relative;
                top: 10px;
            }
            #ds_secao  {
                margin: 0;    
            }
        </style>
        """)
        
        with st.container(border=True, height=500, key="INFO_ITEM"):
            # caso contrário, mostre em cada container.
            st.html(f'<h1 id="ds_secao">Seção: {df_item['DS_SECAO'].values[0]}</h1>')
            for idx, row in df_item.iterrows():
                
                with st.container(border=True, key=f"sub_info_{idx}", height=75):
                    st.html(f"""
                        <p style="font-size: 16px; display: flex; justify-content: space-between; margin: 0;">
                            <span>Desc: {row['DS_ITEM']}</span>
                            <span>Cod Barra: {row['CD_CODIGOBARRA']}</span>
                            <span>Marca: {row['DS_MARCA']}</span>
                            <span>Local: {row['DS_LOCAL']}</span>
                            <span>Fornecedor: {row['CD_FORNECEDOR1']}</span>
                            <span>Estoque: {row['QT_ESTOQ']}</span>
                        </p>
                    """)
    else:
        st.warning("Item não localizado")
    # Limpa o campo de entrada
    st.session_state.consultar_item = ''

def estoque_wms():
    with st.sidebar:
        empresa = st.pills("Selecione a empresa", [7, 40, 50, 60], key="EMPRESA")
    
    if empresa:        
        st.text_input(
            label="Código de Barra",
            key="consultar_item",
            on_change=clear_text_input,
            max_chars=15
        )
    else:
        st.warning("Selecione uma empresa")
