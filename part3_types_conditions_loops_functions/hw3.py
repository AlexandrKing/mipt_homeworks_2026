#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

DATE_FORMAT_LENGTH = 10
MONTHS_IN_YEAR = 12
CATEGORY_PARTS_COUNT = 2

INCOME_COMMAND_ARGS_COUNT = 3
COST_CATEGORIES_COMMAND_ARGS_COUNT = 2
COST_COMMAND_ARGS_COUNT = 4
STATS_COMMAND_ARGS_COUNT = 2

LEAP_YEAR_DIVISOR = 4
CENTURY_YEAR_DIVISOR = 100
FULL_LEAP_YEAR_DIVISOR = 400


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
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    return year % FULL_LEAP_YEAR_DIVISOR == 0 or (
        year % LEAP_YEAR_DIVISOR == 0 and year % CENTURY_YEAR_DIVISOR != 0
    )


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    if len(maybe_dt) != DATE_FORMAT_LENGTH:
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

    if year <= 0 or month < 1 or month > MONTHS_IN_YEAR:
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

    dots_count = 0
    digits_count = 0

    for char in number_part:
        if char == ".":
            dots_count += 1
            if dots_count > 1:
                return None
        elif char.isdigit():
            digits_count += 1
        else:
            return None

    if digits_count == 0:
        return None

    return float(normalized)


def date_to_sort_key(date_str: str) -> tuple[int, int, int]:
    parsed_date = extract_date(date_str)

    if parsed_date is None:
        return 0, 0, 0

    day, month, year = parsed_date
    return year, month, day


def is_date_not_later(date_str: str, report_date: str) -> bool:
    return date_to_sort_key(date_str) <= date_to_sort_key(report_date)


def is_same_month(date_str: str, report_date: str) -> bool:
    transaction_date = extract_date(date_str)
    report_dt = extract_date(report_date)

    if transaction_date is None or report_dt is None:
        return False

    _, transaction_month, transaction_year = transaction_date
    _, report_month, report_year = report_dt

    return transaction_month == report_month and transaction_year == report_year


def get_all_cost_categories() -> list[str]:
    categories = []

    for common_category, target_categories in EXPENSE_CATEGORIES.items():
        categories.extend(
            f"{common_category}::{target_category}"
            for target_category in target_categories
        )

    return sorted(categories)


def is_cost_category_exists(category_name: str) -> bool:
    parts = category_name.split("::")

    if len(parts) != CATEGORY_PARTS_COUNT:
        return False

    common_category = parts[0]
    target_category = parts[1]

    return (
        common_category in EXPENSE_CATEGORIES
        and target_category in EXPENSE_CATEGORIES[common_category]
    )


def get_target_category(category_name: str) -> str:
    return category_name.split("::")[1]


def format_category_for_report(category_name: str) -> str:
    target_category = get_target_category(category_name)
    result = target_category[0]

    for index in range(1, len(target_category)):
        current_char = target_category[index]
        previous_char = target_category[index - 1]

        if current_char.isupper() and previous_char.islower():
            result += " "

        result += current_char

    return result[0].upper() + result[1:].lower()


def format_detail_amount(amount: float) -> str:
    formatted = f"{amount:,.2f}"

    if formatted.endswith(".00"):
        return formatted[:-3]

    if formatted.endswith("0"):
        return formatted[:-1]

    return formatted


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    if extract_date(income_date) is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {
            "type": "income",
            "amount": amount,
            "date": income_date,
        }
    )

    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if not is_cost_category_exists(category_name):
        return f"{NOT_EXISTS_CATEGORY}\n{cost_categories_handler()}"

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    if extract_date(income_date) is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {
            "type": "cost",
            "category": category_name,
            "amount": amount,
            "date": income_date,
        }
    )

    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(get_all_cost_categories())


def stats_handler(report_date: str) -> str:
    if extract_date(report_date) is None:
        return INCORRECT_DATE_MSG

    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    expenses_by_category: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        if not is_date_not_later(transaction["date"], report_date):
            continue

        amount = transaction["amount"]

        if transaction["type"] == "income":
            total_capital += amount

            if is_same_month(transaction["date"], report_date):
                month_income += amount
        else:
            total_capital -= amount

            if is_same_month(transaction["date"], report_date):
                month_expenses += amount
                report_category = format_category_for_report(transaction["category"])

                if report_category not in expenses_by_category:
                    expenses_by_category[report_category] = 0.0

                expenses_by_category[report_category] += amount

    month_result = month_income - month_expenses

    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total_capital:.2f} rubles",
    ]

    if month_result >= 0:
        lines.append(f"This month, the profit amounted to {month_result:.2f} rubles.")
    else:
        lines.append(f"This month, the loss amounted to {-month_result:.2f} rubles.")

    lines += [
        f"Income: {month_income:.2f} rubles",
        f"Expenses: {month_expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    sorted_categories = sorted(
        expenses_by_category,
        key=lambda category: category.lower(),
    )

    for index, category in enumerate(sorted_categories, start=1):
        amount = expenses_by_category[category]
        lines.append(f"{index}. {category}: {format_detail_amount(amount)}")

    return "\n".join(lines)


def handle_income_command(parts: list[str]) -> str:
    if len(parts) != INCOME_COMMAND_ARGS_COUNT:
        return UNKNOWN_COMMAND_MSG

    amount = parse_amount(parts[1])

    if amount is None:
        return UNKNOWN_COMMAND_MSG

    return income_handler(amount, parts[2])


def handle_cost_command(parts: list[str]) -> str:
    if (
        len(parts) == COST_CATEGORIES_COMMAND_ARGS_COUNT
        and parts[1] == "categories"
    ):
        return cost_categories_handler()

    if len(parts) != COST_COMMAND_ARGS_COUNT:
        return UNKNOWN_COMMAND_MSG

    category_name = parts[1]
    amount = parse_amount(parts[2])

    if not is_cost_category_exists(category_name):
        return f"{NOT_EXISTS_CATEGORY}\n{cost_categories_handler()}"

    if amount is None:
        return UNKNOWN_COMMAND_MSG

    return cost_handler(category_name, amount, parts[3])


def handle_stats_command(parts: list[str]) -> str:
    if len(parts) != STATS_COMMAND_ARGS_COUNT:
        return UNKNOWN_COMMAND_MSG

    return stats_handler(parts[1])


def handle_command(command: str) -> str:
    parts = command.split()

    if len(parts) == 0:
        return UNKNOWN_COMMAND_MSG

    command_name = parts[0]

    if command_name == "income":
        return handle_income_command(parts)

    if command_name == "cost":
        return handle_cost_command(parts)

    if command_name == "stats":
        return handle_stats_command(parts)

    return UNKNOWN_COMMAND_MSG


def main() -> None:
    with open(0) as stdin:
        for command in stdin:
            print(handle_command(command.strip()))


if __name__ == "__main__":
    main()