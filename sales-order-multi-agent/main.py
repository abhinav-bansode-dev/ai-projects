import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

"""def order_agent(request):
    return "Order Agent handling: " + request"""

orders = {
    "SO-1001": {
        "customer": "Rahul Enterprises",
        "status": "Shipped",
        "total": 125000
    },
    "SO-1002": {
        "customer": "Priya Enterprises",
        "status": "Processing",
        "total": 85000
    }
}


def order_agent(request):
    if "SO-1001" in request:
        order = orders["SO-1001"]
        return f"Order SO-1001: Customer={order['customer']}, Status={order['status']}, Total=₹{order['total']}"

    if "SO-1002" in request:
        order = orders["SO-1002"]
        return f"Order SO-1002: Customer={order['customer']}, Status={order['status']}, Total=₹{order['total']}"

    return "Order not found."


"""def policy_agent(request):
    return "Policy Agent handling: " + request"""

def policy_agent(request):
    if "refund" in request.lower():
        return "Refund requests can be made within 30 days after delivery. Refunds are processed within 5–7 business days."

    if "cancellation" in request.lower():
        return "Orders can be cancelled before shipment."

    return "Policy information not found."

def coordinator(request):
    if "status" in request.lower() or "order" in request.lower():
        return order_agent(request)

    if "refund" in request.lower() or "policy" in request.lower():
        return policy_agent(request)

    return "I don't know which agent should handle this request."


"""print(coordinator("What is the status of SO-1002?"))
print(coordinator("How long do I have to request a refund?"))"""

user_request = input("What would you like to know? ")

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=f"""
Your job is to route each user request to exactly one specialized agent.

Available agents:
- Order Agent: handles sales order status and order details.
- Policy Agent: handles refund and cancellation policies.

Rules:
- Choose Order Agent for questions about a specific sales order.
- Choose Policy Agent for questions about refunds, returns, or cancellation rules.
- Return only the exact agent name.

User request:

Available agents:
- Order Agent: handles sales order status and order details.
- Policy Agent: handles refund and cancellation policies.

User request:
{user_request}

Return only the agent name:
Order Agent
or
Policy Agent
"""
)

"""print(response.text)"""
agent = response.text.strip()

if agent == "Order Agent":
    print(order_agent(user_request))
elif agent == "Policy Agent":
    print(policy_agent(user_request))
else:
    print("No suitable agent found.")