from langchain_core.messages import RemoveMessage
from gen_ui_backend.langgraph.agents.prompts import general_chat,tool_router,generate_meal_plan,generate_recipe,general_router,meal_plan_display
from gen_ui_backend.utils.config import llm,recipe_retriever,ingredients_db,mongodb_collection
from gen_ui_backend.utils.helpers import get_bert_embeddings,cosine
from pprint import pprint


def trim(state):
    """
    Remove all but the last 4 messages from the state.

    Args:
        state (dict): The current graph state
    
    Returns:
        state (dict): The current graph state with the messages trimmed
    """
    if len(state['messages']) > 4:
        delete_messages = [RemoveMessage(id=m.id) for m in state['messages'][:-4]]
        return {"messages": delete_messages}
    return {"messages": state['messages']}
    
def general_chat_bot(state):
    response = general_chat.invoke({"message": state["messages"], "preferences": state["preferences"], "calorie_goal": state["calorie_goal"], "meal_plan": state["meal_plan"]})
    # response = chat_llm.invoke(state["messages"])
    return {"messages": response}

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
    # response = [doc.page_content for doc in response]
    # print("retrieved: ",response)
    return {"documents": response}

def recipe_generator(state):
    """
    Generate a recipe

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---GENERATE RECIPE---")

    response = generate_recipe.invoke({"message": state["messages"], "preferences": state["preferences"], "documents": state["documents"]})
    return {"messages": response}

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
    
    source = general_router.invoke({"message": message})
    # print("source: ",source.datasource)
    if source.datasource == "general":
        print("---ROUTE QUESTION TO GENERAL CHAT---")
        return "general_chat_route"
    elif source.datasource == "food":
        print("---ROUTE QUESTION TO FOOD---")
        return "food_route"
    raise ValueError(f"Unknown datasource: {source.datasource}")
    
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
    
    source = tool_router.invoke({"message": message})
    # print("source: ",source.datasource)
    if source.datasource == "meal_plan":
        print("---ROUTE QUESTION TO MEAL PLAN---")
        return "meal_plan_route"
    elif source.datasource == "recipe":
        print("---ROUTE QUESTION TO RECIPE---")
        return "recipe_route"
    raise ValueError(f"Unknown datasource: {source.datasource}")
    
def meal_plan_retriever(state):
    """"
    Retrieve documents about the user's preferences
    Args:
        state (dict): The current graph state

    Returns:
        state (dict): The current graph state with the documents about the user's preferences added
    
    """
    print("---MEAL PLANNER RETRIEVER---")
    documents = recipe_retriever.invoke(state["preferences"])
    return ({"documents": documents})

def meal_plan_generator(state):
    """"
    Create a meal plan
    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Added meal plan to the state
    
    """
    redo = state["redo"]
    print("---MEAL PLANNER GENERATOR---")  
    if redo == False:
        meal_plan = generate_meal_plan.invoke({"preferences": state["preferences"], "calorie_goal": state["calorie_goal"], "documents": state["documents"],"message": state["messages"][-1].content})
    else:
        corrected_message = state["messages"][-1].content + " with low calories, make sure that there are at least 2 meals in a day"
        print(corrected_message)
        meal_plan = generate_meal_plan.invoke({"preferences": state["preferences"], "calorie_goal": state["calorie_goal"], "documents": state["documents"],"message": corrected_message})
    # print(meal_plan)
    # print(meal_plan.store)
    return ({"meal_plan": meal_plan})

def general(state):
    print("reached general state")
    return state

def food(state):
    print("reached food state")
    return state

def meal_plan_checker(state):
    """
    Check the calories in the meal plan
    Args:
        state (dict): The current graph state
    Returns:
        state (dict): The current graph state with redo and current_calories added
    """
    print("---CHECK MEAL PLAN---")
    meal_plan = state['meal_plan']
    current_calories = 0
    calorie_goal = state['calorie_goal'] * len(meal_plan)
    print("number of days in meal plan : ",len(meal_plan))

    for day in meal_plan:
        for dish in meal_plan[day]:
            for grams, ingredient in meal_plan[day][dish]:
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
                current_calories += int(grams) * (float(cal)/100)

    print("calorie goal for ",len(meal_plan)," days : ",calorie_goal)
    print("current Calories calcluated : ",current_calories)
    print("current Calories per day : ", current_calories/len(meal_plan))
    if current_calories > calorie_goal:
        if state["redo"]:
            print("Had issues with generating the meal plan")
            return {"redo": True,"meal_plan": meal_plan, "current_calories": current_calories}
        print("REDO ? : True")
        return {"redo": True}
    else:
        print("REDO ? : False")
        return {"redo": False, "current_calories": current_calories}

def redo_meal_plan(state):
    redo = state['redo']
    if redo:
        return "redo_meal_plan"
    else:
        return "continue"
    
def display_meal_plan(state):
    """
    Display the meal plan in a readable format to the user 

    Args: 
        state (dict): The current graph state

    Returns: 
        state (dict): New message summarizing the meal plan
    """
    print("---DISPLAY MEAL PLAN---")
    print("meal plan: ",state['meal_plan'])
    print("current calories: ",state['current_calories'])
    return_message = meal_plan_display.invoke({"meal_plan": state['meal_plan']})
    return {"messages" : return_message}

def create_user(state):
    """
    Reading through the database to populat the user information

    Args:
        state (dict): The current graph state
    Returns:
        state (dict): The current graph state with the user information added
    """
    found_user = mongodb_collection.find_one({"userId": "medhamajumdar1"})
    print(found_user)
    # print(mongodb_collection.find_one({"userId": "medhamajumdar1"}))
    
    preferences = "".join(found_user['preferences'])
    calorie_goal = found_user['profile']['calories']
    meal_plan = found_user['mealPlan']
    return {"preferences":preferences, "calorie_goal":calorie_goal,"redo": False,"meal_plan":meal_plan}

def save_to_db(state):
    """
    Update the database with new meal plan

    Args:
        state (dict): The current graph state
    Returns:
        state (dict): The current graph state 
    """
    print("---SAVED MEAL PLAN---")
    update_result = mongodb_collection.update_one(
        {"userId": "medhamajumdar1"},
        {"$set": {
            "profile.calories": state['calorie_goal'],
            "mealPlan": state['meal_plan']
        }}
    )
    print(f"\nModified {update_result.modified_count} document")

    return state