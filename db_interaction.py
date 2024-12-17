import psycopg2 as pg2
import os
from custom_logging import logger
from dotenv import load_dotenv

load_dotenv()

def create_tables_DB():
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )

    try:
        cursor = connection.cursor()

        # Create bot_logs table
        cursor.execute("""
            CREATE TABLE bot_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,
                message TEXT NOT NULL
            );
        """)
        connection.commit()
        logger.info("Table bot_logs created successfully.")

        # Create USERS table
        logger.info("Creating table USERS...")
        cursor.execute("""
            CREATE TABLE USERS (
                TELEGRAM_ID BIGINT,
                URL VARCHAR(255)
            );
        """)
        logger.info("Table USERS created successfully.")
        connection.commit()

        # Create MAILING_HISTORY table
        logger.info("Creating table MAILING_HISTORY...")
        cursor.execute("""
            CREATE TABLE MAILING_HISTORY (
                DATE DATE UNIQUE
            );
        """)
        logger.info("Table MAILING_HISTORY created successfully.")
        connection.commit()

    except Exception as error:
        logger.error(f"An error occurred while creating tables: {error}")
        

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after table creation.")

def drop_tables_DB():
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT tablename FROM pg_tables WHERE schemaname = 'public'
        """)
        tables = cursor.fetchall()

        for table_name, in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        connection.commit()

    except Exception as error:
        #logger.error(f"An error occurred while dropping tables: {error}")
        print(f"An error occurred while dropping tables: {error}")
        

    finally:
        cursor.close()
        connection.close()

def add_user_DB(telegram_id, url):
    logger.info(f"Adding user {telegram_id} to USERS table...")
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    logger.info("Database connection established for adding user.")

    try:
        cursor = connection.cursor()
        cursor.execute(f"""
            INSERT INTO USERS (TELEGRAM_ID, URL)
            VALUES ({telegram_id}, '{url}');
        """)
        connection.commit()
        logger.info(f"User {telegram_id} added successfully.")

    except Exception as error:
        logger.error(f"An error occurred while adding user {telegram_id}: {error}")
        

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after adding user.")

def add_mailing_date_DB(date):
    logger.info(f"Adding mailing date {date}...")
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    logger.info("Database connection established for adding mailing date.")

    try:
        cursor = connection.cursor()
        cursor.execute(f"""
            INSERT INTO MAILING_HISTORY (DATE) VALUES ('{date}');
        """)
        connection.commit()
        logger.info(f"Mailing date {date} added successfully.")

    except Exception as error:
        logger.error(f"An error occurred while adding mailing date {date}: {error}")
        

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after adding mailing date.")

def get_all_users_DB():
    logger.info("Fetching all users from USERS table...")
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    logger.info("Database connection established for fetching users.")

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM USERS;")
        records = cursor.fetchall()
        logger.info(f"Fetched {len(records)} users.")
        return records

    except Exception as error:
        logger.error(f"An error occurred while fetching users: {error}")

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after fetching users.")

def get_all_mailing_history_DB():
    logger.info("Fetching mailing history...")
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    logger.info("Database connection established for fetching mailing history.")

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM MAILING_HISTORY;")
        records = cursor.fetchall()
        logger.info(f"Fetched {len(records)} mailing history records.")
        return records

    except Exception as error:
        logger.error(f"An error occurred while fetching mailing history: {error}")

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after fetching mailing history.")
