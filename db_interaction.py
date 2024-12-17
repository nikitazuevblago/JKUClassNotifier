import psycopg2 as pg2
import os


def create_tables_DB():
    # Establish the connection
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )

    try:
        # Create USERS table
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE USERS (
                TELEGRAM_ID BIGINT,
                URL VARCHAR(255)
            );
        """)
        print(f"Created table USERS")
        # Commit the changes
        connection.commit()

        # Create mailing table
        cursor.execute("""
            CREATE TABLE MAILING_HISTORY (
                DATE DATE UNIQUE
            );
        """)
        print(f"Created table MAILING_HISTORY")
        # Commit the changes
        connection.commit()

    except Exception as error:
        print(f"An error occurred: {error}")
        connection.rollback()

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()



def drop_tables_DB():

    # Establish the connection
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )

    try:
        # Create a cursor object
        cursor = connection.cursor()

        # Retrieve all table names in the current database
        # We are assuming public schema, modify if a different schema is used
        cursor.execute("""
            SELECT tablename FROM pg_tables WHERE schemaname = 'public'
        """)
        tables = cursor.fetchall()

        # Drop each table
        for table_name, in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
            print(f"Dropped table {table_name}")

        # Commit the changes
        connection.commit()

    except Exception as error:
        print(f"An error occurred: {error}")
        connection.rollback()

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()


def add_user_DB(telegram_id, url):
    # Establish the connection
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )

    try:
        # Create a cursor object
        cursor = connection.cursor()
        cursor.execute(f"""
            INSERT INTO USERS (TELEGRAM_ID, URL)
            VALUES ({telegram_id}, '{url}');
        """)
        print(f"New user added")
        # Commit the changes
        connection.commit()

    except Exception as error:
        print(f"An error occurred: {error}")
        connection.rollback()

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()


def add_mailing_date_DB(date):
    # Establish the connection
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )

    try:
        # Create a cursor object
        cursor = connection.cursor()
        cursor.execute(f"""
            INSERT INTO MAILING_HISTORY (DATE) VALUES ('{date}');
        """)
        print(f"New mailing date added")
        # Commit the changes
        connection.commit()

    except Exception as error:
        print(f"An error occurred: {error}")
        connection.rollback()

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()


def get_all_users_DB():
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM USERS;")
        records = cursor.fetchall()
        return records
    except Exception as error:
        print(f"An error occurred: {error}")
    finally:
        cursor.close()
        connection.close()


def get_all_mailing_history_DB():
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM MAILING_HISTORY;")
        records = cursor.fetchall()
        return records
    except Exception as error:
        print(f"An error occurred: {error}")
    finally:
        cursor.close()
        connection.close()