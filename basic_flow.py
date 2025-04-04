#!/usr/bin/env python
# coding: utf-8

# # Handle imports

# In[1]:


from dotenv import load_dotenv
import os
import cassio
from uuid import uuid4
import numpy as np
import pandas as pd
import json
import pandas as pd
from pprint import pformat

from typing import Literal,List,Annotated

from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AnyMessage,trim_messages,AIMessage,HumanMessage,RemoveMessage
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from langchain_core.documents import Document


from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import add_messages

from typing_extensions import TypedDict

from transformers import BertTokenizer,BertModel
import pickle as pkl

from google import genai

load_dotenv()

# In[ ]:


unique_id = uuid4().hex[0:8]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"Tracing Walkthrough - {unique_id}"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv('LANGCHAIN_API_KEY') # Update to your API key
#os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv('HUGGINGFACEHUB_API_TOKEN')

# In[3]:


from langsmith import Client
client = Client()

# # Connect to the database

# In[4]:


# ingredients_db = pkl.load(open('Dataset/preprocessed_data_with_embeddings.pkl', 'rb'))
ingredients_db = pkl.load(open('Dataset/calories_embedded.pkl', 'rb'))

# In[5]:


ingredients_db.head()

# In[6]:


# connection of Astra DB
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_ID = os.getenv("ASTRA_DB_ID")

GEMINI_TOKEN = os.getenv("GEMINI_TOKEN")
client = genai.Client(api_key=GEMINI_TOKEN)

cassio.init(
    token = ASTRA_DB_APPLICATION_TOKEN,
    database_id = ASTRA_DB_ID
)

# In[7]:


from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")

# In[8]:


from langchain.vectorstores import Cassandra
astra_vector_store = Cassandra(embedding=embeddings,
                               table_name = "CNM_test_table",
                               session=None,
                               keyspace=None)

# In[9]:


recipe_retriever = astra_vector_store.as_retriever(    
                                                search_type="similarity_score_threshold",
                                                search_kwargs={"k": 2, "score_threshold": 0.8},
                                                )   
recipe_retriever.invoke("Give me a cookie recipe")

# # Langgraph

# ### Datamodel

# In[10]:


class GeneralRouteQuery(BaseModel):
    """ Route a user query to the most relavent datasource """
    datasource: Literal["food","general"] = Field(
        ...,
        description="Given a user question choose to route it to general chat or a food"
    )

class ToolRouteQuery(BaseModel):
    """ Route a user query to the most relavent datasource """
    datasource: Literal["meal_plan","recipe"] = Field(
        ...,
        description="Given a user question choose to route it to meal_plan or recipe"
    )

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        messages: recent message history
        preferences: uses' food preferences
        documents: list of documents
        calorie_goal: user's calorie goal
    """
    messages: Annotated[list[AnyMessage], add_messages]
    documents: List[str]
    preferences: str
    calorie_goal: int
    meal_plan: dict
    redo: str
    current_calories : int

# ### LLM links

# In[11]:


from langchain_groq import ChatGroq
# from google.colab import userdata
import os
groq_api_key = os.getenv('groq_api_key')
# print(groq_api_key)

# In[12]:


llm=ChatGroq(groq_api_key=groq_api_key,model_name='Llama-3.3-70b-Versatile')
chat_llm = ChatGroq(groq_api_key=groq_api_key,model_name='Llama-3.3-70b-Versatile')

structured_llm_general_router=llm.with_structured_output(GeneralRouteQuery)
structured_llm_tool_router=llm.with_structured_output(ToolRouteQuery)


# ### Prompts

# In[13]:


# General router Prompt
system = """You are an expert at routing a user question to a food or general.
The food can tools to take care of meal planning, recipe finding and creation.
Use the food for questions on these topics. Otherwise, use general."""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{messages}"),
    ]
)

general_router = route_prompt | structured_llm_general_router

# print(general_router.invoke({"messages": "what is stardew Valley"}))
# print(general_router.invoke({"messages": "How to make a sweet dessert"}))

# In[14]:


# tool router Prompt
system = """
You are an expert at routing a user message to a meal_plan or recipe.
the meal_plan has access to tools to generate a meal plan for your weight goals.
Use the meal_plan for questions on these topics. 
If the message has to do with finding or modifying a recipe, use recipe.
"""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{messages}"),
    ]
)

tool_router = route_prompt | structured_llm_tool_router

# print(tool_router.invoke({"messages": "how to make butter chicken"}))
# print(tool_router.invoke({"messages": "help me plan the food for the week"}))

# In[15]:


# General Chat Prompt
system = """You are a helpful health coach that answers questions to the best of your ability.
Here is the information you have about the user:
preferences: {preferences} 
calorie_goal: {calorie_goal}
meal_plan: {meal_plan}
"""
general_chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{messages}"),
    ]
)

general_chat = general_chat_prompt | chat_llm

# In[16]:


temp_docs = """
[Document(id='d61c2d48df544d9ab1ec4f56b13f4aaa', metadata={'language': 'en-US', 'source': 'https://www.loveandlemons.com/wprm_print/best-homemade-brownies', 'title': 'Best Homemade Brownies - Love and Lemons'}, page_content="Best Homemade Brownies - Love and Lemons     \nGo Back\nPrintRecipe ImageNotes–+\xa0servingsSmallerNormalLargerBest Homemade BrowniesPrep Time: 5 minutes minsCook Time: 45 minutes minsServes 16 browniesThe ultimate recipe for brownies! They're fudgy, moist, and super chocolaty, with perfect crispy edges. From Weeknight Baking by Michelle Lopez.Equipment8x8 Baking Dish (this is the one I use so they don't overcook)Cooking Spray (I love this avocado oil one from Chosen Foods)Parchment Paper (this makes it so much easier to remove the brownies from the pan)Ingredients1 1/2 cups granulated sugar*3/4 cup all-purpose flour2/3 cup cocoa powder, sifted if lumpy1/2 cup powdered sugar, sifted if lumpy1/2 cup dark chocolate chips3/4 teaspoons sea salt2 large eggs1/2 cup canola oil or extra-virgin olive oil**2 tablespoons water1/2 teaspoon vanillaInstructionsPreheat the oven to 325°F. Lightly spray an 8x8 baking dish (not a 9x9 dish or your brownies will overcook) with cooking spray and line it with parchment paper. Spray the parchment paper.In a medium bowl, combine the sugar, flour, cocoa powder, powdered sugar, chocolate chips, and salt.In a large bowl, whisk together the eggs, olive oil, water, and vanilla.Sprinkle the dry mix over the wet mix and stir until just combined.Pour the batter into the prepared pan (it'll be thick - that's ok) and use a spatula to smooth the top. Bake for 40 to 48 minutes, or until a toothpick comes out with only a few crumbs attached (note: it's better to pull the brownies out early than to leave them in too long). Cool completely before slicing.*** Store in an airtight container at room temperature for up to 3 days. These also freeze well!Notes*If you'd like to reduce the sugar, I've had success with 1 cup granulated sugar instead of 1 1/2 cups.\n**I like to use olive oil because it's what I keep on hand and I enjoy the pairing of olive oil with chocolate. Keep in mind that you will taste it here. For a more neutral flavor, use canola oil.\n***When these brownies come out of the oven, they'll be super gooey in the middle. Allow them to cool completely, about 2 hours, before you slice into them to give them a chance to set up. They'll continue to firm up the longer they're out of the oven. If you still prefer a firmer brownie, store them in the fridge.Find it online at https://www.loveandlemons.com/brownies-recipe/"),
 Document(id='0a5a899762784e62804702b8cc9a6b95', metadata={'description': "This easy cake recipe requires just 7 ingredients and tastes like you spent hours making it, even though it's out of the oven in under an hour.", 'language': 'en', 'source': 'https://www.allrecipes.com/recipe/17481/simple-white-cake/?print', 'title': 'Simple White Cake Recipe'}, page_content="Worth the effort\nVery light, very great. This is my second time trying this recipe and it turned out just as amazing as the first time. Very beginner friendly, today I added some nuts on top. \n\n \n05\nof 663\n\n\n\n\n\n\n\n\n\n\n\nPhoto by\xa0\nSayeh Majzoob\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n04/24/2024\nSince I was short of time, I swapped butter with high quality sun flower oil, and also reduced the sugar a tiny bit. I made it in less than 10 minutes and baked it for 40 mins. It turned out amazing, served with blueberry jam and some fresh strawberries. Since it is simple bake its taste will surely highly depend on the quality of the ingredients. Use tasty starting materials. I creamed the egg and sugar thourougly. \n\n \n06\nof 663\n\n\n\n\n\n\n\n\n\n\n\nPhoto by\xa0\nPerkyBao1282\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n04/13/2024\n\n\n\nEasy to follow\n\n\n\nWorth the effort\n\n\n\nCrowd-pleaser\nThis is the third time I'm making this recipe. I love it \n\n \n07\nof 663\n\n\n\n\n\n\n\n\n\n\n\nPhoto by\xa0\nEagerFlour9876\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n02/29/2024\n\n\n\nA keeper!\n\n\n\nCrowd-pleaser\n\n\n\nEasy to follow\n\n\n\nWorth the effort\nI LOVED this recipe. It was quick easy and it was just overall great. I loved the flavor and so did my family. The texture and consistency was perfect. We used it for the Leap Day Party cake. I will definitely make this again. \n\n \n08\nof 663\n\n\n\n\n\n\n\n\n\n\n\nPhoto by\xa0\ncatzrule1990\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n02/25/2024\n\n\n\nWorth the effort\n\n\n\nEasy to follow\n\n\n\nGreat flavors\n\n\n\nA keeper!\n\n\n\nCrowd-pleaser\n\n\n\nFamily favorite\nBeen trying to find a simple vanilla/white cake for a long time that didn't involve egg whites/whipping egg whites. This cake fits the bill! it has a wonderful flavor and texture. Not fragile, but not too dense. Stands up just fine with two layers. It is lovely with or without frosting! I decided to make a buttercream frosting with very subtle strawberry flavor and both the frosting and cake compliment each other very well. I would also imagine that this cake would be perfect to use for strawberry shortcake!Definitely a new keeper recipe for me! Dad and I love it very much. 10/10 \n\n \n09\nof 663\n\n\n\n\n\n\n\n\n\n\n\nPhoto by\xa0\nMintPulp1911\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n01/07/2024\nI made this cake for my family and they loved it so much. Would definitely recommend \n\n \n10\nof 663\n\n\n\n\n\n\n\n\n\n\n\nPhoto by\xa0\nGoldenParm7351\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n01/02/2024\nWas very delicious and fluffy. Totally recommend using this recipe. \n\n\n1\n\n\n2\n\n\n3\n\n\n4\n\n\n5\n\n\n\nNext\n\n\n\n\n\n\n \n\n\n\n\n\nYou’ll Also Love\n\n\n\n\n\n\n\n\n\n \n\n\n\n\n\n\n\n\nWedding Cake\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n161\n\nRatings\n\n\n \n\n\n\n\n\n\n\n\n\n\n \n\n\n\n\n\n\n\n\nEasy Birthday Cake\n\n \n\n\n\n\n\n\n\n\n\n\n \n\n\n\n\n\n\n\n\nCream Cake\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n177\n\nRatings\n\n\n \n\n\n\n\n\n\n\n\n\n\n \n\n\n\n\n\n\n\n\nSmash Cake\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n2\n\nRatings\n\n\n \n\n\n\n\n\n\n\n\n\n\n \n\n\n\n\n\n\n\n\nHeavenly White Cake\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n973\n\nRatings\n\n\n \n\n\n\n\n\n\n\n\n\n\n \n\n\n\n\n\n\n\n\nNany's White Cake\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n136\n\nRatings\n\n\n \n\n\n\n\n\n\n\n\n\n\n \n\n\n\n\n\n\n\n\nLori's White Cake\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n28\n\nRatings\n\n\n \n\n\n\n\n\n\n\n\n\n\n \n\n\n\n\n\n\n\n\nMock Angel Food Cake\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n55\n\nRatings"),
 Document(id='f221c87e5852447eaca5168f2e4349be', metadata={'description': 'These are THE BEST soft chocolate chip cookies! No chilling required. Just ultra thick, soft, classic chocolate chip cookies!', 'language': 'en-US', 'source': 'https://pinchofyum.com/the-best-soft-chocolate-chip-cookies/print/39213', 'title': 'The Best Soft Chocolate Chip Cookies Recipe - Pinch of Yum'}, page_content='Keywords: chocolate chip cookies, best chocolate chip cookies, soft chocolate chip cookies, easy cookie recipe, small batch cookies\n\n\n\n\n\nDid you make this recipe?\nTag\xa0@pinchofyum\xa0on Instagram so we can admire your masterpiece!\xa0🌟\n\n\n\n\n\n\nFind it online: https://pinchofyum.com/the-best-soft-chocolate-chip-cookies'),
 Document(id='3af43e5c1fe84cd6a2ed6f96cd82bb7b', metadata={'description': 'These are THE BEST soft chocolate chip cookies! No chilling required. Just ultra thick, soft, classic chocolate chip cookies!', 'language': 'en-US', 'source': 'https://pinchofyum.com/the-best-soft-chocolate-chip-cookies/print/39213', 'title': 'The Best Soft Chocolate Chip Cookies Recipe - Pinch of Yum'}, page_content='The Best Soft Chocolate Chip Cookies Recipe - Pinch of Yum\n\n\n\n\n\n\n\n\n\n\n\n\nThe Best Soft Chocolate Chip Cookies Recipe - Pinch of Yum\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nPrint\nclock clock iconcutlery cutlery iconflag flag iconfolder folder iconinstagram instagram iconpinterest pinterest iconfacebook facebook iconprint print iconsquares squares iconheart heart iconheart solid heart solid icon\n\n\n \nThe Best Soft Chocolate Chip Cookies\n\n\n                                                 \t\t\t\t5 Stars\t\t\t        \t\t\t\t4 Stars\t\t\t        \t\t\t\t3 Stars\t\t\t        \t\t\t\t2 Stars\t\t\t        \t\t\t\t1 Star\t\t\t  \n4.5 from 1863 reviews\n\n\n\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\tAuthor: Pinch of Yum \n\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tTotal Time: 20 minutes \n\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tYield: 12 cookies 1x \n\n\n\n\n\nDescription\n\nThese are THE BEST soft chocolate chip cookies! No chilling required. Just ultra thick, soft, classic chocolate chip cookies!\n\n\n\n\n\n\nIngredients\n\n\n\nUnits\nUSM \n\nScale\n1/2x1x2x \n\n\n\n\n8 tablespoons of salted butter\n1/2 cup white sugar (I like to use raw cane sugar with a coarser texture)\n1/4 cup packed light brown sugar\n1 teaspoon vanilla\n1 egg\n1 1/2 cups all purpose flour (6.75 ounces)\n1/2 teaspoon baking soda\n1/4 teaspoon salt (but I always add a little extra)\n3/4 cup chocolate chips (I use a combination of chocolate chips and chocolate chunks)\n\n \n\n\n\n\n\n\n\nCook Mode\n\n\t\t\t\tPrevent your screen from going dark\t\t\t\n\n\n\n\n\n\n\nInstructions\n\n\n\nPreheat the oven to 350 degrees. Microwave the butter for about 40 seconds to just barely melt it. It shouldn’t be hot – but it should be almost entirely in liquid form.\nUsing a stand mixer or electric beaters, beat the butter with the sugars until creamy. Add the vanilla and the egg; beat on low speed until just incorporated – 10-15 seconds or so (if you beat the egg for too long, the cookies will be stiff).\nAdd the flour, baking soda, and salt. Mix until crumbles form. Use your hands to press the crumbles together into a dough. It should form one large ball that is easy to handle (right at the stage between “wet” dough and “dry” dough). Add the chocolate chips and incorporate with your hands.\nRoll the dough into 12 large balls (or 9 for HUGELY awesome cookies) and place on a cookie sheet. Bake for 9-11 minutes until the cookies look puffy and dry and just barely golden. Warning, friends: DO NOT OVERBAKE. This advice is probably written on every cookie recipe everywhere, but this is essential for keeping the cookies soft. Take them out even if they look like they’re not done yet (see picture in the post). They’ll be pale and puffy.\nLet them cool on the pan for a good 30 minutes or so (I mean, okay, eat four or five but then let the rest of them cool). They will sink down and turn into these dense, buttery, soft cookies that are the best in all the land. These should stay soft for many days if kept in an airtight container. I also like to freeze them.\n\n\n\n\nEquipment\n\nSpatula\nBuy Now → \n\nNonstick Sheet Pan\nBuy Now → \n\nMixing Bowl\nBuy Now → \nThe equipment section may contain affiliate links to products we know and love. \n\n\nPrep Time: 10 minsCook Time: 10 minsCategory: DessertMethod: BakeCuisine: American')]
"""

# In[17]:


system = """" 
You are an expert at generating a meal plan based on a user's input such as calorie goal and food preferences.
The user's preferences are : {preferences}
The user's calorie goal for the day : {calorie_goal}

You are to take reference from the documents provided below : {documents}

You are to generate a meal plan for a day include 3 meals. The meal plan should be a JSON in the following format:

"butter chicken" : [[500,"chicken"],[100, "spices"],[50, "onion"]],
"coffee" : [[10,"coffee"],[20,"milk"]],
...

Please write 3 recipes only. For each recipe for the key write the name of the dish The contents of each recipe should be the list of ingredients used to make the recipe and the quantity.
It does not matter for breakfast, lunch and dinner, just output 3 meals pertaining to the calorie goals from the documents provided.

where the key is the name of the meal and the value is a list of lists where each list is of the form [quantity,ingredient].
Quantity should ONLY BE in grams

Return the meal plan as a JSON, DO NOT return any other text.
Make it so that the output is in 1 line.
DO not write any text before or after the brackets
"""

generate_meal_plan_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        # ("human", "{messages}"),
    ]
)

generate_meal_plan = generate_meal_plan_prompt | llm | JsonOutputParser()

#temp_mp = generate_meal_plan.invoke({"preferences": "I like spicy food", "calorie_goal": 2000, "documents": temp_docs})

#print(temp_mp)

# print(output_json)

# In[18]:


system = """" 
You are an expert at generating a recipe based on a user's input such as calorie goal and food preferences.
The user's preferences are : {preferences}
Use the information from the following documents to generate the recipe: {documents}
"""
generate_recipe_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{messages}"),
    ]
)

generate_recipe = generate_recipe_prompt | llm

# ### Helper functions

# In[19]:


def cosine(a,b):
    a = a.reshape(-1)  # Reshape to (768,)
    b = b.reshape(-1)
    # if a == 0 or b == 0:
    #     return 0
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

# In[20]:


# Load pre-trained BERT model and tokenizer
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

# Function to get BERT embeddings
def get_bert_embeddings(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=50)
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state[:, 0, :].detach().numpy()
    return embeddings

# ### nodes

# In[21]:


def trim(state):
    # response = trim_messages(
    #     state["messages"],
    #     strategy="last",
    #     token_counter=len, # each message will be counted as 1 token
    #     max_tokens=1,
    #     start_on="human",
    #     end_on=("human", "tool"),
    #     include_system=True,
    # )
    if len(state['messages']) > 2:
        delete_messages = [RemoveMessage(id=m.id) for m in state['messages'][:-2]]
        return {"messages": delete_messages}
    else:
        return {"messages": state['messages']}

# In[22]:


def general_chat_bot(state):
    response = general_chat.invoke({"messages": state["messages"], "preferences": state["preferences"], "calorie_goal": state["calorie_goal"], "meal_plan": state["meal_plan"]})
    # response = chat_llm.invoke(state["messages"])
    return {"messages": response}

# In[23]:


def retrieve_recipes(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    print("retrieved using the prompt: ",state["messages"][-1].content)
    
    response = recipe_retriever.invoke(state["messages"][-1].content)
    # print("retrieved: ",response)
    return {"documents": response}

# In[24]:


def recipe_generator(state):
    
    """
    Generate a recipe

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---GENERATE RECIPE---")

    response = generate_recipe.invoke({"messages": state["messages"], "preferences": state["preferences"], "documents": state["documents"]})
    return {"messages": response}

# In[25]:


def general_route(state):
    """
    Route question to general or food.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION (GENERAL)---")
    message = state["messages"][-1].content
    # print("message: ",message)
    
    source = general_router.invoke({"messages": message})
    # print("source: ",source.datasource)
    if source.datasource == "general":
        print("---ROUTE QUESTION TO GENERAL CHAT---")
        return "general_chat_route"
    elif source.datasource == "food":
        print("---ROUTE QUESTION TO FOOD---")
        return "food_route"
    else:
        raise ValueError(f"Unknown datasource: {source.datasource}")

# In[26]:


def tool_route(state):
    """
    Route question to general or food.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION (TOOLS)---")
    message = state["messages"][-1].content
    # print("message: ",message)
    
    source = tool_router.invoke({"messages": message})
    # print("source: ",source.datasource)
    if source.datasource == "meal_plan":
        print("---ROUTE QUESTION TO MEAL PLAN---")
        return "meal_plan_route"
    elif source.datasource == "recipe":
        print("---ROUTE QUESTION TO RECIPE---")
        return "recipe_route"
    else:
        raise ValueError(f"Unknown datasource: {source.datasource}")

# In[27]:


def meal_plan_retriever(state):
    """"
    Create a meal plan
    Args:
        state (dict): The current graph state

    Returns:
        state (dict): The current graph state with the meal plan added
    
    """
    print("---MEAL PLANNER RETRIEVER---")
    documents = recipe_retriever.invoke(state["preferences"])
    return ({"documents": documents})

# In[28]:


def meal_plan_generator(state):
    """"
    Create a meal plan
    Args:
        state (dict): The current graph state

    Returns:
        state (dict): The current graph state with the meal plan added
    
    """
    print("---MEAL PLANNER GENERATOR---")  
    for i in range(5):
        try: 
            meal_plan = generate_meal_plan.invoke({"preferences": state["preferences"], "calorie_goal": state["calorie_goal"], "documents": state["documents"]})
        except:
            print("---MEAL PLANNER GENERATOR FAILED---")
            print("TRY AGAIN")
            if i == 4:
                print("---FAILED TOO MANY DAMN TIMES---")

    return ({"meal_plan": meal_plan})

# In[29]:


def general(state):
    print("reached general state")
    return state

def food(state):
    print("reached food state")
    return state

# In[30]:


def meal_plan_checker(state):
    print("---CREATE MEAL PLAN---")
    meal_plan = state['meal_plan']
    current_calories = 0
    calorie_goal = state['calorie_goal']

    for dish in meal_plan:
        for grams, ingredient in meal_plan[dish]:
            # vectorize ingredient
            # print(ingredient)
            encoded_input = get_bert_embeddings(ingredient)
            # compare to db
            most_similar = (0,"")
            for index,item in enumerate(ingredients_db['embedding']):
                if cosine(item,encoded_input) > most_similar[0]:
                    most_similar = (cosine(item,encoded_input),index)

            # calculate calories
            cal = ingredients_db['Cals_per100grams'][most_similar[1]][:-4]
            current_calories += grams * (int(cal)/100)

    print("current Calories calcluated : ",current_calories)
    if current_calories > calorie_goal:
        return {"redo": True}
    else:
        return {"redo": False, "current_calories": current_calories}


# In[31]:


def redo_meal_plan(state):
    redo = state['redo']
    if redo:
        return "redo_meal_plan"
    else:
        return "continue"

# In[32]:


def display_meal_plan(state):
    print("---DISPLAY MEAL PLAN---")
    print("meal plan: ",state['meal_plan'])
    print("current calories: ",state['current_calories'])
    return state

# In[33]:


def create_user(state):
    preferences = "I like spicy food"
    calorie_goal = 2000
    return {"preferences":preferences, "calorie_goal":30000}

# ### Graph creation

# In[34]:


workflow = StateGraph(GraphState)

workflow.add_node("create_user",create_user)
workflow.add_node("trim", trim)
workflow.add_node("general_router", general)
workflow.add_node("general_chat_bot", general_chat_bot)
workflow.add_node("tool_router", food)
workflow.add_node("retrieve_recipes", retrieve_recipes)
workflow.add_node("meal_plan_retriever", meal_plan_retriever)
workflow.add_node("generate_meal_plan", meal_plan_generator)
workflow.add_node("check_meal_plan", meal_plan_checker)
# workflow.add_node("redo_meal_plan_router", redo_meal_plan)
workflow.add_node("display_meal_plan", display_meal_plan)
workflow.add_node("generate_recipe", recipe_generator)

# workflow.add_edge(START, "trim")
workflow.add_edge(START,"create_user")
workflow.add_edge("create_user","trim")
workflow.add_edge("trim", "general_router")
workflow.add_conditional_edges(
    "general_router",
    general_route,
    {
        "general_chat_route": "general_chat_bot",
        "food_route": "tool_router",
    },
)
workflow.add_conditional_edges(
    "tool_router",
    tool_route,
    {
        "meal_plan_route": "meal_plan_retriever",
        "recipe_route": "retrieve_recipes",
    },
)
workflow.add_edge("meal_plan_retriever", "generate_meal_plan")
workflow.add_edge("generate_meal_plan", "check_meal_plan")

workflow.add_conditional_edges(
    "check_meal_plan",
    redo_meal_plan,
    {
        "redo_meal_plan": "generate_meal_plan",
        "continue": "display_meal_plan",
    },
)
workflow.add_edge("display_meal_plan", END)
workflow.add_edge("general_chat_bot", END)
workflow.add_edge("retrieve_recipes", "generate_recipe")
workflow.add_edge("generate_recipe", END)
# workflow.add_edge("meal_plan", END)

memory = MemorySaver()
app = workflow.compile(checkpointer = memory)

# In[35]:


from IPython.display import Image, display

try:
    display(Image(app.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    print("ERROR :(")
    pass

# ### Chat and testing

# In[36]:


config = {"configurable": {"thread_id": "1"}}

# In[37]:


#input_message = [HumanMessage(content="What rank is Tri the Tree")]
#output = app.invoke({"messages":input_message},config=config)
#output["messages"][-1].pretty_print()

# In[ ]:


# input_message = [HumanMessage(content="How to make butter chicken"),
#                  HumanMessage(content="Help me createa meal plan for the week"),
#                  HumanMessage(content="What is the capital of France")]

# input_message = [HumanMessage(content="Help me createa meal plan for the week")]

# for input_m in input_message:
#    output = app.invoke({"messages":input_m},config=config)
#    output["messages"][-1].pretty_print()

# In[ ]:



