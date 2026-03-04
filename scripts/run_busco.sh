#!/bin/bash

for file in *headers.faa; do
    base=$(basename "$file" .faa)
    echo "Running BUSCO for $base"
    busco -i "$file" -o "${base}_busco" -m prot -l apicomplexa_odb12 -c 20
done

