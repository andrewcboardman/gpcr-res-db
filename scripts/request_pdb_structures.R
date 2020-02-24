
# Get PDB structures

library(httr)
library(data.table)

structures <- fread('structures.csv',data.table=F)

get_pdb <- function(code) {
  path <- paste("pdb_structures/",code,".pdb.gz",sep="")
  download.file(
    url = paste("http://files.rcsb.org/download/", code, ".pdb.gz",sep=""),
    destfile = path
  )
  system(paste("gunzip", path))
  path
}

pdb_structures <- data.frame()
paths <- sapply(structures$pdb_code, get_pdb)
structures$path <- paths
fwrite(structures,'data/pdb_structures.csv')



