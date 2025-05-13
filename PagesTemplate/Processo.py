import streamlit as st
from Src.Database.Queries import (acompanhamento_separacao, acompanhamento_conferencia, acompanhamento_faturamento, bi_tempo_loja, 
                                  acompanhamento_entrega, tempo_separacao, quantidade_aguardando)
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_autorefresh import st_autorefresh
from plotly.graph_objects import Figure, Indicator


def acompanhamento():
    st_autorefresh(interval=20000, key="ACOMPANHAMENTO_VIEW")

    with st.sidebar:
        st.info("Atualização: 20seg")
        empresa = st.pills("Selecione a empresa: ", options=[7, 40, 50, 60])
        pedidos = st.number_input("Consultar Pedido", value=0)
        vendedor = st.number_input("Consultar Vendedor", value=0)

    if empresa is not None:
        col1, col2= st.columns(2)
        try:

            # Separação Tabela
            with col1: 
                with st.container(border=True, key="Separação", height=420):
                    st.markdown("Separação", unsafe_allow_html=True)

                    separacao_df = acompanhamento_separacao(cd_empresa=empresa, pedidos=pedidos, cd_vendedor=vendedor)
  
                    gb = GridOptionsBuilder.from_dataframe(separacao_df)
                    
                    coluns_name = {"HORA_DATA": "Horario", "PRIORIDADE": "Prioridade", "NR_PEDIDO":"Pedido", "VALOR": "Valor", 
                                   "NM_PESSOA": "Cliente", "CD_VENDEDOR": "Vendedor","SEPARADOR": "Separador", "TEMPO": "Separação"}
                    
                    for old_name, new_name in coluns_name.items():
                        gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=150)
                        if old_name == "NM_PESSOA":
                            gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=150, minWidth=150)
                        elif old_name == "SEPARADOR":
                            gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=120, minWidth=120)
                        elif old_name == "VALOR":
                            gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=85, minWidth=85)
                        elif old_name == "TEMPO":
                            gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=110, minWidth=110)
                        elif old_name == "CD_VENDEDOR":
                            gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=110, minWidth=110)
                        
            
                    #gb.configure_pagination(paginationAutoPageSize=True) # Paginação automática
                    gridOptions = gb.build()
                    AgGrid(separacao_df, gridOptions=gridOptions, height=300, enable_enterprise_modules=True) 
            # Separação Indicadores
            df_separacao = tempo_separacao(cd_empresa=empresa)
            with col2:
                with st.container(border=True, key="separacao_indicadores", height=420):
                    col11, col12 = st.columns(2)
                    with col11:
                        espera = df_separacao["MEDIA_ESPERA"].values[0]
                        fig_balcao = Figure(Indicator(
                            mode = "gauge+number",
                            value = espera,
                            title = {'text': "T.M Aguardando Separação"},
                            gauge = {
                                'axis': {
                                    'range': [0, 60],
                                    'tickmode': 'linear',
                                    'dtick': 5  # Mostra os ticks de 5 em 5
                                },
                                'steps': [
                                    {'range': [0, 5], 'color': "green"},
                                    {'range': [5, 10], 'color': "yellow"},
                                    {'range': [10, 60], 'color': "red"}
                                ],
                                'bar': {'color': "darkblue"}}
                        ))
                        # Atualize o layout para definir o tamanho 
                        fig_balcao.update_layout( 
                            width=250, # largura em pixels 
                            height=200, # altura em pixels 
                            margin=dict(l=20, r=20, t=50, b=0)
                        )
                        st.plotly_chart(fig_balcao,key="espera_tm")
                    with col12:
                        separacao = df_separacao["MEDIA_SEPARACAO"].values[0]
                        fig_balcao_2 = Figure(Indicator(
                            mode = "gauge+number",
                            value = separacao,
                            title = {'text': "T.M Separação"},
                            gauge = {
                                'axis': {
                                    'range': [0, 60],
                                    'tickmode': 'linear',
                                    'dtick': 5  # Mostra os ticks de 5 em 5
                                },
                                'steps': [
                                    {'range': [0, 3], 'color': "green"},
                                    {'range': [3, 10], 'color': "yellow"},
                                    {'range': [10, 60], 'color': "red"}
                                ],
                                'bar': {'color': "darkblue"}}
                        ))
                        # Atualize o layout para definir o tamanho 
                        fig_balcao_2.update_layout( 
                            width=250, # largura em pixels 
                            height=200, # altura em pixels 
                            margin=dict(l=20, r=20, t=50, b=0)
                        )
                        st.plotly_chart(fig_balcao_2, key="separacao_tm")

                    col13, col14 = st.columns(2)
                    with col13:
                        quantidade_aguard = quantidade_aguardando(cd_empresa=empresa)
                        fig_aguar_bullet = Figure(Indicator(
                            mode = "number+gauge+delta",
                            gauge = {
                                'shape': "bullet",
                                'axis': {
                                    'range': [0, 15],
                                    'dtick': 5 
                                },
                            
                                
                                },
                            value = quantidade_aguard["QNTD"].values[0],
                            title = {'text': "Em Espera"})
                        )
                        fig_aguar_bullet.update_layout( 
                            width=400, # largura em pixels 
                            height=150, # altura em pixels 
                            margin=dict(l=120, r=0, t=0, b=50)
                        )
                        st.plotly_chart(fig_aguar_bullet)
                    
                    with col14:

                        total_separacao = df_separacao["MEDIA_TOTAL_SEPARACAO"].values[0]
                        fig_balcao_3 = Figure(Indicator(
                            mode = "gauge+number",
                            value = total_separacao,
                            title = {'text': "T.M Total da Separação"},
                            gauge = {
                                'axis': {
                                    'range': [0, 60],
                                    'tickmode': 'linear',
                                    'dtick': 5  # Mostra os ticks de 5 em 5
                                },
                                'steps': [
                                    {'range': [0, 10], 'color': "green"},
                                    {'range': [10, 30], 'color': "yellow"},
                                    {'range': [30, 60], 'color': "red"}
                                ],
                                'bar': {'color': "darkblue"}}
                        ))
                        # Atualize o layout para definir o tamanho 
                        fig_balcao_3.update_layout( 
                            width=250, # largura em pixels 
                            height=200, # altura em pixels 
                            margin=dict(l=20, r=20, t=30, b=0)
                        )
                        st.plotly_chart(fig_balcao_3, key="total_separacao")

            ### Conferencia ##
            col1_2, col2_2 = st.columns(2)
            with col1_2:
                with st.container(border=True, height=380, key="Conferencia"): 
                    st.markdown("Conferência", unsafe_allow_html=True)
                    conferencia = acompanhamento_conferencia(cd_empresa=empresa, pedidos=pedidos, cd_vendedor=vendedor)    

                    gb2 = GridOptionsBuilder.from_dataframe(conferencia)
                    coluns_name_2 = {"HORA_DATA": "Horario", "PRIORIDADE": "Prioridade", "NR_PEDIDO_2":"Pedido", "VALOR": "Valor", 
                                   "NM_PESSOA": "Cliente", "CD_VENDEDOR": "Vendedor","SEPARADOR": "Separador", "TEMPO_CONFERENCIA": "Conferencia"}
                    

                    for old_name, new_name in coluns_name_2.items():
                        gb2.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=150)
                        if old_name == "NM_PESSOA":
                            gb2.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=250, minWidth=250)
                        elif old_name == "SEPARADOR":
                            gb2.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=120, minWidth=120)
                        elif old_name == "VALOR":
                            gb2.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=85, minWidth=85)     

                    gridOptions_2 = gb2.build()
                    AgGrid(conferencia, gridOptions=gridOptions_2, height=300, enable_enterprise_modules=True) 

            with col2_2:
                with st.container(border=True, key="COnferencia Indicador", height=380):
                    conferencia_t = df_separacao["MEDIA_CONFERENCIA"].values[0]
                    fig_balcao_4 = Figure(Indicator(
                        mode = "gauge+number",
                        value = conferencia_t,
                        title = {'text': "T.M Conferencia"},
                        gauge = {
                            'axis': {
                                'range': [0, 60],
                                'tickmode': 'linear',
                                'dtick': 5  # Mostra os ticks de 5 em 5
                            },
                            'steps': [
                                {'range': [0, 10], 'color': "green"},
                                {'range': [10, 30], 'color': "yellow"},
                                {'range': [30, 60], 'color': "red"}
                            ],
                            'bar': {'color': "darkblue"}}
                    ))
                    # Atualize o layout para definir o tamanho 
                    fig_balcao_4.update_layout( 
                        width=250, # largura em pixels 
                        height=200, # altura em pixels 
                        margin=dict(l=20, r=20, t=50, b=0)
                    )
                    st.plotly_chart(fig_balcao_4, key="CONFERENCIA")

            
            col31, col32 = st.columns(2)

            with col31:
                with st.container(border=True, height=380, key="Faturamento"): 
                    st.markdown("Faturamento", unsafe_allow_html=True)
                    faturamento = acompanhamento_faturamento(cd_empresa=empresa, pedidos=pedidos, cd_vendedor=vendedor)

                    gb3 = GridOptionsBuilder.from_dataframe(faturamento)
                    coluns_name_3 ={"HORA_DATA": "Horario", "PRIORIDADE": "Prioridade", "NR_PEDIDO_3":"Pedido", "VALOR": "Valor", 
                                   "NM_PESSOA": "Cliente", "CD_VENDEDOR": "Vendedor","SEPARADOR": "Separador"}
                    
                    for old_name, new_name in coluns_name_3.items():
                        gb3.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=150)
                        if old_name == "NM_PESSOA":
                            gb3.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=150, minWidth=150)
                        elif old_name == "SEPARADOR":
                            gb3.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=120, minWidth=120)
                       
                    gridOptions_2 = gb3.build()
                    AgGrid(faturamento, gridOptions=gridOptions_2, height=340, enable_enterprise_modules=True) 
            with col32:
                pass

            col43, col44 = st.columns(2)
            with col43:
                with st.container(border=True, height=380, key="PENDENTE_ENTREGA"): 
                    st.markdown("Aguardando Entrega - Motoboy & Despache")
                    motoboy_entrega = acompanhamento_entrega(cd_empresa=empresa, pedidos=pedidos, cd_vendedor=vendedor)

                    gb4 = GridOptionsBuilder.from_dataframe(motoboy_entrega)

                    coluns_name_4 ={"HORA_DATA": "Horario","STATUS": "Status", "TIPO": "Entrega", "NR_PEDIDO_M":"Pedido", "VALOR": "Valor", "CLIENTE": "Cliente", "ENDERECO": "Endereço",
                                    "CD_VENDEDOR": "Vendedor" }

                    for old_name, new_name in coluns_name_4.items():
                        gb4.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=150)
                        if old_name == "NM_PESSOA":
                            gb4.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=150, minWidth=150)
                        if old_name == "SEPARADOR":
                            gb4.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "16px"}, maxWidth=120, minWidth=120)

                    gridOptions_3 = gb4.build()
                    AgGrid(motoboy_entrega, gridOptions=gridOptions_3, height=300, enable_enterprise_modules=True) 

              

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

    
