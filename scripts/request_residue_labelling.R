
library(httr)
library(jsonlite)
library(data.table)
library(dplyr)

proteins <- fread('data/gpcrs.csv',data.table=F,header=T)

# Loop through proteins; get GPCRdb residue labelling and write to file
for (name in proteins$entry_name) {
  request <- paste('http://gpcrdb.org/services/residues/',name,sep = '')
  response <- content(GET(request), as='parsed')
  label.df <- data.frame(do.call(rbind,lapply(response,as.character)),stringsAsFactors = F)
  colnames(label.df) <- c('sequence_no','residue','segment','generic_label')
  label.df$target = name
  write.csv(label.df,file = paste('residue_labels/',name,'.csv',sep=''),row.names = F)
}

