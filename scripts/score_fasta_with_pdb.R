library(Biostrings,warn.conflicts = F,quietly = T)
library(bio3d, quietly = T)
library(dplyr,quietly = T)

# read command line arguments
# 1 = sequence (FASTA format)
# 2 = structure (PDB format)
# 3 = scores linked to residues of the structure file
# 4 = output file
args = commandArgs(trailingOnly=TRUE)

# read sequence from PDB format and write to temporary FASTA file
struct <- read.pdb(args[2])
struct_seq <- AAStringSet(paste(pdbseq(struct,inds = atom.select(struct,chain = chain,string = 'calpha')),collapse=''))
writeXStringSet(struct_seq,'tmp.fasta')

# append wild-type sequence to temporary file
system(paste('cat',args[1],'>> tmp.fasta'))

# align wild-type and structure sequences using clustalo 
system('clustalo -i tmp.fasta -o tmp_aln.fasta')

# Read alignment back from file
aln <- readAAStringSet('tmp_aln.fasta')

# Split into characters and add to data frame
aln.df <- data.frame(seq = strsplit(as.character(aln[2]),split="*")[[1]],
           struct_seq = strsplit(as.character(aln[1]),split="*")[[1]],
           stringsAsFactors = F)

# Index position in sequence
aln.df_numbered <- aln.df %>% 
  mutate(struct_no = cumsum(struct_seq != '-'),
         seq_no = cumsum(seq != '-')) %>% 
  filter(struct_seq != '-'  | seq != '-')

# read PDB residue-linked scores 
struct_scores <- read.csv(args[3])

# Link sequence to scores
out.df <- aln.df_numbered %>% 
  left_join(struct_scores, by = 'struct_no')

# Output csv
write.csv(out.df, args[4])

# Clean up environment
system('rm tmp.fasta; rm tmp_aln.fasta')

