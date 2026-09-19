
#business data
orders = {
    "101": {
        "customer": "Rahul",
        "status": "Shipped"
    },
    "102": {
        "customer": "Priya",
        "status": "Processing"
    },
    "103": {
        "customer": "Amit",
        "status": "Delivered"
    }
}


def get_order_status(order_id):
    return orders.get(order_id, "Order not found")

printOutput = get_order_status("101")
print(printOutput)