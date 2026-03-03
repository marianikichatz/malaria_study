#!/usr/bin/env python3

#Documentation Section

'''

Script name: busco.py

Version: 1.00
Date: 2026-03-03
Name: Maria Niki Chatzantoni

Description:
This script reads BUSCO output folders for multiple species and creates one
protein FASTA file per BUSCO group.

Procedure:
    1. Define input and output paths
    2. Read each species FASTA file into a dictionary (ID -> sequence)
    3. Parse each full_table.tsv and keep only Complete or Duplicated hits
    4. For duplicated BUSCOs, keep only the highest score hit
    5. Find BUSCO IDs shared by all 8 species
    6. Find BUSCO IDs shared by 7 species (excluding Tg)
    7. Write one output FASTA per BUSCO with one sequence per species
    8. Print summary counts

Rules:
1. Keep only BUSCO rows with status Complete or Duplicated
2. If a BUSCO appears multiple times in one species, keep only the best score
3. Write output files only for BUSCOs shared by all compared species
4. Output headers are simple species IDs, for example >Pf, >Pv, >Tg

User-defined functions: get_arguments(), read_fasta(), parse_full_table(),
load_all_species(), find_shared_buscos(), write_output_files(), print_summary(), main()
Non-standard modules: None

Input:
- BUSCO folders under results/proteins/busco/*_busco/run_apicomplexa_odb12/full_table.tsv
- Protein FASTA files under results/proteins/*_headers.faa

Output:
- results/proteins/busco/orthologs_8species/*.faa
- results/proteins/busco/orthologs_7species_no_tg/*.faa

Usage:
python busco.py or
python3 busco.py

'''

#%%

import os
import sys
from pathlib import Path


def get_arguments():
    # main folder containing one BUSCO result folder per species
    busco_root = Path("results/proteins/busco")
    # folder with original fasta files
    protein_root = Path("results/proteins")
    # BUSCO lineage run subfolder name
    run_dir_name = "run_apicomplexa_odb12"

    # output folder for BUSCOs shared by all 8 species
    out_8 = busco_root / "orthologs_8species"
    # output folder for BUSCOs shared by 7 species (without Tg)
    out_7 = busco_root / "orthologs_7species_no_tg"

    return busco_root, protein_root, run_dir_name, out_8, out_7


def read_fasta(fasta_file):
    # dictionary: sequence_id -> protein sequence
    sequences = {}
    # this keeps track of which header we are currently reading
    current_id = ""

    with open(fasta_file, "r") as f_in:
        for line in f_in:
            line = line.strip()

            if not line:
                continue

            if line.startswith(">"):
                # keep only first part after '>' as sequence id
                current_id = line[1:].split()[0]
                # add this id in the dictionary
                sequences[current_id] = ""
            else:
                # if a sequence line appears before a header, ignore it
                if current_id == "":
                    continue
                # add the sequence line to the current id
                sequences[current_id] += line

    return sequences


def parse_full_table(full_table_file):
    # dictionary: busco_id -> chosen sequence id
    chosen_hits = {}
    # dictionary: busco_id -> best score seen so far
    best_score = {}

    with open(full_table_file, "r") as f_in:
        for line in f_in:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            cols = line.split("\t")
            # we need at least 4 columns (id, status, seq, score)
            if len(cols) < 4:
                continue

            busco_id = cols[0]
            status = cols[1]
            seq_id = cols[2]

            # only keep Complete and Duplicated, ignore the rest
            if status not in ["Complete", "Duplicated"]:
                continue

            # score should be numeric; skip row if not numeric
            if cols[3].replace(".", "", 1).isdigit():
                score = float(cols[3])
            else:
                continue

            # keep the highest scoring sequence for each BUSCO id
            if busco_id not in best_score or score > best_score[busco_id]:
                best_score[busco_id] = score
                chosen_hits[busco_id] = seq_id

    return chosen_hits


def load_all_species(busco_root, protein_root, run_dir_name):
    # dictionary: species_code -> {busco_id: seq_id}
    species_hits = {}
    # dictionary: species_code -> {seq_id: protein_sequence}
    species_proteins = {}

    # find all BUSCO result folders
    busco_folders = sorted(busco_root.glob("*_busco"))

    for folder in busco_folders:
        # location of BUSCO table
        full_table = folder / run_dir_name / "full_table.tsv"
        # skip folder if BUSCO table is missing
        if not full_table.exists():
            continue

        # remove "_busco" from folder name
        folder_name = folder.name.replace("_busco", "")

        # give species code used in output headers
        if folder_name.startswith("Ht"):
            species = "Ht"
        else:
            species = folder_name.split("_")[0]

        # parse BUSCO hits for this species
        species_hits[species] = parse_full_table(full_table)

        # find corresponding fasta file
        fasta_file = protein_root / f"{folder_name}.faa"
        if not fasta_file.exists():
            raise FileNotFoundError(f"Missing FASTA file: {fasta_file}")

        # load sequences from fasta
        species_proteins[species] = read_fasta(fasta_file)

    return species_hits, species_proteins


def find_shared_buscos(species_hits, species_list):
    # dictionary to count in how many species each BUSCO id appears
    busco_counts = {}

    # count BUSCO ids species by species
    for sp in species_list:
        # for each BUSCO id in this species, add 1 to the count
        for busco_id in species_hits[sp].keys():
            if busco_id not in busco_counts:
                busco_counts[busco_id] = 0
            busco_counts[busco_id] += 1

    # keep only BUSCO ids that appear in all species
    shared = []
    # a BUSCO id is shared if its count equals the number of species in the list
    for busco_id, count in busco_counts.items():
        if count == len(species_list):
            shared.append(busco_id)

    return shared


def write_output_files(output_dir, busco_set, species_list, species_hits, species_proteins):

    os.makedirs(output_dir, exist_ok=True)

    # one output fasta file per BUSCO id
    for busco_id in sorted(busco_set):
        # output file name is the BUSCO id with .faa 
        output_file = output_dir / f"{busco_id}.faa"

        # write one sequence per species in each file
        with open(output_file, "w") as f_out:
            # for each species, get the sequence id for this BUSCO and then get the sequence from the fasta dictionary
            for sp in species_list:
                seq_id = species_hits[sp][busco_id]
                sequence = species_proteins[sp].get(seq_id)

                # stop if sequence id from BUSCO table is not found in fasta
                if sequence is None:
                    raise ValueError(f"Sequence '{seq_id}' for species '{sp}' was not found.")

                # species code as fasta header
                f_out.write(f">{sp}\n")
                f_out.write(f"{sequence}\n")


def print_summary(species_hits, species_all, shared_8, shared_7):

    print("Species used:", ", ".join(species_all))
    print("Shared BUSCOs in all 8 species:", len(shared_8))
    print("Shared BUSCOs in 7 species (without Tg):", len(shared_7))
    print("\nComplete + Duplicated BUSCOs per species:")

    # print per-species BUSCO counts
    for sp in species_all:
        print(sp, len(species_hits[sp])) # number of BUSCO ids with Complete or Duplicated hits for this species


def main():
    try:
        # get script and paths
        busco_root, protein_root, run_dir_name, out_8, out_7 = get_arguments()

        # load BUSCO hits and protein sequences for all species
        species_hits, species_proteins = load_all_species(busco_root, protein_root, run_dir_name)

        # final species list found in BUSCO folders
        species_all = sorted(species_hits.keys())
        if len(species_all) == 0: # if no species were found, stop with error
            raise RuntimeError("No BUSCO runs were found.")

        # find BUSCO ids shared by all species
        shared_8 = find_shared_buscos(species_hits, species_all)

        # remove Tg to create 7-species comparison
        species_7 = []
        for sp in species_all:
            if sp != "Tg":
                species_7.append(sp)
        if len(species_7) == 0:
            raise RuntimeError("Tg filtering removed all species.")

        # find BUSCO ids shared by the 7-species set
        shared_7 = find_shared_buscos(species_hits, species_7)

        # write one fasta per shared BUSCO for both datasets
        write_output_files(out_8, shared_8, species_all, species_hits, species_proteins)
        write_output_files(out_7, shared_7, species_7, species_hits, species_proteins)

        # print summary to terminal
        print_summary(species_hits, species_all, shared_8, shared_7)

    except Exception as e:
        # print error and stop 
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()