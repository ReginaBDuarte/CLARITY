import os
from utils import parse_vinhetas, parse_vinhetas_csv, get_gpt_response, get_gemini_response, parse_json, parse_prompt
from openai import OpenAI

# paerse vinhetas txt (comment if not needed)
#vinhetas_clinicas_en = parse_vinhetas('vinhetas_2_en.txt')
#vinhetas_clinicas_pt = parse_vinhetas('vinhetas_2_pt.txt')

#parse vinhetas csd
vinhetas_clinicas_en = parse_vinhetas_csv('VinhetasFinaisPT_EN.V1.0.xlsx', language='EN')
vinhetas_clinicas_pt = parse_vinhetas_csv('VinhetasFinaisPT_EN.V1.0.xlsx', language='PT')

system_prompt_en, user_prompt_en = parse_prompt('prompt_5_en.txt', separator='[Vignette]')
system_prompt_pt, user_prompt_pt = parse_prompt('prompt_5_pt.txt', separator='[Vinheta]')

print(os.environ["GEMINI_API_KEY"])

#print(f"Total vinhetas to process: {len(vinhetas_clinicas_en)} (EN) and {len(vinhetas_clinicas_pt)} (PT)")
#print(f"System prompt (EN): {system_prompt_en}")
#print(f"System prompt (PT): {system_prompt_pt}")
#print(f"User prompt (EN): {user_prompt_en}")
#print(f"User prompt (PT): {user_prompt_pt}")
#print("vinhetas_clinicas_en:", vinhetas_clinicas_en[:2])  # Display first two for sanity check
# vinhetas_clinicas_pt: Display first two for sanity check
#print("vinhetas_clinicas_pt:", vinhetas_clinicas_pt[:2])  # Display first two for sanity check


#gpt4_responses = []
gimini_responses_pt = []
gimini_responses_en = []

print('time start')
import time

start = time.time()


#for pt
for idx, vinheta in enumerate(vinhetas_clinicas_pt, start=1):
    print(f"Processing vinheta: {idx}")
    #response = get_gpt4_response(vinheta)
    response_gimini = get_gemini_response(vinheta, 
                                          system_prompt=system_prompt_pt,
                                          user_prompt=user_prompt_pt,
                                          model='gemini-2.5-pro'
                                          )
    # Store the responses
    #gpt4_responses.append(response)
    gimini_responses_pt.append(response_gimini)

end = time.time()
print(f"Execution time: {end - start:.4f} seconds")

ola

#for en
for idx, vinheta in enumerate(vinhetas_clinicas_en, start=1):
    print(f"Processing vinheta: {idx}")
    #response = get_gpt4_response(vinheta)
    response_gimini = get_gemini_response(vinheta, 
                                          system_prompt=system_prompt_en,
                                          user_prompt=user_prompt_en,
                                          model='gemini-2.5-pro'
                                          )
    # Store the responses
    #gpt4_responses.append(response)
    gimini_responses_en.append(response_gimini)


# Output file name
#gpt4_filename = "gpt4_responses.txt"
gimini_filename_pt = "gimini_responses_pt_5_2.5_pro.txt"
gimini_filename_en = "gimini_responses_en_5_2.5_pro.txt"

# Write to file
#with open(gpt4_filename, "w", encoding="utf-8") as f:
 #   for idx, text in enumerate(gpt4_responses, start=1):
  #      f.write(f"###Vinheta {idx}. \n{text}\n\n")

with open(gimini_filename_pt, "w", encoding="utf-8") as f:
    for idx, text in enumerate(gimini_responses_pt, start=1):
        f.write(f"###Vinheta {idx}. \n{text}\n\n")

with open(gimini_filename_en, "w", encoding="utf-8") as f:
    for idx, text in enumerate(gimini_responses_en, start=1):
        f.write(f"###Vinheta {idx}. \n{text}\n\n")






