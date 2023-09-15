import sqlite3
import time
import json

class sqlite_cache:
    def __init__(self, db_filename):
        self.db_filename = db_filename # Database file name
        self.connection = None # SQLite connection object
        self.connect() # Connect to the database on initialization

    def connect(self):
        # Establish a connection to the SQLite database and set up the table if it doesn't exist yet.
        self.connection = sqlite3.connect(self.db_filename)
        self.connection.row_factory = sqlite3.Row  # Return row data as dictionary

        # Create a table for caching responses if it doesn't exist yet.
        self.execute("""
            CREATE TABLE IF NOT EXISTS cached_responses (
                path TEXT,
                paramkey TEXT,
                content BLOB,
                status_code INTEGER,
                headers TEXT,
                timestamp REAL,
                PRIMARY KEY (path, paramkey)
            );
        """)

    def disconnect(self):
        # Close the database connection.
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        # Execute a SQL query with or without parameters and return a cursor object.
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor

    def execute(self, query, params=None):
        # Execute a SQL query and fetch one record from the result set.
        cursor = self.execute_query(query, params)
        try:
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"An error occurred: {e.args[0]}")
        finally:    
             # Commit changes after every transaction.
             # This is important because SQLite doesn't commit transactions automatically.
            self.connection.commit()

    def get_cached_value(self, path, params):
        current_time = time.time()

        params_as_json_string = json.dumps(params)
        
        # Delete data older than 30 seconds for given parameter key
        delete_query = "DELETE FROM cached_responses WHERE (? - timestamp) > 30 AND paramkey=?"
        self.execute(delete_query, (current_time, params_as_json_string))

        select_query = "SELECT content, status_code, headers FROM cached_responses WHERE path=? AND paramkey=?"
        res = self.execute(select_query, (path, params_as_json_string))
       
        return res
    
    def store_value(self, path, content, status_code, headers, params):
        current_time = time.time()

        insert_query = "INSERT OR REPLACE INTO cached_responses (path,paramkey,content,status_code,headers,timestamp) VALUES (?, ?, ?, ?, ?, ?)"
        self.execute(insert_query, (path, params, content, status_code, headers, current_time))

    def close(self):
        self.disconnect()

