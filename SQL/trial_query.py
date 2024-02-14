query2 = """
    SELECT s.sample_id, pc.PC1, pc.PC2, pc.PC3, s.population_code, s.superpopulation_code 
    FROM pca_results as pc
    JOIN sample_table as s ON pc.s_id = s.sample_id;
    WHERE s.population_code IN (%(pop)s)
        OR s.superpopulation_code IN (%(supop)s)
    );
    """
selected_populations= '\'FIN\''  
selected_superpopulation='\'EUR\''
print(query2%{'pop':selected_populations, 'supop':selected_superpopulation})
