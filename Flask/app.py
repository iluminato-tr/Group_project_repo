from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SubmitField, StringField, TextAreaField, RadioField
from wtforms.validators import Optional, DataRequired
import pandas as pd
import psycopg2

# Initialise the Flask application & set secret key for CSRF protection
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdfgklhjersjio49430-9534-5'

# Define form for SNP analysis queries
class SNPAnalysisForm(FlaskForm):
    # Allows selection between population and superpopulation scopes
    query_scope = RadioField('Query Scope', choices=[('superpopulation', 'Superpopulation'), ('population', 'Population')], validators=[DataRequired()])

    # Define choices for populations and superpopulations for the form
    # Each tuple contains a superpopulation and its corresponding populations
    population_choices = [
        ('Europe', [('FIN', 'Finnish - Finnish in Finland'),
                    ('CEU', 'CEPH - Utah residents with Northern and Western European ancestry'),
                    ('IBS', 'Iberian - Iberian populations in Spain'),
                    ('TSI', 'Toscani - Toscani in Italy'),
                    ('GBR', 'British - British in England and Scotland')]),

        ('East Asia', [('CHS', 'Southern Han Chinese - Han Chinese South'),
                       ('KHV', 'Kinh Vietnamese - Kinh in Ho Chi Minh City, Vietnam'),
                       ('JPT', 'Japanese - Japanese in Tokyo, Japan'),
                       ('CHB', 'Han Chinese - Han Chinese in Beijing, China'),
                       ('CDX', 'Dai Chinese - Chinese Dai in Xishuangbanna, China'),
                       ('SIB', 'Siberian - Siberians in Siberia')]),

        ('South Asia', [('PJL', 'Punjabi - Punjabi in Lahore, Pakistan'),
                        ('BEB', 'Bengali - Bengali in Bangladesh'),
                        ('GIH', 'Gujarati - Gujarati Indians in Houston, TX'),
                        ('STU', 'Tamil - Sri Lankan Tamil in the UK'),
                        ('ITU', 'Telugu - Indian Telugu in UK')]),

        ('Africa', [('YRI', 'Yoruba - Yoruba in Ibadan, Nigeria'),
                    ('LWK', 'Luhya - Luhya in Webuye, Kenya'),
                    ('ASW', 'African Ancestry - African Ancestry in Southwest US'),
                    ('GWD', 'Gambian Mandinka - Gambian in Western DIvision, The Gambia'),
                    ('MSL', 'Mende - Mende in Sierra Leone'),
                    ('ESN', 'Esan - Esan in Nigeria')]),
                    
        ('America', [('MXL', 'Mexican Ancestry - Mexican Ancestry in Los Angeles, California'),
                     ('ACB', 'African Caribbean - African Caribbean in Barbados'),
                     ('PUR', 'Puerto Rican in Puerto Rico'),
                     ('CLM', 'Colombian - Colombian in Medellin, Colombia'),
                     ('PEL', 'Peruvian - Peruvian in Lima, Peru')])

    ]

    # Fields for selecting superpopulations and populations
    superpopulations = SelectMultipleField('Select Superpopulations', choices=[(group[0], group[0]) for group in population_choices], validators=[Optional()])
    populations = SelectMultipleField('Select Populations', choices=[(id, name) for group in population_choices for id, name in group[1]], validators=[Optional()])

    # Allows selection of query type
    query_type = RadioField('Query Type', choices=[('snp', 'SNP IDs'), ('gene', 'Gene Names'), ('region', 'Genomic Coordinates')], validators=[DataRequired()])

    # Fields for entering relevant query types
    snp_ids = TextAreaField('SNP IDs (comma-separated)', validators=[Optional()])
    genomic_coords = StringField('Genomic Coordinates (Format: chromosome:start-end)', validators=[Optional()])
    gene_names = StringField('Gene Names (comma-separated)', validators=[Optional()])

    # Submit button for the form
    submit = SubmitField('Submit Query')

# Define form for population analysis queries
class PopulationAnalysisForm(FlaskForm):
    # Selection between population and superpopulation scopes
    Pop_scope = RadioField('Analysis Scope', choices=[('superpopulation', 'Superpopulation'), ('population', 'Population')], validators=[DataRequired()])

    # Define choices for populations and superpopulations for the form
    # Each tuple contains a superpopulation and its corresponding populations
    Pop_choices = [
        ('Europe', [('FIN', 'Finnish - Finnish in Finland'),
                    ('CEU', 'CEPH - Utah residents with Northern and Western European ancestry'),
                    ('IBS', 'Iberian - Iberian populations in Spain'),
                    ('TSI', 'Toscani - Toscani in Italy'),
                    ('GBR', 'British - British in England and Scotland')]),

        ('East Asia', [('CHS', 'Southern Han Chinese - Han Chinese South'),
                       ('KHV', 'Kinh Vietnamese - Kinh in Ho Chi Minh City, Vietnam'),
                       ('JPT', 'Japanese - Japanese in Tokyo, Japan'),
                       ('CHB', 'Han Chinese - Han Chinese in Beijing, China'),
                       ('CDX', 'Dai Chinese - Chinese Dai in Xishuangbanna, China'),
                       ('SIB', 'Siberian - Siberians in Siberia')]),

        ('South Asia', [('PJL', 'Punjabi - Punjabi in Lahore, Pakistan'),
                        ('BEB', 'Bengali - Bengali in Bangladesh'),
                        ('GIH', 'Gujarati - Gujarati Indians in Houston, TX'),
                        ('STU', 'Tamil - Sri Lankan Tamil in the UK'),
                        ('ITU', 'Telugu - Indian Telugu in UK')]),

        ('Africa', [('YRI', 'Yoruba - Yoruba in Ibadan, Nigeria'),
                    ('LWK', 'Luhya - Luhya in Webuye, Kenya'),
                    ('ASW', 'African Ancestry - African Ancestry in Southwest US'),
                    ('GWD', 'Gambian Mandinka - Gambian in Western DIvision, The Gambia'),
                    ('MSL', 'Mende - Mende in Sierra Leone'),
                    ('ESN', 'Esan - Esan in Nigeria')]),
                    
        ('America', [('MXL', 'Mexican Ancestry - Mexican Ancestry in Los Angeles, California'),
                     ('ACB', 'African Caribbean - African Caribbean in Barbados'),
                     ('PUR', 'Puerto Rican in Puerto Rico'),
                     ('CLM', 'Colombian - Colombian in Medellin, Colombia'),
                     ('PEL', 'Peruvian - Peruvian in Lima, Peru')])

    ]

    Pop_superpopulations = SelectMultipleField('Select Superpopulations', choices=[(group[0], group[0]) for group in Pop_choices], validators=[Optional()])
    Pop_populations = SelectMultipleField('Select Populations', choices=[(id, name) for group in Pop_choices for id, name in group[1]], validators=[Optional()])
    Pop_submit = SubmitField('Analyse Population')


# Route for handling SNP analysis form
@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    form = SNPAnalysisForm()
    print("SNP FORM DISPLAY")
    if form.validate_on_submit():
    # Form data processing to be completed, for now it prints input and redirects to results
    
        selected_populations = request.form.getlist('populations')
        selected_superpopulations = request.form.getlist('superpopulations')
        print("Selected Populations:", selected_populations)
        print("Selected Superpopulations:", selected_superpopulations)
        print("SNP IDs:", form.snp_ids.data)
        print("Genomic Coordinates:", form.genomic_coords.data)
        print("Gene Names:", form.gene_names.data)
        return redirect(url_for('results'))
    return render_template('analysis.html', form=form)

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
    # Route for handling the population analysis form
    @app.route('/population_analysis', methods=['GET', 'POST'])
    def population_analysis():
        form = PopulationAnalysisForm()
        if form.validate_on_submit():
            # Retrieve selected populations and superpopulations from form
            SelPop_populations = request.form.getlist('Pop_populations')
            SelPop_superpopulations = request.form.getlist('Pop_superpopulations')
            values = ''
            pop_query= ''
            if len(SelPop_populations) > 0:
                pop_query = """
                SELECT s.sample_id, pc.PC1, pc.PC2, pc.PC3, s.population_code, s.superpopulation_code 
                FROM pca_results as pc
                JOIN sample_table as s ON pc.s_id = s.sample_id
                WHERE s.population_code IN (%(val)s); 
                """
                values = ', '.join(["'{}'".format(value) for value in SelPop_populations])
            else: 
                pop_query = """
                SELECT s.sample_id, pc.PC1, pc.PC2, pc.PC3, s.population_code, s.superpopulation_code 
                FROM pca_results as pc
                JOIN sample_table as s ON pc.s_id = s.sample_id
                WHERE s.superpopulation_code IN (%(val)s);
                """
                values = ', '.join(["'{}'".format(value) for value in SelPop_superpopulations])

            data = pd.read_sql_query((pop_query%{'val':values}), connection)
            # Rest of your code
            
            
        
            return redirect(url_for('results'))
        return render_template('population_analysis.html', form=form)
except psycopg2.Error as e:
    print(f"Error: Unable to connect to the PostgreSQL server. {e}")
# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for results page
@app.route('/results')
def results():
    return render_template('results.html')


if __name__ == '__main__':
    app.run(debug=True)