#!/usr/bin/env python3

#Documentation Section

"""
Script name: concat.py

Version: 1.00
Date: 2026-03-06
Name: Maria Niki Chatzantoni

Description:
This script concatenates BUSCO alignment files into one final FASTA file.
The final FASTA has one long sequence per species.

User-defined functions: get_arguments(), read_fasta(), concatenate_alignments(), write_output(), main()
Non-standard modules: None

Procedure:
    1. Read command line arguments 
    2. Pick alignment folder and species list based on mode
    3. Read each alignment file
    4. Concatenate sequence parts per species
    5. Write one output FASTA file

Input:
- Alignment files in:
  results/proteins/busco/alignments_7species OR
  results/proteins/busco/alignments_8species

Output:
- results/proteins/busco/concat/all7species.faa OR
- results/proteins/busco/concat/all8species.faa

Usage:
python concat.py 7 [output_file_name]
python concat.py 8 [output_file_name]
OR
python3 concat.py 7 [output_file_name]
python3 concat.py 8 [output_file_name]
"""

#%%

import os
import sys

# function to get command line arguments and check them
def get_arguments():
    if len(sys.argv) < 2 or len(sys.argv) > 3: # check if mode and optional output file name are given
        raise ValueError("Please give mode (7 or 8) and optionally output file name") # error if wrong mode or wrong number of arguments

    mode = sys.argv[1] 

    # set path for the output directory
    output_dir = "results/proteins/busco/concat"

    # based on mode, set the alignment directory, default output file name and species list
    if mode == "7":
        align_dir = "results/proteins/busco/alignments_7species"
        default_output_name = "all7species.faa"
        species = ["Ht", "Pb", "Pc", "Pf", "Pk", "Pv", "Py"]
    elif mode == "8":
        align_dir = "results/proteins/busco/alignments_8species"
        default_output_name = "all8species.faa"
        species = ["Ht", "Pb", "Pc", "Pf", "Pk", "Pv", "Py", "Tg"]
    else: # if mode is not 7 or 8 we raise an error
        raise ValueError("Please choose mode 7 or 8")

    # if user gives output file name we set it to that
    if len(sys.argv) == 3:
        output_name = sys.argv[2]
    else: # if they don't give us an output file name we use the default one
        output_name = default_output_name

    # set the full path for the output file
    output_file = os.path.join(output_dir, output_name)

    # check if the alignment directory exists, if not we raise an error
    if not os.path.isdir(align_dir):
        raise ValueError("Alignment directory not found. Please make sure you have the correct path: " + align_dir)

    # create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # check if the output file exists and ask user if they want to overwrite it
    if os.path.exists(output_file):
        response = input("Hey, the output file already exists. Do you want to overwrite it? (Y/N): ").strip().upper()
        if response != "Y":
            print("The output file was not overwritten. The program will stop.")
            sys.exit(0)

    return mode, align_dir, output_file, species

# function to read FASTA and return a dictionary with species as keys and sequences as values
def read_fasta(file_name):
    parts = {}
    current_id = ""

    with open(file_name, "r") as f_in:
        for line in f_in:
            line = line.strip()

            # skip empty lines
            if not line: 
                continue

            # if header line then we get the species name and add it as the key in the dictionary
            if line.startswith(">"):
                current_id = line[1:].split()[0]
                parts[current_id] = ""
            else: # if sequence line then we add it to the current species id as the value in the dictionary
                if current_id == "":
                    continue
                parts[current_id] += line

    return parts

# function for concatenate the sequences for each species across all alignments 
def concatenate_alignments(align_dir, species):
    concat_seq = {}

    # loop through the species list and add the species as key 
    for specie in species:
        concat_seq[specie] = ""

    files = [] # empty list to store the alignment file names

    # loop through the alignment directory and add the .faa files to the list
    for name in os.listdir(align_dir):
        if name.endswith(".faa"):
            files.append(name)

    files.sort() # sort the file names so they are in the same order as the species list

    # if we don't find any .faa files we raise an error 
    if len(files) == 0:
        raise ValueError("No .faa alignment files found in " + align_dir)

    # loop through the alignment files 
    for file_name in files:
        full_path = os.path.join(align_dir, file_name) # get the full path for the file
        parts = read_fasta(full_path) # read the fasta file and get the sequences for each species 

        # loop through the species list
        for specie in species:
            # check if the species is in allignment file, if not we raise an error
            if specie not in parts:
                raise ValueError("Missing species " + specie + " in file " + file_name)

            # concatenate the sequences for each species across all alignments
            concat_seq[specie] += parts[specie]

    return concat_seq

# function to write the concatenated sequences to the output file 
def write_output(concat_seq, species, output_file):
    with open(output_file, "w") as f_out:

        # loop through the species list and write the header and sequence for each species to the output file
        for specie in species:
            f_out.write(">" + specie + "\n")
            f_out.write(concat_seq[specie] + "\n")

    return output_file

# main function 
def main():
    try:
        # get the command line arguments
        mode, align_dir, out_file, species = get_arguments()

        # concatenate the sequences for each species across all alignments 
        concat_seq = concatenate_alignments(align_dir, species)
        
        # write the concatenated sequences to the output file
        write_output(concat_seq, species, out_file)

    except Exception as e: # if anything goes wrong, catch the error
        print("An error occurred:", e)


if __name__ == "__main__":
    main()
