import streamlit as st
from Src.Database.Queries import auditoria_separacao, listar_clientes, listar_vendedor, listar_separador, listar_empresa
from st_aggrid import AgGrid, GridOptionsBuilder


def auditoria():
    st.markdown("""
         <style> 
            .st-key-fizzbuzzcounter {
                width:0px;
                height:0px;
         }
         </style>""",unsafe_allow_html=True)
    
    try:
        with st.sidebar:
            dt_inicio, dt_fim = st.columns(2)
            with dt_inicio:
                data_inicio = st.date_input("Dt Inicio - Pedido", value="today", format="DD/MM/YYYY", key="DATAINICIO")
            with dt_fim:
                data_fim = st.date_input("Dt Fim - Pedido", value="today", format="DD/MM/YYYY", key="DATAFIM")

            empresa, pedido = st.columns(2)
            with empresa:
                cod_empresa = st.multiselect("Empresa", options=[7,40,50,60])
            with pedido:
                numero_pedido = st.number_input(label="Pedido", key="PEDIDO", value=None, min_value=0,)
            
            cliente = st.multiselect(label="Cliente", options=listar_clientes(inico=data_inicio, fim=data_fim), max_selections=4, key="CLIENTE",help="Exibindo todos os clientes no período filtrado entre 'Data Início' e 'Data Fim'")
            separador = st.multiselect(label="Separador", options=listar_separador(inico=data_inicio, fim=data_fim), key="SEPARADOR")
            vendedor = st.multiselect(label="Vendedor", options=listar_vendedor(inico=data_inicio, fim=data_fim),  max_selections=4,key="VENDEDORES",help="Exibindo todos os vendedores no período filtrado entre 'Data Início' e 'Data Fim'")
        
        filtros = {
            "empresa": cod_empresa,
            "pedido": numero_pedido,
            "cliente": cliente,
            "separador": separador,
            "vendedor": vendedor
        }

        # Iniciar a Querie no banco
        read_auditoria = auditoria_separacao(dt_inicio=data_inicio, dt_fim=data_fim, **filtros)

        ####### Criação das Visualizações #########
        #Criação da tabela
        gb = GridOptionsBuilder.from_dataframe(read_auditoria)

        coluns_name = {"CD_EMPRESA":"Empresa", "NIVEL":"Nivel", "NR_PEDIDO": "Pedido", "CLIENTE":"Cliente", "VENDEDOR":"Vendedor",
                    "DT_PEDIDO":"Data Pedido", "SEPARADOR":"Separador", "DT_INICIO": "Inicio Separação", "DT_FIM":"Fim Separação", "TEMPO": "Tempo Separação",
                    "NM_CONFERIDOR":"Conferidor", "INICIO_CONF": "Inicio Conferencia", "FIM_CONF": "Fim Conferência", "TEMPO_CONF": "Tempo Conferencia","CD_USUARIO": "Usuario Faturamento", "INICIO_FAT": "Inicio Faturamento",
                    "FIM_FAT": "Fim Faturamento", "TEMPO_FAT": "Tempo Faturamento"}
        
        # Customizar Colunas 
        for old_name, new_name in coluns_name.items():
            if old_name in ["CLIENTE", "SEPARADOR", "VENDEDOR"]:
                gb.configure_column(old_name, header_name=new_name, 
                                    cellStyle={"text-align": "left"})
            
                
            else:
                gb.configure_column(old_name, header_name=new_name, cellStyle={"text-align": "center"})
        
        gb.configure_default_column(
            cellStyle={"font-size": "14px"},
        )
        

        AgGrid(read_auditoria, 
            gridOptions=gb.build(), 
            custom_css={
                ".ag-header-cell-text": {"font-size": "14px"}
            }, height=580, enable_enterprise_modules=True
        )
    except Exception as e:
        print(f"Erro Auditoria: {e}")

