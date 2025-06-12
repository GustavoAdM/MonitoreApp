from .Connection import db
from .ConnectionV2 import db as db2
import streamlit as st

@st.cache_data()
def buscar_itens(cd_empresa: int):
    slq_cd_grupo = " AND I.CD_GRUPO BETWEEN 40 AND 49"

    if cd_empresa == 7:
        slq_cd_grupo = " AND I.CD_GRUPO BETWEEN 70 AND 79"
    

    _querie = f"""
    SELECT
        {cd_empresa} CD_EMPRESA, I.CD_ITEM, I.DS_ITEM, M.DS_MARCA,
        I.CD_GRUPO AS CD_GRUPO, I.CD_FORNECEDOR1,
        SUBSTRING(I.CD_SUBGRUPO FROM CHAR_LENGTH(I.CD_GRUPO)+1 FOR 3) AS CD_SUBGRUPO,
        SUBSTRING(I.CD_SECAO FROM CHAR_LENGTH(I.CD_SUBGRUPO)+1 FOR 3) AS CD_PECA,
        COALESCE(E.QT_MINIMA, 0) QT_ESTOQUEMIN
    FROM ITEM I
    INNER JOIN MARCA M ON (M.CD_MARCA = I.CD_MARCA)
    LEFT JOIN EXTEND_ESTOQUEMIN E ON (E.CD_EMPRESA = {cd_empresa}
        AND E.CD_ITEM = I.CD_ITEM)
    WHERE I.CD_SECAO IS NOT NULL
        AND I.ST_ATIVO = 'S'
        {slq_cd_grupo}

    """
    return db.read_sql(_querie)
    
def buscar_marcas():
    _querie = f"""
    SELECT DS_MARCA
    FROM MARCA
    """
    return db.read_sql(_querie)


def buscar_mov_bi(cd_empresa: int, cd_item: int):
    empresas = {
        40: (1, 10),
        50: (52, 0),
        52: (52, 0),
        60: (5, 0),
        5: (5, 0),
        7: (7, 0)
    }
    _querie = f"""
    SELECT
        FORMATA_DATA(N.DT_EMISSAO, '%M/%Y') DT_MES,
        SUM(COALESCE(IT.PS_ITEMNOTA, IT.QT_ITEMNOTA)) QT_FAT,
        EXTRACT(MONTH FROM N.DT_EMISSAO) MES,
        EXTRACT(YEAR FROM N.DT_EMISSAO) ANO
    FROM
        NOTA N
        INNER JOIN ITEMNOTA IT ON (IT.CD_EMPRESA = N.CD_EMPRESA
            AND IT.NR_LANCAMENTO = N.NR_LANCAMENTO
            AND IT.TP_NOTA = N.TP_NOTA
            AND IT.CD_SERIE = N.CD_SERIE)
        INNER JOIN ITEM I ON (I.CD_ITEM = IT.CD_ITEM
            AND I.ST_ATIVO = 'S')
        INNER JOIN SECAO S ON (I.CD_SECAO = S.CD_SECAO)
        INNER JOIN MARCA M ON (M.CD_MARCA = I.CD_MARCA)
        INNER JOIN MOVIMENTACAO MO ON (MO.CD_MOVIMENTACAO = IT.CD_MOVIMENTACAO)
    WHERE
        N.ST_NOTA = 'V'
        AND N.TP_NOTA = 'S'
        AND N.CD_EMPRESA IN {empresas[cd_empresa]}
        AND N.DT_EMISSAO BETWEEN PRIMEIRODIAMES(DATEADD(YEAR, -1, CURRENT_DATE)) AND CURRENT_DATE
        AND MO.ST_RECEITA = 'S'
        AND I.CD_ITEM = {cd_item}
    GROUP BY
        DT_MES, ANO, MES
    ORDER BY ANO, MES 

    """
    return db.read_sql(_querie)

def execute_insert_update(cd_item, cd_empresa, qt_minima):
    query = f"""
    MERGE INTO EXTEND_ESTOQUEMIN dst
    USING (SELECT {cd_empresa} AS CD_EMPRESA, {cd_item} AS CD_ITEM, {qt_minima} AS QT_MINIMA FROM RDB$DATABASE) src
    ON (dst.CD_EMPRESA = src.CD_EMPRESA AND dst.CD_ITEM = src.CD_ITEM)
    WHEN MATCHED THEN
        UPDATE SET QT_MINIMA = src.QT_MINIMA
    WHEN NOT MATCHED THEN
        INSERT (CD_EMPRESA, CD_ITEM, QT_MINIMA)
        VALUES (src.CD_EMPRESA, src.CD_ITEM, src.QT_MINIMA)
    """
    db2.execute_UDI(query)