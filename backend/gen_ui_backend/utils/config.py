import os
from dotenv import load_dotenv
from uuid import uuid4
import pickle as pkl
from pymongo import MongoClient, errors
from pathlib import Path

from astrapy import DataAPIClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_astradb import AstraDBVectorStore

print("SERVER : Loading environment variables...")
load_dotenv()

unique_id = uuid4().hex[0:8]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"Tracing Walkthrough - {unique_id}"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv('LANGCHAIN_API_KEY')
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv('HUGGINGFACEHUB_API_TOKEN')
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')

# --- Astra (endpoint-based) ---
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")  
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")            
ASTRA_DB_KEYSPACE = os.getenv("ASTRA_DB_KEYSPACE", "default_keyspace") 

if not ASTRA_DB_APPLICATION_TOKEN or not ASTRA_DB_API_ENDPOINT:
    raise RuntimeError(
        "Missing Astra credentials. Set ASTRA_DB_APPLICATION_TOKEN and ASTRA_DB_API_ENDPOINT in your environment."
    )

client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
db = client.get_database(ASTRA_DB_API_ENDPOINT, keyspace=ASTRA_DB_KEYSPACE)

print("SERVER : Loading preprocessed dataset...")
# ingredients_db = pkl.load(open('Dataset/preprocessed_data_with_embeddings.pkl', 'rb'))
ingredients_db = pkl.load(open(Path("Dataset/calories_embedded.pkl")))

print("SERVER : Initializing vectorized Database (Data API)...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

astra_vector_store = AstraDBVectorStore(
    collection_name="BrokenBasket_DB",              
    embedding=embeddings,
    token=ASTRA_DB_APPLICATION_TOKEN,
    api_endpoint=ASTRA_DB_API_ENDPOINT,
    namespace=ASTRA_DB_KEYSPACE,                   
)

recipe_retriever = astra_vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 7, "score_threshold": 0.6},
)

print("SERVER : Connecting to MongoDB...")
try:
    mongodb_uri = os.environ.get('MONGODB_URI')
    if not mongodb_uri:
        raise ValueError("MONGODB_URI environment variable not set")

    client_mongo = MongoClient(mongodb_uri)
    db_mongo = client_mongo['test']
    mongodb_collection = db_mongo['preferences']

    print(mongodb_collection.find_one({"userId": "medhamajumdar1"}))  # sanity check

except errors.ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
# finally:
#     if 'client_mongo' in locals():
#         client_mongo.close()
#         print("MongoDB connection closed")

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

print("SERVER : Initializing LLMs...")
llm = ChatGroq(groq_api_key=os.environ["GROQ_API_KEY"], model_name='Llama-3.3-70b-Versatile')
# llm = ChatOpenAI(model="gpt-4o-mini")
