#!/bin/bash

Rscript --version  > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
  echo "OK: Rscript found"
else
  echo "FAIL: Missing R"
  exit
fi

Rscript --vanilla --no-save -e "library('VirFinder');"  > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
  echo "OK: VirFinder found"
else
  echo "FAIL: Missing VirFinder"
  exit
fi

bin/parallel-virfinder.py -i test/phage-contigs.fna -o test/phages.csv --verbose -f test/phages.fa -p 0.1 -s 0.5 
if [[ $? -eq 0 ]]; then
  echo "OK: VirFinder executed"
else
  echo "FAIL: Failed VirFinder"
  exit
fi

SEQ=$(grep -c ">" test/phages.fa)
if [[ $SEQ -eq 3 ]]; then
  echo "OK: 3 seqs found"
else
  echo "FAIL: $SEQ seq found, expecting 3"
fi

CSV=$(cat test/phages.csv | wc -l)
if [[ $CSV -eq 4 ]]; then
  echo "OK: 3 seqs found in CSV"
else
  echo "FAIL: $CSV CSV lines found, expecting 4"
fi
