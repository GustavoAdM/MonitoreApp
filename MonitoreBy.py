import streamlit as st
from PagesTemplate.Auditoria import auditoria
from PagesTemplate.Processo import acompanhamento
from PagesTemplate.ViewProcesso import view_processo
from PagesTemplate.estoqueWMS import estoque_wms
from PagesTemplate.ConexaoIp import capturar_ip
import warnings

warnings.simplefilter(action='ignore', category=UserWarning)

st.set_page_config(layout="wide")

st.markdown("""
<style>
    .stMainBlockContainer {
        padding: 3rem 1rem        
    }
</style>
""", unsafe_allow_html=True)

menu = st.navigation([st.Page(acompanhamento, title="Acompanhamento"),
                      st.Page(auditoria, title="Auditoria"), 
                      st.Page(view_processo, title="View Separação"),
                      st.Page(estoque_wms, title="Estoque WMS"),
                      st.Page(capturar_ip, title="Capturar IP"),
                      #st.Page(gerar_audio, title="Gerar Audio"),
                      ])
menu.run()
