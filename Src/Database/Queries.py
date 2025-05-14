from .Connection import db
import streamlit as st
from pandas import DataFrame


def auditoria_separacao(dt_inicio:str, dt_fim:str, **kwargs):
    # Inicia variaveis
    empresa = ""
    pedido = ""
    cliente = ""
    vendedor = ""
    separador = ""

    # Verificado variaveis e moldando para o SQL
    if "empresa" in kwargs:
        if kwargs["empresa"] != []:
            emp_string = ','.join(str(item) for item in kwargs['empresa'])
            empresa = f"AND P.CD_EMPRESA IN ({emp_string})" 
        if kwargs["pedido"] is not None:
            pedido = f"AND P.NR_PEDIDO = {kwargs['pedido']}" 
        if kwargs["cliente"] != []:
            cliente_string = ", ".join(f"'{usuario}'" for usuario in kwargs['cliente'])
            cliente = f"AND PC.NM_PESSOA IN ({cliente_string})"
        if kwargs["vendedor"] != []:
            vendedor_string = ", ".join(f"'{usuario}'" for usuario in kwargs['vendedor'])
            vendedor = f"AND PV.NM_PESSOA IN ({vendedor_string})"
        if kwargs["separador"] != []:
            separador_string = ", ".join(f"'{usuario}'" for usuario in kwargs['separador'])
            separador = f"AND ES.NM_USUARIO IN ({separador_string})"

    _querie = f"""
    SELECT DISTINCT
        P.CD_EMPRESA,
        CASE P.CD_TIPOPEDIDO
            WHEN 1 THEN 'BALCÃO'
            WHEN 2 THEN 'MOTOBOY'
            WHEN 3 THEN 'DESPACHE'
            ELSE 'SEM PRIORIDADE'
        END NIVEL,
        P.NR_PEDIDO,
        PC.NM_PESSOA CLIENTE, PV.NM_PESSOA VENDEDOR,
        CAST(P.DT_PEDIDO||' '||P.HR_PEDIDO AS TIMESTAMP) DT_PEDIDO,
        ES.NM_USUARIO SEPARADOR, ES.DT_INICIO, ES.DT_FIM,
        CASE
            WHEN  DATEDIFF(MINUTE, ES.DT_INICIO, ES.DT_FIM) < 60 THEN CAST( DATEDIFF(MINUTE, ES.DT_INICIO, ES.DT_FIM) AS VARCHAR(5)) || ' MIN'
            ELSE CAST(DATEDIFF(MINUTE, ES.DT_INICIO, ES.DT_FIM) / 60 AS VARCHAR(5)) || 'H ' || CAST(MOD( DATEDIFF(MINUTE, ES.DT_INICIO, ES.DT_FIM), 60) AS VARCHAR(5)) || ' MIN'
        END TEMPO,
        ES.NM_CONFERIDOR, ES.DT_FIM INICIO_CONF, ES.DTFIM_CONF FIM_CONF,
        CASE
            WHEN  DATEDIFF(MINUTE, ES.DT_FIM, ES.DTFIM_CONF) < 60 THEN CAST(DATEDIFF(MINUTE, ES.DT_FIM, ES.DTFIM_CONF) AS VARCHAR(5)) || ' MIN'
            ELSE CAST(DATEDIFF(MINUTE, ES.DT_FIM, ES.DTFIM_CONF) / 60 AS VARCHAR(5)) || 'H ' || CAST(MOD(DATEDIFF(MINUTE, ES.DT_FIM, ES.DTFIM_CONF), 60) AS VARCHAR(5)) || ' MIN'
        END TEMPO_CONF,
        N.CD_USUARIO, ES.DTFIM_CONF INICIO_FAT, CAST(N.DT_EMISSAO||' '||N.HR_NOTA AS TIMESTAMP) FIM_FAT,
        CASE
            WHEN DATEDIFF(MINUTE, ES.DTFIM_CONF, CAST(N.DT_EMISSAO||' '||N.HR_NOTA AS TIMESTAMP)) < 60 THEN CAST(DATEDIFF(MINUTE, ES.DTFIM_CONF, CAST(N.DT_EMISSAO||' '||N.HR_NOTA AS TIMESTAMP)) AS VARCHAR(5)) || ' MIN'
            ELSE CAST(DATEDIFF(MINUTE, ES.DTFIM_CONF, CAST(N.DT_EMISSAO||' '||N.HR_NOTA AS TIMESTAMP)) / 60 AS VARCHAR(5)) || 'H ' || CAST(MOD(DATEDIFF(MINUTE, ES.DTFIM_CONF, CAST(N.DT_EMISSAO||' '||N.HR_NOTA AS TIMESTAMP)), 60) AS VARCHAR(5)) || ' MIN'
        END TEMPO_FAT,
        DATEDIFF(MINUTE, ESP.DT_PEDIDO, CAST(N.DT_EMISSAO||' '||N.HR_NOTA AS TIMESTAMP))||'MIN' TEMPO_TOTAL_SEP,
        DATEDIFF(MINUTE, CAST(P.DT_PEDIDO||' '||P.HR_PEDIDO AS TIMESTAMP), ESP.DT_PEDIDO)||'MIN' TEMPO_PERDIDO_VEND
    FROM
        PEDIDO P
        INNER JOIN EXTEND_SEPARACAO ES ON (ES.CD_EMPRESA = P.CD_EMPRESA
            AND ES.NR_PEDIDO = P.NR_PEDIDO)
        INNER JOIN PESSOA PC ON (PC.CD_PESSOA = P.CD_PESSOA)
        INNER JOIN PESSOA PV ON (PV.CD_PESSOA = P.CD_VENDEDOR)
        INNER JOIN EXTEND_SEPARACAO_TEMPO ESP ON (ESP.CD_EMPRESA = P.CD_EMPRESA
            AND ESP.NR_PEDIDO = P.NR_PEDIDO
            AND ESP.TP_PEDIDO = P.TP_PEDIDO)
        LEFT JOIN RETORNA_CHAVENOTA(P.CD_EMPRESA, P.NR_PEDIDO, P.TP_PEDIDO) RCN ON (1=1)
        LEFT JOIN NOTA N ON (N.CD_EMPRESA = RCN.O_CD_EMPRESA
            AND N.NR_LANCAMENTO = RCN.O_NR_LANCAMENTO
            AND N.CD_SERIE = RCN.O_CD_SERIE
            AND N.TP_NOTA = RCN.O_TP_NOTA)
    WHERE
        P.DT_PEDIDO BETWEEN '{dt_inicio}' AND '{dt_fim}'
        AND P.ST_PEDIDO NOT IN ('C')
        {empresa}
        {pedido}
        {cliente}  
        {vendedor}
        {separador}
        """
    
    df = db.read_sql(query=_querie)
    df["TEMPO"] = df["TEMPO"].fillna("")
    
    return df

def listar_clientes(inico, fim) -> list:
    resultado_df = auditoria_separacao(dt_inicio=inico, dt_fim=fim)
    list_cliente = resultado_df["CLIENTE"].unique().tolist()
    return list_cliente

def listar_vendedor(inico, fim) -> list:
    resultado_df = auditoria_separacao(dt_inicio=inico, dt_fim=fim)
    list_vendedor = resultado_df["VENDEDOR"].unique().tolist()
    return list_vendedor

def listar_separador(inico, fim) -> list:
    resultado_df = auditoria_separacao(dt_inicio=inico, dt_fim=fim)
    list_separador = resultado_df["SEPARADOR"].unique().tolist()
    return list_separador

def listar_empresa(inico, fim) -> list:
    resultado_df = auditoria_separacao(dt_inicio=inico, dt_fim=fim)
    list_empresa = resultado_df["CD_EMPRESA"].unique().tolist()
    return list_empresa


def acompanhamento_separacao(cd_empresa, **filtros):
    sql_pedidos = ""
    sql_vendedor = ""

    if filtros["pedidos"] != 0:
        sql_pedidos = f"AND P.NR_PEDIDO = {filtros['pedidos']}" 
    if filtros["cd_vendedor"] != 0:
        sql_vendedor = f"AND P.CD_VENDEDOR = {filtros['cd_vendedor']}" 

    _querie = f"""
    WITH PEDIDOS_SEPARACAO
    AS (
        SELECT DISTINCT
            FORMATA_DATA(CAST(P.DT_PEDIDO||' '||P.HR_PEDIDO AS TIMESTAMP), '%H:%T %D/%M') HORA_DATA,
            CASE P.CD_TIPOPEDIDO
                WHEN 1 THEN 'Balcão'
                WHEN 2 THEN 'Motoboy'
                WHEN 3 THEN 'Despache'
                ELSE 'Nenhum'
             END PRIORIDADE, P.CD_TIPOPEDIDO,
            P.NR_PEDIDO, PE.NM_PESSOA, P.CD_EMPRESA, PV.NM_PESSOA NM_VENDEDOR, PV.CD_PESSOA CD_VENDEDOR,
            COALESCE(ES.NM_USUARIO, 'Aguardando') SEPARADOR,
            COALESCE(ES.STATUS, 'N') STATUS,
            EX.DT_PEDIDO,
            COALESCE(DATEDIFF(MINUTE, EX.DT_PEDIDO, CURRENT_TIMESTAMP), 1) TEMPO
        FROM
            PEDIDO P

            LEFT JOIN ITEMCONFERENCIAPEDIDO ICP ON (ICP.CD_EMPRESA = P.CD_EMPRESA
                AND ICP.NR_PEDIDO = P.NR_PEDIDO
                AND ICP.TP_PEDIDO = P.TP_PEDIDO)
            LEFT JOIN EXTEND_SEPARACAO ES ON (ES.CD_EMPRESA = P.CD_EMPRESA
                AND ES.NR_PEDIDO = P.NR_PEDIDO)
            INNER JOIN PESSOA PE ON (PE.CD_PESSOA = P.CD_PESSOA)
            INNER JOIN PESSOA PV ON (PV.CD_PESSOA = P.CD_VENDEDOR)
            LEFT JOIN EXTEND_SEPARACAO_TEMPO EX ON (EX.CD_EMPRESA = P.CD_EMPRESA
                AND EX.NR_PEDIDO = P.NR_PEDIDO
                AND EX.TP_PEDIDO = P.TP_PEDIDO)
        WHERE
            P.TP_PEDIDO = 'S'
            AND P.DT_PEDIDO = CURRENT_DATE 
            AND P.CD_EMPRESA IN ({cd_empresa})
            AND ICP.NR_PEDIDO IS NULL
            AND P.ST_PEDIDO NOT IN ('A', 'P', 'C')
            AND P.NR_ORDEMSERVICO IS NULL
            {sql_pedidos}
            {sql_vendedor}
    )
    SELECT
        PE.HORA_DATA,
        PE.PRIORIDADE,
        PE.TEMPO||'Min' TEMPO,
        PE.SEPARADOR,
        PE.NR_PEDIDO,
        PE.NM_PESSOA,
        SUM(IP.VL_TOTAL) VALOR,
        PE.CD_VENDEDOR
        
    FROM PEDIDOS_SEPARACAO PE
    INNER JOIN ITEMPEDIDO IP ON (IP.CD_EMPRESA= PE.CD_EMPRESA
        AND IP.NR_PEDIDO = PE.NR_PEDIDO
        AND IP.TP_PEDIDO = 'S')
    WHERE PE.STATUS <> 'F'
    GROUP BY
        PE.HORA_DATA, PE.PRIORIDADE, PE.NR_PEDIDO, PE.NM_PESSOA,
        PE.CD_VENDEDOR, PE.SEPARADOR, PE.CD_TIPOPEDIDO, PE.TEMPO
    ORDER BY
        COALESCE(PE.CD_TIPOPEDIDO, 4)
    """
    return db.read_sql(query=_querie)

def extend_acompanhamento_1(cd_empresa, **filtros):
    sql_pedidos = ""
    sql_vendedor = ""

    if filtros["pedidos"] != 0:
        sql_pedidos = f"AND P.NR_PEDIDO = {filtros['pedidos']}"
    if filtros["cd_vendedor"] != 0:
        sql_vendedor = f"AND P.CD_VENDEDOR = {filtros['cd_vendedor']}"         

    _querie = f"""
        SELECT
            X.CD_EMPRESA, X.NR_PEDIDO,
            CAST(X.QNT_ITEM * X.TEMPO_MEDIO AS INTEGER) TEMPO
        FROM (
            SELECT
                P.CD_EMPRESA, P.NR_PEDIDO, P.TP_PEDIDO,
                SUM(DATEDIFF(MINUTE, ES.DT_INICIO, ES.DT_FIM)) TEMPO,
                SUM(COALESCE(IP.PS_PEDIDO, IP.QT_PEDIDA)) QNT_ITEM,
                SUM(SUM(DATEDIFF(MINUTE, ES.DT_INICIO, ES.DT_FIM))) OVER () /
                    SUM(SUM(COALESCE(IP.PS_PEDIDO, IP.QT_PEDIDA))) OVER () TEMPO_MEDIO
            FROM
                PEDIDO P
                INNER JOIN ITEMPEDIDO IP ON (IP.CD_EMPRESA = P.CD_EMPRESA
                    AND IP.NR_PEDIDO = P.NR_PEDIDO
                    AND IP.TP_PEDIDO = P.TP_PEDIDO)
                INNER JOIN EXTEND_SEPARACAO ES ON (ES.CD_EMPRESA = P.CD_EMPRESA
                    AND ES.NR_PEDIDO = P.NR_PEDIDO)
            WHERE
                P.TP_PEDIDO = 'S'
                AND P.DT_PEDIDO = CURRENT_DATE
                AND P.CD_EMPRESA IN ({cd_empresa})
                AND P.ST_PEDIDO NOT IN ('C')
                AND P.CD_TIPOPEDIDO IS NOT NULL
                AND P.NR_ORDEMSERVICO IS NULL
                {sql_pedidos}
                {sql_vendedor}
            GROUP BY 1, 2, 3
        ) X
        WHERE X.TEMPO IS NULL
        """
    return db.read_sql(query=_querie)

def acompanhamento_conferencia(cd_empresa, **filtros):
    sql_pedidos = ""
    sql_vendedor = ""
    
    if filtros["pedidos"] != 0:
        sql_pedidos = f"AND P.NR_PEDIDO = {filtros['pedidos']}" 
    if filtros["cd_vendedor"] != 0:
        sql_vendedor = f"AND P.CD_VENDEDOR = {filtros['cd_vendedor']}" 
    
    _querie = f"""
    WITH PEDIDOS_SEPARACAO
    AS (
        SELECT DISTINCT
           FORMATA_DATA(CAST(P.DT_PEDIDO||' '||P.HR_PEDIDO AS TIMESTAMP), '%H:%T %D/%M') HORA_DATA,
            CASE P.CD_TIPOPEDIDO
                WHEN 1 THEN 'Balcão'
                WHEN 2 THEN 'Motoboy'
                WHEN 3 THEN 'Despache'
                ELSE 'Nenhum'
             END PRIORIDADE, P.CD_TIPOPEDIDO,
            P.NR_PEDIDO, PE.NM_PESSOA, P.CD_EMPRESA, PV.NM_PESSOA NM_VENDEDOR, PV.CD_PESSOA CD_VENDEDOR,
            COALESCE(ES.NM_USUARIO, 'Aguardando') SEPARADOR,
            COALESCE(ES.STATUS, 'N') STATUS,
            EX.DT_PEDIDO,
            DATEDIFF(MINUTE, EX.DT_PEDIDO, COALESCE(ES.DTFIM_FAT, CURRENT_TIMESTAMP)) TEMPO_PEDIDO,
            COALESCE(DATEDIFF(MINUTE, ES.DT_FIM, COALESCE(ES.DTFIM_CONF, CURRENT_TIMESTAMP)), 0)||'Min' TEMPO_CONFERENCIA

        FROM
            PEDIDO P
            LEFT JOIN ITEMCONFERENCIAPEDIDO ICP ON (ICP.CD_EMPRESA = P.CD_EMPRESA
                AND ICP.NR_PEDIDO = P.NR_PEDIDO
                AND ICP.TP_PEDIDO = P.TP_PEDIDO)
            INNER JOIN EXTEND_SEPARACAO ES ON (ES.CD_EMPRESA = P.CD_EMPRESA
                AND ES.NR_PEDIDO = P.NR_PEDIDO)
            INNER JOIN EXTEND_SEPARACAO_TEMPO EX ON (EX.CD_EMPRESA = P.CD_EMPRESA
                AND EX.NR_PEDIDO = P.NR_PEDIDO
                AND EX.TP_PEDIDO = P.TP_PEDIDO)
            INNER JOIN PESSOA PE ON (PE.CD_PESSOA = P.CD_PESSOA)
            INNER JOIN PESSOA PV ON (PV.CD_PESSOA = P.CD_VENDEDOR)
            LEFT JOIN PEDIDONOTA PN ON (PN.CD_EMPRPED = P.CD_EMPRESA
                AND PN.NR_PEDIDO = P.NR_PEDIDO
                AND PN.TP_PEDIDO = P.TP_PEDIDO)
        WHERE
            P.TP_PEDIDO = 'S'
            AND P.DT_PEDIDO BETWEEN CURRENT_DATE - 2 AND CURRENT_DATE
            AND ICP.NR_PEDIDO IS NULL
            AND P.CD_EMPRESA IN ({cd_empresa})
            AND ES.STATUS = 'F'
            AND P.ST_PEDIDO NOT IN ('A', 'P', 'C')
            AND P.NR_ORDEMSERVICO IS NULL
            AND PN.NR_LANCAMENTO IS NULL
            {sql_pedidos}
            {sql_vendedor}
    )
    SELECT
        PE.HORA_DATA,
        PE.PRIORIDADE,
        PE.TEMPO_CONFERENCIA,
        PE.NR_PEDIDO NR_PEDIDO_2,
        SUM(IP.VL_TOTAL) VALOR,
        PE.NM_PESSOA,
        PE.CD_VENDEDOR,
        PE.SEPARADOR
    FROM PEDIDOS_SEPARACAO PE
    INNER JOIN ITEMPEDIDO IP ON (IP.CD_EMPRESA= PE.CD_EMPRESA
        AND IP.NR_PEDIDO = PE.NR_PEDIDO
        AND IP.TP_PEDIDO = 'S')
    WHERE PE.STATUS = 'F'
    GROUP BY
        PE.HORA_DATA, PE.PRIORIDADE, PE.NR_PEDIDO, PE.NM_PESSOA,
        PE.CD_VENDEDOR, PE.SEPARADOR, PE.CD_TIPOPEDIDO,PE.TEMPO_CONFERENCIA
    ORDER BY
        COALESCE(PE.CD_TIPOPEDIDO, 4)
    """
    return db.read_sql(query=_querie)


def acompanhamento_faturamento(cd_empresa, **filtros):
    sql_pedidos = ""
    sql_vendedor = ""

    if filtros["pedidos"] != 0:
        sql_pedidos = f"AND P.NR_PEDIDO = {filtros['pedidos']}"
    if filtros["cd_vendedor"] != 0:
        sql_vendedor = f"AND P.CD_VENDEDOR = {filtros['cd_vendedor']}" 
    
    _querie = f"""
    WITH PEDIDOS_SEPARACAO
    AS (
        SELECT DISTINCT
           FORMATA_DATA(CAST(P.DT_PEDIDO||' '||P.HR_PEDIDO AS TIMESTAMP), '%H:%T %D/%M') HORA_DATA,
            CASE P.CD_TIPOPEDIDO
                WHEN 1 THEN 'Balcão'
                WHEN 2 THEN 'Motoboy'
                WHEN 3 THEN 'Despache'
                ELSE 'Nenhum'
             END PRIORIDADE, P.CD_TIPOPEDIDO,
            P.NR_PEDIDO, PE.NM_PESSOA, P.CD_EMPRESA, PV.NM_PESSOA NM_VENDEDOR, PV.CD_PESSOA CD_VENDEDOR,
            COALESCE(ES.NM_USUARIO, 'Aguardando') SEPARADOR,
            COALESCE(ES.STATUS, 'N') STATUS,
            EX.DT_PEDIDO,
            DATEDIFF(MINUTE, EX.DT_PEDIDO, COALESCE(ES.DTFIM_FAT, CURRENT_TIMESTAMP)) TEMPO_PEDIDO,
            COALESCE(DATEDIFF(MINUTE, ES.DTFIM_CONF, COALESCE(ES.DTFIM_FAT, CURRENT_TIMESTAMP)), 0) TEMPO_SEPARACAO
        FROM
            PEDIDO P
            INNER JOIN ITEMCONFERENCIAPEDIDO ICP ON (ICP.CD_EMPRESA = P.CD_EMPRESA
                AND ICP.NR_PEDIDO = P.NR_PEDIDO
                AND ICP.TP_PEDIDO = P.TP_PEDIDO)
            INNER JOIN EXTEND_SEPARACAO ES ON (ES.CD_EMPRESA = P.CD_EMPRESA
                AND ES.NR_PEDIDO = P.NR_PEDIDO)
            INNER JOIN PESSOA PE ON (PE.CD_PESSOA = P.CD_PESSOA)
            INNER JOIN PESSOA PV ON (PV.CD_PESSOA = P.CD_VENDEDOR)
            INNER JOIN EXTEND_SEPARACAO_TEMPO EX ON (EX.CD_EMPRESA = P.CD_EMPRESA
                AND EX.NR_PEDIDO = P.NR_PEDIDO
                AND EX.TP_PEDIDO = P.TP_PEDIDO)
            LEFT JOIN PEDIDONOTA PN ON (PN.CD_EMPRPED = P.CD_EMPRESA
                AND PN.NR_PEDIDO = P.NR_PEDIDO
                AND PN.TP_PEDIDO = P.TP_PEDIDO)
            LEFT JOIN NOTA N ON (N.CD_EMPRESA = PN.CD_EMPRESA
                AND N.NR_LANCAMENTO = PN.NR_LANCAMENTO
                AND N.CD_SERIE = PN.CD_SERIE
                AND N.TP_NOTA = PN.TP_NOTA
                AND N.ST_NOTA = 'V')
        WHERE
            P.TP_PEDIDO = 'S'
            AND P.DT_PEDIDO = CURRENT_DATE
            AND P.CD_EMPRESA IN ({cd_empresa})
            AND N.CD_EMPRESA IS NULL
            AND ES.STATUS = 'F'
            AND P.ST_PEDIDO NOT IN ('A', 'P', 'C')
            AND P.NR_ORDEMSERVICO IS NULL
            AND PN.NR_LANCAMENTO IS NULL
            {sql_pedidos}
            {sql_vendedor}
    )
     SELECT
        PE.HORA_DATA,
        PE.PRIORIDADE,
        PE.NR_PEDIDO NR_PEDIDO_3,
        SUM(IP.VL_TOTAL) VALOR,
        PE.NM_PESSOA,
        PE.CD_VENDEDOR,
        PE.SEPARADOR
    FROM PEDIDOS_SEPARACAO PE
    INNER JOIN ITEMPEDIDO IP ON (IP.CD_EMPRESA= PE.CD_EMPRESA
        AND IP.NR_PEDIDO = PE.NR_PEDIDO
        AND IP.TP_PEDIDO = 'S')
    WHERE PE.STATUS = 'F'
    GROUP BY
        PE.HORA_DATA, PE.PRIORIDADE, PE.NR_PEDIDO, PE.NM_PESSOA,
        PE.CD_VENDEDOR, PE.SEPARADOR, PE.CD_TIPOPEDIDO
    ORDER BY
        COALESCE(PE.CD_TIPOPEDIDO, 4)

    """
    df = db.read_sql(query=_querie)
    return df


def acompanhamento_entrega(cd_empresa, **filtros):
    sql_pedidos = ""
    sql_vendedor = ""

    if filtros["pedidos"] != 0:
        sql_pedidos = f"AND P.NR_PEDIDO = {filtros['pedidos']}" 
    if filtros["cd_vendedor"] != 0:
        sql_vendedor = f"AND P.CD_VENDEDOR = {filtros['cd_vendedor']}" 
        
    _querie = f"""
    SELECT
        FORMATA_DATA(ET.DT_PEDIDO, '%H:%T %D/%M') HORA_DATA,
        CASE
            WHEN RM.ST_REMESSAENTREGA IS NULL THEN 'Aguardando'
            WHEN RM.ST_REMESSAENTREGA = 'I' THEN 'Em viagem'
            ELSE ''
        END  STATUS,
        CASE P.CD_TIPOPEDIDO
            WHEN 2 THEN 'Motoboy'
            ELSE 'Despache'
        END TIPO,
        P.NR_PEDIDO NR_PEDIDO_M,
        SUM(IP.VL_TOTAL) VALOR, PC.NM_PESSOA CLIENTE,
        'Rua '||EP.DS_ENDERECO||', '||COALESCE(EP.NR_ENDERECO, '')||', '||COALESCE(EP.DS_BAIRRO, '') ENDERECO,
        P.CD_VENDEDOR
    FROM
        PEDIDO P
        INNER JOIN PESSOA PC ON (PC.CD_PESSOA = P.CD_PESSOA)
        INNER JOIN EXTEND_SEPARACAO_TEMPO ET ON (ET.CD_EMPRESA = P.CD_EMPRESA
            AND ET.NR_PEDIDO = P.NR_PEDIDO
            AND ET.TP_PEDIDO = P.TP_PEDIDO)
        INNER JOIN ENDERECOPESSOA EP ON (EP.CD_PESSOA = P.CD_PESSOA
            AND EP.CD_ENDERECO = P.CD_ENDERECO)
        INNER JOIN EXTEND_SEPARACAO ES ON (ES.CD_EMPRESA = P.CD_EMPRESA
            AND ES.NR_PEDIDO = P.NR_PEDIDO)
        LEFT JOIN REMESSAENTREGA RM ON (RM.CD_EMPPEDIDO = P.CD_EMPRESA
            AND RM.NR_PEDIDO = P.NR_PEDIDO
            AND RM.TP_PEDIDO = P.TP_PEDIDO)
        INNER JOIN ITEMPEDIDO IP ON (IP.CD_EMPRESA = P.CD_EMPRESA
            AND IP.NR_PEDIDO = P.NR_PEDIDO
            AND IP.TP_PEDIDO = P.TP_PEDIDO)
        INNER JOIN ITEMCONFERENCIAPEDIDO ICP ON (ICP.CD_EMPRESA = IP.CD_EMPRESA
            AND ICP.NR_PEDIDO = IP.NR_PEDIDO
            AND ICP.TP_PEDIDO = IP.TP_PEDIDO
            AND ICP.CD_ITEM = IP.CD_ITEM)
        LEFT JOIN PEDIDONOTA PN ON (PN.CD_EMPRPED = ICP.CD_EMPRESA
            AND PN.NR_PEDIDO = ICP.NR_PEDIDO
            AND PN.TP_PEDIDO = ICP.TP_PEDIDO
            AND PN.CD_ITEM = ICP.CD_ITEM)
        LEFT JOIN NOTA N ON (N.CD_EMPRESA = PN.CD_EMPRESA
            AND N.NR_LANCAMENTO = PN.NR_LANCAMENTO
            AND N.CD_SERIE = PN.CD_SERIE
            AND N.TP_NOTA = PN.TP_NOTA
            AND N.ST_NOTA = 'V'
            AND N.DT_EMISSAO >= CURRENT_DATE - 1)
    WHERE
        P.ST_PEDIDO NOT IN ('C')
        AND P.DT_PEDIDO >= CURRENT_DATE - 1
        AND P.CD_TIPOPEDIDO IN (2, 3)
        AND P.cd_empresa = {cd_empresa}
        AND COALESCE(RM.ST_REMESSAENTREGA, 'A') NOT IN ('C', 'F')
        {sql_pedidos}
        {sql_vendedor}
    GROUP BY
        HORA_DATA, NR_PEDIDO_M, CLIENTE, ENDERECO, P.CD_VENDEDOR, TIPO,
        STATUS
    """
    df = db.read_sql(query=_querie)
    return df

def bi_tempo_loja(cd_empresa):
    _querie = f"""
    SELECT
        CAST(SUM(X.TEMPO) / COUNT(X.NR_PEDIDO) AS INTEGER) TEMPO_LOJA
    FROM (
        SELECT DISTINCT
            P.CD_EMPRESA, P.NR_PEDIDO, DATEDIFF(MINUTE, ET.DT_PEDIDO, ES.DTFIM_CONF) TEMPO
        FROM PEDIDO P
        INNER JOIN EXTEND_SEPARACAO_TEMPO ET ON (ET.CD_EMPRESA = P.CD_EMPRESA
            AND ET.NR_PEDIDO = P.NR_PEDIDO
            AND ET.TP_PEDIDO = P.TP_PEDIDO)
        INNER JOIN EXTEND_SEPARACAO ES ON (ES.CD_EMPRESA = P.CD_EMPRESA
            AND ES.NR_PEDIDO = P.NR_PEDIDO)
        INNER JOIN ITEMCONFERENCIAPEDIDO ICP ON (ICP.CD_EMPRESA = ES.CD_EMPRESA
            AND ICP.NR_PEDIDO = ES.NR_PEDIDO
            AND ICP.TP_PEDIDO = P.TP_PEDIDO)
        WHERE ET.DT_PEDIDO >= DATEADD(HOUR, -3, CURRENT_TIMESTAMP)
            AND P.CD_EMPRESA = {cd_empresa}
            AND P.ST_PEDIDO <> 'C'
    )X
    """
    df= db.read_sql(query=_querie)
    return df

def consultar_estoque(cd_empresa, cd_codigobarra):
    _querie = f"""
    WITH AUXILIAR
    AS (
        SELECT I.CD_SECAO
        FROM ITEM I
        WHERE I.CD_CODIGOBARRA = '{cd_codigobarra}'
    )

    SELECT
        COALESCE(I.CD_CODIGOBARRA, 'N/A') CD_CODIGOBARRA,
        I.CD_ITEM, I.DS_ITEM, S.DS_SECAO,
        LE.DS_LOCAL,
        I.CD_FORNECEDOR1,
        M.DS_MARCA,
        CAST(COALESCE(E.QT_ESTOQUE, 0) AS NUMERIC(15,2))||' '||I.SG_UNIDMED QT_ESTOQ
    FROM AUXILIAR A
    INNER JOIN ITEM I ON (I.CD_SECAO = A.CD_SECAO)
    INNER JOIN ITEMLOCAL IL ON (IL.CD_ITEM = I.CD_ITEM
        AND IL.CD_TIPOLOCAL = CASE {cd_empresa}
                                WHEN 7 THEN 7
                                WHEN 40 THEN 1
                                WHEN 50 THEN 2
                                WHEN 60 THEN 3
                            END)
    INNER JOIN LOCALESTOQUE LE ON (LE.CD_TIPOLOCAL = IL.CD_TIPOLOCAL
        AND LE.CD_LOCAL = IL.CD_LOCAL)
    INNER JOIN SECAO S ON (S.CD_SECAO = I.CD_SECAO)
    LEFT JOIN ESTOQUE E ON (E.CD_ITEM = I.CD_ITEM
        AND E.CD_TIPOLOCAL = IL.CD_TIPOLOCAL
        AND E.CD_LOCAL = IL.CD_LOCAL)
    INNER JOIN MARCA M ON (M.CD_MARCA = I.CD_MARCA)
    PLAN JOIN (JOIN (JOIN (A I INDEX (IDX001_ITEM), S INDEX (PK_SECAO), I INDEX (ITEM_IDX3), IL INDEX (PK_ITEMLOCAL), LE INDEX (PK_LOCALESTOQUE)), E INDEX (RESTOQUE_ITEM)), M INDEX (PK_MARCA))
    ORDER BY IIF(I.CD_CODIGOBARRA = '{cd_codigobarra}', 99999999999, E.QT_ESTOQUE) DESC 
    """

    df= db.read_sql(query=_querie, result=False)
    return df

def tempo_separacao(cd_empresa):
    _querie = f"""
    SELECT
        SUM(ESPERA) / COUNT(DISTINCT NR_PEDIDO) MEDIA_ESPERA,
        SUM(SEPARACAO) / COUNT(DISTINCT NR_PEDIDO) MEDIA_SEPARACAO,
        SUM(CONFERENCIA) / COUNT(DISTINCT NR_PEDIDO) MEDIA_CONFERENCIA,
        SUM(TOTAL_SEPARACAO) / COUNT(DISTINCT NR_PEDIDO) MEDIA_TOTAL_SEPARACAO
    FROM (
        SELECT
            DATEDIFF(MINUTE, ESP.DT_PEDIDO, EX.DT_INICIO ) ESPERA,
            0 SEPARACAO,
            0 TOTAL_SEPARACAO,
            DATEDIFF(MINUTE, EX.DT_FIM, EX.DTFIM_CONF) CONFERENCIA,
            P.NR_PEDIDO
        FROM PEDIDO P
        INNER JOIN EXTEND_SEPARACAO_TEMPO ESP ON (ESP.CD_EMPRESA = P.CD_EMPRESA
            AND ESP.NR_PEDIDO = P.NR_PEDIDO
            AND ESP.TP_PEDIDO = P.TP_PEDIDO)
        INNER JOIN EXTEND_SEPARACAO EX ON (EX.CD_EMPRESA = P.CD_EMPRESA
            AND EX.NR_PEDIDO = P.NR_PEDIDO)
        WHERE P.CD_EMPRESA = {cd_empresa}
            AND P.DT_PEDIDO = CURRENT_DATE
            AND P.TP_PEDIDO = 'S'
            AND EX.STATUS = 'F'
            AND P.CD_TIPOPEDIDO <> 3
        
        UNION ALL
        
        SELECT
            0 ESPERA,
            DATEDIFF(MINUTE, EX.DT_INICIO, EX.DT_FIM) SEPARACAO,
            DATEDIFF(MINUTE, ESP.DT_PEDIDO, EX.DT_FIM) TOTAL_SEPARACAO,
            0 CONFERENCIA,
            P.NR_PEDIDO
        FROM PEDIDO P
        INNER JOIN EXTEND_SEPARACAO_TEMPO ESP ON (ESP.CD_EMPRESA = P.CD_EMPRESA
            AND ESP.NR_PEDIDO = P.NR_PEDIDO
            AND ESP.TP_PEDIDO = P.TP_PEDIDO)
        INNER JOIN EXTEND_SEPARACAO EX ON (EX.CD_EMPRESA = P.CD_EMPRESA
            AND EX.NR_PEDIDO = P.NR_PEDIDO)
        WHERE P.CD_EMPRESA = {cd_empresa}
            AND P.DT_PEDIDO = CURRENT_DATE
            AND P.TP_PEDIDO = 'S'
            AND EX.STATUS = 'F'
            AND P.CD_TIPOPEDIDO <> 3
            AND DATEDIFF(SECOND, CAST(P.DT_PEDIDO||' '||P.HR_PEDIDO AS TIMESTAMP), EX.DT_FIM) > 10
        )

        """
    df= db.read_sql(query=_querie, result=False)
    return df

def quantidade_aguardando(cd_empresa):
    _querie = f"""
    WITH PEDIDOS_SEPARACAO
    AS (
        SELECT DISTINCT
            FORMATA_DATA(CAST(P.DT_PEDIDO||' '||P.HR_PEDIDO AS TIMESTAMP), '%H:%T %D/%M') HORA_DATA,
            CASE P.CD_TIPOPEDIDO
                WHEN 1 THEN 'Balcão'
                WHEN 2 THEN 'Motoboy'
                WHEN 3 THEN 'Despache'
                ELSE 'Nenhum'
             END PRIORIDADE, P.CD_TIPOPEDIDO,
            P.NR_PEDIDO, PE.NM_PESSOA, P.CD_EMPRESA, PV.NM_PESSOA NM_VENDEDOR, PV.CD_PESSOA CD_VENDEDOR,
            COALESCE(ES.NM_USUARIO, 'Aguardando') SEPARADOR,
            COALESCE(ES.STATUS, 'N') STATUS,
            EX.DT_PEDIDO,
            COALESCE(DATEDIFF(MINUTE, EX.DT_PEDIDO, CURRENT_TIMESTAMP), 1) TEMPO
        FROM
            PEDIDO P

            LEFT JOIN ITEMCONFERENCIAPEDIDO ICP ON (ICP.CD_EMPRESA = P.CD_EMPRESA
                AND ICP.NR_PEDIDO = P.NR_PEDIDO
                AND ICP.TP_PEDIDO = P.TP_PEDIDO)
            LEFT JOIN EXTEND_SEPARACAO ES ON (ES.CD_EMPRESA = P.CD_EMPRESA
                AND ES.NR_PEDIDO = P.NR_PEDIDO)
            INNER JOIN PESSOA PE ON (PE.CD_PESSOA = P.CD_PESSOA)
            INNER JOIN PESSOA PV ON (PV.CD_PESSOA = P.CD_VENDEDOR)
            LEFT JOIN EXTEND_SEPARACAO_TEMPO EX ON (EX.CD_EMPRESA = P.CD_EMPRESA
                AND EX.NR_PEDIDO = P.NR_PEDIDO
                AND EX.TP_PEDIDO = P.TP_PEDIDO)
        WHERE
            P.TP_PEDIDO = 'S'
            AND P.DT_PEDIDO = CURRENT_DATE 
            AND P.CD_EMPRESA IN ({cd_empresa})
            AND ICP.NR_PEDIDO IS NULL
            AND P.ST_PEDIDO NOT IN ('A', 'P', 'C')
            AND P.NR_ORDEMSERVICO IS NULL
            AND ES.CD_EMPRESA IS NULL
            AND P.CD_TIPOPEDIDO IS NOT NULL

    )
    SELECT
        COUNT(*) QNTD
    FROM (
    SELECT DISTINCT
        PE.HORA_DATA, PE.PRIORIDADE, PE.NR_PEDIDO, PE.NM_PESSOA,
        PE.CD_VENDEDOR, PE.SEPARADOR, PE.CD_TIPOPEDIDO, PE.TEMPO
        
    FROM PEDIDOS_SEPARACAO PE
    INNER JOIN ITEMPEDIDO IP ON (IP.CD_EMPRESA= PE.CD_EMPRESA
        AND IP.NR_PEDIDO = PE.NR_PEDIDO
        AND IP.TP_PEDIDO = 'S')
    WHERE PE.STATUS <> 'F'
    GROUP BY
        PE.HORA_DATA, PE.PRIORIDADE, PE.NR_PEDIDO, PE.NM_PESSOA,
        PE.CD_VENDEDOR, PE.SEPARADOR, PE.CD_TIPOPEDIDO, PE.TEMPO
    ORDER BY
        COALESCE(PE.CD_TIPOPEDIDO, 4)
        )
    """
    df= db.read_sql(query=_querie, result=False)
    return df

def monitore_tempo(cd_empresa):
    _querie = f"""
    SELECT
        E.O_QTDE_PEDIDO, E.O_QTDE_SEP, E.O_QTDE_CONF, E.O_QTDE_FAT, E.O_HORA
    FROM EXTEND_VIEW_HORA({cd_empresa}) E
    ORDER BY E.O_HORA
    """
    df= db.read_sql(query=_querie, result=False)
    return df