library(Biostrings)

# read command line arguments
args = commandArgs(trailingOnly=TRUE)

input <-  readAAStringSet(args[1],format = 'fasta')
name <- substr(args[1],1,nchar(args[1])-10)

for (i in 1:length(input)) {
  sequence <- input[i]
  output <- paste(name, names(sequence),'.fa',sep='_')
  writeXStringSet(sequence,output)
}