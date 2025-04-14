import numpy as np
from transformers import BertTokenizer,BertModel

print("SERVER : Loading BERT Embedding model...")
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

def cosine(a,b):
    a = a.reshape(-1)  # Reshape to (768,)
    b = b.reshape(-1)
    # if a == 0 or b == 0:
    #     return 0
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))