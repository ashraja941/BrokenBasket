import os
from dotenv import load_dotenv
from uuid import uuid4
import pickle as pkl
import cassio


from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Cassandra

print("SERVER : Loading environment variables...")
# Load environment variables from .env file
load_dotenv()

unique_id = uuid4().hex[0:8]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"Tracing Walkthrough - {unique_id}"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv('LANGCHAIN_API_KEY') # Update to your API key
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv('HUGGINGFACEHUB_API_TOKEN')
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY') # Update to your API key if using OpenAI
os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')
# groq_api_key = os.getenv('GROQ_API_KEY')

ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_ID = os.getenv("ASTRA_DB_ID")

print("SERVER : Loading preprocessed dataset...")
# ingredients_db = pkl.load(open('Dataset/preprocessed_data_with_embeddings.pkl', 'rb'))
ingredients_db = pkl.load(open('D:\TAMU\SEM 4\CNM\gen-ui-python\Dataset\calories_embedded.pkl', 'rb'))


print("SERVER : Initializing vectorized Database...")
cassio.init(
    token = ASTRA_DB_APPLICATION_TOKEN,
    database_id = ASTRA_DB_ID
)

embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")
astra_vector_store = Cassandra(embedding=embeddings,
                               table_name = "CNM_test_table",
                               session=None,
                               keyspace=None)

recipe_retriever = astra_vector_store.as_retriever(    
                                                search_type="similarity_score_threshold",
                                                search_kwargs={"k": 7, "score_threshold": 0.6},
                                                )   

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

print("SERVER : Initializing LLMs...")

llm=ChatGroq(groq_api_key=os.environ["GROQ_API_KEY"],model_name='Llama-3.3-70b-Versatile')
# llm = ChatOpenAI(model = "gpt-4o-mini")
