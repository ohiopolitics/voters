library(arrow)
library(tidyverse)
results <- read_parquet("C:/Users/spenc/Downloads/OH_VT_Predictions.parquet")
og <- read_parquet('../../SWVF_full.parquet')
counties <- read_csv('County Codes.csv')
View(results)
hist(results$VT_prediction)
final <- og %>%
  select("sos_voter_id","county_number","last_name","first_name",
         "street_address") %>%
  left_join(results,by='sos_voter_id') %>%
  left_join(counties, by=join_by(county_number==Code)) %>%
  write_csv("Most of the User Database.csv")
final