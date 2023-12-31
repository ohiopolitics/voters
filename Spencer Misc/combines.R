library(arrow)
library(tidyverse)
setwd("C:/Users/spenc/OneDrive/Documents/GitHub/voters/Spencer Misc")
results <- read_parquet("C:/Users/spenc/Downloads/OH_VT_Predictions.parquet")
dem <- read_parquet("C:/Users/spenc/Downloads/D_probs_df.parquet")
rep <- read_parquet("C:/Users/spenc/Downloads/R_probs_df.parquet")
og <- read_parquet('../../SWVF_full.parquet')
counties <- read_csv('County Codes.csv') %>%
  mutate(County = str_replace(County,' County',''))
#View(results)
#hist(results$VT_prediction)
final <- og %>%
  mutate(Age = 2023-year(as_datetime(date_of_birth))) %>%
  select(sos_voter_id,county_number,last_name,first_name,street_address,Age) %>%
  left_join(results,by='sos_voter_id') %>%
  left_join(dem,by='sos_voter_id') %>%
  left_join(rep,by='sos_voter_id') %>%
  left_join(counties, by=join_by(county_number==Code)) %>%
  select(-c(county_number))

for (county in unique(final$County)) {
  write_csv(filter(final,County==county),paste0(county,".csv"))
  Sys.sleep(.5)
}

