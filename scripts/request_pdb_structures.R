
# Get PDB structures

library(httr)
library(data.table)

structures <- fread('structures.csv',data.table=F)

get_pdb <- function(code) {
  download.file(
    url = paste("http://files.rcsb.org/download/", code, ".pdb.gz",sep=""),
    destfile = paste("pdb_structures/",code,".pdb.gz",sep="")
  )
 system(paste("gunzip pdb_structures/",code,".pdb.gz",sep=""))
}

lapply(structures$pdb_code, get_pdb)



