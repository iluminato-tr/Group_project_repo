from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from matplotlib import pyplot as plt
import numpy as np
from wtforms import SelectMultipleField, SubmitField, StringField, TextAreaField, RadioField
from wtforms.validators import Optional, DataRequired
import helper
from database import setup, close
import pandas as pd
import os
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
        session['query_submitted'] = True
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
        # Paths to the CSV files
        clinical_data_path = 'S:/Documents/UNIVERSITY/POSTGRADUATE/SLACKWARE/Flask/static/txt_files/Clinical_data.txt'
        allele_frequency_data_path = 'S:/Documents/UNIVERSITY/POSTGRADUATE/SLACKWARE/Flask/static/txt_files/allel_frequency_data.txt'
        genotype_frequency_data_path = 'S:/Documents/UNIVERSITY/POSTGRADUATE/SLACKWARE/Flask/static/txt_files/Genotype_frequency_data.txt'
        
        # Delete existing files if they exist before processing a new query
        for file_path in [clinical_data_path, allele_frequency_data_path, genotype_frequency_data_path]:
            if os.path.exists(file_path):
                os.remove(file_path)

        selected_populations = request.form.getlist('populations')
        selected_SNPid = request.form.get('snp_ids')
        selected_gene = request.form.get('gene_names')
        selected_genomic_start= request.form.get('genomic_start')
        selected_genomic_end=request.form.get('genomic_end')
        
        if os.path.exists('S:/Documents/UNIVERSITY/POSTGRADUATE/SLACKWARE/Flask/static/images/fst_plot.png'):
            os.remove('S:/Documents/UNIVERSITY/POSTGRADUATE/SLACKWARE/Flask/static/images/fst_plot.png')
        fst_plot_filename = "fst_plot.png"
        """"
        call method to display clinical relevance for gene, snpid and genomic coordinates.
        
        """

        data2= helper.get_clinical_data(selected_SNPid, selected_gene, selected_genomic_start, selected_genomic_end, connection)
        
        if (":" in selected_SNPid or ";" in selected_SNPid or selected_SNPid.startswith("rs")) or len(selected_gene)>0 or (len(selected_genomic_start)>0 and len(selected_genomic_end)>0):
            if not data2.empty:
                # Specify the file path
                file_path = 'S:/Documents/UNIVERSITY/POSTGRADUATE/SLACKWARE/Flask/static/txt_files/'+'Clinical_data.txt'

                # Save DataFrame to a text file
                data2.to_csv(file_path, sep=',', index=False)

                print(f"DataFrame saved as text file: {file_path}")
        else:
                print("DataFrame is empty. Skipping table image creation.")
        

        """
        call method to display allele frequencies for gene, snpid and genomic coordinates.
        
        """
        data3= helper.get_allele_frequency(selected_SNPid, selected_gene, selected_genomic_start, selected_genomic_end, selected_populations, connection)
        


        if ((":" in selected_SNPid or ";" in selected_SNPid or selected_SNPid.startswith("rs")) or len(selected_gene)>0 or (len(selected_genomic_start)>0 and len(selected_genomic_end)>0)) and len(selected_populations) > 0 :
            if not data3.empty:
                # Specify the file path
                file_path = 'S:/Documents/UNIVERSITY/POSTGRADUATE/SLACKWARE/Flask/static/txt_files/'+'allel_frequency_data.txt'

                # Save DataFrame to a text file
                data3.to_csv(file_path, sep=',', index=False)

                print(f"DataFrame saved as text file: {file_path}")
        else:
                print("DataFrame is empty. Skipping table image creation.")
        
        if ((":" in selected_SNPid or ";" in selected_SNPid or selected_SNPid.startswith("rs")) or len(selected_gene) > 0 or (len(selected_genomic_start) > 0 and len(selected_genomic_end) > 0)) and len(selected_populations) > 1:
            genotype_columns = [col for col in data3.columns if col.endswith('_ref')]
            pop_names = []
            for i in genotype_columns:
                pop_names.append(i[:3])
            
            Fst_matrix = helper.calculate_fst(data3, pop_names)

            # Write Fst matrix to a text file
            with open('S:/Documents/UNIVERSITY/POSTGRADUATE/SLACKWARE/Flask/static/txt_files/'+"Fst_matrix.txt", "w") as f:
                f.write("Fst matrix:\n")
                f.write("\t" + "\t".join(pop_names) + "\n")
                for i in range(len(pop_names)):
                    f.write(pop_names[i] + "\t" + "\t".join(map(str, Fst_matrix[i])) + "\n")

            # Create heatmap
            plt.figure(figsize=(8, 6))
            plt.imshow(Fst_matrix, cmap='hot', interpolation='nearest')
            plt.colorbar(label='Fst values')
            plt.title('Fst Matrix')
            # Annotate heatmap with Fst values
            for i in range(len(pop_names)):
                for j in range(len(pop_names)):
                    plt.text(j, i, format(Fst_matrix[i, j], '.2f'),
                            ha="center", va="center", color="purple")
            plt.xticks(np.arange(len(pop_names)), pop_names)
            plt.yticks(np.arange(len(pop_names)), pop_names)
            plt.xlabel('Populations')
            plt.ylabel('Populations')
            plt.tight_layout()
            plt.savefig('S:/Documents/UNIVERSITY/POSTGRADUATE/SLACKWARE/Flask/static/images/'+'fst_plot.png')
            plt.close()
       
        else: 
            print('allele frequency not provided')
        
        """
        call method to display genotypic frequencies for gene, snpid and genomic coordinates.
        
        """
        data4= helper.get_genotype_frequency(selected_SNPid, selected_gene, selected_genomic_start, selected_genomic_end, selected_populations, connection)

        if not data4.empty:
                # Specify the file path
                file_path = 'S:/Documents/UNIVERSITY/POSTGRADUATE/SLACKWARE/Flask/static/txt_files/'+'Genotype_frequency_data.txt'

                # Save DataFrame to a text file
                data4.to_csv(file_path, sep=',', index=False)

                print(f"DataFrame saved as text file: {file_path}")
        else:
                print("DataFrame is empty. Skipping table image creation.")

        """

        Call method to display pairwise popualtion matrix and visualise it
        
        """
        session['fst_image'] = fst_plot_filename
        session['query_submitted'] = True
        return redirect(url_for('results'))
    return render_template('analysis.html', form=form)

# Route for home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for the results page
@app.route('/results')
def results():
    # Retrieve filenames from session if they exist; else, use None
    pca_image = session.get('pca_image', None)
    adm_image = session.get('adm_image', None)
    fst_image = session.get('fst_image', None)
    fst_matrix_path = os.path.join(app.root_path, 'static', 'txt_files', 'Fst_matrix.txt')
    fst_matrix_exists = os.path.isfile(fst_matrix_path)



    # Initialize variables outside the conditional blocks
    allele_page = request.args.get('allele_page', 1, type=int)
    genotype_page = request.args.get('genotype_page', 1, type=int)
    clinical_page = request.args.get('clinical_page', 1, type=int)
    more_rows_allele = False
    more_rows_genotype = False
    more_rows_clinical = False
    allele_html = None
    genotype_html = None
    clinical_html = None

    # Initialize rows per page
    rows_per_page = 10

    # Clinical Data
    clinical_data_path = 'S:/Documents/UNIVERSITY/POSTGRADUATE/SLACKWARE/Flask/static/txt_files/Clinical_data.txt'
    if os.path.exists(clinical_data_path):
        clinical_skip = (clinical_page - 1) * rows_per_page
        clinical_df = pd.read_csv(clinical_data_path, skiprows=range(1, clinical_skip + 1), nrows=rows_per_page)
        clinical_html = clinical_df.to_html(classes='table table-striped', index=False)
        next_page_clinical_df = pd.read_csv(clinical_data_path, skiprows=range(1, clinical_skip + rows_per_page + 1), nrows=1)
        more_rows_clinical = not next_page_clinical_df.empty

    # Allele Frequency Data
    allele_data_path = 'S:/Documents/UNIVERSITY/POSTGRADUATE/SLACKWARE/Flask/static/txt_files/allel_frequency_data.txt'
    if os.path.exists(allele_data_path):
        allele_skip = (allele_page - 1) * rows_per_page
        allele_df = pd.read_csv(allele_data_path, skiprows=range(1, allele_skip + 1), nrows=rows_per_page)
        allele_html = allele_df.to_html(classes='table table-striped', index=False)
        next_page_allele_df = pd.read_csv(allele_data_path, skiprows=range(1, allele_skip + rows_per_page + 1), nrows=1)
        more_rows_allele = not next_page_allele_df.empty

    # Genotype Frequency Data
    genotype_data_path = 'S:/Documents/UNIVERSITY/POSTGRADUATE/SLACKWARE/Flask/static/txt_files/Genotype_frequency_data.txt'
    if os.path.exists(genotype_data_path):
        genotype_skip = (genotype_page - 1) * rows_per_page
        genotype_df = pd.read_csv(genotype_data_path, skiprows=range(1, genotype_skip + 1), nrows=rows_per_page)
        genotype_html = genotype_df.to_html(classes='table table-striped', index=False)
        next_page_genotype_df = pd.read_csv(genotype_data_path, skiprows=range(1, genotype_skip + rows_per_page + 1), nrows=1)
        more_rows_genotype = not next_page_genotype_df.empty
    query_submitted = session.get('query_submitted', False)
    return render_template('results.html', query_submitted=query_submitted, pca_image=pca_image, adm_image=adm_image, fst_image=fst_image, fst_matrix_exists=fst_matrix_exists, clinical_table=clinical_html, clinical_page=clinical_page, more_rows_clinical=more_rows_clinical, allele_table=allele_html, allele_page=allele_page, more_rows_allele=more_rows_allele, genotype_table=genotype_html, genotype_page=genotype_page, more_rows_genotype=more_rows_genotype)

if __name__ == '__main__':
    app.run(debug=True)

close(cursor, connection)

    