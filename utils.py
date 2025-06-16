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



def get_gemini_response_old(vinheta):
    response = client_google.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction="Função:  És um assistente virtual especializado em cardiologia preventiva que apoia a consulta médica."
            "Objetivo: Analisar a vinheta clínica abaixo, extrair de forma estruturada todos os fatores relevantes para avaliar"
              "o risco cardiovascular, calcular o risco segundo as recomendações da Sociedade Europeia de"
              "Cardiologia de 2021 (ESC 2021), para a Prevenção Cardiovascular, em países de risco moderado (Portugal)"
              "e propor objetivos terapêuticos coerentes"), 
        contents=[

            vinheta,
            "1. Extracção estruturada dos fatores de risco:"
            "- Preenche uma tabela Markdown com as quatro categorias fixas: Fatores de Risco Tradicionais, "
            "Estilo de Vida, Doenças Associadas, Discriminadores de Risco."
            "- Para cada fator: Valor (tal como aparece ou “desconhecido”); Unidade se aplicável (mmHg, mg/dL, anos);"
            "- Mantém exatamente o mesmo nome de cada variável indicado na lista-referência abaixo."
            "- Quando mais do que uma opção é possível (p. ex. doença cardiovascular estabelecida), lista-as separadas por “;”."
            "- Lista-referência (não alterar nomes):"
            "[Fator de Risco -> Valores; Idade -> Numérico; Género->Masculino; Feminino; Tabagismo -> Não fumador; Ex-Fumador; Fumador; Hipertensão Arterial -> Sim, Não;"
            "Pressão Arterial Sistólica -> Valor; Pressão Arterial Diastólica -> Valor; Dislipidemia -> Sim, Não; Colesterol Total -> Numérico; Colesterol HDL -> Numérico; Triglicéridos -> Numérico;"
             "Colesterol LDL -> Numérico; Colesterol não HDL (se necessário calcular) -> Numérico."
            "Estilo de Vida -> Valores; Sedentarismo -> Sim, Não; Dieta inadequada -> Sim, Não; Sono inadequado -> Sim, Não; "
            "Consumo excessivo de álcool -> Sim, Não."
            "Doenças Associadas -> Valores; Diabetes Mellitus-> Sim, Não;"
            "Dislipidemia Familiar -> Não, Possível, Provável, Definitiva; Doença Renal Crónica -> Não; Ligeira, Moderada, Grave;"
            "Doença cardiovascular estabelecida -> Sim, Não; Classificação da doença cardiovascular (pode ser selecionado mais do que um) -> Sindrome Coronária Aguda (ou Enfarte do Miocárdio),"
             "Revascularização (Angioplastia Coronária, Cirurgia de Revascularização Coronária (CABG) ou revascularização arterial periférica), "
             "Acidente Vascular Cerebral (AVC) ou Acidente Isquémico Transitório (AIT), Aneurisma da Aorta, Doença Arterial Periférica, Doença aterosclerótica inequívoca documentada por imagem (AngioTAC cardíaco, Doppler Carótidas ou Coronariografia)."
            "Discriminadores de Risco -> Valores; Pode selecionar mais do que um ->  Score de Cálcio elevado; Placas Carótidas; "
            "Obesidade; Pre-Diabetes; Stress Psicossocial; Baixo Nível Socioeconómico; História Familiar de DCV; Lp (a) aumentada; "
            "Rigidez Arterial aumentada; Índice Perna-Braço diminuído; PCR alta sensibilidade elevada; Doença Inflamatória Crónica; Infecção HIV; "
            "Enxaqueca com aura; Perturbação do sono; Esteatose Hepática Não Alcoólica; Disfunção erétil; Sindrome Ovário Poliquistico; "
            "Menopausa precoce; Complicações Gravidez (Pre-eclampsia, Hipertensão arterial ou diabetes); Doença pulmonar obstrutiva crónica (DPOC); Cancro; "
            "Outro (especificar); Se Score de Cálcio reportado, indique o valor absoluto; "
            "Se reportado, considera que o valor de Score de Cálcio condiciona a classificação de risco? -> Sim, Não] "


            "2. Estratificação de risco segundo recomendações da sociedade europeia de cardiologia 2021 (ESC 2021)"

            "- Verifica se o SCORE2 é aplicável (40–69 anos sem doença cardiovascular, doença renal crónica, diabetes, dislipidemia familiar, ou outra). "
            "Se existir critério de exclusão, indica qual."
            "- Se aplicável, calcula o SCORE-2 (10-anos %): Usa a tabela disponível nas recomendações,"
            " a fórmula original com coeficientes publicados ou uma calculadora online reconhecida, aplicável aos países de risco moderado (Portugal); especifica o método usado." 
            "- Identifica a categoria de risco, tendo em conta a idade (Baixo; Intermédio; Alto; Muito-Alto)"
            "- Se o SCORE2 não se aplica, classifica o doente de acordo com as exceções das recomendações (doença cardiovascular, doença renal crónica, diabetes, dislipidemia familiar, etc.)"
            "- Indica o grau de confiança da categoria de risco indicada (Escolhe apenas uma categoria -> Baixa, Intermédia, Alta, Muito-Alta)."
            "- Apresenta as saídas numa tabela Markdown: | SCORE2 (%) | Método | Categoria | Exceção (se aplicável) | Grau de Confiança"

            "3. Breve explicação clínica"

            "Máx. 150 palavras. Realça os fatores que mais contribuíram para a classificação de risco "
            "(p. ex. HTA mal controlada, LDL elevado, modificadores de risco, etc.)."

            "4. Recomendações tratamento"

            "- Elabora tabela Markdown com duas colunas: | Medida | Valor-Alvo/Observação |."
            "- Com base na categoria de risco identificada, seleciona as intervenções adequadas da seguinte lista:"
            "“Manter a estratégia atual, Redução de peso, Cessação tabágica, Reduzir Colesterol, Controlar Hipertensão Arterial, Controlar Diabetes, "
            "Iniciar terapêutica anti-trombótica (Aspirina ou P2Y12), Outro (especificar)” "
            "- Inclui valores alvo ESC 2021 para colesterol LDL e Pressão arterial, ajustados à categoria de risco, "
            "usando as seguintes opções:"
            "“LDL<116 mg/dL (3.0 mmol/L), LDL<100 mg/dL (2.6 mmol/L), LDL<70 mg/dL (1.8 mmol/L), LDL <55 mg/dL (1.4 mmol/L) e redução ≥50%;"
            " PA sistólica <130 mmHg e PA Diastólica <80mmHg, PA sistólica <140 mmHg e PA Diastólica <80mmHg, Outro (especificar)”"

            "5. Formato geral"

            "- Usa Markdown; não incluas texto fora das secções acima"
            "- Quando um valor não se encontra nos dados, escreve “desconhecido”"
            "- Usa sempre “,” como separador decimal e “.” para milhares (padrão português)"

            "6. Criação de um json file"
            "- No final, cria um json file que sumarize as informações, com a seguinte estrutura: "
            "json_file ={"
            "'Risco':{'Categoria': '..', 'SCORE2': '..', 'confiança': '..' },"
            "'Fatores de risco':{'Fator1':'valor1','Fator2':'valor2', …}}."

            ]
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
                "categoria_de_risco": data["Risco"].get("Categoria", None),
                "risco_absoluto": data["Risco"].get("SCORE2", None),
                "fatores_de_risco": data.get("Fatores de risco", {}),
                "confianca": data["Risco"].get("confiança", None)
            }
            rows.append(row)
    elif language == 'en':
        for vinheta_id, data in json_file.items():
            row = {
                "id": vinheta_id,  # or vinheta_id.replace("Vinheta ", "") if you want just the number
                "categoria_de_risco": data["Risk"].get("Category", None),
                "risco_absoluto": data["Risk"].get("SCORE2", None),
                "fatores_de_risco": data.get("Risk Factors", {}),
                "confianca": data['Risk'].get("Confidence Level", None)
            }
            rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(rows)
    return df
