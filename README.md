# parallel-virfinder

[![Test-Package](https://github.com/quadram-institute-bioscience/parallel-virfinder/actions/workflows/test.yml/badge.svg)](https://github.com/quadram-institute-bioscience/parallel-virfinder/actions/workflows/test.yml)
![License](https://img.shields.io/github/license/quadram-institute-bioscience/parallel-virfinder)
[![Bioconda downloads](https://img.shields.io/conda/dn/bioconda/parallel-virfinder)](https://bioconda.github.io/recipes/parallel-virfinder/README.html)
![Bioconda platforms](https://img.shields.io/conda/pn/bioconda/parallel-virfinder)

Run virfinder in parallel, saving both scores and FASTA file

## Installation

Via conda:

```bash
conda install -c bioconda -c conda-forge parallel-virfinder
```

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

### Benchmark

If [compared with a parallel implementation in R](share/pvirfinder.R), this wrapper performs better (smaller times, smaller memroy usage). See **[benchmark](test/bench/README.md)**.

### Citations

If you use parallel-virfinder, please cite the following paper:

* Ren, J., Ahlgren, N. A., Lu, Y. Y., Fuhrman, J. A., & Sun, F. (2017). VirFinder: a novel k-mer based tool for identifying viral sequences from assembled metagenomic data. [Microbiome, 5(1), 1-20](https://link.springer.com/epdf/10.1186/s40168-017-0283-5?author_access_token=YQgkTWibFIFPtRICkTjZF2_BpE1tBhCbnbw3BuzI2RMCpVMGldKV8DA9scozc7Z-db3ufPFz9-pswHsYVHyEsCrziBuECllLPOgZ6ANHsMeKF5KejrdDKdeASyDkxB5wfFDq523QSd01cnqxCLqCiQ%3D%3D).

* Telatin, A., Fariselli, P., & Birolo, G. (2021). Seqfu: a suite of utilities for the robust and reproducible manipulation of sequence files. [Bioengineering, 8(5), 59](https://doi.org/10.3390/bioengineering8050059).


### License

[VirFinder](https://github.com/jessieren/VirFinder) (see [license](https://github.com/jessieren/VirFinder/blob/master/licence.md))
is free to use for academic or non commercial use only.
[SeqFu](https://telatin.github.io/seqfu2/) and this wrapper are free to use.
