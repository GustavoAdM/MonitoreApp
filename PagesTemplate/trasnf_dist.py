import streamlit as st
from Src.Database.QuerieBi import Qtrasnferencia_dist, Qpendente_transfer
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_autorefresh import st_autorefresh

def dist_transferencia():
    st_autorefresh(interval=10000, key="trasn_refresh")
    with st.sidebar:
        cod_empresa = st.selectbox(label="Empresa", options=[52])
    
    col1,col2 = st.columns(2, border=True)
    
    with col1:
        df_querie = Qtrasnferencia_dist(cd_empresa=cod_empresa)
        gb = GridOptionsBuilder.from_dataframe(df_querie)

        coluns_name = {"CD_DIST": "Cod.", "DS_ITEM": "Descrição", "QT_DISPONIVEL": "Qt Disponivel",
                    "QT_SOLICITADA":"Qt Transferir"}

        for old_name, new_name in coluns_name.items():
            gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "14px"}, maxWidth=600)

            if old_name == "CD_DIST":
                gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "14px"}, maxWidth=90)
            if old_name == "DS_ITEM":
                gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "14px"}, maxWidth=280)

        

        gridOptions = gb.build()
        AgGrid(df_querie, gridOptions=gridOptions, height=600, enable_enterprise_modules=False) 
    
    with col2:
        df_querie_2 = Qpendente_transfer()
        gb_2 = GridOptionsBuilder.from_dataframe(df_querie_2)

        coluns_name2 = {"CD_ITEM": "Cod.", "DS_ITEM": "Descrição", "QT_ITEM": "Qt Pendente",
                    "NR_NOTAFISCAL":"Nr Nota Fornec."}

        for old_name, new_name in coluns_name2.items():
            gb_2.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "14px"}, maxWidth=600)

            if old_name == "CD_ITEM":
                gb_2.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "14px"}, maxWidth=90)
            if old_name == "DS_ITEM":
                gb_2.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "14px"}, maxWidth=260)
            if old_name == "NR_NOTAFISCAL":
                gb_2.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "14px"}, maxWidth=140)

        

        gridOptions_2 = gb_2.build()
        AgGrid(df_querie_2, gridOptions=gridOptions_2, height=600, enable_enterprise_modules=False) 
