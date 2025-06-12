import streamlit as st
from Src.Database.QuerieEstoque import *
from st_aggrid import AgGrid, GridOptionsBuilder
from math import ceil
from pandas import DataFrame, isna
from plotly.express import bar


def add_to_cache(cod, leadtime, duration, purchase):
    """Adiciona ou atualiza um item no cache da sessão."""
    if 'itens' not in st.session_state:
        st.session_state.itens = []

    # Verifica se o item já existe e atualiza
    for item in st.session_state.itens:
        if item['cod'] == cod:
            item.update(
                {'cod': cod, 'QT_ESTOQUEMIN': purchase})
            return

    # Adiciona um novo item se não existir
    new_item = {'cod': cod,  'QT_ESTOQUEMIN': purchase}
    st.session_state.itens.append(new_item)

def build_sidebar_filters():
    """Constrói os filtros na barra lateral e retorna os valores"""
    with st.sidebar:
        empresa = st.sidebar.selectbox(
            "Empresa", [7, 5, 52], key="EMPRESACOMPRA")
        
        g_col, s_col, i_col = st.columns(3)
        with g_col:
            group = st.number_input(
                "Grupo", value=None, min_value=1, max_value=99, key="GRUPO")
        with s_col:
            sub_group = st.number_input(
                "Sub", value=None, min_value=1, max_value=99, key="SUB")
        with i_col:
            piece = st.number_input(
                "Seção", value=None, min_value=1, max_value=999, key="SECAO")

        # Filtros de texto
        tipo_filtro = st.sidebar.toggle("[Começa com]", key="TIPO_FILTRO")
        desc_peca = st.sidebar.text_input(
            f'{"[Começa com]" if tipo_filtro else "[Contém na]"} - Desc. Peça',
            key="DESC_PECA"
        )
        application = st.sidebar.text_input(
            f'{"[Começa com]" if tipo_filtro else "[Contém na]"} - Aplicação',
            key="APPLICATION"
        )
        peca_fornecedor = st.sidebar.text_input(
            f'{"[Começa com]" if tipo_filtro else "[Contém na]"} - Código Peça Fabricante',
            key="PECA_FORNECEDOR"
        )
        # Filtros avançados
        brand_filter = st.sidebar.multiselect(
            "Selecione a(s) Marcas",
            options=buscar_marcas(),
            key="BRAND_FILTER"
        )
            

    return {
        "empresa": empresa,
        "group": group,
        "sub_group": sub_group,
        "piece": piece,
        "tipo_filtro": tipo_filtro,
        "desc_peca": desc_peca,
        "application": application,
        "peca_fornecedor": peca_fornecedor,
        "brand_filter": brand_filter,
    }

def add_to_cache(cod, leadtime, duration, purchase):
    """Adiciona ou atualiza um item no cache da sessão."""
    if 'itens' not in st.session_state:
        st.session_state.itens = []

    # Verifica se o item já existe e atualiza
    for item in st.session_state.itens:
        if item['cod'] == cod:
            item.update(
                {'cod': cod, 'QT_ESTOQUEMIN': purchase})
            return

    # Adiciona um novo item se não existir
    new_item = {'cod': cod,  'QT_ESTOQUEMIN': purchase}
    st.session_state.itens.append(new_item)

def fetch_data(empresa, **filtros):

    filtros = filtros["filtros"]
    """Busca e prepara os dados do banco"""
    df = buscar_itens(cd_empresa=empresa)


    if "itens" in st.session_state:
        # Atualiza QNT_COMPRAR com base no estado da sessão
        for item in st.session_state.itens:
            cod = item['cod']
            df['QT_ESTOQUEMIN'] = df['QT_ESTOQUEMIN'].astype(float)
            # Pega a quantidade a comprar ou 0 se não existir
            quantity = item.get("QT_ESTOQUEMIN", 0.00)
            if st.session_state.get("ARREDONDAR_VALOR"):
                df.loc[df['CD_ITEM'] == cod,
                       'QT_ESTOQUEMIN'] = ceil(quantity)
            else:
                df.loc[df['CD_ITEM'] == cod,
                       'QT_ESTOQUEMIN'] = round(quantity, 2)

    # Aplicar filtros
    if filtros.get("group"):
        df = df[df["CD_GRUPO"] == filtros.get("group")]
    if filtros.get("sub_group"):
        df = df[df["CD_SUBGRUPO"] == str(filtros.get("sub_group")).zfill(2)]
    if filtros.get("piece"):
        df = df[df["CD_PECA"] == str(filtros.get("piece")).zfill(3)]
    if filtros.get("brand_filter"):
        df = df[df["DS_MARCA"].isin(filtros.get("brand_filter"))]
    if filtros.get("application"):
        df['DS_APLICACAO'] = df['DS_APLICACAO'].fillna('')
        if filtros.get("tipo_filtro"):
            df = df[df["DS_APLICACAO"].str.startswith(
                str(filtros.get("application")).upper())]
        else:
            df = df[df["DS_APLICACAO"].str.contains(
                filtros.get("application"), case=False)]
    if filtros.get("peca_fornecedor"):
        df['CD_FORNECEDOR1'] = df['CD_FORNECEDOR1'].fillna('')
        if filtros.get("tipo_filtro"):
            df = df[df["CD_FORNECEDOR1"].str.startswith(
                str(filtros.get("peca_fornecedor")).upper())]
        else:
            df = df[df["CD_FORNECEDOR1"].str.contains(
                filtros.get("peca_fornecedor"), case=False)]
    if filtros.get("desc_peca"):
        df['DS_ITEM'] = df['DS_ITEM'].fillna('')
        if filtros.get("tipo_filtro"):
            df = df[df["DS_ITEM"].str.startswith(
                str(filtros.get("desc_peca")).upper())]
        else:
            df = df[df["DS_ITEM"].str.contains(
                filtros.get("desc_peca"), case=False)]

    return df

def control_estoque():
    filtro = build_sidebar_filters()
    df = fetch_data(empresa=filtro["empresa"], filtros=filtro)

    df_item = df[["CD_EMPRESA", "CD_ITEM", "DS_ITEM","DS_MARCA", "QT_ESTOQUEMIN"]]
    with st.sidebar:
        geral_qt =st.number_input("Quantidade Estoque", min_value=0)
        if st.button("Processar", use_container_width=True):
            for item in df_item.itertuples():
                add_to_cache(
                    cod=item.CD_ITEM,
                    leadtime=0,
                    duration=0,
                    purchase=geral_qt
                )
            st.rerun()
        if st.button("Atualizar Estoque minimo"):
            select = st.session_state.get("itens")
            for list_item in select:
                if not isinstance(select, DataFrame):
                    pass
                execute_insert_update(cd_item=list_item["cod"], cd_empresa=filtro["empresa"], qt_minima=list_item["QT_ESTOQUEMIN"])


    

    col1, col2 = st.columns(2)

    with col1:
        gb = GridOptionsBuilder.from_dataframe(df_item)

        coluns_name = {"CD_EMPRESA": "Empresa", "CD_ITEM": "Cod. Item","DS_ITEM": "Descrição", 
                       "DS_MARCA": "Marca",
                       "QT_ESTOQUEMIN": "Est. Minimo"}
        gb.configure_selection(selection_mode="single", use_checkbox=True)
        for old_name, new_name in coluns_name.items():
            gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "14px"}, maxWidth=600)
                
            if old_name == "DS_ITEM":
                gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "14px"}, maxWidth=260)
            if old_name == "DS_MARCA":
                gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "14px"}, maxWidth=180)
            if old_name == "QT_ESTOQUEMIN":
                gb.configure_column(old_name, header_name=new_name, cellStyle={"font-size": "14px"}, maxWidth=100)
                
        gridOptions = gb.build()
        grid_response = AgGrid(df_item, gridOptions=gridOptions, height=700, enable_enterprise_modules=False) 
        selected = grid_response.get('selected_rows')


    with col2:
        if not isinstance(selected, DataFrame):
            return

        cod_item = selected["CD_ITEM"].values[0]
        df_mov_item = buscar_mov_bi(cd_empresa=filtro["empresa"], cd_item=cod_item)

        estoque_salvo =  st.session_state.get("itens")
        estoque_bk = estoque_salvo
        if estoque_salvo:
            if estoque_salvo[0].get("cod") == cod_item:
                estoque_salvo = estoque_salvo[0].get("QT_ESTOQUEMIN")
            else:
                estoque_salvo = 0
        else:
            estoque_salvo = 0

        estoque_df = df[df["CD_ITEM"] == cod_item]
        estoque_df = estoque_df["QT_ESTOQUEMIN"].values[0]

        if estoque_df != estoque_salvo:
            estoque_salvo = estoque_df

        valor_estoque = st.number_input("Quantidade Estoque", min_value=0, value=int(estoque_salvo))

        add_to_cache(
                cod=cod_item,
                leadtime=0,
                duration=0,
                purchase=valor_estoque
            )

        
        st.plotly_chart(bar(df_mov_item, x="DT_MES", y="QT_FAT"))
    
