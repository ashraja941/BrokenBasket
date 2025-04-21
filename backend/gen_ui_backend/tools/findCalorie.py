import os
from typing import Dict, Union

import requests
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool

from gen_ui_backend.utils.helpers import get_bert_embeddings, cosine
import pickle as pkl

ingredients_db = pkl.load(open('..\Dataset\calories_embedded.pkl', 'rb'))


class FindCalorieInput(BaseModel):
    ingredient: str = Field(..., description="The name of the ingredient.")
    amount: int = Field(..., description="The amount of the ingredient.")


@tool("find-calorie", args_schema=FindCalorieInput, return_direct=False)
def find_calorie(ingredient: str, amount: int) -> Union[float, str]:
    """Get the Calories in a given amount of an ingredient.
    
    Args:
        ingredient (str): The name of the ingredient.
        amount (int): The amount of the ingredient in grams.
    """
    try:
        print("tool is called")
        encoded_input = get_bert_embeddings(ingredient)
        most_similar = (0, "")
        for index, item in enumerate(ingredients_db['embedding']):
            if cosine(item, encoded_input) > most_similar[0]:
                most_similar = (cosine(item, encoded_input), index)
        cal = ingredients_db['Cals_per100grams'][most_similar[1]][:-4]
        print("calories found : ", cal)
        return float(int(amount) * (float(cal) / 100))
    except:
        return "There was an error finding the calories for this ingredient"
