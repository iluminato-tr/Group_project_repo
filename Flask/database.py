import psycopg2
""" 
CHANGE TO YOUR DATABASE INFORMATION

"""
def setup():
    host = "localhost"
    port = "5432"    
    user = "postgres"
    password = "Poojita15$"
    database = "populationgenetics"   
    try:
        # Establish a connection
        connection = psycopg2.connect(
        host=host,
        port=port,        
        user=user,        
        password=password,
        database=database 
        )
        cursor = connection.cursor()

        return cursor, connection
    
    except psycopg2.Error as e:
        print(f"Error: Unable to connect to the PostgreSQL server. {e}")

# Close the cursor and connection   
def close(cursor, connection):
    cursor.close()
    connection.close()
    print("Connection closed.")

    return