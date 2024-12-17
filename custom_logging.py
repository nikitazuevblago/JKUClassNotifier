import logging
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


# Custom PostgreSQL Logging Handler
class PostgresHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        # Establish the connection
        self.connection = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_DATABASE")
        )
        self.connection.autocommit = True


    def emit(self, record):
        log_message = self.format(record)
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO bot_logs (level, message) VALUES (%s, %s)",
                (record.levelname, log_message),
            )
            cursor.close()
        except Exception as e:
            print(f"Failed to log message to PostgreSQL: {e}")


    def close(self):
        logger.info("Bot stopped")
        if self.connection:
            self.connection.close()
        super().close()


# Initialize logging
db_handler = PostgresHandler()
db_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(message)s")  # Customize log format
db_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(db_handler)