import pandas as pd
import numpy as np
import os
from utils import parse_responses, parse_json
import json

#responses_processed_gpt4 = parse_responses('gpt4_responses.txt', 'gpt4_responses.json')
print("Processing responses...")
print("----- processing gemini flesh -----")
responses_processed_gimini_en = parse_responses('gimini_responses_en_5.txt', 'gimini_responses_en_5.json')
responses_processed_gimini_pt = parse_responses('gimini_responses_pt_5.txt', 'gimini_responses_pt_5.json')

print("----- processing gpt 5 nano -----")
responses_processed_gpt_en = parse_responses('gpt_responses_en_5.txt', 'gpt_responses_en_5.json', gemini=False)
responses_processed_gpt_pt = parse_responses('gpt_responses_pt_5.txt', 'gpt_responses_pt_5.json', gemini=False)

print("----- processing gpt 5 -----")

responses_processed_gpt_5_en = parse_responses('gpt_responses_en_5_5.txt', 'gpt_responses_en_5_5.json', gemini=False)
responses_processed_gpt_5_pt = parse_responses('gpt_responses_pt_5_5.txt', 'gpt_responses_pt_5_5.json', gemini=False)

print("----- processing gemini pro -----")
responses_processed_gimini_en_pro = parse_responses('gimini_responses_en_5_2.5_pro.txt', 'gimini_responses_en_5_2.5_pro.json')
responses_processed_gimini_pt_pro = parse_responses('gimini_responses_pt_5_2.5_pro.txt', 'gimini_responses_pt_5_2.5_pro.json')





# Create DataFrame
df_gpt_pt = parse_json(responses_processed_gpt_pt, language='pt')
df_gpt_en = parse_json(responses_processed_gpt_en, language='en')
df_pt = parse_json(responses_processed_gimini_pt, language='pt')
df_en = parse_json(responses_processed_gimini_en, language='en')
df_pt_g_pro = parse_json(responses_processed_gimini_pt_pro, language='pt')
df_en_g_pro = parse_json(responses_processed_gimini_en_pro, language='en')
df_gpt_pt_5 = parse_json(responses_processed_gpt_5_pt, language='pt')
df_gpt_en_5 = parse_json(responses_processed_gpt_5_en, language='en')

print(f"DataFrame Gemini Pro PT: {df_pt_g_pro.shape}")
print(f"DataFrame Gemini Pro EN: {df_en_g_pro.shape}")

print(f"DataFrame Gemini PT: {df_pt.shape}")
print(f"DataFrame Gemini EN: {df_en.shape}")

print(f"DataFrame GPT 5 PT: {df_gpt_pt_5.shape}")
print(f"DataFrame GPT 5 EN: {df_gpt_en_5.shape}")

print(f"DataFrame GPT NANO PT: {df_gpt_pt.shape}")
print(f"DataFrame GPT NANO EN: {df_gpt_en.shape}")

# Merge DataFrames
#df_gpt['Modelo'] = 'GPT-4.1'
df_pt['Modelo'] = 'Gemini-2.0-flash'
df_en['Modelo'] = 'Gemini-2.0-flash'
df_pt['Language'] = 'pt'
df_en['Language'] = 'en'

df_pt_g_pro['Modelo'] = 'Gemini-2.5-pro'
df_en_g_pro['Modelo'] = 'Gemini-2.5-pro'
df_pt_g_pro['Language'] = 'pt'
df_en_g_pro['Language'] = 'en'

df_gpt_pt['Modelo'] = 'GPT-5-nano'
df_gpt_en['Modelo'] = 'GPT-5-nano'
df_gpt_pt['Language'] = 'pt'
df_gpt_en['Language'] = 'en'

df_gpt_pt_5['Modelo'] = 'GPT-5'
df_gpt_en_5['Modelo'] = 'GPT-5'
df_gpt_pt_5['Language'] = 'pt'
df_gpt_en_5['Language'] = 'en'

df = pd.concat([df_pt, df_en, df_gpt_en, df_gpt_pt, df_en_g_pro, df_pt_g_pro, df_gpt_en_5, df_gpt_pt_5], ignore_index=True)

#df = pd.concat([df_pt, df_en], ignore_index=True)

df.to_csv('model_responses_5.csv', index=False, encoding='utf-8', sep=';')

#in notebook 3
#df.to_excel('model_responses_5.xlsx', index=False)


