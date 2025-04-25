from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser

from gen_ui_backend.langgraph.states import GeneralRouteQuery,ToolRouteQuery,MealPlanState
from gen_ui_backend.utils.config import llm

# General router Prompt
system_general_route = """You are an expert at routing a user question to a food or general.
The food can tools to take care of meal planning, recipe finding and creation.
Use the food for questions on these topics. Otherwise, use general."""

general_route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_general_route),
        ("human", "{message}"),
    ]
)
structured_llm_general_router=llm.with_structured_output(GeneralRouteQuery)
general_router = general_route_prompt | structured_llm_general_router

# tool router Prompt
system_tool_route = """
You are an expert at routing a user message to a meal_plan or recipe.
the meal_plan has access to tools to generate a meal plan for your weight goals.
Use the meal_plan for questions on these topics. 
If the message has to do with finding or modifying a recipe, use recipe.
"""

tool_route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_tool_route),
        ("human", "{message}"),
    ]
)
structured_llm_tool_router=llm.with_structured_output(ToolRouteQuery)
tool_router = tool_route_prompt | structured_llm_tool_router

# General Chat Prompt
system_general_chat = """You are a helpful health coac called Broken Basket that answers questions to the best of your ability.
Here is the information you have about the user:
preferences: {preferences} 
calorie_goal: {calorie_goal}
meal_plan: {meal_plan}
"""
general_chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_general_chat),
        ("human", "{message}"),
    ]
)

general_chat = general_chat_prompt | llm

system_meal_plan = """
You are an expert at generating a HEALTHY meal plan based on the user's dietary preferences and calorie goals. 
Make sure to have at least 3 dishes per day (breakfast, lunch, dinner) in the meal plan. You can also add snacks if needed.
You can make changes to recipes to fit their calories such as reducing the amount of oil used.

Here is the user's request: {message}

The user's preferences are : {preferences}
The user's calorie goal for the day : {calorie_goal}

You are to take reference from the documents provided below : {documents}


Find the number of days that the user wants a meal plan for and generate a meal plan for exactly that many days. 

For example: 
if the user says that they want a meal plan for a week, then create a meal plan for 7 days. 
if the user says that they want a meal plan for today or tomorrow, then create a meal plan for 1 day. 
if the user says that they want a meal plan for 3 days, then create a meal plan for 3 days.


The meal plan should be a JSON in the following format : 

"0" : 
    "butter chicken" : [[5,"lemon juice"],[5,"salt"],[10,"Chilli powder"],[6,"garam masala"],[2,"kasuri methi"],[2,"tumeric"],[3,"cumin powder"],[4,"corrainder powder"],[20,"ginger garlic paste"],[35,"heavy cream"],[500,"chicken"]],
    "coffee" : [[10,"coffee"],[20,"milk"]],
    ...
,
...

Where the first key is the day in the form of a number (for example the first day is 0). The value should be a JSON where the key is the name of the dish and the value is a array of ingredients and the amount of it in grams.

where the key is the name of the meal and the value is a list of lists where each list is of the form [quantity,ingredient].
Quantity should ONLY BE in grams

Return the meal plan as a JSON, DO NOT return any other text.
Make it so that the output is in 1 line.
DO not write any text before or after the brackets

"""

generate_meal_plan_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_meal_plan),
        ("human", "{message}"),
    ]
)

generate_meal_plan = generate_meal_plan_prompt | llm | JsonOutputParser()

system_recipe_generation = """" 
You are an expert at generating a recipe based on a user's input such as calorie goal and food preferences.
The user's preferences are : {preferences}
Use the information from the following documents to generate the recipe: {documents}
"""
generate_recipe_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_recipe_generation),
        ("human", "{message}"),
    ]
)

generate_recipe = generate_recipe_prompt | llm

system_display_meal_plan = """
I will provide you with a meal plan in the form of a JSON of the format below:

"0" : 
    "butter chicken" : [[5,"lemon juice"],[5,"salt"],[10,"Chilli powder"],[6,"garam masala"],[2,"kasuri methi"],[2,"tumeric"],[3,"cumin powder"],[4,"corrainder powder"],[20,"ginger garlic paste"],[35,"heavy cream"],[500,"chicken"]],
    "coffee" : [[10,"coffee"],[20,"milk"]],
    ...
,
...

Where the first key is the day in the form of a number (for example the first day is 0). The value should be a JSON where the key is the name of the dish and the value is a array of ingredients and the amount of it in grams.

I want you to summarize the dishes and give 1 line about each dish in the meal plan.
Write it in a concise and easily readable manner. 
"""
display_meal_plan_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_display_meal_plan),
        ("human", "{meal_plan}"),
    ]
)

meal_plan_display = display_meal_plan_prompt | llm | StrOutputParser()