import pandas as pd
import configparser
import logging
from firebird.driver import driver_config, connect as fb_connect, Connection
from contextlib import contextmanager
from typing import Optional, Generator


class FirebirdDB:
    def __init__(self, config_file: str = 'Config/Config.ini', logger: Optional[logging.Logger] = None):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.usuario: str = self.config.get(
            'database', 'usuario', fallback=None)
        self.senha: str = self.config.get('database', 'senha', fallback=None)
        self.ip: str = self.config.get('database', 'ip', fallback=None)
        self.caminho: str = self.config.get(
            'database', 'caminho', fallback=None)
        self.porta: int = self.config.getint(
            'database', 'porta', fallback=3050)
        self.lib_path: str = self.config.get(
            'database', 'lib_path', fallback=None)

        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self._validate_config()
        self._configure_driver()

    def _validate_config(self) -> None:
        """Valida se todas as configurações necessárias estão presentes"""
        missing = [key for key, val in {
            'usuario': self.usuario,
            'senha': self.senha,
            'ip': self.ip,
            'caminho': self.caminho,
            'lib_path': self.lib_path
        }.items() if not val]

        if missing:
            raise ValueError(
                f"Parâmetros de configuração ausentes: {', '.join(missing)}")

    def _configure_driver(self) -> None:
        """Configura o driver do Firebird"""
        driver_config.server_defaults.host.value = self.ip
        driver_config.server_defaults.port.value = str(self.porta)  # ✅ Conversão aqui
        driver_config.server_defaults.user.value = self.usuario
        driver_config.server_defaults.password.value = self.senha
        driver_config.fb_client_library.value = self.lib_path
        self.logger.info("Configuração do driver Firebird realizada com sucesso.")

    @contextmanager
    def session_scope(self) -> Generator[Connection, None, None]:
        """Context manager para gerenciar a conexão"""
        connection: Optional[Connection] = None
        try:
            connection = fb_connect(self.caminho)
            self.logger.info("Conexão com o banco de dados estabelecida.")
            yield connection
            connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            self.logger.error(
                f"Erro ao conectar ou operar no banco de dados: {e}")
            raise
        finally:
            if connection:
                connection.close()
                self.logger.info("Conexão encerrada.")

    def read_sql(self, query: str, fill_empty: bool = True) -> pd.DataFrame:
        """Executa uma consulta SQL e retorna um DataFrame"""
        try:
            with self.session_scope() as conn:
                df = pd.read_sql(query, conn)

                if df.empty and fill_empty:
                    self.logger.warning(
                        "Consulta retornou DataFrame vazio. Preenchendo com valores padrão.")
                    df = self._fill_empty_dataframe(df)

                return df

        except Exception as e:
            self.logger.error(f"Erro ao executar consulta SQL: {e}")
            return pd.DataFrame()

    @staticmethod
    def _fill_empty_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Preenche DataFrame vazio com valores padrão baseados no tipo das colunas."""
        filled_data = {col: [FirebirdDB._default_value(
            dtype)] for col, dtype in zip(df.columns, df.dtypes)}
        return pd.DataFrame(filled_data)

    @staticmethod
    def _default_value(dtype) -> Optional[object]:
        """Retorna valor padrão baseado no tipo de dado."""
        if pd.api.types.is_integer_dtype(dtype):
            return 0
        elif pd.api.types.is_float_dtype(dtype):
            return 0.0
        elif pd.api.types.is_object_dtype(dtype):
            return "-"
        else:
            return pd.NaT

db = FirebirdDB()