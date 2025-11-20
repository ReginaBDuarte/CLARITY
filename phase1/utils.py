import os
from openai import OpenAI
from google import genai
from google.genai import types
import json
import re
import pandas as pd
import ast
import numpy as np


#define clients
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client_google = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


def parse_vinhetas_csv(filepath, language):
    #data = pd.read_excel('VinhetasFinaisPT_EN.V1.0.xlsx')
    data = pd.read_excel(filepath)
    vinhetas = data.loc[data['Versão (EN/PT)']==language, 'Resumo'].values.tolist()
    return vinhetas



def parse_vinhetas(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split the content by 'Vinheta' headers
    import re
    vinhetas = re.split(r'VINHETA\d+:', content)

    # Remove the first empty element if the text starts with 'Vinheta1:'
    vinhetas = vinhetas[1:] if vinhetas[0].strip() == '' else vinhetas

    # Strip extra whitespace from each vignette
    vinhetas = [v.strip() for v in vinhetas]

    return vinhetas

def parse_prompt(file_path, separator='[vinheta]'):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if separator not in content:
            raise ValueError(f"Separator '{separator}' not found in the file.")

    system_prompt, user_prompt = content.split(separator, 1)
    return system_prompt.strip(), user_prompt.strip()

    



def get_gpt_response(vinheta, system_prompt, user_prompt, model):
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system", 
                "content": system_prompt
                },

            {   "role": "user",
                "content": vinheta
                },

            {   "role": "user",
                "content": user_prompt
                }   
        ]       
    )
    return(response.output_text)


def get_gemini_response(vinheta, system_prompt, user_prompt, model="gemini-2.0-flash"):

    response = client_google.models.generate_content(
        model=model,
        config=types.GenerateContentConfig(system_instruction=system_prompt), 
        contents=[ vinheta,
                  user_prompt]
                  )

    
    return(response.text)



def parse_responses(response_text, json_name, gemini=True):
    
    # Load your .txt file content
    with open(response_text, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match each Vinheta section
    sections = re.split(r'###Vinheta (\d+)\.', content)
    

    # Dictionary to store extracted JSONs
    vinheta_jsons = {}
    
    # Iterate through the split content, skipping the first (before the first Vinheta)
    for i in range(1, len(sections), 2):
        vinheta_number = sections[i].strip()
        vinheta_content = sections[i + 1]
        if gemini:
            # Look for the JSON block after '**6. JSON File:**'
            match = re.search(r'```json(.*?)```', vinheta_content, re.DOTALL)
            ##for parsing gemini
            if match:
                json_block = match.group(1).strip()

                try:   
                    parsed_json = json.loads(json_block)
                    vinheta_jsons[f"Vinheta {vinheta_number}"] = parsed_json
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON in Vinheta {vinheta_number}: {e}")
        else:
            match_alt = re.search(r'json_file\s*=\s*(.*?)\n?```', vinheta_content, re.DOTALL)
            match_alt_2 = re.search(r'json_file\s*=\s*(.*?)(?:\r?\n){2}', vinheta_content, re.DOTALL)
            match_alt_3 = re.search(r'Json File Creation\s*\r?\n(.*?)(?:\r?\n){2}', vinheta_content, re.DOTALL)
            match_alt_4 = re.search(r'json_file\s*[\r\n]+\s*(\{[\s\S]*\})\s',vinheta_content, re.DOTALL)
            match = re.search(r'```json(.*?)```', vinheta_content, re.DOTALL)

            if match_alt:
                #print(vinheta_number, "alt")
                json_block = match_alt.group(1).strip()
                try:
                    parsed_json = ast.literal_eval(json_block)
                    vinheta_jsons[f"Vinheta {vinheta_number}"] = parsed_json
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON in Vinheta {vinheta_number}: {e}")
            elif match_alt_2:
                #print(vinheta_number, "alt2")
                json_block = match_alt_2.group(1).strip()
                try:
                    parsed_json = ast.literal_eval(json_block)
                    vinheta_jsons[f"Vinheta {vinheta_number}"] = parsed_json
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON in Vinheta {vinheta_number}: {e}")
            elif match_alt_3:
                #print(vinheta_number, "alt3")
                json_block = match_alt_3.group(1).strip() 
                try:
                    parsed_json = ast.literal_eval(json_block)
                    vinheta_jsons[f"Vinheta {vinheta_number}"] = parsed_json
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON in Vinheta {vinheta_number}: {e}")
            elif match_alt_4:
                #print(vinheta_number, "alt4")
                json_block = match_alt_4.group(1).strip()
                #print(json_block)
                try:
                    parsed_json = ast.literal_eval(json_block)
                    vinheta_jsons[f"Vinheta {vinheta_number}"] = parsed_json
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON in Vinheta {vinheta_number}: {e}")
        
            elif match:
                #print(vinheta_number, "match")
                json_block = match.group(1).strip() 
                try:
                    parsed_json = ast.literal_eval(json_block)
                    vinheta_jsons[f"Vinheta {vinheta_number}"] = parsed_json
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON in Vinheta {vinheta_number}: {e}")
          
   
    # Output result to a file or use it
    with open(json_name, 'w', encoding='utf-8') as f:
        json.dump(vinheta_jsons, f, ensure_ascii=False, indent=2)
    return vinheta_jsons

def parse_claude_responses(response_text, json_name, language='pt'):
    # Load your .txt file content
    with open(response_text, 'r', encoding='utf-8') as f:
        content = f.read()

    if language == 'en':
        # Pattern to match each Vinheta section
        sections = re.split(r'VIGNETTE #\d+', content)
    else:
        sections = re.split(r'VINHETA \d+.', content)
    
    # Dictionary to store extracted JSONs
    vinheta_jsons = {}
    
    # Iterate through the split content, skipping the first (before the first Vinheta)
    for i in range(1, len(sections)):
        vinheta_number = i
        vinheta_content = sections[i]

        # Look for the JSON block after '**6. JSON File:**'
        match = re.search(r'```json(.*?)```', vinheta_content, re.DOTALL)
        if match:
            json_block = match.group(1).strip()
            try:
                parsed_json = json.loads(json_block)
                vinheta_jsons[f"Vinheta {vinheta_number}"] = parsed_json
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON in Vinheta {vinheta_number}: {e}")

    # Output result to a file or use it
    with open(json_name, 'w', encoding='utf-8') as f:
        json.dump(vinheta_jsons, f, ensure_ascii=False, indent=2)
    return vinheta_jsons


def parse_json(json_file, language='pt'):
    # Build list of rows
    rows = []
    if language == 'pt':
        for vinheta_id, data in json_file.items():

            row = {
                "id": vinheta_id,  # or vinheta_id.replace("Vinheta ", "") if you want just the number
                "score_2_aplica": data['Risco'].get("SCORE2 Aplicável", None),
                "score2_motivonaoaplica": data['Risco'].get("Exceção", None),
                "score_2_absoluto_calculado": data["Risco"].get("SCORE2", None),
                "categoria_de_risco": data["Risco"].get("Categoria", None),
                "confianca": data["Risco"].get("confiança", None),
                "fatores_de_risco": data.get("Fatores de risco", {}),
                'modificadores_de_risco': data.get("Modificadores de risco", {})
            }
            rows.append(row)
    elif language == 'en':
        for vinheta_id, data in json_file.items():
            row = {
                "id": vinheta_id,  # or vinheta_id.replace("Vinheta ", "") if you want just the number
                "score_2_aplica": data['Risk'].get("SCORE2 Applicable", None),
                "score2_motivonaoaplica": data['Risk'].get("Exception", None),
                "score_2_absoluto_calculado": data["Risk"].get("SCORE2", None),
                "categoria_de_risco": data["Risk"].get("Category", None),
                "confianca": data["Risk"].get("Confidence Level", None),
                "fatores_de_risco": data.get("Risk Factors", {}),
                "modificadores_de_risco": data.get("Risk Modifiers", {})
            }
            rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(rows)
    return df


def score2(idade, sexo, tabagismo, PAS, CT, HDL):
    """Calculate SCORE2 risk percentage based on input parameters.
    
    Parameters:
    idade (int): Age of the individual in years.
    sexo (str): 'male' or 'female'.
    tabagismo (bool): True if the individual is a smoker, False otherwise.
    PAS (int): Systolic blood pressure in mmHg.
    CT (int): Total cholesterol level in mmol/L.
    HDL (int): HDL cholesterol level in mmol/L.

    Returns:
    float: Estimated 10-year risk percentage of cardiovascular disease
    for portuguese population.
    
    """
    #vairables
    c_age = (idade -60) / 5
    c_sbd = (PAS - 120) / 20
    c_tchol = (CT - 6) / 1
    c_hdl = (HDL-1.3) / 0.5

    diabetes = 0  # Assuming no diabetes for this calculation
    smoker = 1 if tabagismo else 0

    c_age_smoker = c_age * smoker
    c_age_sbp = c_age * c_sbd
    c_age_tchol = c_age * c_tchol
    c_age_hdl = c_age * c_hdl
    c_age_diabetes = c_age * diabetes

    variables = np.array([
        c_age,
        smoker,
        c_sbd,
        diabetes,
        c_tchol,
        c_hdl,
        c_age_smoker,
        c_age_sbp,
        c_age_tchol,
        c_age_hdl,
        c_age_diabetes
    ])

    So_h = 0.9605 # Survival at 10 years
    coefficients_homens = np.array([
        0.3742,
        0.6012,
        0.2777,
        0.6457,
        0.1458,
        -0.2698,
        -0.0755,
        -0.0255,
        -0.0281,
        0.0426,
        -0.0983
    ])

    coefficients_mulheres = np.array([
        0.4648,
        0.7744,
        0.3131,
        0.8096,
        0.1002,
        -0.2606,
        -0.1088,
        -0.0277,
        -0.0226,
        0.0613,
        -0.1272
    ])

    So_m = 0.9776 # Survival at 10 years

    LP_homens = np.dot(variables, coefficients_homens)
    LP_mulheres = np.dot(variables, coefficients_mulheres)

    # score 
    p_homens = 1 - So_h ** np.exp(LP_homens)
    p_mulheres = 1 - So_m ** np.exp(LP_mulheres)

    # calibracao para portugal (risco moderado)

    scale1_homens = -0.1565
    scale2_homens = 0.8009

    scale1_mulheres = -0.3143
    scale2_mulheres = 0.7701

    z_homens = np.log(-np.log(1 - p_homens)) 
    z_mulheres = np.log(-np.log(1 - p_mulheres))

    z_homens_star = scale1_homens + scale2_homens * z_homens
    z_mulheres_star = scale1_mulheres + scale2_mulheres * z_mulheres

    score_homens = 1 - np.exp(-np.exp(z_homens_star))
    score_mulheres = 1 - np.exp(-np.exp(z_mulheres_star))

    if sexo.lower() == 'male':
        score = score_homens * 100  # Convert to percentage
    else:
        score = score_mulheres * 100  # Convert to percentage
    
    return score


print(score2(65, 'male', True, 140, 6.5, 1.2))