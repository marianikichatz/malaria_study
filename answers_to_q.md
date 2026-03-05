## Answers to questions

1. **Do you think that in a phylogenetic tree the parasites that use 
similar hosts will group together?**

Not always. In a phylogenetic tree, parasites usually group by how genetically related they are
not only by what host they infect. So parasites with similar hosts can group together
but they can also be in different branches if host switching happened.

2. **With the new genome file, make a gene prediction. You will probably still have
some scaﬀolds that derive from the bird. These should be short. Why?***

They can still remain because GC filtering is not perfect.
Some host scaffolds have GC content similar to the parasite
so they pass the filter. The remaining contaminanted scaffolds 
are usually short fragments from mixed assembly.

3. **Insert the missing data in the above table. Use bash, not inter-
net!**

Commands used: 
for the genome size 
```bash
grep -v "^>" data/Plasmodium_berghei.genome | tr -d "\n"| wc -m [this was used for all the species]
```

for the number of genes 
``` bash
cut -f3  data/vivax.gtf | grep -c "gene" #this was used for all the species expect from the Toxoplasma for which we used this command: 
cut -f9 data/Tg.gff |sort | uniq | wc -l]
```

for the GC content
``` bash 
GC=$(grep -v "^>"  data/Plasmodium_cynomolgi.genome| grep -o "[GC]" | wc -l)
TOTAL=$(grep -v "^>" data/Plasmodium_cynomolgi.genome| tr -d "\n"| wc -m)
echo "scale=4; $GC * 100 / $TOTAL" | bc
#this was used for all the species
```
The final table is as follows:
![table with the genome size, number of genes and GC content for the 8 species](table.png)
                    
