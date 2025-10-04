from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai

from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    intent: str

def classify_intent(state: State):
    """
    Classifies the user's intent as 'query' or 'greeting'.
    """
    # tracing
    print(f"classify_intent: {state}")

    latest_message = state['messages'][-1].content.lower()
    if any(keyword in latest_message for keyword in ['hello', 'hi', 'hey']):
        return {"intent": "greeting"}
    else:
        return {"intent": "query"}


from langchain_core.messages import AIMessage

def generate_response(state: State):
    """
    Generates a final response based on the intent.
    """
    # tracing
    print(f"generate_response: {state}")

    if state['intent'] == 'greeting':
        response = "Hello there! How can I help you today?"
    else:
        response = "I need more information to answer that. Could you please elaborate?"
    return {"messages": [AIMessage(content=response)]}

from langgraph.graph import StateGraph, START, END

# Create the graph builder
graph_builder = StateGraph(State)

# Add the two nodes
graph_builder.add_node("classify_intent", classify_intent)
graph_builder.add_node("generate_response", generate_response)

# Set the entry point to the classification node
graph_builder.set_entry_point("classify_intent")

# Add a normal edge from classification to response generation
graph_builder.add_edge("classify_intent", "generate_response")

# The graph finishes after the response is generated
graph_builder.set_finish_point("generate_response")

# Compile the graph
graph = graph_builder.compile()


server = FastAPI()

# CORS setup
origins = [
    "http://localhost:3000",  # for using React/Vue frontend locally
]

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or origins to allow only some origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    text: str

@server.post("/")
def root(data: Question):
    
    # expeeriment with langgraph
#    print(graph.invoke({"messages": [HumanMessage(content=data.text)]}))
#    return {"text": "Have a nice day"}
#    return {"text": graph.invoke({"messages": [HumanMessage(content=data.text)]})['messages'][-1].content}
    
    # call OpenAI
    client = openai.OpenAI(
        api_key=api_key,
        base_url="http://172.30.32.241:8000/v1"
        )

    messages = [
        {"role": "system", "content": "Jesteś pomocnym asystentem"},
        {"role": "user", "content": data.text}
    ]

    # Call the API to get a completion.
    try:
        response = client.chat.completions.create(
            model="speakleash/Bielik-4.5B-v3.0-Instruct",
            messages=messages
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"text": "Error occurred while processing the request."}

    return {"text": response.choices[0].message.content}
