import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# 1. Load environment variables
# ============================================================

load_dotenv()


# ============================================================
# 2. Mock Sales Order Data
# ============================================================

sales_orders = {
    "SO-1001": {
        "customer": "Rahul Enterprises",
        "status": "Shipped",
        "total_amount": 125000
    },
    "SO-1002": {
        "customer": "ABC Retail",
        "status": "Processing",
        "total_amount": 85000
    },
    "SO-1003": {
        "customer": "XYZ Industries",
        "status": "Delivered",
        "total_amount": 210000
    }
}


# ============================================================
# 3. Business Function / Tool
# ============================================================

def get_sales_order_status(order_id: str) -> dict:

    order = sales_orders.get(order_id)

    if order is None:
        return {
            "error": f"Sales order {order_id} was not found."
        }

    return {
        "order_id": order_id,
        "customer": order["customer"],
        "status": order["status"],
        "total_amount": order["total_amount"]
    }


# ============================================================
# 4. Gemini Client
# ============================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ============================================================
# 5. Define Tool for Gemini
# ============================================================

get_sales_order_status_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_sales_order_status",
            description="Get the current status and details of a sales order.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "order_id": types.Schema(
                        type="STRING",
                        description="Sales order ID, for example SO-1001"
                    )
                },
                required=["order_id"]
            )
        )
    ]
)


# ============================================================
# 6. Model Configuration
# ============================================================

config = types.GenerateContentConfig(
    tools=[get_sales_order_status_tool]
)


# ============================================================
# 7. User Question
# ============================================================

#user_question = "What is the status of sales order SO-1001?"  #FOR STATIC TESTING
user_question = input("Enter your question: ")


# ============================================================
# 8. First call to Gemini
# ============================================================

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=user_question,
    config=config
)


# ============================================================
# 9. Process Gemini's tool call
# ============================================================

for part in response.candidates[0].content.parts:

    if part.function_call:

        function_call = part.function_call

        print("Gemini requested a tool:")
        print("Tool:", function_call.name)
        print("Arguments:", function_call.args)

        # ----------------------------------------------------
        # Execute our Python function
        # ----------------------------------------------------

        if function_call.name == "get_sales_order_status":

            result = get_sales_order_status(
                function_call.args["order_id"]
            )

            print("\nTool result:")
            print(result)

            # ------------------------------------------------
            # 10. Send tool result back to Gemini
            # ------------------------------------------------

            tool_response = types.Part.from_function_response(
                name=function_call.name,
                response=result
            )

            final_response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(
                                text=user_question
                            )
                        ]
                    ),
                    response.candidates[0].content,
                    types.Content(
                        role="user",
                        parts=[tool_response]
                    )
                ],
                config=config
            )

            # ------------------------------------------------
            # 11. Print final answer
            # ------------------------------------------------

            print("\nFinal answer:")
            print(final_response.text)