
library(httr)
library(jsonlite)
library(data.table)
library(dplyr)

proteins <- fread('gpcrs.csv',data.table=F,header=T)

requests <- paste('http://gpcrdb.org/services/residues/',proteins$entry_name,sep = '')
responses <- lapply(requests, function(request) content(GET(request), as='parsed'))


#Modify responses into dataframe

label.dfs <- list()
for (i in 1:length(responses)) {
  label.dfs[[i]] <- data.frame(do.call(rbind,lapply(responses[[i]],as.character)),stringsAsFactors = F)
  colnames(label.dfs[[i]]) <- c('sequence_no','residue','segment','generic_label')
  label.dfs[[i]]$target = targets$name[i]
}
label.df.combined <- bind_rows(label.dfs)


# Write dataframe to CSV


write.csv(label.df.combined,file = 'generic_res_labels.csv')



