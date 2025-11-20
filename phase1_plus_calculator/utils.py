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



def parse_vinhetas_csv(filepath, language):
    #data = pd.read_excel('VinhetasFinaisPT_EN.V1.0.xlsx')
    data = pd.read_excel(filepath)
    vinhetas = data.loc[data['Versão (EN/PT)']==language, 'Resumo'].values.tolist()
    return vinhetas



def parse_prompt(file_path, separator='[vinheta]'):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if separator not in content:
            raise ValueError(f"Separator '{separator}' not found in the file.")

    system_prompt, user_prompt = content.split(separator, 1)
    return system_prompt.strip(), user_prompt.strip()

def parse_prompt2(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return content.strip()



def get_gpt_response(conversation, model):
    response = client.responses.create(
        model=model,
        input= conversation     
    )

    assistant_reply = response.output_text
    
    # Append GPT's reply so it remembers it
    conversation.append({"role": "assistant", "content": assistant_reply})
    
    return (assistant_reply)
 

def inserir_score2(texto, score2):
    # Substitui apenas o resto da linha após ":" sem tocar no que está depois da quebra de linha
    return re.sub('score_valor',
                str(score2)+'%',
                texto
    )


def parse_response(response_text):
    # Extract JSON part from the response text
    match = re.search(r'```json(.*?)```', response_text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in the response text.")
    
    # Remove the ```json and ``` markers and any leading/trailing whitespace
    json_str = match.group(1).strip()

   
    try:
        response_data = json.loads(json_str)  # Use json.loads for valid JSON
    except Exception as e:
        raise ValueError(f"Error parsing JSON: {e}")
    
    return response_data
    

def export_conversation_to_txt(conversation, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        for msg in conversation:
            role = msg["role"].upper()

            f.write(f"=== {role} ===\n")
            f.write(msg["content"].strip() + "\n\n")






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

    if sexo.lower() == 'masculino':
        score = score_homens * 100  # Convert to percentage
    else:
        score = score_mulheres * 100  # Convert to percentage
    
    return round(score,2)


def aplica_score2(json_response):
    if json_response['Aplicabilidade']['SCORE2 Aplicável'] == 'Sim':
        fatores = json_response['Fatores de risco']

        idade = int(fatores.get('Idade', '0').replace(',', '.'))
        genero = fatores.get('Género', '').strip()
        tabagismo = fatores.get('Tabagismo', '').strip()
        pas = int(fatores.get('Pressão Arterial Sistólica', '0').replace(',', '.'))
        colesterol_total = int(fatores.get('Colesterol Total', '0').replace(',', '.'))
        hdl = int(fatores.get('Colesterol HDL', '0').replace(',', '.'))
        n_hdl = int(fatores.get('Colesterol não HDL', '0').replace(',', '.'))
        
        if tabagismo == 'Não fumador':
            tabagismo = False
        else:
            tabagismo = True

        ct_mmol = round(colesterol_total * 0.02586,1)
        hdl_mmol = round(hdl * 0.02586,1)
   
        score2_result = score2(idade, genero, tabagismo, pas, ct_mmol, hdl_mmol)

        return score2_result

    else:
        return "SCORE2 not applicable"
    


