pip install matplotlib
pip install pandas
pip install -U Flask
pip install matplotlib
pip install Python-IO

from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from io import BytesIO
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    selected_populations = request.form.getlist('populations')
    selected_superpopulation = request.form.getlist('superpopulations')
    
    # SQL query to retrieve data for selected populations
    pop_query = """
    SELECT s.sample_id, pc.PC1, pc.PC2, pc.PC3, s.population_code, s.superpopulation_code 
    FROM pca_results as pc
    JOIN sample_table as s ON pc.s_id = s.sample_id;
    WHERE s.population_code IN (%(pop)s)
        OR s.superpopulation_code IN (%(supop)s)
    );
    """
    # Execute the SQL query (replace this with your database connection and query execution logic)
    # Example using pandas to simulate the data retrieval
    data = pd.read_sql_query((pop_query%{'pop':selected_populations, 'supop':selected_superpopulation}), connection)

    # Create a 3D PCA plot
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    for p_code in data['population_code'].unique():
        subset = data[data['population_code'] == p_code]
        ax.scatter(subset['PC1'], subset['PC2'], subset['PC3'], label=p_code)

    for sp_code in data['superpopulation_code'].unique():
        subset = data[data['superpopulation_code'] == sp_code]
        ax.scatter(subset['PC1'], subset['PC2'], subset['PC3'], label=sp_code)


    ax.set_xlabel('PCA_Component_1')
    ax.set_ylabel('PCA_Component_2')
    ax.set_zlabel('PCA_Component_3')
    ax.set_title('3D PCA Analysis')
    ax.legend()

    # Save the plot to a BytesIO object
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)

    # Convert the image to base64 for embedding in HTML
    plot_img = base64.b64encode(image_stream.read()).decode('utf-8')

    return render_template('plot.html', plot_img=plot_img)

if __name__ == '__main__':
    app.run(debug=True)
