from .ConnectionV2 import db


def nome_separadores(dtInicio, dtFim):
    """ Nome dos separadores que tiveram movimentação nos ultimos 20 dias """
    _querie = f"""
    SELECT DISTINCT ES.NM_USUARIO
    FROM EXTEND_SEPARACAO ES
    WHERE CAST(ES.DT_INICIO AS DATE) BETWEEN '{dtInicio}' AND '{dtFim}'
    """
    return db.read_sql(query=_querie)


def separacao_pedido_geral(dt_incio: str, dt_fim: str, separador: list):
    """Pedidos feito na mesma semana (Segunda a Sexta) da semana atual"""
    sql_separador = ""

    if separador != []:
        string_separador = ", ".join(
            [f"'{elemento}'" for elemento in separador])
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
    SELECT FIRST 10
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
        string_separador = ", ".join(
            [f"'{elemento}'" for elemento in separador])
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


def tempo_total_separacao(empresa: int, data_inicio: str, data_fim: str):
    """
    Indicador local: Auditoria
    Explicação: Contabiliza o tempo médio desde a abertura do pedido com o tipo infomado ate a finalização pelo separador.
    - Pegar a data e hora em que o pedido foi feito de forma "Correta" com o tipo de pedido informado ou a data e hora que aparece na tela de separação.
    - Media e o tempo dividido pelo total de PEDIDO separado para uma media de tempo por pedido
    - Não pega pedidos com menos de 10s, iniciou e finalizou de forma quase imediata não e considerado

    """
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
        WHERE P.CD_EMPRESA = {empresa}
            AND P.DT_PEDIDO BETWEEN '{data_inicio}' AND '{data_fim}'
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
        WHERE P.CD_EMPRESA = {empresa}
            AND P.DT_PEDIDO BETWEEN '{data_inicio}' AND '{data_fim}'
            AND P.TP_PEDIDO = 'S'
            AND EX.STATUS = 'F'
            AND P.CD_TIPOPEDIDO <> 3
            AND DATEDIFF(SECOND, CAST(P.DT_PEDIDO||' '||P.HR_PEDIDO AS TIMESTAMP), EX.DT_FIM) > 10
        )
    """
    return db.read_sql(query=_querie)


def Qtrasnferencia_dist(cd_empresa: int):


    _querie = f"""
    WITH ESTOQ_LOJAS
    AS (
        SELECT
            I.CD_ITEM CD_ITEM_LOJAS, CAST(E.QT_ESTOQUE AS NUMERIC(15,2)) QT_EST_ATUAL,
            COALESCE(I.QT_ESTOQUEMIN, 0) MIN_EST_LOJAS, I.QT_ESTOQUEMAX MAS_EST_LOJAS,
            ABS(E.QT_ESTOQUE - COALESCE(I.QT_ESTOQUEMIN, 0)) QT_SOLICITADA
        FROM ITEM I
        INNER JOIN ITEMLOCAL IL ON (IL.CD_ITEM = I.CD_ITEM
            AND IL.CD_TIPOLOCAL = CASE {cd_empresa}
                                    WHEN 52 THEN 2
                                    WHEN 5 THEN 3
                                  END  )
        INNER JOIN ESTOQUE E ON (E.CD_EMPRESA = {cd_empresa}
            AND E.CD_ITEM = IL.CD_ITEM
            AND E.CD_TIPOLOCAL = IL.CD_TIPOLOCAL
            AND E.CD_LOCAL = IL.CD_LOCAL)
        WHERE I.CD_GRUPO BETWEEN 40 AND 49
            AND I.CD_SECAO IS NOT NULL
            AND E.QT_ESTOQUE >= 0
            AND E.QT_ESTOQUE < COALESCE(I.QT_ESTOQUEMIN, 0)

    ),
    ESTOQ_DIST
    AS (
        SELECT
            I.CD_ITEM CD_DIST, E.QT_ESTOQUE, I.DS_ITEM,
            I.QT_ESTOQUEMIN MIN_EST_LOJAS, I.QT_ESTOQUEMAX MAS_EST_LOJAS,
            (E.QT_ESTOQUE - COALESCE(I.QT_ESTOQUEMIN, 0)) QT_DISPONIVEL,
            CASE CHAR_LENGTH(I.CD_ITEM)
                WHEN 7 THEN I.CD_ITEM - 3000000
                WHEN 8 THEN I.CD_ITEM - 30000000
                WHEN 9 THEN I.CD_ITEM - 300000000
            END CD_LOJAS
        FROM ITEM I
        INNER JOIN ITEMLOCAL IL ON (IL.CD_ITEM = I.CD_ITEM
            AND IL.CD_TIPOLOCAL = 7)
        INNER JOIN ESTOQUE E ON (E.CD_EMPRESA = 7
            AND E.CD_ITEM = IL.CD_ITEM
            AND E.CD_TIPOLOCAL = IL.CD_TIPOLOCAL
            AND E.CD_LOCAL = IL.CD_LOCAL)
        WHERE I.CD_GRUPO BETWEEN 70 AND 79
            AND I.CD_SECAO IS NOT NULL
            AND E.QT_ESTOQUE > COALESCE(I.QT_ESTOQUEMIN, 0)
    ),
    NOTA_VENDA
    AS (
        SELECT
            IT.CD_ITEM, COALESCE(IT.PS_ITEMNOTA, IT.QT_ITEMNOTA) QT_ITEM,
            N2.NR_NOTAFOR
        FROM NOTA N
        INNER JOIN ITEMNOTA IT ON (IT.CD_EMPRESA = N.CD_EMPRESA
            AND IT.NR_LANCAMENTO = N.NR_LANCAMENTO
            AND IT.TP_NOTA = N.TP_NOTA
            AND IT.CD_SERIE = N.CD_SERIE)
        LEFT JOIN NOTA N2 ON (N2.CD_EMPRESA = 52
            AND N2.NR_NOTAFOR = N.NR_NOTAFISCAL
            AND N2.CD_SERIEFOR = N.CD_SERIE
            AND N2.TP_NOTA = 'E'
            AND N2.ST_NOTA = 'V'
            AND N2.DT_EMISSAO BETWEEN CURRENT_DATE - 10 AND CURRENT_DATE)
        WHERE N.CD_EMPRESA = 7
            AND N.ST_NOTA = 'V'
            AND N.TP_NOTA = 'S'
            AND N.CD_PESSOA = 41035
            AND N.DT_EMISSAO BETWEEN CURRENT_DATE - 10 AND CURRENT_DATE

    )
    SELECT
        D.CD_DIST, D.DS_ITEM,
        D.QT_DISPONIVEL,
        (E.QT_SOLICITADA - COALESCE(N.QT_ITEM, 0)) QT_SOLICITADA
    FROM ESTOQ_DIST D
    INNER JOIN ESTOQ_LOJAS E ON (E.CD_ITEM_LOJAS = D.CD_LOJAS)
    LEFT JOIN NOTA_VENDA N ON (N.CD_ITEM = D.CD_DIST)
    WHERE  D.QT_DISPONIVEL >= E.QT_SOLICITADA
        AND (E.QT_SOLICITADA - COALESCE(N.QT_ITEM, 0)) > 0




    """
    return db.read_sql(query=_querie)


def Qpendente_transfer():
    _querie = f"""
    SELECT
        IT.CD_ITEM, I.DS_ITEM, COALESCE(IT.PS_ITEMNOTA, IT.QT_ITEMNOTA) QT_ITEM,
        N.NR_NOTAFISCAL
    FROM NOTA N
    INNER JOIN ITEMNOTA IT ON (IT.CD_EMPRESA = N.CD_EMPRESA
        AND IT.NR_LANCAMENTO = N.NR_LANCAMENTO
        AND IT.TP_NOTA = N.TP_NOTA
        AND IT.CD_SERIE = N.CD_SERIE)
    INNER JOIN ITEM I ON (I.CD_ITEM = IT.CD_ITEM)
    LEFT JOIN NOTA N2 ON (N2.CD_EMPRESA = 52
        AND N2.NR_NOTAFOR = N.NR_NOTAFISCAL
        AND N2.CD_SERIEFOR = N.CD_SERIE
        AND N2.TP_NOTA = 'E'
        AND N2.ST_NOTA = 'V'
        AND N2.DT_EMISSAO BETWEEN CURRENT_DATE - 10 AND CURRENT_DATE)
    WHERE N.CD_EMPRESA = 7
        AND N.ST_NOTA = 'V'
        AND N.TP_NOTA = 'S'
        AND N.CD_PESSOA = 41035
        AND N.DT_EMISSAO BETWEEN CURRENT_DATE - 10 AND CURRENT_DATE
        AND N2.NR_NOTAFOR IS NULL
    """
    return db.read_sql(query=_querie)