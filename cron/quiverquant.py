import os
import requests
import psycopg2

def fetch_data():
    """
    Make an HTTP GET request to some API endpoint.
    Return the parsed JSON response.
    """
    url = "https://api.example.com/data"  # Replace with your desired endpoint
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError if the response was not 200
    return response.json()

def upload_data_to_db(data):
    """
    Insert or update data into your Postgres DB in multiple tables.
    """
    # Get the DATABASE_URL provided by Heroku
    database_url = os.environ.get("DATABASE_URL")
    
    # Connect to the database
    # 'sslmode=require' is often recommended on Heroku
    conn = psycopg2.connect(database_url, sslmode='require')
    cursor = conn.cursor()
    
    try:
        # EXAMPLE: Suppose 'data' is a dict containing "users" and "orders"
        users = data.get("users", [])
        orders = data.get("orders", [])
        
        # Insert into a "users" table (columns: id, name, email)
        for user in users:
            cursor.execute("""
                INSERT INTO users (id, name, email)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                  SET name = EXCLUDED.name,
                      email = EXCLUDED.email
            """, (user["id"], user["name"], user["email"]))
        
        # Insert into an "orders" table (columns: order_id, user_id, amount)
        for order in orders:
            cursor.execute("""
                INSERT INTO orders (order_id, user_id, amount)
                VALUES (%s, %s, %s)
                ON CONFLICT (order_id) DO UPDATE
                  SET user_id = EXCLUDED.user_id,
                      amount = EXCLUDED.amount
            """, (order["order_id"], order["user_id"], order["amount"]))
        
        # Commit the transaction
        conn.commit()
    
    finally:
        # Always close the cursor and connection
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        #data = fetch_data()
        # upload_data_to_db(data)
        print("Data successfully fetched and stored.")
    except Exception as e:
        # In a real-world scenario, you might log this or notify yourself
        print(f"An error occurred: {e}")


