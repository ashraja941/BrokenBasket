import streamlit as st
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser

from basic_flow import app, config
from pprint import pformat

# Streamlit app title
st.title("Meal Plan Recommender")

# Sidebar for user preferences
st.sidebar.header("User Preferences")

# Main input area
st.header("Chat with the Meal Plan Recommender")
user_input = st.text_input("Ask a question or request a workout plan:", "")

# Mock app.invoke for testing
def mock_invoke(input_data, config=None):
    # Simulate a response from the LLM
    return {
        "messages": [
            HumanMessage(content="This is a mock response for testing purposes.")
        ]
    }

# Replace app.invoke with the mock function for testing
# app.invoke = mock_invoke

# Button to send the query
if st.button("Submit"):
    if user_input:
        # Prepare input for the chatbot
        input_message = [HumanMessage(content=user_input)]
        
        try:
            # Invoke the chatbot logic
            response = ""
            for input_m in input_message:
                output = app.invoke({"messages": input_m}, config=config)  # Use the mock function for testing
                
                # Extract the chatbot's response
                #if (output["messages"][-1] != None) and (output["messages"][-1].content != NoneType):
                    #response += output["messages"][-1].content
                response += pformat(output["messages"][-1])  # Get the last message from the response

            # Display the response
            st.subheader("Response from Meal Plan Recommender")
            st.text(response)  # Display the string response in the Streamlit app
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query.")
