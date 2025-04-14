from typing import Literal,List,Annotated,Union

from langchain_core.messages import AnyMessage,AIMessage, HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel
from langgraph.graph import add_messages


class ChatInputType(BaseModel):
    # messages: Annotated[list[AnyMessage], add_messages]
    messages: List[Union[HumanMessage, AIMessage, SystemMessage]]
    # messages: AnyMessage
