#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"


EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    if len(maybe_dt) != 10:
        return None

    if maybe_dt[2] != "-" or maybe_dt[5] != "-":
        return None

    day_str = maybe_dt[:2]
    month_str = maybe_dt[3:5]
    year_str = maybe_dt[6:]

    if not day_str.isdigit() or not month_str.isdigit() or not year_str.isdigit():
        return None

    day = int(day_str)
    month = int(month_str)
    year = int(year_str)

    if year <= 0 or month < 1 or month > 12:
        return None

    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if is_leap_year(year):
        days_in_month[1] = 29

    if day < 1 or day > days_in_month[month - 1]:
        return None

    return day, month, year


def parse_amount(maybe_amount: str) -> float | None:
    normalized = maybe_amount.replace(",", ".")

    if normalized == "":
        return None

    number_part = normalized[1:] if normalized[0] in "+-" else normalized

    if number_part in {"", "."}:
        return None

    if number_part.count(".") > 1:
        return None

    if not any(char.isdigit() for char in number_part):
        return None

    for char in number_part:
        if not char.isdigit() and char != ".":
            return None

    return float(normalized)


def date_to_sort_key(date_value: tuple[int, int, int] | None) -> tuple[int, int, int]:
    if date_value is None:
        return 0, 0, 0

    day, month, year = date_value
    return year, month, day


def is_same_month(
    transaction_date: tuple[int, int, int] | None,
    report_date: tuple[int, int, int],
) -> bool:
    if transaction_date is None:
        return False

    _, transaction_month, transaction_year = transaction_date
    _, report_month, report_year = report_date

    return transaction_month == report_month and transaction_year == report_year


def is_date_not_later(
    transaction_date: tuple[int, int, int] | None,
    report_date: tuple[int, int, int],
) -> bool:
    return date_to_sort_key(transaction_date) <= date_to_sort_key(report_date)


def get_all_cost_categories() -> list[str]:
    categories: list[str] = []

    for common_category, target_categories in EXPENSE_CATEGORIES.items():
        for target_category in target_categories:
            categories.append(f"{common_category}::{target_category}")

    return categories


def cost_categories_handler() -> str:
    return "\n".join(get_all_cost_categories())


def is_cost_category_exists(category_name: str) -> bool:
    parts = category_name.split("::")

    if len(parts) != 2:
        return False

    common_category = parts[0]
    target_category = parts[1]

    return common_category in EXPENSE_CATEGORIES and target_category in EXPENSE_CATEGORIES[common_category]


def get_target_category(category_name: str) -> str:
    return category_name.split("::")[1]


def format_category_for_report(category_name: str) -> str:
    target_category = get_target_category(category_name)
    result = ""

    for index, char in enumerate(target_category):
        if index > 0 and char.isupper() and target_category[index - 1].islower():
            result += " "

        result += char

    return result.lower().capitalize()


def format_detail_amount(amount: float) -> str:
    formatted = f"{amount:,.2f}"

    if formatted.endswith(".00"):
        return formatted[:-3]

    if formatted.endswith("0"):
        return formatted[:-1]

    return formatted


def income_handler(amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)

    financial_transactions_storage.append(
        {
            "type": "income",
            "amount": amount,
            "date": parsed_date,
        }
    )

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    if parsed_date is None:
        return INCORRECT_DATE_MSG

    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)

    financial_transactions_storage.append(
        {
            "type": "cost",
            "category": category_name,
            "amount": amount,
            "date": parsed_date,
        }
    )

    if not is_cost_category_exists(category_name):
        return f"{NOT_EXISTS_CATEGORY}\n{cost_categories_handler()}"

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    if parsed_date is None:
        return INCORRECT_DATE_MSG

    return OP_SUCCESS_MSG


def get_month_result(
    report_date: tuple[int, int, int],
) -> tuple[float, float, dict[str, float]]:
    income = 0.0
    expenses = 0.0
    details: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        if not is_same_month(transaction["date"], report_date):
            continue

        if transaction["type"] == "income":
            income += transaction["amount"]
        else:
            expenses += transaction["amount"]
            category = format_category_for_report(transaction["category"])
            details[category] = details.get(category, 0.0) + transaction["amount"]

    return income, expenses, details


def get_total_capital(report_date: tuple[int, int, int]) -> float:
    total = 0.0

    for transaction in financial_transactions_storage:
        if not is_date_not_later(transaction["date"], report_date):
            continue

        if transaction["type"] == "income":
            total += transaction["amount"]
        else:
            total -= transaction["amount"]

    return total


def stats_handler(report_date: str) -> str:
    parsed_date = extract_date(report_date)

    if parsed_date is None:
        return INCORRECT_DATE_MSG

    total_capital = get_total_capital(parsed_date)
    income, expenses, details = get_month_result(parsed_date)
    month_result = income - expenses

    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total_capital:.2f} rubles",
    ]

    if month_result >= 0:
        lines.append(f"This month, the profit amounted to {month_result:.2f} rubles.")
    else:
        lines.append(f"This month, the loss amounted to {-month_result:.2f} rubles.")

    lines.extend(
        [
            f"Income: {income:.2f} rubles",
            f"Expenses: {expenses:.2f} rubles",
            "",
            "Details (category: amount):",
        ]
    )

    for index, category in enumerate(sorted(details), start=1):
        lines.append(f"{index}. {category}: {format_detail_amount(details[category])}")

    return "\n".join(lines)


def handle_income_command(parts: list[str]) -> str:
    if len(parts) != 3:
        return UNKNOWN_COMMAND_MSG

    amount = parse_amount(parts[1])

    if amount is None:
        return UNKNOWN_COMMAND_MSG

    return income_handler(amount, parts[2])


def handle_cost_command(parts: list[str]) -> str:
    if len(parts) == 2 and parts[1] == "categories":
        return cost_categories_handler()

    if len(parts) != 4:
        return UNKNOWN_COMMAND_MSG

    amount = parse_amount(parts[2])

    if amount is None:
        return UNKNOWN_COMMAND_MSG

    return cost_handler(parts[1], amount, parts[3])


def handle_stats_command(parts: list[str]) -> str:
    if len(parts) != 2:
        return UNKNOWN_COMMAND_MSG

    return stats_handler(parts[1])


def handle_command(command: str) -> str:
    parts = command.split()

    if not parts:
        return UNKNOWN_COMMAND_MSG

    if parts[0] == "income":
        return handle_income_command(parts)

    if parts[0] == "cost":
        return handle_cost_command(parts)

    if parts[0] == "stats":
        return handle_stats_command(parts)

    return UNKNOWN_COMMAND_MSG


def main() -> None:
    with open(0) as stdin:
        for command in stdin:
            print(handle_command(command.strip()))


if __name__ == "__main__":
    main()
