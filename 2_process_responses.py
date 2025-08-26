import pandas as pd
import numpy as np
import os
from utils import parse_responses, parse_json

#responses_processed_gpt4 = parse_responses('gpt4_responses.txt', 'gpt4_responses.json')
responses_processed_gimini_en = parse_responses('gimini_responses_en_5.txt', 'gimini_responses_en_5.json')
responses_processed_gimini_pt = parse_responses('gimini_responses_pt_5.txt', 'gimini_responses_pt_5.json')


# Create DataFrame
#df_gpt = parse_json(responses_processed_gpt4)
df_pt = parse_json(responses_processed_gimini_pt, language='pt')
df_en = parse_json(responses_processed_gimini_en, language='en')

print(f"DataFrame PT: {df_pt.shape}")
print(f"DataFrame EN: {df_en.shape}")

# Merge DataFrames
#df_gpt['Modelo'] = 'GPT-4.1'
df_pt['Modelo'] = 'Gemini-2.0-flash'
df_en['Modelo'] = 'Gemini-2.0-flash'
df_pt['Language'] = 'pt'
df_en['Language'] = 'en'





df = pd.concat([df_pt, df_en], ignore_index=True)


df.to_csv('model_responses_5.csv', index=False, encoding='utf-8', sep=';')

#in notebook 3
#df.to_excel('model_responses_5.xlsx', index=False)


