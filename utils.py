import os
from openai import OpenAI
from google import genai
from google.genai import types
import json
import re
import pandas as pd


#define clients
#client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
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

    



def get_gpt4_response(vinheta):
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "system", 
                "content":"“És um assistente de cardiologia a dar apoio a uma consulta médica. "
                "Lê a vinheta clínica e analisa o risco cardiovascular do doente."
                },

            {   "role": "user",
                "content": vinheta
                },

            {   "role": "user",
                "content": "Tarefas:"
                "1. Identifica e enumera todos os fatores de risco cardiovascular mencionados e presentes na vinheta;"
                "utiliza uma tabela para listar os fatores de risco presentes"
                "2. Utilizando a classificação para países de risco moderado, "
                "calcula o risco de eventos cardiovasculares a 10 anos de acordo com as diretrizes de 2021 da Sociedade Europeia de Cardiologia "
                "sobre Prevenção Cardiovascular e indica os seguintes: a) categoria de risco do doente (baixo, moderado, elevado ou muito elevado); "
                "b) valor de risco absoluto em percentagem calculado pelas tabelas de risco constantes das diretrizes; reporta os valores numa tabela, "
                "incluindo a categoria de risco e o risco absoluto"
                "3. Fornece uma breve explicação da tua avaliação, referindo os fatores de risco do doente e de que forma influenciam"
                " o risco cardiovascular;"
                "4. Classifica o grau de confiança (baixa, intermédia, alta ou muito alta) da categoria de risco identificada para este doente;"
                " não justifiques a resposta, reporta apenas o grau de confiança da tua resposta"
                "5. Com base na categoria de risco, indica os objetivos terapêuticos para este doente e inclui recomendações relativas aos principais"
                " fatores de risco cardiovascular, conforme as diretrizes da Sociedade Europeia de Cardiologia; "
                "reporta os resultados numa tabela com duas colunas, indicando na primeira os fatores de risco identificados e na segunda os objectivos "
                "de tratamento"
                "6. No final, cria um json_file com a seguinte estrutura: json_file ={'Risco':{'Categoria': '..', 'Risco absoluto': '..' },"
                "'Fatores de risco':{'Fator1':'valor1','Fator2':'valor2'},'confiança': ..}."
                }   

        ]

        
    )
    return(response.output_text)


def get_gemini_response(vinheta, system_prompt, user_prompt):

    response = client_google.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=system_prompt), 
        contents=[ vinheta,
                  user_prompt]
                  )

    
    return(response.text)



def parse_responses(response_text, json_name):
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
