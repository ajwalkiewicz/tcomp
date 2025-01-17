"""
This script compares transactions from two different files: a JSON file and a CSV file.
It imports necessary modules, defines a main function that reads transactions from both
files, compares them, and prints out the differences in a formatted table.
Transactions present in the JSON file but not in the CSV file, and vice versa,
are displayed with their date, amount (in thousands), and description.
"""

import argparse

from tabulate import tabulate

from tcomp import compare, transaction


def parse_arguments(argv: None | list[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare transactions between YNAB and other bank account"
    )
    parser.add_argument(
        "file_a",
        type=str,
        help="json file with YNAB transactions history",
    )
    parser.add_argument(
        "file_b",
        type=str,
        help="csv file with transactions from bank",
    )
    parser.add_argument(
        "--bank",
        type=str,
        default="millennium",
        required=False,
        choices=transaction.BankManager.SUPPORTED_BANKS,
        help="from what bank is the csv file, defaults to millennium",
    )

    return parser.parse_args(argv)


def main(argv: None | list[str] = None):
    args = parse_arguments(argv=argv)
    file_a, file_b, bank = args.file_a, args.file_b, args.bank

    transaction_manager = transaction.TransactionManager()
    transactions_a = transaction_manager.transactions_from_json(file_a)
    transactions_b = transaction_manager.transactions_from_csv(file_b, bank=bank)

    diff = compare(transactions_a, transactions_b)

    print(f"# In {file_a} but not in {file_b}:")
    print(
        tabulate(
            [
                (transaction.date, transaction.amount / 1000, transaction.description)
                for transaction in diff.only_in_a
            ],
            headers=["Date", "Amount", "Description"],
            tablefmt="github",
        )
    )

    print(f"\n# In {file_b} but not in {file_a}:")
    print(
        tabulate(
            [
                (transaction.date, transaction.amount / 1000, transaction.description)
                for transaction in diff.only_in_b
            ],
            headers=["Date", "Amount", "Description"],
            tablefmt="github",
        )
    )


if __name__ == "__main__":
    exit(main())
