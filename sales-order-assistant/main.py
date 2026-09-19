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
# 3. Tool 1 - Get Sales Order Status
# ============================================================

def get_sales_order_status(order_id: str) -> dict:

    order = sales_orders.get(order_id)

    if order is None:
        return {
            "error": f"Sales order {order_id} was not found."
        }

    return {
        "order_id": order_id,
        "status": order["status"]
    }


# ============================================================
# 4. Tool 2 - Get Sales Order Total
# ============================================================

def get_sales_order_total(order_id: str) -> dict:

    order = sales_orders.get(order_id)

    if order is None:
        return {
            "error": f"Sales order {order_id} was not found."
        }

    return {
        "order_id": order_id,
        "total_amount": order["total_amount"]
    }


# ============================================================
# 5. Tool 3 - Get Customer Sales Orders
# ============================================================

def get_customer_sales_orders(customer_name: str) -> dict:

    results = []

    for order_id, order in sales_orders.items():

        if order["customer"].lower() == customer_name.lower():

            results.append({
                "order_id": order_id,
                "status": order["status"],
                "total_amount": order["total_amount"]
            })

    if not results:
        return {
            "error": f"No sales orders found for {customer_name}."
        }

    return {
        "customer": customer_name,
        "orders": results
    }


# ============================================================
# 6. Gemini Client
# ============================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ============================================================
# 7. Define Multiple Tools
# ============================================================

sales_order_tools = types.Tool(
    function_declarations=[

        types.FunctionDeclaration(
            name="get_sales_order_status",
            description="Get the current status of a sales order.",
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
        ),

        types.FunctionDeclaration(
            name="get_sales_order_total",
            description="Get the total amount of a sales order.",
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
        ),

        types.FunctionDeclaration(
            name="get_customer_sales_orders",
            description="Get all sales orders belonging to a customer.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "customer_name": types.Schema(
                        type="STRING",
                        description="Customer name, for example Rahul Enterprises"
                    )
                },
                required=["customer_name"]
            )
        )
    ]
)


# ============================================================
# 8. Model Configuration
# ============================================================

config = types.GenerateContentConfig(
    tools=[sales_order_tools]
)


# ============================================================
# 9. Get User Question
# ============================================================

user_question = input("Enter your question: ")


# ============================================================
# 10. First Gemini Call
# ============================================================

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=user_question,
    config=config
)


# ============================================================
# 11. Process Tool Call
# ============================================================

for part in response.candidates[0].content.parts:

    if part.function_call:

        function_call = part.function_call

        print("\nGemini requested a tool:")
        print("Tool:", function_call.name)
        print("Arguments:", function_call.args)

        # ----------------------------------------------------
        # Execute the selected tool
        # ----------------------------------------------------

        if function_call.name == "get_sales_order_status":

            result = get_sales_order_status(
                function_call.args["order_id"]
            )

        elif function_call.name == "get_sales_order_total":

            result = get_sales_order_total(
                function_call.args["order_id"]
            )

        elif function_call.name == "get_customer_sales_orders":

            result = get_customer_sales_orders(
                function_call.args["customer_name"]
            )

        else:

            result = {
                "error": f"Unknown tool: {function_call.name}"
            }


        # ----------------------------------------------------
        # Display tool result
        # ----------------------------------------------------

        print("\nTool result:")
        print(result)


        # ----------------------------------------------------
        # Send tool result back to Gemini
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # Final Answer
        # ----------------------------------------------------

        print("\nFinal answer:")
        print(final_response.text)