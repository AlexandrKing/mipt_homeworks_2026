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
ZERO = 0

INCOME_COMMAND = "income"
COST_COMMAND = "cost"
STATS_COMMAND = "stats"
CATEGORIES_COMMAND = "categories"

INCOME_TYPE = INCOME_COMMAND
COST_TYPE = COST_COMMAND

TYPE_KEY = "type"
AMOUNT_KEY = "amount"
DATE_KEY = "date"
CATEGORY_KEY = "category"

DATE_SEPARATOR = "-"
CATEGORY_SEPARATOR = "::"
DECIMAL_COMMA = ","
DECIMAL_POINT = "."
PLUS_SIGN = "+"
MINUS_SIGN = "-"

Date = tuple[int, int, int]
MaybeDate = Date | None

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
    is_quad_century = year % QUAD_CENTURY_MULTIPLE == ZERO
    is_simple_leap = year % LEAP_YEAR_MULTIPLE == ZERO
    is_century = year % CENTURY_MULTIPLE == ZERO
    return is_quad_century or (is_simple_leap and not is_century)


def has_date_dashes(maybe_dt: str) -> bool:
    first_dash_is_valid = maybe_dt[FIRST_DASH_INDEX] == DATE_SEPARATOR
    second_dash_is_valid = maybe_dt[SECOND_DASH_INDEX] == DATE_SEPARATOR
    return first_dash_is_valid and second_dash_is_valid


def has_date_digits(maybe_dt: str) -> bool:
    has_day_digits = maybe_dt[:DAY_END].isdigit()
    has_month_digits = maybe_dt[MONTH_START:MONTH_END].isdigit()
    has_year_digits = maybe_dt[YEAR_START:].isdigit()
    return has_day_digits and has_month_digits and has_year_digits


def has_valid_date_format(maybe_dt: str) -> bool:
    if len(maybe_dt) != DATE_LEN:
        return False

    return has_date_dashes(maybe_dt) and has_date_digits(maybe_dt)


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


def extract_date(maybe_dt: str) -> MaybeDate:
    if not has_valid_date_format(maybe_dt):
        return None

    day = int(maybe_dt[:DAY_END])
    month = int(maybe_dt[MONTH_START:MONTH_END])
    year = int(maybe_dt[YEAR_START:])

    if not has_valid_date_values(day, month, year):
        return None

    return day, month, year


def parse_amount(maybe_amount: str) -> float | None:
    normalized = maybe_amount.replace(DECIMAL_COMMA, DECIMAL_POINT)

    if not normalized:
        return None

    number_part = (
        normalized[1:]
        if normalized.startswith((PLUS_SIGN, MINUS_SIGN))
        else normalized
    )
    amount_parts = number_part.split(DECIMAL_POINT)

    if not number_part or len(amount_parts) > MAX_AMOUNT_PARTS:
        return None

    if not any(part.isdigit() for part in amount_parts):
        return None

    for part in amount_parts:
        if part and not part.isdigit():
            return None

    return float(normalized)


def date_to_sort_key(date_value: MaybeDate) -> Date:
    if date_value is None:
        return ZERO, ZERO, ZERO

    day, month, year = date_value
    return year, month, day


def is_same_month(transaction_date: MaybeDate, report_date: Date) -> bool:
    if transaction_date is None:
        return False

    _, transaction_month, transaction_year = transaction_date
    _, report_month, report_year = report_date
    return transaction_month == report_month and transaction_year == report_year


def is_date_not_later(transaction_date: MaybeDate, report_date: Date) -> bool:
    return date_to_sort_key(transaction_date) <= date_to_sort_key(report_date)


def get_all_cost_categories() -> list[str]:
    categories: list[str] = []

    for common_category, target_categories in EXPENSE_CATEGORIES.items():
        categories.extend(
            f"{common_category}{CATEGORY_SEPARATOR}{target_category}"
            for target_category in target_categories
        )

    return categories


def cost_categories_handler() -> str:
    return "\n".join(get_all_cost_categories())


def is_cost_category_exists(category_name: str) -> bool:
    parts = category_name.split(CATEGORY_SEPARATOR)

    if len(parts) != CATEGORY_PARTS_LEN:
        return False

    common_category = parts[ZERO]
    target_category = parts[1]

    if common_category not in EXPENSE_CATEGORIES:
        return False

    return target_category in EXPENSE_CATEGORIES[common_category]


def get_target_category(category_name: str) -> str:
    return category_name.split(CATEGORY_SEPARATOR)[1]


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


def save_income(amount: float, parsed_date: Date) -> None:
    financial_transactions_storage.append(
        {
            TYPE_KEY: INCOME_TYPE,
            AMOUNT_KEY: amount,
            DATE_KEY: parsed_date,
        }
    )


def save_cost(category_name: str, amount: float, parsed_date: Date) -> None:
    financial_transactions_storage.append(
        {
            TYPE_KEY: COST_TYPE,
            CATEGORY_KEY: category_name,
            AMOUNT_KEY: amount,
            DATE_KEY: parsed_date,
        }
    )


def save_invalid_transaction() -> None:
    financial_transactions_storage.append({})


def income_handler(amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)

    if amount <= ZERO:
        save_invalid_transaction()
        return NONPOSITIVE_VALUE_MSG

    if parsed_date is None:
        save_invalid_transaction()
        return INCORRECT_DATE_MSG

    save_income(amount, parsed_date)
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)

    if not is_cost_category_exists(category_name):
        save_invalid_transaction()
        return NOT_EXISTS_CATEGORY

    if amount <= ZERO:
        save_invalid_transaction()
        return NONPOSITIVE_VALUE_MSG

    if parsed_date is None:
        save_invalid_transaction()
        return INCORRECT_DATE_MSG

    save_cost(category_name, amount, parsed_date)
    return OP_SUCCESS_MSG


def transaction_belongs_to_month(transaction: dict[str, Any], report_date: Date) -> bool:
    if not transaction:
        return False

    transaction_date = transaction[DATE_KEY]
    is_not_future_transaction = is_date_not_later(transaction_date, report_date)
    return is_not_future_transaction and is_same_month(transaction_date, report_date)


def add_cost_to_details(details: dict[str, float], transaction: dict[str, Any]) -> None:
    category = format_category_for_report(transaction[CATEGORY_KEY])
    details[category] = details.get(category, ZERO) + transaction[AMOUNT_KEY]


def get_month_result(report_date: Date) -> tuple[float, float, dict[str, float]]:
    income: float = ZERO
    expenses: float = ZERO
    details: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        if not transaction_belongs_to_month(transaction, report_date):
            continue

        if transaction[TYPE_KEY] == INCOME_TYPE:
            income += transaction[AMOUNT_KEY]
            continue

        expenses += transaction[AMOUNT_KEY]
        add_cost_to_details(details, transaction)

    return income, expenses, details


def get_total_capital(report_date: Date) -> float:
    total: float = ZERO

    for transaction in financial_transactions_storage:
        if not transaction:
            continue

        if not is_date_not_later(transaction[DATE_KEY], report_date):
            continue

        if transaction[TYPE_KEY] == INCOME_TYPE:
            total += transaction[AMOUNT_KEY]
        else:
            total -= transaction[AMOUNT_KEY]

    return total


def add_month_result_line(lines: list[str], month_result: float) -> None:
    if month_result >= ZERO:
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
    if len(parts) == CMD_CATEGORIES_LEN and parts[1] == CATEGORIES_COMMAND:
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

    command_name = parts[ZERO]

    if command_name == INCOME_COMMAND:
        return handle_income_command(parts)

    if command_name == COST_COMMAND:
        return handle_cost_command(parts)

    if command_name == STATS_COMMAND:
        return handle_stats_command(parts)

    return UNKNOWN_COMMAND_MSG


def main() -> None:
    with open(0) as stdin:
        for command in stdin:
            print(handle_command(command.strip()))


if __name__ == "__main__":
    main()