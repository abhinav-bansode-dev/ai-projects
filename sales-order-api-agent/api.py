from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="Sales Order API",
    description="API for retrieving sales order information",
    version="1.0.0"
)


# Mock sales order data
sales_orders = {
    "SO-1001": {
        "order_id": "SO-1001",
        "customer": "Rahul Enterprises",
        "status": "Shipped",
        "total_amount": 125000
    },
    "SO-1002": {
        "order_id": "SO-1002",
        "customer": "ABC Retail",
        "status": "Processing",
        "total_amount": 85000
    },
    "SO-1003": {
        "order_id": "SO-1003",
        "customer": "XYZ Industries",
        "status": "Delivered",
        "total_amount": 210000
    }
}


@app.get("/sales-orders/{order_id}")
def get_sales_order(order_id: str):

    order = sales_orders.get(order_id)

    if order is None:
        raise HTTPException(
        status_code=404,
        detail=f"Sales order {order_id} was not found."
    )

    return order