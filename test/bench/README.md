# Benchmark

Comparing the pure-R implementation of the parallelism with the python script with
a simple 140 contigs input files, as described in `test/speed.sh`.


## 2 Cores

| Command | Mean [s] | Min [s] | Max [s] | Relative |
|:---|---:|---:|---:|---:|
| `parallel-virfinder.py -i ./input.fa -o ./py.csv -f ./py.fa -n 2` | 4.682 ± 0.033 | 4.653 | 4.741 | 1.00 |
| `pvirfinder.R ./input.fa 2 ./` | 10.956 ± 0.095 | 10.844 | 11.082 | 2.34 ± 0.03 |



## 4 Cores
| Command | Mean [s] | Min [s] | Max [s] | Relative |
|:---|---:|---:|---:|---:|
| `parallel-virfinder.py -i ./input.fa -o ./py.csv -f ./py.fa -n 4` | 4.022 ± 0.072 | 3.944 | 4.144 | 1.00 |
| `pvirfinder.R ./input.fa 4 ./` | 8.013 ± 0.095 | 7.909 | 8.128 | 1.99 ± 0.04 |



## 8 Cores

| Command | Mean [s] | Min [s] | Max [s] | Relative |
|:---|---:|---:|---:|---:|
| `parallel-virfinder.py -i ./input.fa -o ./py.csv -f ./py.fa -n 8` | 4.911 ± 0.079 | 4.819 | 5.032 | 1.00 |
| `pvirfinder.R ./input.fa 8 ./` | 6.816 ± 0.086 | 6.714 | 6.927 | 1.39 ± 0.03 |
