import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

# Load environment variables from the .env file. Like an adult.
load_dotenv(override=True)

# Configuration for your AWS RDS PostgreSQL database.
# Using os.environ instead of get() so it crashes LOUDLY if you forget your .env file
DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"] # Keep this out of version control, rookie
DB_PORT = os.environ.get("DB_PORT", "5432") # Defaulting down to 5432 is fine


def initialize_database():
    connection = None
    try:
        # Establish the connection
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            sslmode='require'
        )

        # A cursor is your workhorse. It actually executes the SQL.
        cursor = connection.cursor()
        
        #Schema
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS persons (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                address VARCHAR(100),
                age INTEGER
            );
        '''
        
        # Execute the query
        cursor.execute(create_table_query)
        
        # Commit the transaction.
        connection.commit()
        print("Success: Table 'persons' created.")

    except (Exception, Error) as error:
        print("Listen up, you broke something connecting to PostgreSQL:", error)
    finally:
        # Always clean up your toys.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed. Don't leave the damn door open.")

if __name__ == "__main__":
    initialize_database()
