#pip install psycopg2

import psycopg2
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
    #Create a cursor object
    cursor = connection.cursor()
    #cursor.execute("SELECT * FROM pca_results;")
    #print(cursor.fetchall())
except psycopg2.Error as e:
    print(f"Error: Unable to connect to the PostgreSQL server. {e}")
    
finally:
    # Close the cursor and connection
    if connection:
        cursor.close()
        connection.close()
        print("Connection closed.")