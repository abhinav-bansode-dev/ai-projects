import os
from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer
import numpy as np




load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

"""
def search_policy(question):

    with open("sales_order_policy.txt", "r") as file:
        policy = file.read()

    question_words = question.lower().split()

    relevant_lines = []

    for line in policy.splitlines():

        for word in question_words:

            if len(word) > 3 and word in line.lower():
                relevant_lines.append(line)
                break

    return "\n".join(relevant_lines)
"""
def load_policy_chunks():

    with open("sales_order_policy.txt", "r") as file:
        policy = file.read()

    chunks = [
        chunk.strip()
        for chunk in policy.split("\n\n")
        if chunk.strip()
    ]

    return chunks

question = input("Enter your question: ")

chunks = load_policy_chunks()

chunk_embeddings = embedding_model.encode(chunks, normalize_embeddings=True)
question_embedding = embedding_model.encode(question, normalize_embeddings=True)

similarities = np.dot(chunk_embeddings, question_embedding)

top_indices = np.argsort(similarities)[-2:][::-1]

result = "\n\n".join(chunks[i] for i in top_indices)

print("\nRetrieved information:")
print(result)

#Take retrived information and give it to Gemini so Gemini can formulate the answer.
# For true semantic RAG system

prompt = f"""
Answer the user's question using only the information provided below.

User question:
{question}

Retrieved information:
{result}
"""


response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)


print("\nFinal answer:")
print(response.text)