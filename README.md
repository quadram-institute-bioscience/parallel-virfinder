# parallel-virfinder

[![Test-Package](https://github.com/quadram-institute-bioscience/parallel-virfinder/actions/workflows/test.yml/badge.svg)](https://github.com/quadram-institute-bioscience/parallel-virfinder/actions/workflows/test.yml)
Run virfinder in parallel

## Usage

```bash
parallel-virfinder.py -i input.fasta -o output.csv -t THREADS [-f output.fasta]
```

## Options

```text
usage: parallel-virfinder.py [-h] -i INPUT -o OUTPUT [-f FASTA] [-n PARALLEL] [-t TMPDIR] [-s MIN_SCORE] [-p MAX_P_VALUE] [-v] [-d]

Execute virfinder on a FASTA file in parallel

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input FASTA file
  -o OUTPUT, --output OUTPUT
                        Output CSV file
  -f FASTA, --fasta FASTA
                        Save FASTA file
  -n PARALLEL, --parallel PARALLEL
                        Number of parallel processes [default: 4]
  -t TMPDIR, --tmpdir TMPDIR
                        Temporary directory [default: /tmp]

VirFinder arguments:
  -s MIN_SCORE, --min-score MIN_SCORE
                        Minimum score [default: 0.9]
  -p MAX_P_VALUE, --max-p-value MAX_P_VALUE
                        Maximum p-value [default: 0.05]

Miscallaneous arguments:
  -v, --verbose         Verbose output
  -d, --debug           Debug output

```
