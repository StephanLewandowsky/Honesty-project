from pathlib import Path
import json
import pandas as pd
from tqdm import tqdm
#ls *.json|cut -f 1 --delimiter="."|cut -c 1-4|sort -u > years.txt
years = [line.strip() for line in open("years.txt", 'r')]
df = pd.DataFrame()
#loop over years
for year in tqdm(years):
   result = {'id':[], 'created_at':[], 'text':[]}
   #pattern match year to get files
   p = Path('.')
   files = list(p.glob(str(year)+'*'+'.json'))
   #loop over files 
   for file in files:
       with open(file,'r') as inp_f:
           data = json.load(inp_f)
       for doc in data['response']['docs']:
           text = doc['snippet']
           pub_date = doc['pub_date']
           doc_id = doc['_id']
           if text:
               result['id'].append(doc_id)
               result['created_at'].append(pub_date)
               result['text'].append(text)

   year_df = pd.DataFrame.from_dict(result)   
   df = df.append(year_df)

df.to_csv('NYT_id_date_text.csv', index=False)
            
            
