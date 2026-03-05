#!/usr/bin/env bash

# This script runs Clustalo and RAxML on BUSCO fasta files.
# We can run either:
#   8 species (with Tg as outgroup)
#   7 species (without Tg, no outgroup -> unrooted tree)

# Usage:
#   bash scripts/align.sh 8
#   bash scripts/align.sh 7


mode="$1" # we get the mode (8 or 7) from the command line argument

# set directories based on the mode
if [ "$mode" = "8" ]; then
    input_dir="results/proteins/busco/orthologs_8species"
    align_dir="results/proteins/busco/alignments_8species"
    tree_dir="results/proteins/busco/raxml_trees_8species"
    use_outgroup="yes"
elif [ "$mode" = "7" ]; then
    input_dir="results/proteins/busco/orthologs_7species_no_tg"
    align_dir="results/proteins/busco/alignments_7species"
    tree_dir="results/proteins/busco/raxml_trees_7species"
    use_outgroup="no"
# if the mode is not 8 or 7, print error message 
else
    echo "Watch out! You need to specify if you want to use 8 or 7 species. Please choose mode 8 or 7" 
    exit 1
fi

# make output directories 
mkdir -p "$align_dir"
mkdir -p "$tree_dir"

# loop through each *.faa file in the input directory
for file in "$input_dir"/*.faa
do
    name=$(basename "$file" .faa) # get the base name of the file without the .faa 
    aligned="$align_dir/${name}_aligned.faa" # set the output file name for the aligned sequences

    echo "Aligning $name"
    # run Clustalo to align the sequences in the file 
    clustalo -i "$file" -o "$aligned" -v --threads=32

    echo "Running RAxML for $name"
    # run RAxML to build the tree from the aligned sequences
    # if we are using 8 species -> Tg is the outgroup 
    if [ "$use_outgroup" = "yes" ]; then
        raxmlHPC -s "$aligned" -n "$name" -m PROTGAMMAAUTO -p 12345 -o Tg -w "$(realpath "$tree_dir")" -T 32
    # If we are using 7 species we do not specify an outgroup and get an unrooted tree
    else
        raxmlHPC -s "$aligned" -n "$name" -m PROTGAMMAAUTO -p 12345 -w "$(realpath "$tree_dir")" -T 32
    fi
done

echo "Done"
