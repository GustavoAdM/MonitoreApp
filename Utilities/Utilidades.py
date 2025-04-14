import os
import locale
from datetime import datetime


def cwd():
    return os.getcwd()


def format_und_monetaria(valor, unidade: str = "BRL"):
    # Setando a unidade monetaria
    if unidade.upper() == "BRL":
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    if unidade.upper() == "USD":
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    if unidade.upper() == "EUR":
        locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

    if str(valor) == "nan":
        formatado = locale.currency(0.00, grouping=True)
        return formatado

    if isinstance(valor, (float, int)):
        formatado = locale.currency(valor, grouping=True)
        return formatado
    return valor


def format_milhar(valor, casas_decimais: int = None):
    if str(valor) == "nan":
        return 0
    if casas_decimais:
        valor = round(valor, casas_decimais)
        return f"{valor}".replace(',', '.')
    return f"{valor:,.0f}".replace(',', '.')


def format_percentual(valor):
    if isinstance(valor, (float, int)):
        return f"{valor:,.2f}%".replace(".", ",")


def primerio_dia_mes():
    data_atual = datetime.now()  # Obter a data atual

    # Obter o primeiro dia do mês atual
    primeiro_dia_mes = data_atual.replace(day=1).date()
    return primeiro_dia_mes


def data_atual():
    data_atual = datetime.now()
    return data_atual.strftime("%d-%m-%Y")


def diff_data(data_inico, data_fim, diff: int):

    # Calcula a diferença entre as datas
    diferenca = data_fim - data_inico

    if diferenca.days < diff:
        return True

    return False


def converter_minutos(tempo):
    if tempo:
        # Parte inteira dos minutos
        minutos = int(tempo)

        # Converte a parte decimal dos minutos em segundos
        segundos = int((tempo - minutos) * 60)

        return minutos, segundos
    return 0, 0
