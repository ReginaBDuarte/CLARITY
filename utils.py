import os
from openai import OpenAI
from google import genai
from google.genai import types
import json


#define clients
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client_google = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


def parse_vinhetas(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split the content by 'Vinheta' headers
    import re
    vinhetas = re.split(r'Vinheta\d+:', content)

    # Remove the first empty element if the text starts with 'Vinheta1:'
    vinhetas = vinhetas[1:] if vinhetas[0].strip() == '' else vinhetas

    # Strip extra whitespace from each vignette
    vinhetas = [v.strip() for v in vinhetas]

    return vinhetas



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



def get_gemini_response(vinheta):
    response = client_google.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction="És um assistente de cardiologia a dar apoio a uma consulta médica. "
                "Lê a vinheta clínica e analisa o risco cardiovascular do doente."), 
        contents=[

            vinheta,
            "Tarefas:"

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
            "de tratamento."
            "6. No final, cria um json_file com a seguinte estrutura: json_file ={'Risco':{'Categoria': '..', 'Risco absoluto': '..' },"
            "'Fatores de risco':{'Fator1':'valor1','Fator2':'valor2'},'confiança': ..}."

            ]
    )

    
    return(response.text)

def parse_json(json_string):
    pass
