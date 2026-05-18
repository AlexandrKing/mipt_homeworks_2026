#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

DATE_LEN = 10
FIRST_DASH_INDEX = 2
SECOND_DASH_INDEX = 5
DAY_END = 2
MONTH_START = 3
MONTH_END = 5
YEAR_START = 6
MONTHS_IN_YEAR = 12
FEBRUARY_INDEX = 1
LEAP_FEBRUARY_DAYS = 29

LEAP_YEAR_MULTIPLE = 4
CENTURY_MULTIPLE = 100
QUAD_CENTURY_MULTIPLE = 400

CMD_INCOME_LEN = 3
CMD_COST_LEN = 4
CMD_STATS_LEN = 2
CMD_CATEGORIES_LEN = 2
CATEGORY_PARTS_LEN = 2
MAX_AMOUNT_PARTS = 2

FIRST_POSITION = 0
FIRST_LIST_NUMBER = 1

DATE_LENGTH = 10
MONTHS_IN_YEAR = 12
CATEGORY_PARTS_COUNT = 2

INCOME_COMMAND_LENGTH = 3
COST_CATEGORIES_COMMAND_LENGTH = 2
COST_COMMAND_LENGTH = 4
STATS_COMMAND_LENGTH = 2

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

DAYS_IN_MONTH = (
    31,
    28,
    31,
    30,
    31,
    30,
    31,
    31,
    30,
    31,
    30,
    31,
)

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    is_quad_century = year % QUAD_CENTURY_MULTIPLE == 0
    is_simple_leap = year % LEAP_YEAR_MULTIPLE == 0
    is_century = year % CENTURY_MULTIPLE == 0
    return is_quad_century or (is_simple_leap and not is_century)


def has_valid_date_format(maybe_dt: str) -> bool:
    if len(maybe_dt) != DATE_LEN:
        return False

    has_dashes = maybe_dt[FIRST_DASH_INDEX] == "-" and maybe_dt[SECOND_DASH_INDEX] == "-"
    has_digits = (
        maybe_dt[:DAY_END].isdigit() and maybe_dt[MONTH_START:MONTH_END].isdigit() and maybe_dt[YEAR_START:].isdigit()
    )
    return has_dashes and has_digits


def get_days_in_month(month: int, year: int) -> int:
    days = list(DAYS_IN_MONTH)

    if is_leap_year(year):
        days[FEBRUARY_INDEX] = LEAP_FEBRUARY_DAYS

    return days[month - 1]


def has_valid_date_values(day: int, month: int, year: int) -> bool:
    if year < 1:
        return False

    if month < 1 or month > MONTHS_IN_YEAR:
        return False

    return 1 <= day <= get_days_in_month(month, year)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    if not has_valid_date_format(maybe_dt):
        return None

    day = int(maybe_dt[:DAY_END])
    month = int(maybe_dt[MONTH_START:MONTH_END])
    year = int(maybe_dt[YEAR_START:])

    if not has_valid_date_values(day, month, year):
        return None

    return day, month, year


def parse_amount(maybe_amount: str) -> float | None:
    normalized = maybe_amount.replace(",", ".")

    if not normalized:
        return None

    number_part = normalized[1:] if normalized.startswith(("+", "-")) else normalized
    amount_parts = number_part.split(".")

    if not number_part or len(amount_parts) > MAX_AMOUNT_PARTS:
        return None

    if not any(part.isdigit() for part in amount_parts):
        return None

    for part in amount_parts:
        if part and not part.isdigit():
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
        categories.extend(f"{common_category}::{target_category}" for target_category in target_categories)

    return categories


def cost_categories_handler() -> str:
    return "\n".join(get_all_cost_categories())


def is_cost_category_exists(category_name: str) -> bool:
    parts = category_name.split("::")

    if len(parts) != CATEGORY_PARTS_LEN:
        return False

    common_category = parts[0]
    target_category = parts[1]
    return common_category in EXPENSE_CATEGORIES and target_category in EXPENSE_CATEGORIES[common_category]


def get_target_category(category_name: str) -> str:
    return category_name.split("::")[1]


def need_space_before_char(category_name: str, index: int, char: str) -> bool:
    if index == FIRST_POSITION:
        return False

    previous_char = category_name[index - 1]
    return char.isupper() and previous_char.islower()


def format_category_for_report(category_name: str) -> str:
    target_category = get_target_category(category_name)
    result_chars: list[str] = []

    for index, char in enumerate(target_category):
        if need_space_before_char(target_category, index, char):
            result_chars.append(" ")

        result_chars.append(char)

    return "".join(result_chars).lower().capitalize()


def format_detail_amount(amount: float) -> str:
    formatted = f"{amount:,.2f}"

    if formatted.endswith(".00"):
        return formatted[:-3]

    if formatted.endswith("0"):
        return formatted[:-1]

    return formatted


def income_handler(amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)

    if amount <= 0.0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    if parsed_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {
            "type": "income",
            "amount": amount,
            "date": parsed_date,
        }
    )
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)

    if not is_cost_category_exists(category_name):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    if amount <= 0.0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    if parsed_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {
            "type": "cost",
            "category": category_name,
            "amount": amount,
            "date": parsed_date,
        }
    )
    return OP_SUCCESS_MSG


def get_month_result(
    report_date: tuple[int, int, int],
) -> tuple[float, float, dict[str, float]]:
    income = 0.0
    expenses = 0.0
    details: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        if not transaction:
            continue

        if not is_date_not_later(transaction["date"], report_date):
            continue

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
        if not transaction:
            continue

        if not is_date_not_later(transaction["date"], report_date):
            continue

        if transaction["type"] == "income":
            total += transaction["amount"]
        else:
            total -= transaction["amount"]

    return total


def add_month_result_line(lines: list[str], month_result: float) -> None:
    if month_result >= 0.0:
        lines.append(f"This month, the profit amounted to {month_result:.2f} rubles.")
        return

    month_loss = -month_result
    lines.append(f"This month, the loss amounted to {month_loss:.2f} rubles.")


def add_detail_lines(lines: list[str], details: dict[str, float]) -> None:
    for index, category in enumerate(sorted(details), start=FIRST_LIST_NUMBER):
        amount = format_detail_amount(details[category])
        lines.append(f"{index}. {category}: {amount}")


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

    add_month_result_line(lines, month_result)

    lines.extend(
        [
            f"Income: {income:.2f} rubles",
            f"Expenses: {expenses:.2f} rubles",
            "",
            "Details (category: amount):",
        ]
    )
    add_detail_lines(lines, details)

    return "\n".join(lines)


def handle_income_command(parts: list[str]) -> str:
    if len(parts) != CMD_INCOME_LEN:
        return UNKNOWN_COMMAND_MSG

    amount = parse_amount(parts[1])

    if amount is None:
        return UNKNOWN_COMMAND_MSG

    return income_handler(amount, parts[2])


def handle_cost_command(parts: list[str]) -> str:
    if len(parts) == CMD_CATEGORIES_LEN and parts[1] == "categories":
        return cost_categories_handler()

    if len(parts) != CMD_COST_LEN:
        return UNKNOWN_COMMAND_MSG

    amount = parse_amount(parts[2])

    if amount is None:
        return UNKNOWN_COMMAND_MSG

    result = cost_handler(parts[1], amount, parts[3])

    if result == NOT_EXISTS_CATEGORY:
        return f"{NOT_EXISTS_CATEGORY}\n{cost_categories_handler()}"

    return result


def handle_stats_command(parts: list[str]) -> str:
    if len(parts) != CMD_STATS_LEN:
        return UNKNOWN_COMMAND_MSG

    return stats_handler(parts[1])


def handle_command(command: str) -> str:
    parts = command.split()

    if not parts:
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
