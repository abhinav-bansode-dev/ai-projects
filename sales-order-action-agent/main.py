import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
    },
    "SO-1003": {
        "customer": "ABC Traders",
        "status": "Delivered",
        "total": 95000
    }
}


def cancel_order(order_id):
    if order_id not in orders:
        return "Order not found."

    if orders[order_id]["status"] == "Cancelled":
        return "Order is already cancelled."

    orders[order_id]["status"] = "Cancelled"

    return f"Order {order_id} has been cancelled."

def get_human_approval(order_id):
    answer = input(f"Approve cancellation of {order_id}? (yes/no): ")

    return answer.lower() == "yes"

def get_order_status(order_id: str):
    if order_id not in orders:
        return "Order not found."

    order = orders[order_id]

    return (
        f"Order {order_id}: "
        f"Customer={order['customer']}, "
        f"Status={order['status']}, "
        f"Total=₹{order['total']}"
    )

def request_cancellation(order_id: str):
    return f"Cancellation requested for {order_id}. Human approval is required."

tools = [
    get_order_status,
    request_cancellation
]

"""order_id = "SO-1001"

if get_human_approval(order_id):
    print(cancel_order(order_id))
else:
    print("Cancellation rejected by user.")"""
"""
print(get_order_status("SO-1001"))
print(get_order_status("SO-9999"))"""

user_request = input("What would you like to do? ")

#print(user_request)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=user_request,
    config={
        "tools": tools
    }
)

#print(response.text)
if "cancel" in user_request.lower():
    order_id = user_request.split()[-1]

    print(get_order_status(order_id))

    if get_human_approval(order_id):
        print(cancel_order(order_id))
    else:
        print("Cancellation rejected by user.")
else:
    print(response.text)