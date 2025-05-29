import fdb  # Biblioteca fdb (Firebird driver)
import configparser
from contextlib import contextmanager
from pandas import read_sql, DataFrame, NaT


class FirebirdDB:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('Config\\Config.ini')

        self.usuario = self.config['database']['usuario']
        self.senha = self.config['database']['senha']
        self.ip = self.config['database']['ip']
        self.caminho = self.config['database']['caminho']
        self.porta = self.config['database']['porta']
        self.lib_path = self.config['database']['lib_path']

        # Estabelecendo a conexão com o Firebird usando fdb
        self.dsn = f'{self.ip}/{self.porta}:{self.caminho}'  # DSN: ip/porta:caminho
        self.connection = None

    def connect(self):
        try:
            # A conexão agora é feita com fdb.connect sem o parâmetro 'db_lib'
            self.connection = fdb.connect(
                host=self.ip,
                database=self.caminho,
                port=int(self.porta),
                user=self.usuario,
                password=self.senha,
                charset='UTF8',
                fb_library_name=self.lib_path
            )
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def disconnect(self):
        if self.connection:
            self.connection.close()

    @contextmanager
    def session_scope(self):
        """Context manager para gerenciar a conexão"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        try:
            yield cursor
        except Exception as e:
            print(f"Erro durante a execução da consulta: {e}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def read_sql(self, query, result = True):
        """Executa uma consulta SQL e retorna os resultados em um DataFrame pandas"""
        if not self.connection:
            self.connect()

        try:
            # Usando pandas.read_sql para executar a consulta e retornar um DataFrame
            df = read_sql(query, self.connection)
            
            if df.empty:
                df = DataFrame(columns=df.columns)
            return df
        except Exception as e:
            print(f"Erro ao consultar: {e}")
            return DataFrame(columns=df.columns)


# Exemplo de uso
db = FirebirdDB()

