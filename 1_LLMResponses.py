import os
from utils import parse_vinhetas, get_gpt4_response, get_gemini_response, parse_json
from openai import OpenAI


vinhetas_clinicas = parse_vinhetas('vinhetas.txt')

gpt4_responses = []
gimini_responses = []


for idx, vinheta in enumerate(vinhetas_clinicas, start=1):
    print(f"Processing vinheta: {idx}")
    response = get_gpt4_response(vinheta)
    response_gimini = get_gemini_response(vinheta)
    # Store the responses
    gpt4_responses.append(response)
    gimini_responses.append(response_gimini)


# Output file name
gpt4_filename = "gpt4_responses.txt"
gimini_filename = "gimini_responses.txt"

# Write to file
with open(gpt4_filename, "w", encoding="utf-8") as f:
    for idx, text in enumerate(gpt4_responses, start=1):
        f.write(f"###Vinheta {idx}. \n{text}\n\n")

with open(gimini_filename, "w", encoding="utf-8") as f:
    for idx, text in enumerate(gimini_responses, start=1):
        f.write(f"###Vinheta {idx}. \n{text}\n\n")





