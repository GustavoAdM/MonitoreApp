from fpdf import FPDF
from pandas import DataFrame
from Src.Database.QuerieRelatorio import relatorio_vendedor, extend_devolucao
from Utilities.Utilidades import format_und_monetaria
import warnings

warnings.simplefilter(action='ignore', category=UserWarning)

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.valor = 0
        self.quantidade = 0
        self.valor_devol = 0
        self.quant_devol = 0

    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Relatório De Vendedor', 0, 1, 'C')
        self.ln(3)

    def sub_header(self, subs_header: list):
        self.set_font("Arial", "B", 10)
        # Ajustando as larguras das células para balancear as colunas
        col_widths = [25, 22, 100, 25, 22]  # Ajuste para 5 colunas
        for i, subsheader in enumerate(subs_header):
            self.cell(col_widths[i], 5, f"{subsheader}", border=1, align='C' if i != 2 else 'L')
        self.ln()
        self.ln(1)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, f"Vendedor: {title}", 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, data: DataFrame):
        # Ajustando as larguras das células para as colunas de forma consistente
        col_widths = [25, 22, 100, 25, 18]  # Ajuste para 5 colunas
        if not data.empty:
            for row in data.itertuples():
                self.set_font('Arial', '', 8)
                # Preenchendo as células com os dados do DataFrame
                self.cell(col_widths[0], 3, str(row.DT_EMISSAO), 0, 0, "C")
                self.cell(col_widths[1], 3, str(row.NR_NOTA), 0, 0, "C")
                self.cell(col_widths[2], 3, str(row.NM_PESSOA), 0, 0, "L")
                self.cell(col_widths[3], 3, f"{row.QT_ITEM:.0f}", 0, 0, "C")
                self.cell(col_widths[4], 3, f"{format_und_monetaria(row.VL_NOTAFISCAL)}", 0, 0, "R")
                self.ln()
                self.valor += row.VL_NOTAFISCAL
                self.quantidade += row.QT_ITEM
                
                # Adicionando as devoluções para cada nota fiscal
                self.chapter_devolucao(nr_lanc=row.NR_LANCAMENTO, 
                                       cd_emp=row.CD_EMPRESA, 
                                       tp_nota=row.TP_NOTA,
                                       cd_serie=row.CD_SERIE)

    def chapter_devolucao(self, nr_lanc, cd_emp, tp_nota, cd_serie):
        self.set_font("Arial", "", 8)
        df_querie = extend_devolucao(nr_lanc=nr_lanc, cd_emp=cd_emp, tp_nota=tp_nota, cd_serie=cd_serie)

        if not df_querie.empty:
            for row in df_querie.itertuples():
                self.cell(30, 5, "|--> Devolução - ", 0, 0, "R")
                self.cell(35, 5, f"Emissão: {row.DT_EMISSAO}", 0, 0, "L")
                self.cell(25, 5, f"NF: {row.NR_NOTA}", 0, 0, "L")
                self.cell(25, 5, f"Quantidade: {row.QT_DEVOLUCAO:.0f}", 0, 0, "L")
                self.cell(25, 5, f"Valor: {format_und_monetaria(row.VL_NOTAFISCAL)}", 0, 0, "L")
                self.ln()
                self.quant_devol += row.QT_DEVOLUCAO
                self.valor_devol += row.VL_NOTAFISCAL

            self.ln(1)

    def summary(self):
        self.ln(10)
        self.set_font("Arial", "B", 9)
        # Exibindo o resumo final
        self.cell(0, 5, f"Quant. Nota: {self.quantidade:.0f}       Valor Nota: {format_und_monetaria(self.valor)}", 0, 1, 'R')
        self.cell(0, 5, f"Quant. Devoluções: {self.quant_devol:.0f}       Valor Devolução: {format_und_monetaria(self.valor_devol)}", 0, 1, 'R')
        self.cell(0, 5, f"Quant. Nota - Dev: {self.quantidade - self.quant_devol:.0f}    Valor Nota - Dev: {format_und_monetaria(self.valor - self.valor_devol)}", 0, 1, 'R')


