library(stringr)
library(dplyr)
library(httr)
library(tidyr)
library(tibble)

# Class A GPCR family
family_id <- '001'

# List of segment names
segments = c('N-term','TM1','ICL1','TM2','ECL1','TM3','ICL2','TM4','ECL2','TM5','ICL3','TM6','ECL3','TM7','C-term')

# Request alignment of Class A GPCRs from GPCRdb for each of these sections

requests <- paste('http://gpcrdb.org/services/alignment/family/',family_id,'/',segments,sep = '')
responses <- lapply(requests, GET)
aligned.segments <- lapply(responses, function (x) unlist(content(x,as='parsed')))

# Shape responses into dataframe

alignment.df <- data.frame(do.call(cbind, aligned.segments),stringsAsFactors = F)
colnames(alignment.df) <- segments


# pivot to long  

alignment.df <- alignment.df %>%
  rownames_to_column('name') %>% 
  filter(name != 'false' & name != 'CONSENSUS') %>% 
  pivot_longer(-name, names_to = 'segment',values_to = 'segment_sequence') 

# split into residues

residues <- alignment.df %>% 
  mutate(residue=strsplit(segment_sequence,split = '')) %>% 
  select(-segment_sequence) %>% 
  unnest(cols=residue)

# Number by alignment position & position in sequence

residues <- residues %>% 
  group_by(name) %>% 
  mutate(n_alignment = row_number()) %>%
  filter(residue != '-') %>%
  mutate(n_sequence = row_number())

# Write to file
write.csv(residues,'data/align_residues.csv',row.names = F)


