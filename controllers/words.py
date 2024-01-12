from components.models import ModelComponents
from configs.config import DB_TABLE_WORDS


class WordsControllers(ModelComponents):
    def __init__(self) -> None:
        super().__init__()      


    def get(self):
        """Get all words from database table"""
        
        rows = []

        self.db_connection()

        try:

            sql = f"SELECT * FROM {DB_TABLE_WORDS}"

            rows = self.select(sql)

        except Exception as ex:
            self._logger.error(ex)

        self.db_close_connection()

        return rows
    

    def add_word(self, word: str):
        """Add word to database table"""

        self.db_connection()

        try:

            word = self.magic_quotes(word)

            sql = f"SELECT COUNT(*) FROM {DB_TABLE_WORDS} WHERE word LIKE '{word}'"

            row = self.select_one(sql)

            if row[0] == 0:
                
                sql = f"INSERT INTO {DB_TABLE_WORDS} (word) VALUES ('{word}')"

                self.insert(sql)

                self._logger.info(f'Word "{word}" was added')

        except Exception as ex:
            self._logger.error(ex)

        self.db_close_connection()