from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph

from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from gen_ui_backend.langgraph.states import GraphState
from gen_ui_backend.langgraph.agents.nodes import save_to_db,create_user,trim,general,food,general_chat_bot,meal_plan_retriever,meal_plan_generator,meal_plan_checker,recipe_generator,retrieve_recipes,display_meal_plan,tool_route,general_route,redo_meal_plan

def create_graph() -> CompiledGraph:
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
    workflow.add_node("save_to_db", save_to_db)

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
    workflow.add_edge("display_meal_plan", "save_to_db")
    workflow.add_edge("save_to_db", END)
    workflow.add_edge("general_chat_bot", END)
    workflow.add_edge("retrieve_recipes", "generate_recipe")
    workflow.add_edge("generate_recipe", END)
    # workflow.add_edge("meal_plan", END)

    memory = MemorySaver()
    app = workflow.compile(checkpointer = memory)
    # app = workflow.compile()

    return app