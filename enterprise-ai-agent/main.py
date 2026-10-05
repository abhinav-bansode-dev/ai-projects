import os
import logging
from dotenv import load_dotenv
from google import genai

load_dotenv()

logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

"""user_request = input("Ask something: ")"""

user_request = input("Ask something: ")

logging.info("User request received: %s", user_request)

blocked_terms = ["ignore previous instructions", "system prompt", "api key"]

if any(term in user_request.lower() for term in blocked_terms):
    logging.warning("Request blocked by security filter: %s", user_request)
    print("Request blocked for security reasons.")
    exit()

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=f"""
You are an enterprise sales assistant.

Answer the user's question clearly and concisely.

User question:
{user_request}
"""
)

evaluation_terms = ["30 days", "cancellation", "refund"]

if all(term in response.text.lower() for term in evaluation_terms):
    evaluation_result = "PASS"
else:
    evaluation_result = "FAIL"

logging.info("Evaluation result: %s", evaluation_result)

print(response.text)
print(f"\nEvaluation: {evaluation_result}")