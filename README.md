# Malaria case study pipeline

*Author: Maria Niki Chatzantoni*  
*Class: BINP29*  
*Date: March 2026*

## Scope

In this repository, the main goal was to process the *Haemoproteus tartakovskyi* genome assembly, predict genes, and check the evolutionary relationships of the different malaria host species. 

## Workflow 

1. Prepare and filter the *Haemoproteus tartakovskyi* assembly
2. Predict genes with GeneMark-ES
3. Extract gene and protein sequences
4. Make predictions against SwissProt for avian host contamination
5. Retrieve scaffold IDs associated with bird like hits
6. Run orthology clustering with proteinortho6.pl using the 8 proteomes
7. Run BUSCO to evaluate completeness of the predicted proteomes across species
8. Extract shared BUSCOs and create FASTA files for each BUSCO with one sequence per species
9. Align the shared BUSCOs with Clustalo and make trees with RaxML per BUSCO
10. Make a consensus tree using the trees from the previous step and `consense` from Phylip



## Environment and dependencies

Main tools used:

- `gmes_petap.pl` (GeneMark-ES)
- `gffParse.pl` 
- `blastx`, `blastp` (BLAST)
- `python3`
- `proteinortho6.pl` (Proteinortho) [version: 6.3.6]
- `busco` (BUSCO) [version: 6.0.0]
- `clustalo` (Clustalo) [version: 1.2.4]
- `raxmlHPC` (RAxML) [version: 8.2.12]
- `consense` (Phylip) [version: 3.697]

External data linked into this workspace:

- `/resources/binp29/Data/malaria/taxonomy.dat`
- `/resources/binp29/Data/malaria/uniprot_sprot.dat`

## Scripts

- `removeScaffold.py`: A Python script to filter scaffolds based on length and GC content.
- `gffParse.pl`: A Perl script to convert GFF3 files into a tab-delimited format and extract gene and protein sequences.
- `datParse.py`: A Python script to parse BLAST results and extract scaffold IDs associated with avian hits.
- `cleanFastaNObirds.py`: A Python script to filter out scaffolds with avian hits from the assembly.
- `busco.py`: A Python script to parse BUSCO results and extract shared BUSCOs across species.

## Steps 

*Step 1:*
- Prepare and filter the *Haemoproteus tartakovskyi* assembly. We used the `removeScaffold.py` script to filter out scaffolds shorter than 3000 bp, which are likely to be of low quality and may not contain complete genes and we also removed scaffolds with GC content greater than 35%. We decided on these filtering criteria based on the GC curve of the assembly. The command used was:

```bash
python3 scripts/removeScaffold.py data/Haemoproteus_tartakovskyi.raw.genome 35 Ht.genome 3000
```
*Step 2:*
- Predict genes with GeneMark-ES. We ran GeneMark-ES on the filtered assembly to predict gene models. The command used was:

```bash
nohup gmes_petap.pl --ES --cores 20 --min_contig 10000 --sequence results/cleaned/Ht.genome > logmin.txt 1>&2&
```

*Step 3:*
- Change the GTF file format so the separator is a tab and not a space. We used the `gffParse.pl` script to convert the GFF3 output from GeneMark-ES into a tab-delimited format. The command used was:

```bash
cat results/gene_predicted/genemark.gtf | sed "s/ GC=.*\tGeneMark.hmm/\tGeneMark.hmm/" > Ht2.gff

gffParse.pl -i results/cleaned/Ht.genome -g results/gene_predicted/Ht2.gff -b H.tartakovskyi_genes -c -p 
```

*Step 4:*
- Make predictions against SwissProt for avian host contamination. We used `blastx` and `blastp` to search the predicted protein sequences against the SwissProt database. We used different parameters for each search. The parameters were chosesn based on the expected sensitivity and specificity of the searches. The commands used were:

```bash
blastx -query results/gene_predicted/H.tartakovskyi_genes.fna -db SwissProt -out avian_results.txt -evalue 1e-10 -num_threads 32

nohup blastp -query results/gene_predicted/H.tartakovskyi_genes.faa -db SwissProt -out avian_results_blastp -num_descriptions 10 -num_alignments 5 -num_threads 20
```
*Step 5:*
- Retrieve scaffold IDs associated with bird like hits. We used the `datParse.py` script to parse the BLAST results and extract the scaffold IDs that had hits to avian proteins. The command used was:

for blastx results:
```bash
python3 scripts/datParser.py results/BLAST/avian_results_blastx results/gene_predicted/H.tartakovskyi_genes.fna taxonomy.dat uniprot_sprot.dat > scaffolds_blastx.txt
```
for blastp results:
```bash
python3 scripts/datParser.py results/BLAST/avian_results_blastp results/gene_predicted/H.tartakovskyi_genes.faa taxonomy.dat 
uniprot_sprot.dat > scaffolds_blastp.txt
```

*Step 6:*
- Remove scaffolds with avian hits from the assembly. We used the `cleanFastaNObirds.py` script to filter out the scaffolds that had hits to avian proteins. The command used was:

for blastx results:
```bash
python3 scripts/cleanFastaNObirds.py results/gene_predicted/H.tartakovskyi_genes.fna results/scaffolds_birds/scaffolds_blastx.txt cleaned_x.fasta
```

for blastp results:
```bash
python3 scripts/cleanFastaNObirds.py results/gene_predicted/H.tartakovskyi_genes.faa results/scaffolds_birds/scaffolds_blastp.txt cleaned_p.fasta
```

*Step 7:*
- Generate refrence gene/protein files with `gffParse.pl` for the 8 species. We used the `gffParse.pl` script. To prepare comparable proteomes for BUSCO/orthology analysis, we extracted coding and protein sequences from each species genome. This produced per species outputs with prefixes Pb, Pc, Pf, Pk, Pv, Tg, and Py, used in downstream BUSCO and proteinortho steps. The command used was:

```bash
bin/gffParse.pl -i data/Plasmodium_berghei.genome -g data/P_berghei.gtf -b Pb -c -p

bin/gffParse.pl -i data/Plasmodium_cynomolgi.genome -g data/cynomolgi.gtf -b Pc -c -p

bin/gffParse.pl -i data/Plasmodium_faciparum.genome -g data/Pfalciparum.gtf -b Pf -c -p

bin/gffParse.pl -i data/Plasmodium_knowlesi.genome -g data/knowlesi.gtf -b Pk -c -p

bin/gffParse.pl -i data/Plasmodium_vivax.genome -g data/vivax.gtf -b Pv -c -p

bin/gffParse.pl -i data/Toxoplasma_gondii.genome -g data/Tg.gff -b Tg -c -p

bin/gffParse.pl -i data/Plasmodium_yoelii.genome -g data/Plasmodium_yoelii.gtf -b Py -c -p
```

*Step 8:*
- Run orthology clustering with proteinortho6.pl using the 8 proteomes. We used the `proteinortho6.pl` script to cluster the protein sequences from the 8 species into orthologous groups. We selected diamond as the alignment tool as it is faster and more sensitive than BLAST for this task. Also we decided to proceed with the blastp results, as they provided a stricter criteria for the orthology analysis. The command used was:

```bash
nohup proteinortho6.pl -p=diamond -cpus=20 -project=malaria_proteinortho Ht_cleaned_headers.faa Pb_headers.faa Pc_headers.faa Pf_headers.faa Pk_headers.faa Pv_headers.faa Py_headers.faa Tg_headers.faa > proteinortho.log 2>&1 &
```

*Step 9:*
- Run BUSCO to evaluate completeness of the predicted proteomes across species. We used the `run_busco.sh` script to run BUSCO on the predicted protein sequences for each species. We used the `apicomplexa_odb12` lineage dataset as it is specific to the group of organisms we are studying. The command used was:

```bash
nohup ./run_busco.sh > busco.log 2>&1 &
```
*Step 10:*
- Extract shared BUSCOs and create FASTA files for each BUSCO with one sequence per species. We used the `busco.py` script to parse the BUSCO results and extract the shared BUSCOs across all species. We then created FASTA files for each BUSCO with one sequence per species. The command used was:

```bash
python3 scripts/busco.py
```
*Step 11:*
- Align the shared BUSCOs with Clustalo and concatenate the alignments using `raxml`. We used `clustalo` to align the sequences for each BUSCO and then concatenated the alignments into a single file for phylogenetic analysis. The script used for this step is `align.sh` and it takes the FASTA files of the shared BUSCOs as input aligns them and makes a tree with RAxML per BUSCO. The command used was:

for the 8 species:
```bash
nohup scripts/align.sh 8 > align8.log 2>&1 &
```

for the 7 species:
```bash
nohup scripts/align.sh 7 > align7.log 2>&1 &
```

*Step 12:*
- Make a consensus tree using the trees from the previous step and `consense` from Phylip. We used the `consense` program from the Phylip package to create a consensus tree from the individual trees generated for each BUSCO. Before running `consense`, we moved the individual trees to a single file. The command used was:

to move the trees to a single file:
```bash
cat trees_8/*.tree > all_trees_8.txt

cat trees_7/*.tree > all_trees_7.txt
```
to create the consensus tree:

for the 8 species:
```bash
consense < all_trees_8.txt > consensus_8species.tree
```

for the 7 species:
```bash
consense < all_trees_7.txt > consensus_7species.tree
```

## Results

The final output of this pipeline includes consensus trees that illustrate the phylogenetic relationships among the species based on shared BUSCOs. The trees can be visualized using tools like iTOL to interpret the evolutionary relationships among the malaria host species. The results provide insights into the evolutionary history of malaria parasites and their hosts, which can be valuable for understanding disease dynamics and developing strategies for malaria control.
The consensus 8 species tree from the analysis is displayed here:

- [trees/consensus_tree8.svg](trees/consensus_tree8.svg)

## Conclusion

In this pipeline, we processed the *Haemoproteus tartakovskyi* genome assembly, predicted genes, and evaluated the evolutionary relationships of malaria host species. The final output includes consensus trees that illustrate the phylogenetic relationships among the species based on shared BUSCOs. This analysis provides insights into the evolutionary history of malaria parasites and their hosts. 
As we observed, the *Haemoproteus tartakovskyi* is closely related to *Plasmodium* species, which is consistent with previous studies. The trees also show that although the *Haemoproteus tartakovskyi* is closely related to *Plasmodium* species, it forms a distinct clade, which suggests that it has a unique evolutionary history. 
In conclusion, this pipeline provides a comprehensive approach to analyze the genome assembly of *Haemoproteus tartakovskyi* and its evolutionary relationships with other malaria host species, contributing to our understanding of malaria parasite evolution and host interactions. 