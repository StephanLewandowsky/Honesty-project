#NewsGuard Scraping


# Scrape ---------------------------------------------------------------

#load libraries

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, data.table, reticulate)


#load urls
df <- fread('tweets_with_urls.csv')

#clean urls
df_cleaned <- df %>% 
  filter(Domain != "",
         Domain != 'youtube.com') %>% 
  filter(str_detect(url, ".com/|.gov/")) %>% 
  mutate(link_text = NA) %>% #preallocate text column
  select(url, Score, link_text) %>% 
  distinct()


#loop newspaper3k: extract main text of articles
for (i in 1:nrow(df_cleaned)){
  
  url <- df_cleaned$url[i]
  
  tryCatch({
    #python bit
    reticulate::py_run_file("article_script.py")
    
    #back to r
    df_cleaned$link_text[i] <- py$article_text
  }, error=function(e){})
  
}

#write data file
write_rds(df_cleaned,"scraped_corpus_raw.rds", "gz")
