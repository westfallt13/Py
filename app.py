import os
import psycopg2
from psycopg2 import Error
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load env variables again, just to be safe
load_dotenv(override=True)

app = Flask(__name__)

# Helper function to get a database connection. We open a NEW connection for every request. Don't leave a single global one open,  or multiple users will trip over each other and crash your app.
def get_db_connection():
    return psycopg2.connect(
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        database=os.environ["DB_NAME"],
        sslmode='require'
    )

@app.route('/add_person', methods=['POST'])
def add_person():
    # Grab the JSON data sent by the client
    data = request.json
    
    # Basic validation.
    if not data or not 'first_name' in data or not 'last_name' in data:
        return jsonify({"error": "first_name and last_name are required!"}), 400

    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Parameterized query to prevent SQL Injection. 
        # Never use f-strings or string concatenation for SQL, or you'll get hacked.
        insert_query = '''
            INSERT INTO persons (first_name, last_name, address, age)
            VALUES (%s, %s, %s, %s)
        '''
        record_to_insert = (data['first_name'], data['last_name'], data.get('address'), data.get('age'))
        
        cursor.execute(insert_query, record_to_insert)
        connection.commit()
        
        return jsonify({"message": "Person added successfully!"}), 201

    except (Exception, Error) as error:
        print("Error inserting data:", error)
        return jsonify({"error": "Failed to add person to database"}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.route('/get_persons', methods=['GET'])
def get_persons():
    connection = None
    try:
        connection = get_db_connection()
        # Using RealDictCursor parses the SQL rows directly into Python dictionaries. Very handy.
        from psycopg2.extras import RealDictCursor
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT * FROM persons;")
        records = cursor.fetchall()
        
        # jsonify takes our list of dictionaries and turns it into a JSON string for the client
        return jsonify(records), 200

    except (Exception, Error) as error:
        print("Error fetching data:", error)
        return jsonify({"error": "Failed to fetch persons"}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == '__main__':
    # Run the Flask app on port 5000. 
    # debug=True means it automatically restarts if you change the code. Handy for development.
    app.run(debug=True, port=5000)