import argparse

from tabulate import tabulate

from tcomp import compare, transactions


def main(file_a: str, file_b: str, bank: str = "millenium"):
    transactions_a = transactions.transactions_from_json(file_a)
    transactions_b = transactions.transactions_from_csv(file_b, bank=bank)

    diff = compare(transactions_a, transactions_b)

    print(f"# In {file_a} but not in {file_b}:")
    print(
        tabulate(
            [
                (transaction.date, transaction.amount / 1000, transaction.description)
                for transaction in diff.atob
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
                for transaction in diff.btoa
            ],
            headers=["Date", "Amount", "Description"],
            tablefmt="github",
        )
    )


def parse_arguments() -> argparse.Namespace:
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
        default="millenium",
        required=False,
        choices=["millenium", "pkobp"],
        help="from what bank is the csv file, defaults to millenium",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    file_a, file_b, bank = args.file_a, args.file_b, args.bank
    main(file_a, file_b, bank)
