from business_query import (
    get_order_summary,
    get_top_customers,
    get_missing_amount_count,
    get_order_count_by_status
)


def answer_question(question):
    question = question.lower().strip()

    # 1. Individual order status
    status_keywords = {
        "completed": "completed",
        "cancelled": "cancelled",
        "canceled": "cancelled",
        "pending": "pending"
    }

    asks_for_specific_status = any(
        phrase in question
        for phrase in [
            "how many",
            "count",
            "number of",
            "show me",
            "show",
            "total"
        ]
    )

    if asks_for_specific_status:
        for keyword, status in status_keywords.items():
            if keyword in question:
                result = get_order_count_by_status(status)
                count = result["rows"][0][0]

                print(f"\n{status.capitalize()} orders: {count}")
                return

    # 2. Order status summary
    if (
        "order status" in question
        or "orders by status" in question
        or "status summary" in question
        or "all order statuses" in question
    ):
        result = get_order_summary()

        print("\n========== ORDER STATUS SUMMARY ==========")

        total_orders = 0

        for row in result["rows"]:
            status = row[0]
            count = row[1]

            print(f"{status.capitalize()}: {count} orders")
            total_orders += count

        print(f"Total orders: {total_orders}")

    # 3. Top customers
    elif (
        "top customer" in question
        or "most orders" in question
        or "highest number of orders" in question
        or "customers with the most" in question
    ):
        result = get_top_customers(5)

        print("\n========== TOP 5 CUSTOMERS ==========")

        for rank, row in enumerate(result["rows"], start=1):
            print(f"{rank}. Customer {row[0]}: {row[1]} orders")

    # 4. Missing order amounts
    elif (
        "missing amount" in question
        or "missing amounts" in question
        or "amounts missing" in question
    ):
        result = get_missing_amount_count()
        count = result["rows"][0][0]

        print("\n========== MISSING ORDER AMOUNTS ==========")
        print(f"Orders with missing amounts: {count}")

    # 5. Help
    elif question in ["help", "what can you do", "help me"]:
        print("\n========== AVAILABLE QUESTIONS ==========")

        print("1. Show me the order status")
        print("2. How many completed orders?")
        print("3. How many cancelled orders?")
        print("4. How many pending orders?")
        print("5. Who are the top customers?")
        print("6. How many orders have missing amounts?")
        print("7. Type 'exit' to stop")

    # 6. Unknown question
    else:
        print("\nSorry, I cannot answer that question yet.")
        print("Type 'help' to see available questions.")


def main():
    print("=" * 50)
    print("          INSTAMART COPILOT")
    print("          BUSINESS ASSISTANT")
    print("=" * 50)

    print("\nAsk questions about Instamart business data.")
    print("Type 'help' for available questions.")
    print("Type 'exit' to stop.")

    while True:
        try:
            question = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nInstamart Copilot stopped.")
            break

        if question.lower() == "exit":
            print("\nInstamart Copilot stopped.")
            break

        if not question:
            print("Please enter a question.")
            continue

        try:
            answer_question(question)
        except Exception as error:
            print("\nUnable to process your question.")
            print("Error:", error)


if __name__ == "__main__":
    main()