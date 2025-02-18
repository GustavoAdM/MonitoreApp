import streamlit as st
from Src.Database.QuerieBi import nome_separadores, separacao_pedido_geral, total_pedidos, total_pedidos_pecas_separador, pedidos_mais_30s
import plotly.express as px
from Utilities.Utilidades import primerio_dia_mes, diff_data, converter_minutos

def view_processo():
    try:
        # Sidebar de seleção
        with st.sidebar:
            # Entrada de datas
            col_dtinicio, col_dtfim = st.columns(2)
            with col_dtinicio:
                dt_inicio = st.date_input("Data Inicio", format="DD/MM/YYYY", value="today") 
            with col_dtfim:
                dt_fim = st.date_input("Data Fim", format="DD/MM/YYYY", value="today")
                
            separadores = nome_separadores(dtInicio=dt_inicio, dtFim=dt_fim)["NM_USUARIO"].tolist()
            separador_selecionado = st.pills("Selecione o Separador", separadores, selection_mode="multi")

            
        # Validação da diferença entre as datas
        if diff_data(data_inico=dt_inicio, data_fim=dt_fim, diff=30):
            # Layout para os gráficos
            col1, col2 = st.columns([2,1], border=True)
            with col1:
                # Grafico de Pedidos Gerais
                pedidos_geral_df = separacao_pedido_geral(dt_incio=dt_inicio, dt_fim=dt_fim, separador=separador_selecionado)

                # Converter DT_PEDIDO para string
                pedidos_geral_df["DT_PEDIDO"] = pedidos_geral_df["DT_PEDIDO"].astype(str)

                # Criar uma nova coluna combinando data e nome
                pedidos_geral_df["Data_Nome"] = pedidos_geral_df["DT_PEDIDO"] + " - " + pedidos_geral_df["NM_USUARIO"]

                # Renomear as colunas
                pedidos_geral_df.rename(columns={"QT_ITEM": "Quantidade de Itens", 
                                                 "QNT_PEDIDOS": "Número de Pedidos", 
                                                 "Data_Nome": "Data-Nome"}, inplace=True)

                # Criar um dataframe longo para plotly express
                pedidos_geral_df_long = pedidos_geral_df.melt(id_vars=["Data-Nome"], 
                                                            value_vars=["Quantidade de Itens", "Número de Pedidos"], 
                                                            var_name="Metrica", value_name="Valores")

                # Plotar o gráfico de barras
                fig = px.bar(pedidos_geral_df_long, x="Data-Nome", y="Valores", color="Metrica", barmode="group", 
                            title="Quantidade de Itens e Pedidos por Data e Nome de Usuário", height=350)
                fig.update_traces(texttemplate='%{y}', textposition='outside')
                st.plotly_chart(fig)

            with col2:
                sub_col1, sub_col2 = st.columns(2)
                
                # Calcular o total de QT_ITEM e QNT_PEDIDOS
                with sub_col1:
                    total_qt_item = pedidos_geral_df["Quantidade de Itens"].sum()
                    st.metric("Total de Peças", value=f"{total_qt_item:.0f}", border=True)

                with sub_col2:
                    total_qnt_pedidos = pedidos_geral_df["Número de Pedidos"].sum()
                    st.metric("Total de Pedidos", value=f"{total_qnt_pedidos:.0f}", border=True)

                # Métricas adicionais
                col_media, col_pc_peca, col_pc_pedido = st.columns(3)
                with col_media:
                    pedido_menor30s = pedidos_geral_df["QNT_MENOR_30S"].sum()
                    st.metric("Qnt. Ped.Menor 30s", value=pedido_menor30s, border=True)
                
                # Total de pedidos e peças
                totais_pedido_peca = total_pedidos(dt_inicio=dt_inicio, dt_fim=dt_fim)
                with col_pc_peca:
                    total_pecas = totais_pedido_peca["QT_ITEM"].values[0]
                    pc_peca = (total_qt_item * 100) / total_pecas if total_pecas else 0
                    st.metric("% Peças", value=f"{pc_peca:.1f}", border=True, 
                              help="Porcentagem de peças separadas em relação ao total de peças.")

                with col_pc_pedido:
                    total_pedido = totais_pedido_peca["QNT_PEDIDOS"].values[0]
                    pc_pedido = (total_qnt_pedidos * 100) / total_pedido if total_pedido else 0
                    st.metric("% Pedidos", value=f"{pc_pedido:.1f}", border=True, 
                              help="Porcentagem de pedidos separados em relação ao total de pedidos.")

                # Tempo total e tempo médio
                col_tempo, col_m_tempo = st.columns(2)
                with col_tempo:
                    tempo = converter_minutos(pedidos_geral_df["TEMPO_TOTAL"].sum() / 60)
                    st.metric("Tempo Total", value=f"{tempo[0]}m:{tempo[1]}s", border=True)

                with col_m_tempo:
                    tempo_medio = pedidos_mais_30s(dataInicio=dt_inicio, dataFim=dt_fim, separador=separador_selecionado)
                    tempo_medio = converter_minutos(tempo_medio["TEMPO_MEDIO"].values[0])
                    st.metric("Tempo Médio por Pedido", value=f"{tempo_medio[0]}m:{tempo_medio[1]}s", border=True)

        else:
            st.warning("A diferença entre as datas não deve ser maior que 30 dias.")

        # Total por Separador
        col_pie, col_peca, col_extara = st.columns(3)
        df_total_peca_pedido = total_pedidos_pecas_separador(dataInicio=dt_inicio, DataFim=dt_fim) 
        with col_pie:
            with st.container(key="PieSeparadorPedidos", height=400):
                fig2 = px.pie(df_total_peca_pedido, values="N_PEDIDOS", names='NM_USUARIO', title="Percentual de Pedidos por Separadores", height=400,
                            labels={"NM_USUARIO": "Separador", "N_PEDIDOS": "Qnt Pedidos"})
                st.plotly_chart(fig2)

        with col_peca:
            with st.container(key="PieSeparadorPeças", height=400):
                fig2 = px.pie(df_total_peca_pedido, values="QT_ITEM", names='NM_USUARIO', title="Percentual de Peças por Separadores", height=400,
                            labels={"NM_USUARIO": "Separador", "QT_ITEM": "Qnt Peças"})
                st.plotly_chart(fig2)
    
    except Exception as e:
        print(f"Erro ViewProcesso: {e}")
