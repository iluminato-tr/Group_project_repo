import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
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
    pop_query = """
    SELECT s.sample_id, pc.PC1, pc.PC2, pc.PC3, s.population_code, s.superpopulation_code 
    FROM pca_results as pc
    JOIN sample_table as s ON pc.s_id = s.sample_id
    WHERE s.population_code IN ('FIN', 'GBR')
        OR s.superpopulation_code IN ('EUR','EAS');
    """
    #selected_populations= ['FIN', 'GBR'] 'EUR'
    #selected_superpopulation=['EUR','EAS']
    # Execute the SQL query (replace this with your database connection and query execution logic)
    # Example using pandas to simulate the data retrieval
    data = pd.read_sql_query(pop_query, connection)
    print(data)
    # Create a 3D PCA plot
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    for p_code in data['population_code'].unique():
        subset = data[data['population_code'] == p_code]
        plt.scatter(subset['pc1'], subset['pc2'], label='p_code')

    for sp_code in data['superpopulation_code'].unique():
        subset = data[data['superpopulation_code'] == sp_code]
        plt.scatter(subset['pc1'], subset['pc2'], label='sp_code')

    #for code_column in ['population_code', 'superpopulation_code']:
        #for code_value in data[code_column].unique():
            #subset = data[data[code_column] == code_value]
            #sns.scatterplot(x=subset['pc1'], y=subset['pc2'], label=code_value, hue=code_column)

    
    plt.xlabel('PCA_Component_1')
    plt.ylabel('PCA_Component_2')
    plt.title('2D PCA Analysis')
    plt.legend()
    plt.show()

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