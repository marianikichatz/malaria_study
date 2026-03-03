# Malaria case study pipeline

*Author: Maria Niki Chatzantoni*  
*Class: BINP29*  
*Date: March 2026*

## Scope

In this repository, the main goal was to process the *Haemoproteus tartakovskyi* genome assembly, predict genes, and check the evolutionary relationships of the different malaria host species. The workflow included:

1. Prepare and filter the *Haemoproteus tartakovskyi* assembly
2. Predict genes with GeneMark-ES
3. Extract gene and protein sequences
4. Make predictions against SwissProt for avian host contamination
5. Retrieve scaffold IDs associated with bird like hits

## Repository structure (key folders)

- `data/`: input genomes and training data
- `scripts/`: custom filtering/parsing scripts
- `results/cleaned/`: filtered genome assemblies
- `results/gene_predicted/`: GeneMark predictions and extracted genes/proteins
- `results/BLAST/`: BLAST host-screening outputs
- `results/scaffolds_birds/`: scaffold lists flagged as possible host-derived

## Environment and dependencies

Main tools used:

- `gmes_petap.pl` (GeneMark-ES)
- `gffParse.pl`
- `blastx`, `blastp` (BLAST)
- `python3`
- `sed`, `gunzip`

External data linked into this workspace:

- `/resources/binp29/Data/malaria/taxonomy.dat`
- `/resources/binp29/Data/malaria/uniprot_sprot.dat`

## Steps 

### 1) Gene prediction test run on *Plasmodium cynomolgi*

```bash
gmes_petap.pl --cores 10 --ES --sequence data/Plasmodium_cynomolgi.genome
```

### 2) Decompress raw *Haemoproteus tartakovskyi* genome

```bash
gunzip data/Haemoproteus_tartakovskyi.raw.genome.gz
```

Input used after decompression: `data/Haemoproteus_tartakovskyi.raw.genome`

### 3) Contamination filtering (GC + minimum scaffold length)

```bash
python3 scripts/removeScaffold.py data/Haemoproteus_tartakovskyi.raw.genome 35 results/cleaned/Ht.genome 3000
```

Parameters:

- GC threshold: `35`
- minimum scaffold length: `3000`

Output:

- `results/cleaned/Ht.genome`

### 4) Gene prediction on filtered *H. tartakovskyi* assembly

```bash
nohup gmes_petap.pl --ES --cores 20 --min_contig 10000 --sequence results/cleaned/Ht.genome > logmin.txt 2>&1 &
```

Main output used in later steps:

- `results/gene_predicted/genemark.gtf`

### 5) Reformat GeneMark GTF -> GFF-like file for parsing

```bash
cat results/gene_predicted/genemark.gtf | sed "s/ GC=.*\tGeneMark.hmm/\tGeneMark.hmm/" > results/gene_predicted/Ht2.gff
```

Output:

- `results/gene_predicted/Ht2.gff`

### 6) Extract predicted genes and proteins

```bash
gffParse.pl -i results/cleaned/Ht.genome -g results/gene_predicted/Ht2.gff -b H.tartakovskyi_genes -c -p
```

Generated files (in `results/gene_predicted/`):

- `H.tartakovskyi_genes.fna`
- `H.tartakovskyi_genes.faa`

### 7) BLAST screening against SwissProt for avian contamination

```bash
blastx -query results/gene_predicted/H.tartakovskyi_genes.fna -db SwissProt -out results/BLAST/avian_results_blastx -evalue 1e-10 -num_threads 32
```

```bash
nohup blastp -query results/gene_predicted/H.tartakovskyi_genes.faa -db SwissProt -out results/BLAST/avian_results_blastp -num_descriptions 10 -num_alignments 5 -num_threads 20 > blastp.log 2>&1 &
```

Output files:

- `results/BLAST/avian_results_blastx`
- `results/BLAST/avian_results_blastp`

### 8) Link taxonomy and SwissProt metadata

```bash
ln -s /resources/binp29/Data/malaria/taxonomy.dat taxonomy.dat
ln -s /resources/binp29/Data/malaria/uniprot_sprot.dat uniprot_sprot.dat
```

### 9) Retrieve scaffolds with potential bird-host hits

From BLASTX output:

```bash
python3 scripts/datParser.py results/BLAST/avian_results_blastx results/gene_predicted/H.tartakovskyi_genes.fna taxonomy.dat uniprot_sprot.dat > results/scaffolds_birds/scaffolds_blastx.txt
```

From BLASTP output:

```bash
python3 scripts/datParser.py results/BLAST/avian_results_blastp results/gene_predicted/H.tartakovskyi_genes.faa taxonomy.dat uniprot_sprot.dat > results/scaffolds_birds/scaffolds_blastp.txt
```

Outputs:

- `results/scaffolds_birds/scaffolds_blastx.txt`
- `results/scaffolds_birds/scaffolds_blastp.txt`

## Status

Completed:

- filtered the *H. tartakovskyi* genome for likely contamination
- predicted genes and extracted nucleotide/protein sequences
- screened predicted genes with BLASTX/BLASTP against SwissProt
- retrieved scaffold candidates associated with bird-related hits