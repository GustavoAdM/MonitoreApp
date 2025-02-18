from .ConnectionV2 import db


def nome_separadores(dtInicio, dtFim):
    """ Nome dos separadores que tiveram movimentação nos ultimos 20 dias """
    _querie = f"""
    SELECT DISTINCT ES.NM_USUARIO
    FROM EXTEND_SEPARACAO ES
    WHERE CAST(ES.DT_INICIO AS DATE) BETWEEN '{dtInicio}' AND '{dtFim}'
    """
    return db.read_sql(query=_querie)


def separacao_pedido_geral(dt_incio:str, dt_fim:str,separador:list):
    """Pedidos feito na mesma semana (Segunda a Sexta) da semana atual"""
    sql_separador = ""

    if separador != []:
        string_separador = ", ".join([f"'{elemento}'" for elemento in separador])
        sql_separador = f"AND ES.NM_USUARIO IN ({string_separador})"

    _querie = f"""
    SELECT
      CAST(ES.NM_USUARIO AS VARCHAR(20))NM_USUARIO,
      SUM(X.QT_ITEM) QT_ITEM, SUM(X.QNT_PEDIDOS) QNT_PEDIDOS, X.DT_PEDIDO,
      SUM( DATEDIFF(SECOND, ES.DT_INICIO, ES.DT_FIM)) TEMPO_TOTAL,
      COUNT(DISTINCT IIF(DATEDIFF(SECOND, ES.DT_INICIO, ES.DT_FIM) < 30, X.NR_PEDIDO, Null)) QNT_MENOR_30S

    FROM (
        SELECT
            P.DT_PEDIDO, P.CD_EMPRESA, P.NR_PEDIDO, P.TP_PEDIDO,
            SUM(COALESCE(IP.PS_PEDIDO, IP.QT_PEDIDA)) QT_ITEM,
            COUNT(DISTINCT P.NR_PEDIDO) QNT_PEDIDOS
        FROM
            PEDIDO P
            INNER JOIN ITEMPEDIDO IP ON (IP.CD_EMPRESA = P.CD_EMPRESA
                AND IP.NR_PEDIDO = P.NR_PEDIDO
                AND IP.TP_PEDIDO = P.TP_PEDIDO)  
        WHERE
            P.ST_PEDIDO NOT IN ('C')
            AND P.DT_PEDIDO BETWEEN '{dt_incio}' AND '{dt_fim}'
        GROUP BY P.DT_PEDIDO, P.CD_EMPRESA, P.NR_PEDIDO, P.TP_PEDIDO
    )X
    INNER JOIN EXTEND_SEPARACAO ES ON (ES.CD_EMPRESA = X.CD_EMPRESA
        AND ES.NR_PEDIDO = X.NR_PEDIDO)
    WHERE ES.STATUS = 'F'
        {sql_separador}
    GROUP BY NM_USUARIO, X.DT_PEDIDO
    ORDER BY X.DT_PEDIDO, NM_USUARIO
    """
    return db.read_sql(query=_querie)

def total_pedidos(dt_inicio, dt_fim):
    _querie = f"""
    SELECT
        SUM(COALESCE(IP.PS_PEDIDO, IP.QT_PEDIDA)) QT_ITEM,
        COUNT(DISTINCT P.NR_PEDIDO) QNT_PEDIDOS,
        COUNT(DISTINCT IIF(DATEDIFF(SECOND, ES.DT_INICIO, ES.DT_FIM) < 30, P.NR_PEDIDO, Null)) QNT_MENOR_30S  
    FROM
        PEDIDO P
        INNER JOIN EXTEND_SEPARACAO ES ON (ES.CD_EMPRESA = P.CD_EMPRESA
            AND ES.NR_PEDIDO = P.NR_PEDIDO)
        INNER JOIN ITEMPEDIDO IP ON (IP.CD_EMPRESA = P.CD_EMPRESA
            AND IP.NR_PEDIDO = P.NR_PEDIDO
            AND IP.TP_PEDIDO = P.TP_PEDIDO)     
    WHERE
        P.ST_PEDIDO NOT IN ('C')
        AND P.DT_PEDIDO BETWEEN '{dt_inicio}' AND '{dt_fim}'
        AND ES.STATUS = 'F'
    """
    return db.read_sql(query=_querie)


def total_pedidos_pecas_separador(dataInicio, DataFim):
    _querie = f"""
    SELECT FIRST 4
        CAST(ES.NM_USUARIO AS VARCHAR(20))NM_USUARIO,
        COUNT(DISTINCT P.NR_PEDIDO) N_PEDIDOS,
        SUM(COALESCE(IP.PS_PEDIDO, IP.QT_PEDIDA)) QT_ITEM   
    FROM
        PEDIDO P
        INNER JOIN EXTEND_SEPARACAO ES ON (ES.CD_EMPRESA = P.CD_EMPRESA
            AND ES.NR_PEDIDO = P.NR_PEDIDO)
        INNER JOIN ITEMPEDIDO IP ON (IP.CD_EMPRESA = P.CD_EMPRESA
            AND IP.NR_PEDIDO = P.NR_PEDIDO
            AND IP.TP_PEDIDO = P.TP_PEDIDO)     
    WHERE
        P.ST_PEDIDO NOT IN ('C')
        AND P.DT_PEDIDO BETWEEN '{dataInicio}' AND '{DataFim}'
        AND ES.STATUS = 'F'
    GROUP BY ES.NM_USUARIO
    ORDER BY COUNT(DISTINCT P.NR_PEDIDO) + SUM(COALESCE(IP.PS_PEDIDO, IP.QT_PEDIDA)) DESC 
    """
    return db.read_sql(query=_querie)

def pedidos_mais_30s(dataInicio, dataFim, separador):
    """Pedidos com menos de 30m segundos"""
    sql_separador = ""

    if separador != []:
        string_separador = ", ".join([f"'{elemento}'" for elemento in separador])
        sql_separador = f"AND ES.NM_USUARIO IN ({string_separador})"

    _querie = f"""
    SELECT
        (CAST(SUM(DATEDIFF(SECOND, ES.DT_INICIO, ES.DT_FIM)) AS NUMERIC(15,2)) / COUNT(P.NR_PEDIDO)) / 60 TEMPO_MEDIO
    FROM
        PEDIDO P
        INNER JOIN EXTEND_SEPARACAO ES ON (ES.CD_EMPRESA = P.CD_EMPRESA
            AND ES.NR_PEDIDO = P.NR_PEDIDO)
    WHERE
        P.ST_PEDIDO NOT IN ('C')
        AND P.DT_PEDIDO BETWEEN '{dataInicio}' AND '{dataFim}'
        AND ES.STATUS = 'F'
        AND DATEDIFF(SECOND, ES.DT_INICIO, ES.DT_FIM) >= 30
        {sql_separador}
    """
    return db.read_sql(query=_querie)
