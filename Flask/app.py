from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SubmitField, StringField, TextAreaField, RadioField
from wtforms.validators import Optional, DataRequired
import helper
from database import setup, close

# Initialise the Flask application & set secret key for CSRF protection
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdfgklhjersjio49430-9534-5'

# Setup DB connection
cursor, connection = setup()

# Define form for SNP analysis queries
class SNPAnalysisForm(FlaskForm):

    # Define choices for populations and superpopulations for the form
    # Each tuple contains a superpopulation and its corresponding populations
    population_choices = [
        ([('EUR','Europe')], [('FIN', 'Finnish - Finnish in Finland'),
                    ('CEU', 'CEPH - Utah residents with Northern and Western European ancestry'),
                    ('IBS', 'Iberian - Iberian populations in Spain'),
                    ('TSI', 'Toscani - Toscani in Italy'),
                    ('GBR', 'British - British in England and Scotland')]),

        ([('EAS','East Asia')], [('CHS', 'Southern Han Chinese - Han Chinese South'),
                       ('KHV', 'Kinh Vietnamese - Kinh in Ho Chi Minh City, Vietnam'),
                       ('JPT', 'Japanese - Japanese in Tokyo, Japan'),
                       ('CHB', 'Han Chinese - Han Chinese in Beijing, China'),
                       ('CDX', 'Dai Chinese - Chinese Dai in Xishuangbanna, China'),
                       ('SIB', 'Siberian - Siberians in Siberia')]),

        ([('SAS','South Asia')], [('PJL', 'Punjabi - Punjabi in Lahore, Pakistan'),
                        ('BEB', 'Bengali - Bengali in Bangladesh'),
                        ('GIH', 'Gujarati - Gujarati Indians in Houston, TX'),
                        ('STU', 'Tamil - Sri Lankan Tamil in the UK'),
                        ('ITU', 'Telugu - Indian Telugu in UK')]),

        ([('AFR','Africa')], [('YRI', 'Yoruba - Yoruba in Ibadan, Nigeria'),
                    ('LWK', 'Luhya - Luhya in Webuye, Kenya'),
                    ('ASW', 'African Ancestry - African Ancestry in Southwest US'),
                    ('GWD', 'Gambian Mandinka - Gambian in Western DIvision, The Gambia'),
                    ('MSL', 'Mende - Mende in Sierra Leone'),
                    ('ESN', 'Esan - Esan in Nigeria')]),
                    
        ([('AMR','America')], [('MXL', 'Mexican Ancestry - Mexican Ancestry in Los Angeles, California'),
                     ('ACB', 'African Caribbean - African Caribbean in Barbados'),
                     ('PUR', 'Puerto Rican in Puerto Rico'),
                     ('CLM', 'Colombian - Colombian in Medellin, Colombia'),
                     ('PEL', 'Peruvian - Peruvian in Lima, Peru')])

    ]

    # Fields for selecting superpopulations and populations
    populations = SelectMultipleField('Select Populations', choices=[(id, name) for group in population_choices for id, name in group[1]], validators=[DataRequired()])

    # Allows selection of query type
    query_type = RadioField('Query Type', choices=[('snp', 'SNP IDs'), ('gene', 'Gene Names'), ('region', 'Genomic Coordinates')], validators=[DataRequired()])

    # Fields for entering relevant query types
    snp_ids = TextAreaField('SNP IDs (comma-separated)', validators=[Optional()])
    #genomic_coords = StringField('Genomic Coordinates (Format: chromosome:start-end)', validators=[Optional()])
    gene_names = StringField('Gene Names (comma-separated)', validators=[Optional()])


    genomic_start = StringField('Genomic Start Position:', validators=[Optional()])
    genomic_end = StringField('Genomic End Position:', validators=[Optional()])

    # Submit button for the form
    submit = SubmitField('Submit Query')



# Define form for population analysis queries
class PopulationAnalysisForm(FlaskForm):
    # Selection between population and superpopulation scopes
    Pop_scope = RadioField('Analysis Scope', choices=[('superpopulation', 'Superpopulation'), ('population', 'Population')], validators=[DataRequired()])

    # Define choices for populations and superpopulations for the form
    # Each tuple contains a superpopulation and its corresponding populations
    Pop_choices = [
        ([('EUR','Europe')], [('FIN', 'Finnish - Finnish in Finland'),
                    ('CEU', 'CEPH - Utah residents with Northern and Western European ancestry'),
                    ('IBS', 'Iberian - Iberian populations in Spain'),
                    ('TSI', 'Toscani - Toscani in Italy'),
                    ('GBR', 'British - British in England and Scotland')]),

        ([('EAS','East Asia')], [('CHS', 'Southern Han Chinese - Han Chinese South'),
                       ('KHV', 'Kinh Vietnamese - Kinh in Ho Chi Minh City, Vietnam'),
                       ('JPT', 'Japanese - Japanese in Tokyo, Japan'),
                       ('CHB', 'Han Chinese - Han Chinese in Beijing, China'),
                       ('CDX', 'Dai Chinese - Chinese Dai in Xishuangbanna, China'),
                       ('SIB', 'Siberian - Siberians in Siberia')]),

        ([('SAS','South Asia')], [('PJL', 'Punjabi - Punjabi in Lahore, Pakistan'),
                        ('BEB', 'Bengali - Bengali in Bangladesh'),
                        ('GIH', 'Gujarati - Gujarati Indians in Houston, TX'),
                        ('STU', 'Tamil - Sri Lankan Tamil in the UK'),
                        ('ITU', 'Telugu - Indian Telugu in UK')]),

        ([('AFR','Africa')], [('YRI', 'Yoruba - Yoruba in Ibadan, Nigeria'),
                    ('LWK', 'Luhya - Luhya in Webuye, Kenya'),
                    ('ASW', 'African Ancestry - African Ancestry in Southwest US'),
                    ('GWD', 'Gambian Mandinka - Gambian in Western DIvision, The Gambia'),
                    ('MSL', 'Mende - Mende in Sierra Leone'),
                    ('ESN', 'Esan - Esan in Nigeria')]),
                    
        ([('AMR','America')], [('MXL', 'Mexican Ancestry - Mexican Ancestry in Los Angeles, California'),
                     ('ACB', 'African Caribbean - African Caribbean in Barbados'),
                     ('PUR', 'Puerto Rican in Puerto Rico'),
                     ('CLM', 'Colombian - Colombian in Medellin, Colombia'),
                     ('PEL', 'Peruvian - Peruvian in Lima, Peru')])

    ]

    Pop_superpopulations = SelectMultipleField('Select Superpopulations', choices=[(id, name) for group in Pop_choices for id, name in group[0]], validators=[Optional()])
    Pop_populations = SelectMultipleField('Select Populations', choices=[(id, name) for group in Pop_choices for id, name in group[1]], validators=[Optional()])
    Pop_submit = SubmitField('Analyse Population')

# Route for handling the population analysis form
@app.route('/population_analysis', methods=['GET', 'POST'])
def population_analysis():
    form = PopulationAnalysisForm()
    if form.validate_on_submit():
        # Retrieve selected populations and superpopulations from form
        SelPop_populations = request.form.getlist('Pop_populations')
        SelPop_superpopulations = request.form.getlist('Pop_superpopulations')
        data = helper.get_population_data(SelPop_populations, SelPop_superpopulations, connection)
        data1 = helper.get_pop_data(SelPop_populations, SelPop_superpopulations, connection)
        """
        call method to do plot pca result

        """

        pca_plot_filename = "pca_plot.png"
        admixture_plot_filename = "adm_plot.png"

        if len(SelPop_populations) > 0:
            pca_plot_filename = helper.plot_pca(data, 'population_code', SelPop_populations, pca_plot_filename)
        else:
            # Plot based on superpopulations (P2)
            pca_plot_filename = helper.plot_pca(data, 'superpopulation_code', SelPop_populations, pca_plot_filename) 
        
        """
        call method to plot admixture result

        """

        if len(SelPop_populations) > 0:
            admixture_plot_filename = helper.plot_adm(data1, 'population_code', SelPop_populations, admixture_plot_filename) 
        else:
            # Plot based on superpopulations (P2)
            admixture_plot_filename = helper.plot_adm(data1, 'superpopulation_code', SelPop_populations, admixture_plot_filename) 
        session['pca_image'] = pca_plot_filename
        session['adm_image'] = admixture_plot_filename
        return redirect(url_for('results'))
        # return render_template('results.html', pca_image=pca_plot_filename, adm_image = admixture_plot_filename)
    return render_template('population_analysis.html', form=form)

# Route for handling SNP analysis form
@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    form = SNPAnalysisForm()
    print("SNP FORM DISPLAY")
    if form.validate_on_submit():
    # Form data processing to be completed, for now it prints input and redirects to results
    
        selected_populations = request.form.getlist('populations')
        selected_SNPid = request.form.get('snp_ids')
        selected_gene = request.form.get('gene_names')
        selected_genomic_start= request.form.get('genomic_start')
        selected_genomic_end=request.form.get('genomic_end')

        """"
        call method to display clinical relevance for gene, snpid and genomic coordinates.
        
        """
        # Inside your /analysis route
        data2 = helper.get_clinical_data(selected_SNPid, selected_gene, selected_genomic_start, selected_genomic_end, connection)

        # Initializing an empty list for clinical data to handle cases where no data is found or provided
        session['clinical_data'] = []

        # The if conditions remain the same to check which data to fetch based on the input
        if ":" in selected_SNPid or ";" in selected_SNPid or selected_SNPid.startswith("rs"):
            # If data2 is not empty, convert it to a list of dictionaries and store in session
            if not data2.empty:
                print("before ssetting", session.get('clinical_data'))
                session['clinical_data'] = data2.to_dict('records')
                print("after setiing", session["clinical_data"])
            else:
                print('No clinical data found for the SNP ID')
        elif len(selected_gene) > 0:
            if not data2.empty:
                print("before ssetting", session.get('clinical_data'))
                session['clinical_data'] = data2.to_dict('records')
                print("after setiing", session["clinical_data"])
            else:
                print('No clinical data found for the gene name')
        elif len(selected_genomic_start) > 0 and len(selected_genomic_end) > 0:
            if not data2.empty:
                print("before ssetting", session.get('clinical_data'))
                session['clinical_data'] = data2.to_dict('records')
                print("after setiing", session["clinical_data"])
            else:
                print('No clinical data found for the genomic coordinates')
        else:
            print('Clinical relevance not provided')

        """
        call method to display allele frequencies for gene, snpid and genomic coordinates.
        
        """
        # Inside your /analysis route
        data3 = helper.get_allele_frequency(selected_SNPid, selected_gene, selected_genomic_start, selected_genomic_end, selected_populations, connection)

        # Initializing an empty list for allele frequency data to handle cases where no data is found or provided
        session['allele_frequency_data'] = []

        # The if conditions remain the same to check which data to fetch based on the input
        if ":" in selected_SNPid or ";" in selected_SNPid or selected_SNPid.startswith("rs") and len(selected_populations) > 0:
            if not data3.empty:
                session['allele_frequency_data'] = data3.to_dict('records')
                print(data3)
            else:
                print('No allele frequency data found for the SNP ID')
        elif len(selected_gene) > 0 and len(selected_populations) > 0:
            if not data3.empty:
                session['allele_frequency_data'] = data3.to_dict('records')
                print(data3)
            else:
                print('No allele frequency data found for the gene name')
        elif len(selected_genomic_start) > 0 and len(selected_genomic_end) > 0 and len(selected_populations) > 0:
            if not data3.empty:
                session['allele_frequency_data'] = data3.to_dict('records')
                print(data3)
            else:
                print('No allele frequency data found for the genomic coordinates')
        else:
            print('Allele frequency not provided')


        """
        call method to display genotypic frequencies for gene, snpid and genomic coordinates.
        
        """
        # Inside your /analysis route
        data4 = helper.get_genotype_frequency(selected_SNPid, selected_gene, selected_genomic_start, selected_genomic_end, selected_populations, connection)

        # Initializing an empty list for genotype frequency data to handle cases where no data is found or provided
        session['genotype_frequency_data'] = []

        # The if conditions remain the same to check which data to fetch based on the input
        if ":" in selected_SNPid or ";" in selected_SNPid or selected_SNPid.startswith("rs") and len(selected_populations) > 0:
            if not data4.empty:
                session['genotype_frequency_data'] = data4.to_dict('records')
                print(data4)
            else:
                print('No genotype frequency data found for the SNP ID')
        elif len(selected_gene) > 0 and len(selected_populations) > 0:
            if not data4.empty:
                session['genotype_frequency_data'] = data4.to_dict('records')
                print(data4)
            else:
                print('No genotype frequency data found for the gene name')
        elif len(selected_genomic_start) > 0 and len(selected_genomic_end) > 0 and len(selected_populations) > 0:
            if not data4.empty:
                session['genotype_frequency_data'] = data4.to_dict('records')
                print(data4)
            else:
                print('No genotype frequency data found for the genomic coordinates')
        else:
            print('Genotype frequency not provided')

        return redirect(url_for('results'))
    return render_template('analysis.html', form=form)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/results')
def results():
    # Retrieve filenames from session if they exist; else, use None
    pca_image = session.get('pca_image', None)
    adm_image = session.get('adm_image', None)
    
    # Retrieve data for tables from session
    clinical_data = session.get('clinical_data', [])
    allele_frequency_data = session.get('allele_frequency_data', [])
    genotype_frequency_data = session.get('genotype_frequency_data', [])

    # Pass all the data to the template
    return render_template(
        'results.html',
        pca_image=pca_image,
        adm_image=adm_image,
        clinical_data=clinical_data,
        allele_frequency_data=allele_frequency_data,
        genotype_frequency_data=genotype_frequency_data,
    )

if __name__ == '__main__':
    app.run(debug=True)

close(cursor, connection)