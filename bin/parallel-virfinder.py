#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import subprocess
import logging
import tempfile

# parse csv
import csv
def parse_csv(filename):
    """
    Parse CSV file
    """

    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row[0]) > 0:
                yield row

def read_fasta(path):
    if path.endswith('.gz'):
        import gzip
    name = None
    with (gzip.open if path.endswith('.gz') else open)(path, 'rt') as fasta:
        for line in fasta:
            if line.startswith('>'):
                if name is not None:
                    yield name, seq
                name = line[1:].rstrip()
                seq = ''
            else:
                seq += line.rstrip()
    yield name, seq
 

def has_r():
    """
    Check if R is installed
    """
    try:
        subprocess.call(['Rscript', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def has_virfinder():
    """
    Check if virfinder is installed
    """
    try:
        cmd = ["Rscript", "--vanilla", "--no-save", "-e", "library('VirFinder');"]
        subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def split_fasta(inputfasta, outputdir, n):
    """
    Split fasta file into n files
    """
    outpattern = os.path.join(outputdir, "split_00000.fasta")
    cmd = ["fu-split", "-i", inputfasta, "-o", outpattern, "-n", str(n), "--threads", str(n)]
    job = subprocess.call(cmd)
    return job == 0

def run_virfinder(fasta, output):
    cmdstring = "library('VirFinder'); Result <- VF.pred('{}'); write.csv(Result, file='{}', row.names=TRUE);".format(fasta, output)
    cmd = ["Rscript", "--vanilla", "--no-save", "-e", cmdstring]
    # Execute job in background
    job = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return job.pid, output

if __name__ == "__main__":
    args = argparse.ArgumentParser(description="Execute virfinder on a FASTA file in parallel")
    args.add_argument("-i", "--input",    help="Input FASTA file", required=True)
    args.add_argument("-o", "--output",   help="Output CSV file", required=True)
    args.add_argument("-f", "--fasta",   help="Save FASTA file", required=False)
    
    args.add_argument("-n", "--parallel", help="Number of parallel processes [default: %(default)s]", default=4, type=int)
    args.add_argument("-t", "--tmpdir",   help="Temporary directory [default: %(default)s]", default=tempfile.gettempdir())

    # Virfinder specific
    vf = args.add_argument_group("VirFinder arguments")
    vf.add_argument("-s", "--min-score", help="Minimum score [default: %(default)s]", default=0.9, type=float)
    vf.add_argument("-p", "--max-p-value",   help="Maximum p-value [default: %(default)s]", default=0.05, type=float)
    # Miscallaneous arguments group
    misc_group = args.add_argument_group("Miscallaneous arguments")
    misc_group.add_argument("-v", "--verbose",  help="Verbose output", action="store_true")
    misc_group.add_argument("-d", "--debug",    help="Debug output", action="store_true")
    args = args.parse_args()

    if args.debug:
        DELETE=False
        logLevel = logging.DEBUG
    if args.verbose:
        DELETE=False
        logLevel = logging.INFO
    else:
        DELETE=True
        logLevel = logging.WARN

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logLevel)
    
    if not has_r():
        logging.error("R is not installed")
        sys.exit(1)
    
    if not has_virfinder():
        logging.error("VirFinder is not installed")
        sys.exit(1)

  
    # Split FASTA into chunks
    if split_fasta(args.input, args.tmpdir, args.parallel):
        logging.info("FASTA split into %d chunks", args.parallel)
    else:
        logging.error("Failed to split FASTA file")
        sys.exit(1)

    # Run virfinder on each chunk
    jobOutput = {}
    for i in range(args.parallel):
        N = i + 1
        chunk = os.path.join(args.tmpdir, "split_%05d.fasta" % N)
        output = os.path.join(args.tmpdir, "split_%05d.csv" % N)
        pid, file = run_virfinder(chunk, output)
        jobOutput[pid] = file
        logging.debug("Started virfinder on chunk %d with PID %d: %s", i, pid, output)
    
    # Wait for all jobs to finish
    for pid, outfile in jobOutput.items():
        os.waitpid(pid, 0)
        logging.info("Virfinder on chunk %d finished: %s", pid, outfile)
    
    # Concatenate all results

    passed = 0
    parsed = 0
    sequences = []

    # open output file
    with open(args.output, "w") as f:
        print('"","name","length","score","pvalue"', file=f)
        for _, outfile in jobOutput.items():
            lines = []
            for i in parse_csv(outfile):
                parsed += 1
                #"","name","length","score","pvalue"
                if float(i[3]) >= args.min_score and float(i[4]) <= args.max_p_value:
                    passed += 1
                    lines.append(i)
                    sequences.append(i[1])
                    print('"{}","{}",{},{},{}'.format(passed, i[1], i[2], i[3], i[4]), file=f)
        
    logging.info("Saved CSV file to: %s", args.output)

    if args.fasta is not None:
        check = 0
        logging.info("Saving FASTA file to: %s" % args.fasta)
        with open(args.fasta, "w") as fa:
            for id, seq in read_fasta(args.input):
                if id in sequences:
                    check += 1
                    print(">", id, "\n", seq, sep="", file=fa)
        
        if check != passed:
            logging.error("Failed to save all sequences, printed %d while %d passed" % ( check, passed) )
            
    logging.info("Passed %d out of %d sequences" % ( passed, parsed))