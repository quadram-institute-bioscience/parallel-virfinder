#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import subprocess
import logging
import tempfile

__VERSION__="0.3.1"

# parse csv
import csv
def parse_csv(filename):
    """
    Parse CSV file, row generator
    """

    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row[0]) > 0:
                yield row

def read_fasta(path):
    """
    Parse FASTA File (TODO move to cdhit_reader?)
    """
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
    except subprocess.CalledProcessError as e:
        return False
    except Exception as e:
        print("Unexpected error when checking Rscript: %s" % e, file=sys.stderr)
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


def has_seqfu():
    """
    Check if virfinder is installed
    """
    try:
        cmd = ["seqfu", "version"]
        # Get command STDOUT
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        # Check if stdout contains "seqfu 1.14+"
        ver = out.decode("utf-8").strip().split(".")
        if len(ver) == 3 and int(ver[0]) >= 1 and int(ver[1]) >= 14:
            return True
        else:
            print("seqfu version {} is not supported".format(out.decode("utf-8")), file=sys.stderr)
            return False
            
    except subprocess.CalledProcessError:
        return False
def split_fasta(inputfasta, outputdir, n):
    """
    Split fasta file into n files using SeqFu 1.14+
    """
    outpattern = os.path.join(outputdir, "split_00000.fasta")
    cmd = ["fu-split", "-i", inputfasta, "-o", outpattern, "-n", str(n), "--threads", str(n)]
    logging.debug("Running command: %s" % " ".join(cmd))
    job = subprocess.call(cmd)
    return job == 0

def run_virfinder(fasta, output):
    cmdstring = "library('VirFinder'); Result <- VF.pred('{}'); write.csv(Result, file='{}', row.names=TRUE);".format(fasta, output)
    logging.debug("Running command: Rscript --vanilla --no-save -e \"\n\t{}\"".format(cmdstring.replace(";", ";\n\t")))
    cmd = ["Rscript", "--vanilla", "--no-save", "-e", cmdstring]
    # Execute job in background
    job = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return job.pid, output

if __name__ == "__main__":
    args = argparse.ArgumentParser(description="Execute virfinder on a FASTA file in parallel")
    
    # input and output
    args.add_argument("-i", "--input",    help="Input FASTA file", required=True)
    args.add_argument("-o", "--output",   help="Output CSV file", required=True)
    args.add_argument("-f", "--fasta",   help="Save FASTA file", required=False)
    
    # Processing parameters
    args.add_argument("-n", "--parallel", help="Number of parallel processes [default: %(default)s]", default=4, type=int)
    args.add_argument("-t", "--tmpdir",   help="Temporary directory [default: %(default)s]", default=tempfile.gettempdir())

    # Virfinder specific parameters
    vf = args.add_argument_group("VirFinder options")
    vf.add_argument("-s", "--min-score", help="Minimum score [default: %(default)s]", default=0.9, type=float)
    vf.add_argument("-p", "--max-p-value",   help="Maximum p-value [default: %(default)s]", default=0.05, type=float)

    # Miscallaneous arguments group
    misc_group = args.add_argument_group("Running options")
    misc_group.add_argument("--version", action="version", version="%(prog)s {}".format(__VERSION__))
    misc_group.add_argument("--no-check",  help="Do not check dependencies at startup", action="store_true")
    misc_group.add_argument("-v", "--verbose",  help="Verbose output", action="store_true")
    misc_group.add_argument("-d", "--debug",    help="Debug output and do not remove temporary files", action="store_true")

    
    args = args.parse_args()

    if args.debug:
        DELETE=False
        logLevel = logging.DEBUG
    elif args.verbose:
        DELETE=True
        logLevel = logging.INFO
    else:
        DELETE=True
        logLevel = logging.WARN

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logLevel)

    logging.info("Starting parallel-virfinder v{}".format(__VERSION__))

     # Check input file
    if not os.path.exists(args.input) or os.path.getsize(args.input) == 0:
        logging.error("Input file does not exist or is empty: %s" % args.input)
        sys.exit(1)

    if args.parallel < 2:
        logging.error("Number of parallel processes must be at least 2")
        sys.exit(1)
        
    if not args.no_check and not has_r():
        logging.error("R is not installed")
        sys.exit(1)
    elif not args.no_check and not has_virfinder():
        logging.error("VirFinder is not installed")
        sys.exit(1)
    elif not args.no_check and not has_seqfu():
        logging.error("SeqFu is not installed, please install seqfu 1.14+")
        sys.exit(1)
    elif not args.no_check:
        logging.info("R and VirFinder were found")



    # Split FASTA into chunks
    if split_fasta(args.input, args.tmpdir, args.parallel):
        logging.info("FASTA split into %d chunks to %s", args.parallel, args.tmpdir)
    else:
        logging.error("Failed to split FASTA file")
        sys.exit(1)

    # Run virfinder on each chunk
    jobOutput = {}
    for i in range(args.parallel):
        N = i + 1
        chunk = os.path.join(args.tmpdir, "split_%05d.fasta" % N)
        output = os.path.join(args.tmpdir, "split_%05d.csv" % N)
        if os.path.exists(chunk) and not os.path.getsize(chunk) == 0:
            pid, file = run_virfinder(chunk, output)
            jobOutput[pid] = file
            logging.debug("Started virfinder on chunk %d with PID %d: %s -> %s", i, pid, chunk, output)
        else:
            logging.info("Skipping chunk %d: %s", i, chunk)
    
    # Wait for all jobs to finish
    for pid, outfile in jobOutput.items():
        os.waitpid(pid, 0)
        logging.info("Virfinder job #%d finished: %s", pid, outfile)
    
    # Concatenate all results

    passed = 0
    parsed = 0
    sequences = []

    # open output file
    with open(args.output, "w") as f:
        print('"","name","length","score","pvalue"', file=f)
        for _, outfile in jobOutput.items():
            lines = []
            if not os.path.exists(outfile) or os.path.getsize(outfile) == 0:
                logging.info("Skipping empty output file: %s", outfile)
                continue
            logging.debug("Parsing partial output file: %s", outfile)
            for i in parse_csv(outfile):
                parsed += 1
                #"","name","length","score","pvalue"
                if float(i[3]) >= args.min_score and float(i[4]) <= args.max_p_value:
                    passed += 1
                    lines.append(i)
                    sequences.append(i[1])
                    print('"{}","{}",{},{},{}'.format(passed, i[1], i[2], i[3], i[4]), file=f)
                
            if DELETE:
                logging.debug("Deleting temporary file: %s", outfile)
                os.remove(outfile)

        
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

    # Finally, delete temporary FASTA files
    if DELETE:
        for i in range(args.parallel):
            N = i + 1
            chunk = os.path.join(args.tmpdir, "split_%05d.fasta" % N)         
            logging.debug("Deleting temporary FASTA file: %s", chunk)
            os.remove(chunk)

    logging.info("Saved %d predictions (out of %d input sequences)" % ( passed, parsed))

