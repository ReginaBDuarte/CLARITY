import pandas as pd
import numpy as np
import os
from utils import parse_responses, parse_json

responses_processed_gpt4 = parse_responses('gpt4_responses.txt', 'gpt4_responses.json')
responses_processed_gimini = parse_responses('gimini_responses.txt', 'gimini_responses.json')


# Create DataFrame
df_gpt = parse_json(responses_processed_gpt4)
df_gimini = parse_json(responses_processed_gimini)

# Merge DataFrames
df_gpt['Modelo'] = 'GPT-4.1'
df_gimini['Modelo'] = 'Gemini-2.0-flash'

df = pd.concat([df_gpt, df_gimini], ignore_index=True)
df.to_csv('model_responses.csv', index=False, encoding='utf-8', sep=';')
df.to_excel('model_responses.xlsx', index=False)


