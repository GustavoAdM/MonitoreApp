import streamlit as st
from Src.Database.Queries import (acompanhamento_separacao, acompanhamento_conferencia, acompanhamento_faturamento, bi_tempo_loja, 
                                  acompanhamento_entrega)
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_autorefresh import st_autorefresh
from plotly.graph_objects import Figure, Indicator


def acompanhamento():
    st_autorefresh(interval=20000, key="ACOMPANHAMENTO_VIEW")

    with st.sidebar:
        st.info("Atualização: 20seg")
        empresa = st.pills("Selecione a empresa: ", options=[7, 40, 50, 60])
        pedidos = st.number_input("Consultar Pedido", value=None)

    if empresa is not None:
        col1, col2= st.columns(2)
        try:
            with col1: 
                with st.container(border=True, key="Separação", height=380):
                    st.markdown("Separação", unsafe_allow_html=True)

                    separacao_df = acompanhamento_separacao(cd_empresa=empresa, pedidos=pedidos)
  
                    gb = GridOptionsBuilder.from_dataframe(separacao_df)
                    
                    coluns_name = {"HORA_DATA": "Horario", "PRIORIDADE": "Prioridade", "NR_PEDIDO":"Pedido", "VALOR": "Valor", 
                                   "NM_PESSOA": "Cliente", "CD_VENDEDOR": "Vendedor","SEPARADOR": "Separador"}
                    
                    for old_name, new_name in coluns_name.items():
                        gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=150)
                        if old_name == "NM_PESSOA":
                            gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=250, minWidth=250)
                        elif old_name == "SEPARADOR":
                            gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=120, minWidth=120)
                        
            
                    #gb.configure_pagination(paginationAutoPageSize=True) # Paginação automática
                    gridOptions = gb.build()
                    AgGrid(separacao_df, gridOptions=gridOptions, height=300)  

            with col2:
                with st.container(border=True, height=380, key="Conferencia"): 
                    st.markdown("Conferência", unsafe_allow_html=True)
                    conferencia = acompanhamento_conferencia(cd_empresa=empresa, pedidos=pedidos)    

                    gb2 = GridOptionsBuilder.from_dataframe(conferencia)
                    coluns_name_2 = {"HORA_DATA": "Horario", "PRIORIDADE": "Prioridade", "NR_PEDIDO_2":"Pedido", "VALOR": "Valor", 
                                   "NM_PESSOA": "Cliente", "CD_VENDEDOR": "Vendedor","SEPARADOR": "Separador"}
                    

                    for old_name, new_name in coluns_name_2.items():
                        gb2.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=150)
                        if old_name == "NM_PESSOA":
                            gb2.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=250, minWidth=250)
                        if old_name == "SEPARADOR":
                            gb2.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=120, minWidth=120)
                        
                            

                    gridOptions_2 = gb2.build()
                    AgGrid(conferencia, gridOptions=gridOptions_2, height=300) 

            col3, col4 = st.columns(2)

            with col3:
                with st.container(border=True, height=380, key="Faturamento"): 
                    st.markdown("Faturamento", unsafe_allow_html=True)
                    faturamento = acompanhamento_faturamento(cd_empresa=empresa, pedidos=pedidos)

                    gb3 = GridOptionsBuilder.from_dataframe(faturamento)
                    coluns_name_3 ={"HORA_DATA": "Horario", "PRIORIDADE": "Prioridade", "NR_PEDIDO_3":"Pedido", "VALOR": "Valor", 
                                   "NM_PESSOA": "Cliente", "CD_VENDEDOR": "Vendedor","SEPARADOR": "Separador"}
                    
                    for old_name, new_name in coluns_name_3.items():
                        gb3.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=150)
                        if old_name == "NM_PESSOA":
                            gb3.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=250, minWidth=250)
                        if old_name == "SEPARADOR":
                            gb3.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=120, minWidth=120)
                       
                    gridOptions_2 = gb3.build()
                    AgGrid(faturamento, gridOptions=gridOptions_2, height=300) 

            with col4:
                with st.container(border=True, height=380, key="PENDENTE_ENTREGA"): 
                    st.markdown("Aguardando Entrega - Motoboy & Despache")
                    motoboy_entrega = acompanhamento_entrega(cd_empresa=empresa, pedidos=pedidos)

                    gb4 = GridOptionsBuilder.from_dataframe(motoboy_entrega)

                    coluns_name_4 ={"HORA_DATA": "Horario","STATUS": "Status", "TIPO": "Entrega", "NR_PEDIDO_M":"Pedido", "VALOR": "Valor", "CLIENTE": "Cliente", "ENDERECO": "Endereço",
                                    "CD_VENDEDOR": "Vendedor" }

                    for old_name, new_name in coluns_name_4.items():
                        gb4.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=150)
                        if old_name == "NM_PESSOA":
                            gb4.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=250, minWidth=250)
                        if old_name == "SEPARADOR":
                            gb4.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=120, minWidth=120)

                    gridOptions_3 = gb4.build()
                    AgGrid(motoboy_entrega, gridOptions=gridOptions_3, height=300) 

            with st.container(border=True, height=350, key="BI"):
                st.markdown("Tempo Médio de Pedido por Nível", unsafe_allow_html=True)
                col_balcao, col_motoboy = st.columns(2)

                with col_balcao:
                    df_tempo_loja = bi_tempo_loja(cd_empresa=empresa)
            
                    df_tempo_loja = df_tempo_loja["TEMPO_LOJA"].iloc[0]

                    fig_balcao = Figure(Indicator(
                        mode = "gauge+number",
                        value = df_tempo_loja,
                        #domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Tempo Médio Loja (Min)"},
                        gauge = {
                            'axis': {'range': [0, 60]},
                            'steps': [
                                {'range': [0, 20], 'color': "green"},
                                {'range': [21, 40], 'color': "yellow"},
                                {'range': [41, 60], 'color': "red"}
                            ],
                            'bar': {'color': "darkblue"}}
                    ))
                    # Atualize o layout para definir o tamanho 
                    fig_balcao.update_layout( 
                        width=380, # largura em pixels 
                        height=300 # altura em pixels 
                    )

                    st.plotly_chart(fig_balcao)


            st.markdown("""
            <style> 
                .st-key-ACOMPANHAMENTO_VIEW {
                    width:0px;
                    height:0px;
            }
            </style>""",unsafe_allow_html=True)

        except Exception as e:
            print(f"Erro Processo: {e}")
    else:
        st.warning("Por favor, selecione uma empresa")

    
