import os
from utils import  parse_vinhetas_csv, get_gpt_response, parse_prompt, parse_response, aplica_score2, inserir_score2, parse_prompt2, export_conversation_to_txt, LLM_Response
from openai import OpenAI

print(os.environ["OPENAI_API_KEY"])

#parse vinhetas
vinhetas_clinicas_pt = parse_vinhetas_csv('VinhetasFinaisPT_EN.V1.0.xlsx', language='PT')
system_prompt_pt, user_prompt_pt = parse_prompt('prompt1.txt', separator='[Vinheta]')
prompt2 = parse_prompt2('prompt2.txt')
prompt2a = parse_prompt2('prompt2a.txt')

prompts = [system_prompt_pt, user_prompt_pt, prompt2, prompt2a]


### INITIAL CHECKS ##########

#print(f"Total vinhetas to process:  {len(vinhetas_clinicas_pt)} (PT)")
#print(f"System prompt (PT): {system_prompt_pt}")
#print(f"User prompt (PT): {user_prompt_pt}")
#print("vinhetas_clinicas_pt:", vinhetas_clinicas_pt[:2])  # Display first two for sanity check

#i=5
#LLM_Response(prompts, i, vinhetas_clinicas_pt[i-1], model='gpt-5')


import pandas as pd
#for pt

df_final = pd.read_csv('intermediate_results_phase1_plus_calculator_5.csv') 
for idx, vinheta in enumerate(vinhetas_clinicas_pt[15:], start=16):
    dic ={}
    print(f"Processing vinheta index: {idx}")
    dic[idx] = LLM_Response(prompts, idx, vinheta, model='gpt-5')
    df = pd.DataFrame.from_dict(dic, orient='index').reset_index().rename(columns={'index': 'Vinheta_Index'})
    df_final = pd.concat([df_final, df], ignore_index=True)
    df_final.to_csv('intermediate_results_phase1_plus_calculator_5.csv', index=False)



















