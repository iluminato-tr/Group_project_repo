import pandas as pd
import numpy as np
import matplotlib
#import allel
import seaborn as sns
matplotlib.use('Agg') # Set the backend to 'Agg' before importing pyplot
import matplotlib.pyplot as plt

def get_population_data(SelPop_populations, SelPop_superpopulations, connection):
    """
    This method gets population data for pca analysis. 
    """
    values = ''
    pop_query= ''
    if len(SelPop_populations) > 0:
        pop_query = """
        SELECT s.sample_id, pc.PC1, pc.PC2, s.population_code, s.superpopulation_code 
        FROM pca as pc
        JOIN sample_table as s ON pc.s_id = s.sample_id
        WHERE s.population_code IN (%(val)s); 
        """
        values = ', '.join(["'{}'".format(value) for value in SelPop_populations])
    elif len(SelPop_superpopulations) > 0: 
        pop_query = """
        SELECT s.sample_id, pc.PC1, pc.PC2, s.population_code, s.superpopulation_code 
        FROM pca as pc
        JOIN sample_table as s ON pc.s_id = s.sample_id
        WHERE s.superpopulation_code IN (%(val)s);
        """
        values = ', '.join(["'{}'".format(value) for value in SelPop_superpopulations])

    data = pd.read_sql_query((pop_query%{'val':values}), connection)
    return data

def plot_pca(data, column_name, SelPop_populations, filename="pca_plot.png"): # File name for saved plot image
    """
    This method plots a scatter plot for pca results. 
    """
    unique_values=[]
    data_subset=[]
    # Get unique values (populations or superpopulations) from the specified column
    if len(SelPop_populations) > 0:
        unique_values = data['population_code'].unique()
    else: 
        unique_values = data['superpopulation_code'].unique()

    # Create a color map based on the number of unique values
    colors = plt.cm.get_cmap('gist_rainbow_r', len(unique_values))
    
    # Create a dictionary to map values to colors
    value_colors = {val: colors(i) for i, val in enumerate(unique_values)}

    # Create a new figure for the PCA plot
    plt.figure(figsize=(10, 8))

    # Iterate over each value
    for val in unique_values:
        if len(SelPop_populations) > 0:
            #filter data for population
            data_subset = data[data['population_code'] == val]
        else: 
            data_subset = data[data['superpopulation_code'] == val]

        # Scatter plot for the current value with specified color and label
        plt.scatter(data_subset['pc1'], data_subset['pc2'], color=value_colors[val], label=val, s=50)
    # Set plot title and axis labels
    plt.title(f'PCA Plot with {column_name.capitalize()}')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2') 

    # Add a legend with value labels
    plt.legend(title=column_name.capitalize(), loc='best')

    # Display the plot

    pca_path = 'C:/Users/andre/OneDrive/Masaüstü/Group_project_repo/Flask/static/images/' # CHANGE PATH TO YOUR PATH
    plt.savefig(pca_path+filename)
    plt.close()
    return filename

def get_pop_data(SelPop_populations, SelPop_superpopulations, connection):
    """
    This method gets popultion data for admixture analysis.
    
    """
    value1 = ''
    adm_query= ''
    if len(SelPop_populations) > 0:
        adm_query = """
        SELECT s.sample_id, s.population_code, s.superpopulation_code, a.P1, a.P2, a.P3, a.P4, a.P5
        FROM sample_table s
        JOIN admixture_q a ON s.sample_id = a.sample_id
        WHERE s.population_code IN (%(val)s); 
        """
        value1 = ', '.join(["'{}'".format(value) for value in SelPop_populations])
    else: 
        adm_query = """
        SELECT s.sample_id, s.population_code, s.superpopulation_code, a.P1, a.P2, a.P3, a.P4, a.P5
        FROM sample_table s
        JOIN admixture_q a ON s.sample_id = a.sample_id
        WHERE s.superpopulation_code IN (%(val)s);
        """
        value1 = ', '.join(["'{}'".format(value) for value in SelPop_superpopulations])

    data1 = pd.read_sql_query((adm_query%{'val':value1}), connection)

    return data1

def plot_adm(data1, column_name, SelPop_populations, filename="adm_plot.png"): # File name for saved adm plot
    """
    This method returns the heatmap for admixture analysis.
    
    """
    unique_values1=[]
    data_subset1=[]
    # Get unique values (populations or superpopulations) from the specified column
    if len(SelPop_populations) > 0:
        unique_values1 = data1['population_code'].unique()
    else: 
        unique_values1 = data1['superpopulation_code'].unique()

    # Calculate proportions
    proportions = {}
    for val in unique_values1:
        if len(SelPop_populations) > 0:
            #filter data for population
            data_subset1=data1[data1['population_code'] == val]
            pop_proportions = data_subset1[['p1', 'p2', 'p3', 'p4', 'p5']].mean() * 100
            proportions[val] = pop_proportions
        else: 
            data_subset1=data1[data1['superpopulation_code'] == val]
            suppop_proportions = data_subset1[['p1', 'p2', 'p3', 'p4', 'p5']].mean() * 100
            proportions[val] = suppop_proportions

    heatmap_data = np.array([proportions[val] for val in unique_values1])

    # Plot heatmap
    plt.figure(figsize=(10, 8))
    plt.imshow(heatmap_data, cmap='plasma', aspect='auto')

    # Customize plot
    plt.colorbar(label='Proportion')
    plt.title('Ancestral Proportions by ' + column_name.capitalize())
    plt.xlabel('Ancestral Population')
    plt.ylabel(column_name.capitalize())
    plt.xticks(np.arange(len(proportions[val])), proportions[val].index)
    plt.yticks(np.arange(len(unique_values1)), unique_values1)
    plt.xticks(rotation=45)

    # Show plot
    plt.tight_layout()
    adm_path= 'C:/Users/andre/OneDrive/Masaüstü/Group_project_repo/Flask/static/images/' # CHANGE PATH TO YOUR PATH
    plt.savefig(adm_path+filename)
    plt.close()
    return filename


def get_clinical_data(selected_SNPid, selected_gene, selected_genomic_start, selected_genomic_end, connection):
    """
    Retrieves clinical relevance information for a selected SNP ID, gene name, or genomic coordinates.

    """
    value2 = ''
    snpclinical_query = ''

    # Check the format of the user input
    if ":" in selected_SNPid or ";" in selected_SNPid or selected_SNPid.startswith("rs") :
        """
        If the input contains a colon, assume it's in the "1:1049470:G:A" format, If the input contains a 
        #semicolon, assume it's in the "rs2274976;1:11790870:C:T" format, If the input starts with "rs", assume it's in the "rs2274976" format
        
        """ 
        snpclinical_query = """
        SELECT v.pos, v.snpid, v.refe, v.alt, v.geneName, sr.hgvscodon, sr.hgvsprotein, sr.phenotype, sr.molecular_consequence, sr.variant_significance, sr.NM_ID, sr.cytogenic_region
        FROM variant as v
        JOIN SNP_clinical_relevance as sr 
        ON sr.chromStart = v.pos AND v.refe = sr.ref_a AND v.alt = sr.alt_a 
        WHERE sr.phenotype != 'not provided'
        AND v.snpid = %(val)s; 
        """
        value2 = {'val':selected_SNPid}

    elif len(selected_gene)>0:
        
        snpclinical_query = """
        SELECT v.pos, v.snpid, v.refe, v.alt, v.geneName, sr.hgvscodon, sr.hgvsprotein, sr.phenotype, sr.molecular_consequence, sr.variant_significance, sr.NM_ID, sr.cytogenic_region
        FROM variant as v
        JOIN SNP_clinical_relevance as sr 
        ON sr.chromStart = v.pos AND v.refe = sr.ref_a AND v.alt = sr.alt_a 
        WHERE sr.phenotype != 'not provided'
        AND sr.geneName = %(val)s; 
        """
        value2 = {'val': selected_gene}

    elif len(selected_genomic_start) and len(selected_genomic_end)>0:

        snpclinical_query= """
        SELECT v.pos, v.snpid, v.refe, v.alt, v.geneName, sr.hgvscodon, sr.hgvsprotein, sr.phenotype, sr.molecular_consequence, sr.variant_significance, sr.NM_ID, sr.cytogenic_region
        FROM variant as v
        JOIN SNP_clinical_relevance as sr 
        ON sr.chromStart = v.pos AND v.refe = sr.ref_a AND v.alt = sr.alt_a 
        WHERE sr.phenotype != 'not provided'
        AND v.pos BETWEEN %(start)s AND %(end)s;
        """
        value2 = {'start': selected_genomic_start, 'end': selected_genomic_end}
    else:
        # Handle other cases if needed
        print("Clinical relevance not provided")

    print(snpclinical_query)

    data2 = pd.read_sql_query(snpclinical_query, connection, params=value2)

    return data2
    
def get_allele_frequency(selected_SNPid, selected_gene, selected_genomic_start, selected_genomic_end, selected_populations, connection):
    """
    Retrieves allele frequencies for a selected population based on criteria such as SNP ID, gene name, or genomic coordinates.

    """
    value3 = ''
    allele_query = ''
    
    if len(selected_populations) > 0 and (":" in selected_SNPid or ";" in selected_SNPid or selected_SNPid.startswith("rs")):
        # Assuming the column names follow the pattern: population_ref, population_alt
        population_columns = [f"{pop}_ref, {pop}_alt" for pop in selected_populations]
        selected_columns = ", ".join(population_columns)
        
        allele_query = f"""
        SELECT pos, geneName, snpId, refe, alt, {selected_columns}
        FROM population_allele_frq
        WHERE snpId = %(val)s
        """
        value3 = {'val': selected_SNPid}

    elif len(selected_populations)>0 and len(selected_gene)>0:
        # Assuming the column names follow the pattern: population_ref, population_alt
        population_columns = [f"{pop}_ref, {pop}_alt" for pop in selected_populations]
        selected_columns = ", ".join(population_columns)
        
        allele_query = f"""
        SELECT pos, snpId, geneName, refe, alt, {selected_columns}
        FROM population_allele_frq
        WHERE geneName = %(val)s
        """
        value3 = {'val': selected_gene}

    elif len(selected_populations)>0 and len(selected_genomic_start) and len(selected_genomic_end)>0:
        # Assuming the column names follow the pattern: population_ref, population_alt
        population_columns = [f"{pop}_ref, {pop}_alt" for pop in selected_populations]
        selected_columns = ", ".join(population_columns)

        allele_query = f"""
        SELECT pos, snpId, geneName, refe, alt, {selected_columns}
        FROM population_allele_frq
        WHERE pos BETWEEN %(start)s AND %(end)s;
        """
        value3 = {'start': selected_genomic_start, 'end': selected_genomic_end}

    else: 
        print('Allele frequency not provided')

    data3= pd.read_sql_query(allele_query, connection, params=value3)

    return data3

def get_genotype_frequency(selected_SNPid, selected_gene, selected_genomic_start, selected_genomic_end, selected_populations, connection):
    """
    Retrieves genotypic frequencies for a selected population based on criteria such as SNP ID, gene name, or genomic coordinates.
 
    """
    value4 = ''
    genotype_query = ''
    
    if len(selected_populations) > 0 and (":" in selected_SNPid or ";" in selected_SNPid or selected_SNPid.startswith("rs")):
        # Assuming the column names follow the pattern: population_hom_ref, population_hom_alt and population_het
        population_columns = [f"{pop}_hom_alt, {pop}_het, {pop}_hom_ref" for pop in selected_populations]
        selected_columns = ", ".join(population_columns)
        
        genotype_query= f"""
        SELECT pos, geneName, snpId, refe, alt, {selected_columns}
        FROM pop_gen_frq
        WHERE snpId = %(val)s
        """
        value4 = {'val': selected_SNPid}

    elif len(selected_populations)>0 and len(selected_gene)>0:
        # Assuming the column names follow the pattern: population_hom_ref, population_hom_alt and population_het
        population_columns = [f"{pop}_hom_alt, {pop}_het, {pop}_hom_ref" for pop in selected_populations]
        selected_columns = ", ".join(population_columns)
        
        genotype_query = f"""
        SELECT pos, snpId, geneName, refe, alt, {selected_columns}
        FROM pop_gen_frq
        WHERE geneName = %(val)s
        """
        value4 = {'val': selected_gene}

    elif len(selected_populations)>0 and len(selected_genomic_start) and len(selected_genomic_end)>0:
        # Assuming the column names follow the pattern: population_hom_ref, population_hom_alt and population_het
        population_columns = [f"{pop}_hom_alt, {pop}_het, {pop}_hom_ref" for pop in selected_populations]
        selected_columns = ", ".join(population_columns)

        genotype_query = f"""
        SELECT pos, snpId, geneName, refe, alt, {selected_columns}
        FROM pop_gen_frq
        WHERE pos BETWEEN %(start)s AND %(end)s;
        """
        value4 = {'start': selected_genomic_start, 'end': selected_genomic_end}

    else: 
        print('Allele frequency not provided')

    data4= pd.read_sql_query(genotype_query, connection, params=value4)

    return data4

def calculate_fst(data, pop_names):
    # Identify genotype columns
    genotype_columns = [col for col in data.columns if col.endswith('_ref') or col.endswith('_alt')]
    allele_counts_df = data[genotype_columns]

    # Replace NoneType values with 0
    allele_counts_df = allele_counts_df.fillna(0)

    # Compute allele frequencies across populations
    allele_counts = allele_counts_df.values

    # Calculate sums along rows
    row_sums = np.sum(allele_counts, axis=1)

    # Avoid division by zero
    row_sums[row_sums == 0] = 1

    allele_freqs = allele_counts / row_sums[:, np.newaxis]

    # Calculate average allele frequencies across populations
    avg_allele_freqs = np.mean(allele_freqs, axis=0)

    # Calculate expected heterozygosity within populations (Hs)
    Hs = 2 * avg_allele_freqs * (1 - avg_allele_freqs)

    # Calculate expected heterozygosity across populations (Ht)
    Ht = np.sum(Hs)

    # Initialize Fst matrix
    num_pops = len(pop_names)
    Fst_matrix = np.zeros((num_pops, num_pops))

    for i, pop1 in enumerate(pop_names):
        for j, pop2 in enumerate(pop_names):
            if i > j:  # Calculate Fst only for upper triangular part
                # Extract allele counts for the two populations
                pop1_counts = allele_counts_df[[col for col in genotype_columns if pop1 in col]].sum(axis=1)
                pop2_counts = allele_counts_df[[col for col in genotype_columns if pop2 in col]].sum(axis=1)

                # Convert NoneType values to 0
                pop1_counts = np.nan_to_num(pop1_counts)
                pop2_counts = np.nan_to_num(pop2_counts)

                # Avoid division by zero
                pop1_total = np.sum(pop1_counts)
                pop2_total = np.sum(pop2_counts)
                if pop1_total == 0 or pop2_total == 0:
                    Fst_matrix[i, j] = np.nan
                    Fst_matrix[j, i] = np.nan
                    continue

                # Compute allele frequencies
                allele_freqs_pop1 = pop1_counts / pop1_total
                allele_freqs_pop2 = pop2_counts / pop2_total

                # Calculate Fst using the Weir and Cockerham method
                Fst_ij = (Ht - (Hs[i] + Hs[j]) / 2) / Ht

                Fst_matrix[i, j] = Fst_ij
                Fst_matrix[j, i] = Fst_ij  # Assign to the symmetric position as well

    return Fst_matrix