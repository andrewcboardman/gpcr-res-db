library(bio3d)
library(Biostrings)

# read command line arguments
args = commandArgs(trailingOnly=TRUE)


struct <- read.pdb(args[1])
chains <- unique(struct$atom$chain)
seqs <- AAStringSet()
for (chain in chains) {
  seq <- paste(pdbseq(struct,inds = atom.select(struct,chain = chain,string = 'calpha')),collapse='')
  names(seq) <- chain
  seqs <- append(seqs,AAStringSet(seq,use.names = T))
}
writeXStringSet(seqs,args[2])