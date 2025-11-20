import pandas as pd
import numpy as np
import os
from utils import parse_responses, parse_json, parse_claude_responses
import re


responses_processed_gimini_en = parse_claude_responses('claude_responses_en_5.txt', 'claude_responses_en_5.json',language='en')
responses_processed_gimini_pt = parse_claude_responses('claude_responses_pt_5.txt', 'claude_responses_pt_5.json')


# Create DataFrame
#df_gpt = parse_json(responses_processed_gpt4)
#df_pt = parse_json(responses_processed_gimini_pt, language='pt')
df_en = parse_json(responses_processed_gimini_en, language='en')


#print(f"DataFrame PT: {df_pt.shape}")
print(f"DataFrame EN: {df_en.shape}")

# Merge DataFrames
#df_gpt['Modelo'] = 'GPT-4.1'
#df_pt['Modelo'] = 'Claude'
df_en['Modelo'] = 'Claude'
#df_pt['Language'] = 'pt'
df_en['Language'] = 'en'


#df = pd.concat([df_pt, df_en], ignore_index=True)


df_en.to_csv('model_claude_responses_5.csv', index=False, encoding='utf-8', sep=';')