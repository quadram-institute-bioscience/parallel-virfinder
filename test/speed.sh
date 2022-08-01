
#!/bin/bash

set -exuo pipefail

for CORES in 2 4 8;
do
hyperfine --max-runs 6 \
 "bin/parallel-virfinder.py -i test/tmp/input.fa -o test/tmp/py.csv -f test/tmp/py.fa -n $CORES" \
 "share/pvirfinder.R test/tmp/input.fa $CORES test/tmp/" \
 --export-markdown test/bench/bench-$CORES-cores.md \
 --export-csv      test/bench/bench-$CORES-cores.csv
done
