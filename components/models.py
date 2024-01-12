import psycopg2
from utils.logger import Logger
from configs.config import CONFIG_DB_HOST, CONFIG_DB_PORT, CONFIG_DB_NAME, CONFIG_DB_USER, CONFIG_DB_PASS


class ModelComponents():
    def __init__(self) -> None:
        self._logger = Logger().get_logger(__name__)


    def db_connection(self):

        self.connection = psycopg2.connect(
            dbname=CONFIG_DB_NAME,
            user=CONFIG_DB_USER,
            password=CONFIG_DB_PASS,
            host=CONFIG_DB_HOST,
            port=CONFIG_DB_PORT
        )

        self.cursor = self.connection.cursor()


    def db_close_connection(self):

        self.cursor.close()

        self.connection.close()


    def select(self, sql):

        self.cursor.execute(sql)

        rows = self.cursor.fetchall()

        return rows
    
    
    def select_one(self, sql):

        self.cursor.execute(sql)

        row = self.cursor.fetchone()

        return row
    

    def insert(self, sql):

        self.cursor.execute(sql)

        self.connection.commit()


    def magic_quotes(self, value: str):

        return value.replace("'", "''")

