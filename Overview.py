import os
from utils import parse_vinhetas


########GIMINI############

from google import genai
from google.genai import types



print('import worked')

vinhetas_clinicas = parse_vinhetas('vinhetas.txt')

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction="És um assistente de cardiologia a dar apoio a uma consulta médica. "
            "Lê a vinheta clínica e analisa o risco cardiovascular do doente."), 
    contents=[

        vinhetas_clinicas[1],
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
print(response.text)





###########OPENAI###############

from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "system", 
            "content":"És um assistente de cardiologia a dar apoio a uma consulta médica. "
            "Lê a vinheta clínica e analisa o risco cardiovascular do doente."
            },

        {   "role": "user",
            "content": vinhetas_clinicas[1]
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
            "de tratamento."
            "6. No final, cria um json_file com a seguinte estrutura: json_file ={'Risco':{'Categoria': '..', 'Risco absoluto': '..' },"
            "'Fatores de risco':{'Fator1':'valor1','Fator2':'valor2'},'confiança': ..}."
            }   

    ]

    
)

print(response.output_text)
