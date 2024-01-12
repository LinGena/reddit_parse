import os
import dotenv

dotenv.load_dotenv(dotenv_path=".env.reddit")

# PostgreSql connection
CONFIG_DB_HOST = os.getenv('CONFIG_DB_HOST', '')
CONFIG_DB_PORT = os.getenv('CONFIG_DB_PORT', '5432')
CONFIG_DB_NAME = os.getenv('CONFIG_DB_NAME', '')
CONFIG_DB_USER = os.getenv('CONFIG_DB_USER', '')
CONFIG_DB_PASS = os.getenv('CONFIG_DB_PASS', '')

# Logger settings
CONFIG_LOGGER_LEVEL = os.getenv('CONFIG_LOGGER_LEVEL', 'INFO')
CONFIG_LOGGER_DIR = os.getenv('CONFIG_LOGGER_DIR', 'logs')

# Proxy
CONFIG_PROXY = os.getenv('CONFIG_PROXY', '')
proxy_data = {
    'http': 'http://' + CONFIG_PROXY,
    'https': 'http://' + CONFIG_PROXY,
}

# Names of database tables
DB_TABLE_WORDS = 'sm_words'
DB_TABLE_POSTS = 'sm_posts'


