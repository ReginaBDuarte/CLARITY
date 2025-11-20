import os
from openai import OpenAI
from google import genai
from google.genai import types
import json
import re
import pandas as pd
import ast
import numpy as np



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
        score = round(score_homens * 100, 1)  # Convert to percentage
    else:
        score = round(score_mulheres * 100 , 1) # Convert to percentage
    
    return score


print(score2(65, 'male', True, 140, 6.5, 1.2))
print(score2(48, 'female', False, 130, 5.8, 1.5))