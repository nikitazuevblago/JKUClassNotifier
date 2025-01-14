import psycopg2 as pg2
from psycopg2 import errors
import os
from custom_logging import logger
from dotenv import load_dotenv

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

        # Create USERS table with display_hour and display_minutes columns
        logger.info("Creating table USERS...")
        cursor.execute("""
            CREATE TABLE USERS (
                TELEGRAM_ID BIGINT UNIQUE,
                URL VARCHAR(255),
                display_hour SMALLINT CHECK (display_hour >= 0 AND display_hour < 24),
                display_minutes SMALLINT CHECK (display_minutes >= 0 AND display_minutes < 60)
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
        if connection:
            connection.rollback()

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
        print(f"An error occurred while dropping tables: {error}")
        if connection:
            connection.rollback()
        

    finally:
        cursor.close()
        connection.close()

def drop_table_by_name(table_name):
    """
    Drops a specific table from the database using its name.
    """
    logger.info(f"Attempting to drop table: {table_name}")
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    logger.info("Database connection established for dropping a table.")

    try:
        cursor = connection.cursor()

        # Drop the specified table
        cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        connection.commit()
        logger.info(f"Table {table_name} dropped successfully.")

    except Exception as error:
        logger.error(f"An error occurred while dropping table {table_name}: {error}")
        if connection:
            connection.rollback()

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after attempting to drop the table.")

        
def add_user_DB(telegram_id, url, display_hour=0, display_minutes=0):
    logger.info(f"Adding user {telegram_id} to USERS table with default display time: {display_hour:02d}:{display_minutes:02d}...")
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
        cursor.execute("""
            INSERT INTO USERS (TELEGRAM_ID, URL, display_hour, display_minutes)
            VALUES (%s, %s, %s, %s);
        """, (telegram_id, url, display_hour, display_minutes))
        connection.commit()  # Commit changes immediately
        logger.info(f"User {telegram_id} added successfully with display time: {display_hour:02d}:{display_minutes:02d}.")

    except errors.UniqueViolation:
        logger.error(f"User {telegram_id} already exists.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()



def update_display_time(telegram_id, display_hour, display_minutes):
    logger.info(f"Updating display time for user {telegram_id} to {display_hour:02d}:{display_minutes:02d}...")
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    logger.info("Database connection established for updating display time.")

    try:
        cursor = connection.cursor()

        # Update display_hour and display_minutes for the specified TELEGRAM_ID
        cursor.execute("""
            UPDATE USERS
            SET display_hour = %s, display_minutes = %s
            WHERE TELEGRAM_ID = %s;
        """, (display_hour, display_minutes, telegram_id))

        if cursor.rowcount == 0:
            logger.warning(f"No user found with TELEGRAM_ID {telegram_id}.")
        else:
            connection.commit()
            logger.info(f"Display time for user {telegram_id} updated successfully to {display_hour:02d}:{display_minutes:02d}.")

    except Exception as e:
        logger.error(f"An error occurred while updating display time: {e}")
        if connection:
            connection.rollback()  # Rollback transaction in case of an error

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after updating display time.")



def remove_user_DB(telegram_id):
    logger.info(f"Removing user {telegram_id} from USERS table...")
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    logger.info("Database connection established for removing user.")

    try:
        cursor = connection.cursor()
        cursor.execute(f"""
            DELETE FROM USERS
            WHERE TELEGRAM_ID = {telegram_id};
        """)
        connection.commit()
        logger.info(f"User {telegram_id} removed successfully.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        if connection:
            connection.rollback()  # Rollback transaction in case of an error

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after removing user.")



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
        if connection:
            connection.rollback()
        

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
        if connection:
            connection.rollback()
        return []  # Return an empty list in case of failure

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
        if connection:
            connection.rollback()

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after fetching mailing history.")