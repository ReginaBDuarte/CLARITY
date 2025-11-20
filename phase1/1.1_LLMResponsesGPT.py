import os
from utils import parse_vinhetas, parse_vinhetas_csv, get_gpt_response, get_gemini_response, parse_json, parse_prompt
from openai import OpenAI

# paerse vinhetas txt (comment if not needed)
#vinhetas_clinicas_en = parse_vinhetas('vinhetas_2_en.txt')
#vinhetas_clinicas_pt = parse_vinhetas('vinhetas_2_pt.txt')


print(os.environ["OPENAI_API_KEY"])

#parse vinhetas csd
vinhetas_clinicas_en = parse_vinhetas_csv('VinhetasFinaisPT_EN.V1.0.xlsx', language='EN')
vinhetas_clinicas_pt = parse_vinhetas_csv('VinhetasFinaisPT_EN.V1.0.xlsx', language='PT')

system_prompt_en, user_prompt_en = parse_prompt('prompt_5_en.txt', separator='[Vignette]')
system_prompt_pt, user_prompt_pt = parse_prompt('prompt_5_pt.txt', separator='[Vinheta]')



#print(f"Total vinhetas to process: {len(vinhetas_clinicas_en)} (EN) and {len(vinhetas_clinicas_pt)} (PT)")
#print(f"System prompt (EN): {system_prompt_en}")
#print(f"System prompt (PT): {system_prompt_pt}")
#print(f"User prompt (EN): {user_prompt_en}")
#print(f"User prompt (PT): {user_prompt_pt}")
#print("vinhetas_clinicas_en:", vinhetas_clinicas_en[:2])  # Display first two for sanity check
# vinhetas_clinicas_pt: Display first two for sanity check
#print("vinhetas_clinicas_pt:", vinhetas_clinicas_pt[:2])  # Display first two for sanity check


#gpt4_responses = []
responses_pt = []
responses_en = []
import time

start = time.time()

#for pt
for idx, vinheta in enumerate(vinhetas_clinicas_pt, start=1):
    print(f"Processing vinheta: {idx}")
    #response = get_gpt4_response(vinheta)
    response_gpt = get_gpt_response(vinheta, 
                                          system_prompt=system_prompt_pt,
                                          user_prompt=user_prompt_pt,
                                          model='gpt-5-nano')
    # Store the responses
    #gpt4_responses.append(response)
    responses_pt.append(response_gpt)

end = time.time()
print(f"Execution time: {end - start:.4f} seconds")

ola

# Output file name

filename_pt = "gpt_responses_pt_5.txt"
filename_en = "gpt_responses_en_5.txt"



with open(filename_pt, "w", encoding="utf-8") as f:
    for idx, text in enumerate(responses_pt, start=1):
        f.write(f"###Vinheta {idx}. \n{text}\n\n")

#for en
for idx, vinheta in enumerate(vinhetas_clinicas_en, start=1):
    print(f"Processing vinheta: {idx}")
    #response = get_gpt4_response(vinheta)
    response_gpt = get_gpt_response(vinheta, 
                                          system_prompt=system_prompt_en,
                                          user_prompt=user_prompt_en,
                                          model='gpt-5-nano'
                                          )
    # Store the responses
    responses_en.append(response_gpt)

with open(filename_en, "w", encoding="utf-8") as f:
    for idx, text in enumerate(responses_en, start=1):
        f.write(f"###Vinheta {idx}. \n{text}\n\n")






