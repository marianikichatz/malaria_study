#!/usr/bin/env python3

#Documentation Section

"""
Script name: cleanFastaNObirds.py

Version: 1.00
Date: 2026-03-02
Name: Maria Niki Chatzantoni

Description: This script will clean the fasta files from the Blast query, by removing all sequences that belong to bird species. 
This is done by removing the contigs that have an AC number that is associated with a bird species in the uniprot_sprot.dat file. 
The contigs that are associated with birds were identified in the datParser.py script, by parsing the taxonomy.dat file and 
retrieving the scientific names of all bird species. 
As a result, the fasta files that are used for the downstream analyses will only contain sequences that do not belong to bird species, 
which is important for the accuracy of the results. 

User-defined functions: get_arguments(), read_bird_scaffolds(), clean_fasta(), write_output(), main()
Non-standard modules: None

Procedure:
    1. Read command-line arguments for input and output files
    2. Read the scaffold names associated with birds from the second input file
    3. Clean the fasta file by removing sequences that belong to bird species
    4. Write the cleaned sequences to the output file

Input: Fasta file (either .fna or .faa) and scaffold names that are associated with birds (identified in datParser.py)
Output: cleaned.fasta [default name, can be changed by user]

Usage: python cleanFastaNObirds.py H.tartakovskyi_genes.fna scaffolds_blastx.txt output_file.fasta [optional] or 
python cleanFastaNObirds.py H.tartakovskyi_genes.faa scaffolds_blastp.txt output_file.fasta or 
python3 cleanFastaNObirds.py H.tartakovskyi_genes.fna scaffolds_blastx.txt output_file.fasta or 
python3 cleanFastaNObirds.py H.tartakovskyi_genes.faa scaffolds_blastp.txt output_file.fasta

"""

#%%

import sys
import os
import re

# function for getting the command-line arguments and checking if they are in the correct format
def get_arguments():
    
    pattern = r".*\.(fna|faa)$" # regex that checks if file ends with right extension
    python_script_name = None
    input_file1 = None
    input_file2 = None
    output_file = None

    # check if the input file is in correct format
    if len(sys.argv) < 3:
         raise ValueError("Wrong number of arguments!")
    
    if re.match(pattern, sys.argv[1]):
        pass
    else: 
        raise ValueError("The input file name is invalid. Please give a correct FASTA file. Thank you!")
    
    # the output file is optional, so we have to handle 2 different cases
    # case 1: user only gives input file (2 arguments total)
    # case 2: user gives input AND output file (3 arguments total)
    if len(sys.argv)==3:                       
                                              
        python_script_name = sys.argv[0]       # this is the script name
        input_file1 = sys.argv[1]              # this is what the user wants to read
        input_file2 = sys.argv[2]              # this is the file with bird scaffolds
        output_file = "cleaned.fasta"          # we use this default name if they don't give us one

        # check if file already exists so we don't accidentally delete someone's work
        if os.path.exists(output_file):        
            # ask the user if they want to replace the existing file
            response = input("Hey, the output file already exists. Do you want to overwrite it? (Y/N): ").strip().upper()
            if response != "Y":
                print("Operation cancelled by user.")
                sys.exit(0)  # stop the program
            else:
                print("Overwriting existing file...")
        
        print("Python script name:", python_script_name)
        print("Input file names:", input_file1, input_file2)

        print("Output file name:", output_file) 

# if the user gives 3 arguments (script name, input file, output file)   
    elif len(sys.argv)==4:  
        
        python_script_name = sys.argv[0]       # this is the script name
        input_file1 = sys.argv[1]              # this is what the user wants to read
        input_file2 = sys.argv[2]              # this is the file with bird scaffolds
        output_file = sys.argv[3]              # this is where we write the results
        
        # we check if a file with the same name already exists
        if os.path.exists(output_file):        
            response = input("Hey, the output file already exists. Do you want to overwrite it? (Y/N): ").strip().upper()
            if response != "Y":
                print("Operation cancelled by user.")
                sys.exit(0)
            else:
                print("Overwriting existing file...")
        print("Python script name:", python_script_name)
        print("Input file names:", input_file1, input_file2)
        print("Output file name:", output_file) 
    
    # if user gives wrong number of arguments, we stop and tell them
    else:                                      
        raise ValueError("Wrong number of arguments!")
        
    return python_script_name, input_file1, input_file2, output_file

# function for reading the scaffold names that are associated with birds, which we want to remove from the fasta file
def read_bird_scaffolds(input_file2):
    bird_scaffolds = []

    with open(input_file2, "r") as f_in:
        for line in f_in:
            scaffold = line.strip()
            bird_scaffolds.append(scaffold)

    return bird_scaffolds


# function for cleaning the fasta file by removing the sequences that belong to bird species
def clean_fasta(input_file1, bird_scaffolds):
    cleaned_sequences = {}  # store the cleaned sequences here

    with open(input_file1, "r") as f_in:
        for line in f_in:
            line = line.strip()            # remove extra spaces at the beginning and end
            if not line:                   # if the line is empty, skip it
                continue

            if line.startswith(">"):     # if the line is a header line
                current_header = line
                scaffold = current_header.split('\t')[2].split("=", 1)[1]

                # read the next line as the sequence line
                seq_line = next(f_in, "").strip()

                # keep only non-bird scaffolds
                if scaffold not in bird_scaffolds:
                    cleaned_sequences[current_header] = seq_line  

    return cleaned_sequences

# function for writing the cleaned sequences to the output file
def write_output(cleaned_sequences, output_file):
    with open(output_file, "w") as f_out:
        for header, sequence in cleaned_sequences.items():
            f_out.write(header + "\n")  # write the header
            f_out.write(sequence + "\n")  # write the sequence

# main function 
def main():
    try:  # we try to run the program
        # first get the arguments from the command line
        python_script_name, input_file1, input_file2, output_file = get_arguments()

        # read the bird scaffold names from the second input file
        bird_scaffolds = read_bird_scaffolds(input_file2)
    
        # remove the sequences that belong to bird species from the fasta file 
        cleaned_seq = clean_fasta(input_file1, bird_scaffolds)

        # write the cleaned sequences to the output file
        write_output(cleaned_seq, output_file)

    except Exception as e:  # if anything goes wrong, catch the error
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()



