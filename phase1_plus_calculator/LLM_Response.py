import os
from utils import  parse_vinhetas_csv, get_gpt_response, parse_prompt, parse_response, aplica_score2, inserir_score2, parse_prompt2, export_conversation_to_txt
from openai import OpenAI

print(os.environ["OPENAI_API_KEY"])

#parse vinhetas
vinhetas_clinicas_pt = parse_vinhetas_csv('VinhetasFinaisPT_EN.V1.0.xlsx', language='PT')
system_prompt_pt, user_prompt_pt = parse_prompt('prompt1.txt', separator='[Vinheta]')
prompt2 = parse_prompt2('prompt2.txt')

### INITIAL CHECKS ##########

#print(f"Total vinhetas to process:  {len(vinhetas_clinicas_pt)} (PT)")
#print(f"System prompt (PT): {system_prompt_pt}")
#print(f"User prompt (PT): {user_prompt_pt}")
#print("vinhetas_clinicas_pt:", vinhetas_clinicas_pt[:2])  # Display first two for sanity check

#### INITIALIZE CONVERSATION ############
conversation=[
            {
                "role": "system", 
                "content": system_prompt_pt
                },

            {   "role": "user",
                "content": vinhetas_clinicas_pt[0]
                },

            {   "role": "user",
                "content": user_prompt_pt
                }   
        ]  

response_gpt = get_gpt_response(conversation, model='gpt-4o')

###### GET EXTRACTED FACTORS AND CALCULATE SCORE2 ########

json= parse_response(response_gpt)  # Sanity
score= aplica_score2(json)  # Sanity

########## ADD SCORE2 TO CONVERSATION ###########

inserted_text= inserir_score2(prompt2, score)
conversation.append({
    "role": "user", "content": inserted_text
})  # add to the conversation as a new user message for the next

response_gpt = get_gpt_response(conversation, model='gpt-4o')

######## EXPORT CONVERSATION TO TXT FOR INSPECTION #########
filepath = "conversation_checkpoint.txt"
export_conversation_to_txt(conversation, filepath)  # Save



    

checkpoint



#gpt4_responses = []
responses_pt = []

import time

start = time.time()

#for pt
for idx, vinheta in enumerate(vinhetas_clinicas_pt, start=1):
    print(f"Processing vinheta: {idx}")
    #response = get_gpt4_response(vinheta)
    response_gpt = get_gpt_response(vinheta, 
                                          system_prompt=system_prompt_pt,
                                          user_prompt=user_prompt_pt,
                                          model='gpt-4o')
    # Store the responses
    #gpt4_responses.append(response)
    responses_pt.append(response_gpt)

end = time.time()
print(f"Execution time: {end - start:.4f} seconds")



# Output file name

filename_pt = "gpt_responses.txt"

with open(filename_pt, "w", encoding="utf-8") as f:
    for idx, text in enumerate(responses_pt, start=1):
        f.write(f"###Vinheta {idx}. \n{text}\n\n")





