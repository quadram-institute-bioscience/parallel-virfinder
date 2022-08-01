#!/usr/bin/env Rscript

###############################################################################


###############################################################################
# Take the input passed by Nextflow, which are
# ${scaffold}
# ${task.cpus}
# $workflow.projectDir
args <- commandArgs(trailingOnly = TRUE) 

# check at least three args
if (length(args) < 3) {
  stop("Need at least three arguments: Contigs, Cores, projectDir")
}
fileinFASTA <- args[1] 
taskcpus <- args[2]
workdir <- args[3]
# MaxPvalue = args[4] or 0.05 if not specified
MaxPvalue <- 0.05
if (length(args) >= 4) {
  MaxPvalue <- args[4]
}

cat("Input: ", fileinFASTA, "\n", sep = "")
cat("Cores: ", taskcpus, "\n", sep = "")
cat("ProjectDir: ", workdir, "\n", sep = "")

# Check taskcpus is an integer
if (!is.integer(as.integer(taskcpus))) {
  stop("Cores must be an integer: ", taskcpus)
}

cat(" * Loading library Virfinder\n")
suppressPackageStartupMessages(library(VirFinder))
cat(" * Loading library Biostrings\n")
suppressPackageStartupMessages(library(Biostrings)) #bioconductor-biostrings
cat(" * Loading library parallel\n")
suppressPackageStartupMessages(library(parallel))
cat(" * Loading library seqinr\n")
suppressPackageStartupMessages(library(seqinr)) #r-seqinr
cat(" ** Libraries loaded\n")

# Check if workdir exists, if not create it
if (!dir.exists(workdir)) {
  cat("Creating directory: ", workdir, "\n", sep = "")
  mkdir(workdir)
}
outFasta = paste(workdir, "virfinder.fasta", sep = "/")
outText = paste(workdir, "virfinder.txt", sep = "/")

# Check if the parVF_pred script is in the bin folder
getScriptPath <- function(){
    cmd.args <- commandArgs()
    m <- regexpr("(?<=^--file=).+", cmd.args, perl=TRUE)
    script.dir <- dirname(regmatches(cmd.args, m))
    if(length(script.dir) == 0) stop("can't determine script dir: please call the script with Rscript")
    if(length(script.dir) > 1) stop("can't determine script dir: more than one '--file' argument detected")
    return(script.dir)
}

scriptPath = getScriptPath()
libFileName = "parvf-functions.R"
joinedPaths = paste(scriptPath, libFileName, sep = "/")

if (!file.exists(joinedPaths)) {
  stop("The parVF_pred script is not in the bin folder:", libFile)
}
if(!exists("parVF_pred", mode="function")) source(file.path(joinedPaths))

# In predResult, store parVF_pred results, runned with ${scaffold} and ${task.cpus} values from NF

cat("***    [1] Start prediction\n", sep = "")
predResult <- parVF.pred(fileinFASTA, taskcpus)

# Subset the result for pvalues < 0.005
subsetted <- subset(predResult, pvalue < MaxPvalue)
options(width=10000) 

# Order the result by increasing pvalues (smaller first)
predResult <- predResult[order(predResult$pvalue),]

# Order the subset by increasing pvalues (smaller first)
subsetted <- subsetted[order(subsetted$pvalue),]

# Fix rownames of predResult to not repeat
rownames(predResult) <- 1:nrow(predResult)

# Store the predResult output in results.txt file 
sink(outText)
print(predResult)
sink()

# Create a df of the subset output
dfFASTA <- data.frame(subsetted)
# Fix name problem creating empy fasta files
dfFASTA$name <- sub(" .*", "", dfFASTA$name)

seqFASTA <- read.fasta(file = fileinFASTA, forceDNAtolower = FALSE, 
                       seqtype = "DNA", as.string = TRUE, set.attributes = FALSE)

sub <- seqFASTA[names(seqFASTA) %in% dfFASTA$name]
names(sub) = sub("^", "virfinder_", names(sub))


write.fasta(sequences = sub, names = names(sub), as.string=TRUE,
            nbchar = 60, file.out = outFasta)