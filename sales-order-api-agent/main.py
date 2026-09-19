import os
from urllib import response
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# 1. Load environment variables
# ============================================================

load_dotenv()


# ============================================================
# 2. Function that calls our FastAPI
# ============================================================

def get_sales_order_from_api(order_id: str) -> dict:

    url = f"http://127.0.0.1:8000/sales-orders/{order_id}"

    response = requests.get(url)

    if response.status_code == 404:
        return {
        "error": response.json()["detail"]
    }

    response.raise_for_status()

    return response.json()


# ============================================================
# 3. Gemini Client
# ============================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ============================================================
# 4. Define Tool for Gemini
# ============================================================

sales_order_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_sales_order",
            description="Get sales order details from the sales order API.",
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
# 5. Model Configuration
# ============================================================

config = types.GenerateContentConfig(
    tools=[sales_order_tool]
)


# ============================================================
# 6. Get User Question
# ============================================================

user_question = input("Enter your question: ")


# ============================================================
# 7. First Gemini Call
# ============================================================

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=user_question,
    config=config
)


# ============================================================
# 8. Process Gemini Tool Call
# ============================================================

for part in response.candidates[0].content.parts:

    if part.function_call:

        function_call = part.function_call

        print("\nGemini requested a tool:")
        print("Tool:", function_call.name)
        print("Arguments:", function_call.args)


        # ----------------------------------------------------
        # Call FastAPI
        # ----------------------------------------------------

        if function_call.name == "get_sales_order":

            result = get_sales_order_from_api(
                function_call.args["order_id"]
            )

        else:

            result = {
                "error": f"Unknown tool: {function_call.name}"
            }


        # ----------------------------------------------------
        # Display API result
        # ----------------------------------------------------

        print("\nFastAPI result:")
        print(result)


        # ----------------------------------------------------
        # Send API result back to Gemini
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
        '''print("\nDEBUG response:")
        print(final_response)'''
        print("\nFinal answer:")
        print(final_response.text)